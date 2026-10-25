# 用 Word 只读打开 paper/main.docx，Repaginate 后逐段记录显示页码，输出 _tmp/pagemap.tsv。
# 目录页码的实测环节：md2docx.py -> (本脚本) -> make_toc.py -> toc_entries.json -> md2docx.py
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$src  = Join-Path $root "paper\main.docx"
$out  = Join-Path $root "_tmp\pagemap.tsv"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $word.Documents.Open($src, $false, $true)
$n = $doc.Paragraphs.Count
$doc.Repaginate()
Write-Host ("paras={0} pages={1}" -f $n, $doc.Content.Information(4))

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("idx`tdisp`tphys`tstyle`ttext")
for ($i = 1; $i -le $n; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $t = $p.Range.Text -replace "[`r`n`a`t]", " "
    if ($t.Length -gt 60) { $t = $t.Substring(0, 60) }
    [void]$sb.AppendLine(("{0}`t{1}`t{2}`t{3}`t{4}" -f $i,
        $p.Range.Information(1), $p.Range.Information(3), $p.Style.NameLocal, $t))
}
[System.IO.File]::WriteAllText($out, $sb.ToString(), [System.Text.Encoding]::UTF8)
$doc.Close(0)
$word.Quit()
Write-Host "written $out"
