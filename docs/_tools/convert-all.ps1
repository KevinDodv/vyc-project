# Convert 2 design docx to markdown (read-only on sources). ASCII-only to avoid encoding issues.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$proj = Split-Path -Parent $root
$files = Get-ChildItem -LiteralPath $proj -Filter *.docx
Write-Output ("found docx: " + $files.Count)
foreach ($f in $files) {
  if ($f.Name.StartsWith('L')) { $out = Join-Path $root 'lo-trinh-chuyen-doi-so.md' }
  elseif ($f.Name.StartsWith('T')) { $out = Join-Path $root 'thiet-ke-chi-tiet.md' }
  else { Write-Output ("skip " + $f.Name); continue }
  & (Join-Path $here 'docx2md.ps1') -In $f.FullName -Out $out
}
