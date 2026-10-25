# -*- coding: utf-8 -*-
"""数据图公共工具：统一风格、稳定配色、保存、轴清理与向量热力图。

配色取自工作区既有数据图的实测像素（#2E5C8A 主蓝 / #E8833A 橙 / #C0392B 红 …），
保证重绘前后观感一致；Word 模式只输出 PNG，save_fig 默认 350 DPI 防中文小字发糊。
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 配色 ────────────────────────────────────────────────────────────
PALETTE = ["#2E5C8A", "#E8833A", "#C0392B", "#3E8E5A",
           "#7D5BA6", "#2A9D8F", "#D4A017", "#4A6FA5"]
PALETTE_LIGHT = ["#A9C3DD", "#F5C89A", "#E8AFA6", "#A8CFB8",
                 "#C3B0D6", "#9AD3CC", "#EBD08A", "#B4C4DC"]
COLORS = {
    "grid": "#C9CED6",      # 网格线（declutter_axes 会再提亮）与"其他"散点
    "ref_line": "#888888",  # 参考线 / 阈值线
    "text": "#333333",      # 文字
    "axis": "#4D4D4D",      # 坐标轴标签
    "muted": "#8A93A0",     # 次要元素
    "bg": "#FFFFFF",
}

CJK_FONTS = ["SimHei", "Microsoft YaHei", "SimSun", "KaiTi", "DejaVu Sans"]


def _lighten(base, t):
    """把颜色按比例 t 向白色混合（t=0 原色，t=1 纯白）。"""
    t = float(np.clip(t, 0.0, 1.0))
    r, g, b = to_rgb(base)
    return (r + (1.0 - r) * t, g + (1.0 - g) * t, b + (1.0 - b) * t)


def setup_style():
    """全局 rcParams：中文黑体、无上右边框、浅灰网格、负号正常显示。"""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": CJK_FONTS,
        "font.serif": ["Times New Roman"] + CJK_FONTS,
        "axes.unicode_minus": False,
        "font.size": 9,
        "axes.titlesize": 10.5,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.dpi": 110,
        "savefig.dpi": 350,
        "figure.facecolor": COLORS["bg"],
        "axes.facecolor": COLORS["bg"],
        "savefig.facecolor": COLORS["bg"],
        "axes.edgecolor": COLORS["axis"],
        "axes.linewidth": 0.8,
        "axes.labelcolor": COLORS["text"],
        "text.color": COLORS["text"],
        "xtick.color": COLORS["axis"],
        "ytick.color": COLORS["axis"],
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "lines.linewidth": 1.3,
        "lines.markersize": 4,
        "patch.linewidth": 0.6,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def save_fig(fig, path, dpi=350):
    """保存为 PNG（Word 模式唯一格式），自动建目录，350 DPI。"""
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=0.06,
                facecolor=COLORS["bg"], edgecolor="none")
    plt.close(fig)
    print("saved", os.path.relpath(p, ROOT))
    return p


def set_paper_placement(fig, width_fraction=1.0):
    """记录该图在论文版心中的占宽比例，供后续排版核对；不改动 figure 尺寸。"""
    fig._paper_width_fraction = float(width_fraction)
    return fig


def declutter_axes(ax, grid_axis="both"):
    """去掉上/右边框，按方向加浅灰网格，网格置于数据之下。"""
    for side in ("top", "right"):
        if side in ax.spines:
            ax.spines[side].set_visible(False)
    axis = {"x": "x", "y": "y", "both": "both"}.get(grid_axis, "both")
    ax.grid(True, axis=axis, color=_lighten(COLORS["grid"], 0.45),
            linewidth=0.7, linestyle="-", zorder=0)
    ax.set_axisbelow(True)
    return ax


def dynamic_limits(values, pad=0.06, include_zero=False):
    """按数据范围给出留白的 (lo, hi)；include_zero 时强制包含 0。"""
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return 0.0, 1.0
    lo, hi = float(np.min(v)), float(np.max(v))
    if include_zero:
        lo, hi = min(lo, 0.0), max(hi, 0.0)
    span = hi - lo
    if span <= 0:
        span = max(abs(hi), 1.0)
    return lo - span * pad, hi + span * pad


def smart_labels(labels, max_len=14, sep="…"):
    """过长标签居中截断，保留首尾可辨识字符。"""
    out = []
    for s in labels:
        s = str(s)
        if len(s) <= max_len:
            out.append(s)
        else:
            head = (max_len - 1) // 2
            tail = max_len - 1 - head
            out.append(s[:head] + sep + s[-tail:])
    return out


def auto_legend(ax, **kw):
    """统一图例样式；无句柄时安全返回 None。"""
    h, l = ax.get_legend_handles_labels()
    if not h:
        return None
    kw.setdefault("framealpha", 0.9)
    kw.setdefault("handletextpad", 0.4)
    kw.setdefault("borderpad", 0.3)
    kw.setdefault("labelspacing", 0.35)
    return ax.legend(h, l, **kw)


def draw_vector_heatmap(ax, cm, xlabels=None, ylabels=None, annot="auto",
                        fmt=".0f", cmap="YlOrRd", cbar=True,
                        cbar_label=None, origin="lower"):
    """整数计数矩阵热力图：逐格标注 + 可选色条。返回 QuadMesh。"""
    cm = np.asarray(cm, dtype=float)
    im = ax.imshow(cm, cmap=cmap, origin=origin, aspect="auto",
                   interpolation="nearest")
    if xlabels is not None:
        ax.set_xticks(np.arange(len(xlabels)))
        ax.set_xticklabels(smart_labels(xlabels), fontsize=7)
    if ylabels is not None:
        ax.set_yticks(np.arange(len(ylabels)))
        ax.set_yticklabels(smart_labels(ylabels), fontsize=7)
    if annot is not None:
        vmax = np.nanmax(cm) if cm.size else 1.0
        thr = 0.55 * vmax if annot == "auto" else None
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                val = cm[i, j]
                if not np.isfinite(val):
                    continue
                dark = (val > thr) if thr is not None else False
                ax.text(j, i, format(val, fmt), ha="center", va="center",
                        fontsize=6.2, color="white" if dark else COLORS["text"])
    for s in ("top", "right", "left", "bottom"):
        if s in ax.spines:
            ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    if cbar:
        cb = ax.figure.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
        cb.outline.set_visible(False)
        cb.ax.tick_params(labelsize=7, length=2)
        if cbar_label:
            cb.set_label(cbar_label, fontsize=8)
    return im
