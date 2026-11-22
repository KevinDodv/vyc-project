# Read-only: dump strategy docx (via docx2md) and cost xlsx text to docs/_tools/tmp/. ASCII-only script.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$tmp = Join-Path $here 'tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$base = [System.IO.Directory]::GetDirectories('D:\') | Where-Object { (Split-Path -Leaf $_).StartsWith('S') -and (Split-Path -Leaf $_) -like '*qu*' } | Select-Object -First 1
Write-Output ("base: " + $base)
$files = Get-ChildItem -LiteralPath $base -Recurse -File
foreach ($f in $files) {
  Write-Output ("file: " + $f.FullName + " " + $f.Length)
  if ($f.Extension -eq '.docx') {
    & (Join-Path $here 'docx2md.ps1') -In $f.FullName -Out (Join-Path $tmp 'strategy.md')
  }
  if ($f.Extension -eq '.xlsx') {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($f.FullName)
    $out = New-Object System.Text.StringBuilder
    try {
      $ss = @()
      $e = $zip.GetEntry('xl/sharedStrings.xml')
      if ($e) {
        $x = New-Object System.Xml.XmlDocument
        $r = New-Object System.IO.StreamReader($e.Open(), [System.Text.Encoding]::UTF8); $x.LoadXml($r.ReadToEnd()); $r.Close()
        foreach ($si in $x.GetElementsByTagName('si')) { $ss += $si.InnerText }
      }
      foreach ($en in $zip.Entries) {
        if ($en.FullName -like 'xl/worksheets/sheet*.xml') {
          [void]$out.AppendLine('## ' + $en.FullName)
          $x = New-Object System.Xml.XmlDocument
          $r = New-Object System.IO.StreamReader($en.Open(), [System.Text.Encoding]::UTF8); $x.LoadXml($r.ReadToEnd()); $r.Close()
          foreach ($row in $x.GetElementsByTagName('row')) {
            $cells = @()
            foreach ($c in $row.GetElementsByTagName('c')) {
              $v = $c.GetElementsByTagName('v') | Select-Object -First 1
              $fm = $c.GetElementsByTagName('f') | Select-Object -First 1
              $val = ''
              if ($v) { $val = $v.InnerText; if ($c.GetAttribute('t') -eq 's') { $val = $ss[[int]$val] } }
              if ($val -ne '' -or $fm) { $cells += ($c.GetAttribute('r') + '=' + $val) }
            }
            if ($cells.Count) { [void]$out.AppendLine(($cells -join ' | ')) }
          }
        }
      }
    } finally { $zip.Dispose() }
    [System.IO.File]::WriteAllText((Join-Path $tmp 'cost.txt'), $out.ToString(), (New-Object System.Text.UTF8Encoding($false)))
  }
}
