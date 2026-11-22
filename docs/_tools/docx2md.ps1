param([string]$In, [string]$Out)
# Chuyển docx -> markdown (tiêu đề, danh sách, bảng). Chỉ đọc file gốc.
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($In)
try {
  $e = $zip.GetEntry('word/document.xml')
  $sr = New-Object System.IO.StreamReader($e.Open(), [System.Text.Encoding]::UTF8)
  $xml = New-Object System.Xml.XmlDocument
  $xml.LoadXml($sr.ReadToEnd()); $sr.Close()
} finally { $zip.Dispose() }
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')

function RunText($p, $keepNl = $false) {
  $sb = New-Object System.Text.StringBuilder
  foreach ($r in $p.SelectNodes('.//w:r', $ns)) {
    $t = ''
    foreach ($c in $r.ChildNodes) {
      switch ($c.LocalName) {
        't' { $t += $c.InnerText }
        'tab' { $t += ' ' }
        'br' { if ($keepNl) { $t += "`n" } else { $t += ' ' } }
      }
    }
    if ($t -eq '') { continue }
    $bold = $r.SelectSingleNode('w:rPr/w:b', $ns)
    if ($bold -and $bold.GetAttribute('val', $ns.LookupNamespace('w')) -ne '0' -and $t.Trim() -ne '') {
      [void]$sb.Append('**' + $t.Trim() + '** ')
    } else { [void]$sb.Append($t) }
  }
  if ($keepNl) { return (($sb.ToString() -replace '\*\* \*\*', ' ') -replace '[ \t]+', ' ').Trim() }
  ($sb.ToString() -replace '\*\* \*\*', ' ' -replace '\s+', ' ').Trim()
}

$lines = New-Object System.Collections.Generic.List[string]
$body = $xml.SelectSingleNode('/w:document/w:body', $ns)
foreach ($n in $body.ChildNodes) {
  if ($n.LocalName -eq 'p') {
    $raw = RunText $n $true
    if ($raw -eq '') { $lines.Add(''); continue }
    if (([regex]::Matches($raw, "`n")).Count -ge 3) {
      $lines.Add(''); $lines.Add('```sql')
      foreach ($cl in ($raw -replace '\*\*', '' -split "`n")) { $lines.Add($cl.TrimEnd()) }
      $lines.Add('```'); $lines.Add(''); continue
    }
    $txt = ($raw -replace '\s+', ' ').Trim()
    $style = $n.SelectSingleNode('w:pPr/w:pStyle', $ns)
    $sv = if ($style) { $style.GetAttribute('val', $ns.LookupNamespace('w')) } else { '' }
    $num = $n.SelectSingleNode('w:pPr/w:numPr', $ns)
    if ($sv -match '^(Heading|Title|heading)\s*(\d)?') {
      $lvl = if ($Matches[2]) { [int]$Matches[2] } else { 1 }
      if ($sv -match '^Title') { $lvl = 1 }
      $plain = $txt -replace '\*\*', ''
      $lines.Add(''); $lines.Add(('#' * $lvl) + ' ' + $plain); $lines.Add('')
    } elseif ($num) {
      $il = $num.SelectSingleNode('w:ilvl', $ns)
      $d = 0; if ($il) { $d = [int]$il.GetAttribute('val', $ns.LookupNamespace('w')) }
      $lines.Add(('  ' * $d) + '- ' + $txt)
    } else {
      if ($lines.Count -gt 0 -and $lines[$lines.Count - 1] -match '^\s*- ') { $lines.Add('') }
      $lines.Add($txt); $lines.Add('')
    }
  } elseif ($n.LocalName -eq 'tbl') {
    $lines.Add('')
    $first = $true
    foreach ($tr in $n.SelectNodes('w:tr', $ns)) {
      $cells = @()
      foreach ($tc in $tr.SelectNodes('w:tc', $ns)) {
        $ps = @(); foreach ($p in $tc.SelectNodes('w:p', $ns)) { $x = RunText $p; if ($x) { $ps += $x } }
        $cells += (($ps -join '<br>') -replace '\|', '\|')
      }
      $lines.Add('| ' + ($cells -join ' | ') + ' |')
      if ($first) { $lines.Add('|' + (' --- |' * $cells.Count)); $first = $false }
    }
    $lines.Add('')
  }
}
$text = ($lines -join "`n") -replace "(\n){3,}", "`n`n"
[System.IO.File]::WriteAllText($Out, $text.Trim() + "`n", (New-Object System.Text.UTF8Encoding($false)))
Write-Output ("OK " + $Out + " " + $lines.Count)
