# -*- coding: utf-8 -*-
"""paper/main.md -> paper/main.docx（竞赛论文中文排版，复刻旧稿格式）。
- A4，页边距 上下2cm/左右2.5cm；正文 10.5pt，TNR/宋体，1.5倍行距，首行缩进2字符
- 题目22pt黑体居中；一级标题14pt黑体；二级12pt黑体；图题居中；表题居中
- 三线表；图片居中5.7in；代码 Consolas 9pt；LaTeX 公式经 latex2mathml + MML2OMML.XSL 转原生 OMML
- 页脚 “第 X 页 共 Y 页” PAGE/NUMPAGES 域
"""
import os, re, sys
import latex2mathml.converter as L2M
from lxml import etree
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import (WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER,
                            WD_LINE_SPACING, WD_BREAK)
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

ROOT = r"E:\华数数据\workspaces\b6875cacdc9d"
MD = os.path.join(ROOT, "paper", "main.md")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "paper", "main.docx")
MML2OMML = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_xslt = etree.XSLT(etree.parse(MML2OMML))

# ---------- 字号（pt） ----------
SZ_TITLE, SZ_H1, SZ_H2, SZ_BODY, SZ_CAP, SZ_NOTE, SZ_CODE, SZ_TBL = 22, 14, 12, 10.5, 10.5, 9, 9, 10.5
ASCII_F, EA_F, HEI_F, MONO_F = "Times New Roman", "宋体", "SimHei", "Consolas"
WITH_TOC = os.environ.get("NO_TOC", "") != "1"

# ---------- LaTeX -> OMML ----------
def preprocess_tex(t):
    t = re.sub(r"\\tag\{[^}]*\}", "", t)
    t = t.replace(r"\operatorname*", r"\operatorname")
    for big in [r"\Bigg", r"\bigg", r"\Big", r"\big", r"\left", r"\right"]:
        t = t.replace(big, "")
    t = (t.replace(r"\,", " ").replace(r"\;", " ").replace(r"\:", " ")
           .replace(r"\!", "").replace(r"\quad", "  ").replace(r"\qquad", "  "))
    return t.strip()

def omml_element(tex):
    """返回独立的 m:oMath lxml 元素。失败返回 None。"""
    try:
        mml = L2M.convert(preprocess_tex(tex))
        dom = _xslt(etree.fromstring(mml))
        root = dom.getroot()
        return etree.fromstring(etree.tostring(root))  # 深拷贝，脱离XSLT树
    except Exception as e:
        print("  [MATH FAIL]", tex[:60], "||", repr(e)[:100])
        return None

# ---------- 字体 ----------
def set_font(run, ascii_f=ASCII_F, ea=EA_F, size=SZ_BODY, bold=False, italic=False, color=None):
    run.font.name = ascii_f
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts"); rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), ascii_f); rFonts.set(qn("w:hAnsi"), ascii_f)
    rFonts.set(qn("w:eastAsia"), ea); rFonts.set(qn("w:cs"), ascii_f)

# 行内 token：$...$ / **...** / `...` / 文本
_TOKEN_RE = re.compile(r"(\$[^$\n]+\$)|(\*\*.+?\*\*)|(`[^`\n]+`)|([^$*`]+)")
_MATH_CODE_RE = re.compile(r"(\$[^$\n]+\$)|(`[^`\n]+`)")
def _emit_math_or_code(p, seg, size, ea, ascii_f, bold):
    """处理已切出的 $...$ 或 `...` 片段。"""
    if seg.startswith("$"):
        om = omml_element(seg[1:-1])
        if om is not None:
            p._p.append(om)
        else:
            r = p.add_run(seg[1:-1]); set_font(r, ascii_f, ea, size, bold)  # 失败也去掉 $
    else:
        r = p.add_run(seg[1:-1]); set_font(r, MONO_F, MONO_F, size, bold)

def _emit_with_inner(p, text, size, ea, ascii_f, bold):
    """对一段普通/加粗文本，再解析其中可能嵌套的 $...$ 与 `...`。"""
    pos = 0
    for mm in _MATH_CODE_RE.finditer(text):
        if mm.start() > pos:
            r = p.add_run(text[pos:mm.start()]); set_font(r, ascii_f, ea, size, bold)
        _emit_math_or_code(p, mm.group(0), size, ea, ascii_f, bold)
        pos = mm.end()
    if pos < len(text):
        r = p.add_run(text[pos:]); set_font(r, ascii_f, ea, size, bold)

def add_inline(p, text, size=SZ_BODY, ea=EA_F, ascii_f=ASCII_F, base_bold=False, indent_math_ok=True):
    for m in _TOKEN_RE.finditer(text):
        math, bold, code, plain = m.groups()
        if math:
            _emit_math_or_code(p, math, size, ea, ascii_f, base_bold)
        elif bold:
            _emit_with_inner(p, bold[2:-2], size, ea, ascii_f, True)
        elif code:
            r = p.add_run(code[1:-1]); set_font(r, MONO_F, MONO_F, size, base_bold)
        elif plain:
            _emit_with_inner(p, plain, size, ea, ascii_f, base_bold)

# ---------- 段落构造 ----------
def new_para(doc, align=None, first_indent=None, line=1.5, before=0, after=0,
             left=None, keep_with_next=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    if align is not None: pf.alignment = align
    if first_indent is not None: pf.first_line_indent = Pt(first_indent)
    if line is not None: pf.line_spacing = line
    pf.space_before = Pt(before); pf.space_after = Pt(after)
    if left is not None: pf.left_indent = left
    pf.keep_with_next = keep_with_next
    return p

def abstract_para(doc, text):
    """摘要段：比正文略紧的行距，保证题目+摘要+关键词同处第一页。
    行距必须留足余量——摘要一旦占满第 1 页，关键词会被挤到第 2 页，
    目录就落到第 3 页，违反官方「第二页为目录页」。"""
    p = new_para(doc, first_indent=21, line=1.22, before=0, after=2)
    add_inline(p, text, size=SZ_BODY)
    return p


def body_para(doc, text):
    p = new_para(doc, first_indent=24)
    add_inline(p, text)
    return p

def heading(doc, text, level):
    sz = SZ_H1 if level == 1 else SZ_H2
    before, after = (9, 4.5) if level == 1 else (6, 3)
    p = new_para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, first_indent=0,
                 before=before, after=after, keep_with_next=True)
    # 大纲级别，供自动目录（TOC）收录
    pPr = p._p.get_or_add_pPr()
    ol = OxmlElement("w:outlineLvl"); ol.set(qn("w:val"), str(level - 1)); pPr.append(ol)
    r = p.add_run(text); set_font(r, ASCII_F, HEI_F, sz, True)
    return p

def caption(doc, text, before=3, after=6):
    p = new_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, first_indent=0,
                 line=1.0, before=before, after=after, keep_with_next=True)
    r = p.add_run(text); set_font(r, ASCII_F, EA_F, SZ_CAP, True)
    return p

def image_block(doc, alt, path):
    p = new_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, first_indent=0,
                 line=1.0, before=6, after=2, keep_with_next=True)
    run = p.add_run()
    try:
        run.add_picture(path, width=Inches(5.7))
    except Exception as e:
        print("  [IMG FAIL]", path, repr(e))
    caption(doc, alt)

def note_block(doc, text):
    p = new_para(doc, first_indent=0, line=1.25, before=2, after=6, left=Pt(12))
    add_inline(p, text, size=SZ_NOTE)

def list_item(doc, text):
    p = new_para(doc, first_indent=0, line=1.25, before=0, after=0, left=Pt(18))
    pf = p.paragraph_format; pf.first_line_indent = Pt(-12)
    r = p.add_run("• "); set_font(r, ASCII_F, EA_F, SZ_BODY)
    add_inline(p, text)

def code_block(doc, code):
    p = new_para(doc, first_indent=0, line=1.0, before=4, after=8, left=Pt(6))
    pf = p.paragraph_format
    # 浅灰底纹（段落）
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "F4F4F4")
    p._p.get_or_add_pPr().append(shd)
    lines = code.split("\n")
    for i, ln in enumerate(lines):
        if i > 0:
            p.add_run().add_break()
        r = p.add_run(ln if ln else " ")
        set_font(r, MONO_F, MONO_F, SZ_CODE)
        # 保留前导空格
        r._element.find(qn("w:rPr")).get_or_add_rPr() if False else None

def display_math(doc, tex, tag=None):
    if tag:
        p = new_para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, first_indent=0, line=1.5,
                     before=4, after=4)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(3.15), WD_TAB_ALIGNMENT.CENTER)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.3), WD_TAB_ALIGNMENT.RIGHT)
        p.add_run("\t")
        om = omml_element(tex)
        if om is not None: p._p.append(om)
        else: p.add_run(tex)
        p.add_run("\t")
        r = p.add_run(f"({tag})"); set_font(r, ASCII_F, EA_F, SZ_BODY)
    else:
        p = new_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, first_indent=0, line=1.5,
                     before=4, after=4)
        om = omml_element(tex)
        if om is not None: p._p.append(om)
        else: p.add_run(tex)

# ---------- 三线表 ----------
def set_cell_border_bottom(cell, sz=6):
    tcPr = cell._tc.get_or_add_tcPr()
    tcB = tcPr.find(qn("w:tcBorders"))
    if tcB is None:
        tcB = OxmlElement("w:tcBorders"); tcPr.append(tcB)
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single"); b.set(qn("w:sz"), str(sz))
    b.set(qn("w:space"), "0"); b.set(qn("w:color"), "000000")
    tcB.append(b)

def three_line_table(doc, rows, aligns):
    ncol = len(rows[0])
    table = doc.add_table(rows=len(rows), cols=ncol)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    # 表宽 100%
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW"); tblPr.append(tblW)
    tblW.set(qn("w:type"), "pct"); tblW.set(qn("w:w"), "5000")
    # 表格边框：仅 top/bottom
    borders = OxmlElement("w:tblBorders")
    for edge, sz in (("top", 12), ("bottom", 12)):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(sz))
        e.set(qn("w:space"), "0"); e.set(qn("w:color"), "000000")
        borders.append(e)
    for edge in ("left", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"), "none"); borders.append(e)
    tblPr.append(borders)
    for ri, row in enumerate(rows):
        for ci, cell_text in enumerate(row):
            cell = table.cell(ri, ci)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if ri == 0:
                set_cell_border_bottom(cell, sz=6)
            # 清空默认空段
            cp = cell.paragraphs[0]
            cp.paragraph_format.space_before = Pt(1); cp.paragraph_format.space_after = Pt(1)
            cp.paragraph_format.line_spacing = 1.0
            al = aligns[ci] if ci < len(aligns) else "left"
            cp.alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT, "right": WD_ALIGN_PARAGRAPH.RIGHT,
                            "center": WD_ALIGN_PARAGRAPH.CENTER}.get(al, WD_ALIGN_PARAGRAPH.LEFT)
            add_inline(cp, cell_text.strip(), size=SZ_TBL, base_bold=(ri == 0))
    return table

# ---------- 页脚页码 ----------
def add_field(run, instr):
    fldBegin = OxmlElement("w:fldChar"); fldBegin.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText"); instrText.set(qn("xml:space"), "preserve"); instrText.text = instr
    fldEnd = OxmlElement("w:fldChar"); fldEnd.set(qn("w:fldCharType"), "end")
    run._r.append(fldBegin); run._r.append(instrText); run._r.append(fldEnd)

def build_footer(sec):
    """页脚：页脚中部、阿拉伯数字页码（PAGE 域），只给正文节用。"""
    sec.footer.is_linked_to_previous = False
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(); set_font(r, ASCII_F, EA_F, 9); add_field(r, " PAGE ")

# ---------- 封面与目录 ----------
from docx.shared import Twips
def cover_block(doc):
    """官方模板封面：顶部居中 2x2 队伍编号/赛道表 + 一条横线。"""
    tbl = doc.add_table(rows=2, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    data = [("队伍编号", "MCB2600304"), ("赛  道", "A")]
    for ri, row in enumerate(tbl.rows):
        row.height = Twips(460)
        for ci, cell in enumerate(row.cells):
            cell.width = Twips(2217)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cp = cell.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_before = Pt(2); cp.paragraph_format.space_after = Pt(2)
            cp.paragraph_format.line_spacing = 1.0
            r = cp.add_run(data[ri][ci]); set_font(r, ASCII_F, EA_F, 11, bold=False)
    # 全细边框
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4")
        e.set(qn("w:space"), "0"); e.set(qn("w:color"), "000000")
        borders.append(e)
    tblPr.append(borders)
    # 表格下方横贯页面的浅灰横线
    line = new_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, first_indent=0, line=1.0, before=12, after=8)
    pPr = line._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single"); bot.set(qn("w:sz"), "6")
    bot.set(qn("w:space"), "1"); bot.set(qn("w:color"), "808080")
    pBdr.append(bot); pPr.append(pBdr)

def page_break(doc):
    p = new_para(doc, first_indent=0, line=1.0, before=0, after=0)
    p.add_run().add_break(WD_BREAK.PAGE)
    return p

def _load_toc_entries():
    """目录条目（含正文页码）由 _tmp/make_toc.py 依据 Word 实测分页生成。
    这里写成静态目录而不是 TOC 域：域需要在 Word 里更新才显示内容，
    而本文档近 900 段、23 张大图，自动更新目录会让 Word 长时间无响应。"""
    fp = os.path.join(ROOT, "_tmp", "toc_entries.json")
    if not os.path.exists(fp):
        return []
    import json
    return json.load(open(fp, encoding="utf-8"))


def toc_block(doc):
    """摘要后、正文前：分页 + 目录标题 + 静态目录（点线引导 + 右侧页码）。"""
    page_break(doc)
    p = new_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, first_indent=0, before=0, after=10)
    r = p.add_run("目  录"); set_font(r, ASCII_F, HEI_F, SZ_H1, True)

    entries = _load_toc_entries()
    if not entries:
        # 兜底：没有分页数据时退化为提示行，避免目录页空白
        tp = new_para(doc, first_indent=0, line=1.5)
        r2 = tp.add_run("（目录条目待生成）"); set_font(r2, ASCII_F, EA_F, 10.5)
        return

    for e in entries:
        lvl = e.get("level", 1)
        # 41 条目录必须压进一页：行距 1.12 + 一级条目 3pt 段前，实测约 645pt，页内可用 728pt
        tp = new_para(doc, first_indent=0, line=1.12,
                      before=(3 if lvl == 1 else 0), after=0,
                      left=Pt(0 if lvl == 1 else 21))
        pf = tp.paragraph_format
        pf.tab_stops.add_tab_stop(Inches(6.25), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        r = tp.add_run(e["text"])
        set_font(r, ASCII_F, EA_F, SZ_BODY if lvl == 1 else SZ_CAP, bold=(lvl == 1))
        r2 = tp.add_run("\t" + str(e["page"]))
        set_font(r2, ASCII_F, EA_F, SZ_BODY if lvl == 1 else SZ_CAP, bold=(lvl == 1))

def start_body_section(doc):
    """正文起始：另起一节（新页），页码从 1 重新编号，页脚居中阿拉伯数字，无页眉。
    前置部分（题目/摘要/关键词）单独成节且不编页码。"""
    from docx.enum.section import WD_SECTION
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.page_width = Inches(8.268); sec.page_height = Inches(11.693)
    sec.top_margin = Inches(0.787); sec.bottom_margin = Inches(0.787)
    sec.left_margin = Inches(0.985); sec.right_margin = Inches(0.985)
    # 页码从 1 起；w:pgNumType 必须排在 w:cols 之前，否则 Word 报文件损坏
    sectPr = sec._sectPr
    pg = OxmlElement("w:pgNumType"); pg.set(qn("w:start"), "1")
    cols = sectPr.find(qn("w:cols"))
    if cols is not None:
        cols.addprevious(pg)
    else:
        sectPr.append(pg)
    build_footer(sec)
    return sec

# ---------- 解析主流程 ----------
def parse_table(lines, i):
    rows = []
    j = i
    while j < len(lines) and lines[j].strip().startswith("|"):
        rows.append(lines[j].strip())
        j += 1
    # 解析
    def split_row(r):
        cells = r.strip().strip("|").split("|")
        return [c.strip() for c in cells]
    header = split_row(rows[0])
    sep = rows[1]
    aligns = []
    for c in sep.strip().strip("|").split("|"):
        c = c.strip()
        a = "center"
        if c.startswith(":") and c.endswith(":"): a = "center"
        elif c.endswith(":"): a = "right"
        elif c.startswith(":"): a = "left"
        else: a = "left"
        aligns.append(a)
    data = [split_row(r) for r in rows[2:]]
    return [header] + data, aligns, j

def main():
    text = open(MD, encoding="utf-8").read()
    lines = text.split("\n")
    doc = Document()
    # 页面
    sec = doc.sections[0]
    sec.page_width = Inches(8.268); sec.page_height = Inches(11.693)
    sec.top_margin = Inches(0.787); sec.bottom_margin = Inches(0.787)
    sec.left_margin = Inches(0.985); sec.right_margin = Inches(0.985)
    # Normal 样式
    normal = doc.styles["Normal"]
    normal.font.name = ASCII_F; normal.font.size = Pt(SZ_BODY)
    normal.element.rPr.find(qn("w:rFonts")).set(qn("w:eastAsia"), EA_F) if False else None
    rPr = normal.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts"); rPr.append(rFonts)
    for k, v in (("w:ascii", ASCII_F), ("w:hAnsi", ASCII_F), ("w:eastAsia", EA_F), ("w:cs", ASCII_F)):
        rFonts.set(qn(k), v)
    # 前置部分（题目/摘要/关键词/目录）不编页码；正文节另建并从头编号
    cover_block(doc)

    i = 0
    n = len(lines)
    in_refs = False
    toc_inserted = False
    saw_abstract = False
    in_abstract = False
    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1; continue
        # 代码块
        if s.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1  # 跳过结束 ```
            code_block(doc, "\n".join(buf))
            continue
        # 表格
        if s.startswith("|"):
            rows, aligns, j = parse_table(lines, i)
            three_line_table(doc, rows, aligns)
            new_para(doc, first_indent=0, line=1.0, before=0, after=2)
            i = j; continue
        # 图片
        mimg = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", s)
        if mimg:
            alt, path = mimg.group(1), mimg.group(2)
            if not os.path.isabs(path): path = os.path.join(ROOT, path)
            image_block(doc, alt, path)
            i += 1; continue
        # 块公式（$$ 开头）
        if s.startswith("$$"):
            if s.count("$$") >= 2 and len(s) > 4:  # 单行 $$...$$
                tex = s.strip("$").strip(); tag = None
                i += 1
            else:
                buf = []; i += 1
                while i < n and lines[i].strip() != "$$":
                    buf.append(lines[i]); i += 1
                i += 1
                joined = "\n".join(buf)
                mt = re.search(r"\\tag\{([^}]*)\}", joined)
                tag = mt.group(1) if mt else None
                tex = re.sub(r"\\tag\{[^}]*\}", "", joined).strip()
            display_math(doc, tex, tag)
            continue
        # 标题
        if s.startswith("#"):
            hashes = len(s) - len(s.lstrip("#"))
            title = s[hashes:].strip()
            if hashes == 1:
                p = new_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, first_indent=0,
                             line=1.5, before=6, after=10)
                r = p.add_run(title); set_font(r, ASCII_F, HEI_F, SZ_TITLE, True)
            elif hashes == 2:
                if title == "摘要":
                    p = new_para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, first_indent=0,
                                 before=8, after=6)
                    r = p.add_run("摘  要"); set_font(r, ASCII_F, EA_F, SZ_H2, True)
                    saw_abstract = True; in_abstract = True
                else:
                    if saw_abstract and not toc_inserted:
                        # 前置部分结束 → 正文另起一节，页码从 1 开始
                        if WITH_TOC:
                            toc_block(doc)
                        start_body_section(doc)
                        toc_inserted = True; in_abstract = False
                    in_refs = (title == "参考文献")
                    heading(doc, title, 1)
            elif hashes == 3:
                heading(doc, title, 2)
            else:
                heading(doc, title, 2)
            i += 1; continue
        # 引用
        if s.startswith(">"):
            note_block(doc, s.lstrip(">").strip()); i += 1; continue
        # 列表
        if re.match(r"^[-*]\s+", s):
            list_item(doc, re.sub(r"^[-*]\s+", "", s)); i += 1; continue
        # 表题（整行加粗、以表N开头）
        mtcap = re.match(r"^\*\*表\s*\d+[：:].*\*\*$", s)
        if mtcap:
            caption(doc, s[2:-2], before=8, after=3); i += 1; continue
        # 代码文件名标签（**code/xxx.py**）
        if re.match(r"^\*\*[^*]+\*\*$", s) and (".py" in s or "/" in s):
            p = new_para(doc, first_indent=0, line=1.25, before=6, after=2, keep_with_next=True)
            r = p.add_run(s[2:-2]); set_font(r, MONO_F, EA_F, SZ_BODY, True)
            i += 1; continue
        # 关键词
        if s.startswith("**关键词**"):
            p = new_para(doc, first_indent=0, line=1.5, before=6, after=6)
            add_inline(p, s, size=SZ_H2)
            i += 1; continue        # 参考文献条目
        if in_refs and re.match(r"^\[\d+\]", s):
            p = new_para(doc, first_indent=0, line=1.3, before=0, after=2, left=Pt(20))
            p.paragraph_format.first_line_indent = Pt(-20)
            add_inline(p, s, size=SZ_BODY)
            i += 1; continue
        # 普通段落
        if in_abstract:
            abstract_para(doc, s)
        else:
            body_para(doc, s)
        i += 1

    doc.save(OUT)
    print("SAVED", OUT)
    print("paragraphs", len(doc.paragraphs), "tables", len(doc.tables))

if __name__ == "__main__":
    main()
