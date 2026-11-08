param(
    [Parameter(Mandatory = $true)][string]$Docx,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [int]$From = 1,
    [int]$To = 0
)
# Renders pages of a .docx to PNG files using Word's own layout engine (for visual QA only).
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $true
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($Docx, $false, $true)
    $word.ActiveWindow.View.Type = 3
    $doc.Repaginate()
    $count = $doc.ComputeStatistics(2)
    if ($To -le 0 -or $To -gt $count) { $To = $count }
    $pane = $word.ActiveWindow.ActivePane
    for ($i = $From; $i -le $To; $i++) {
        $page = $pane.Pages.Item($i)
        $bytes = $page.EnhMetaFileBits
        $emf = Join-Path $OutDir ("page_{0:D2}.emf" -f $i)
        [System.IO.File]::WriteAllBytes($emf, $bytes)
        $img = [System.Drawing.Image]::FromFile($emf)
        $w = 1000
        $h = [int]($img.Height * $w / $img.Width)
        $bmp = New-Object System.Drawing.Bitmap $w, $h
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.Clear([System.Drawing.Color]::White)
        $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $g.DrawImage($img, 0, 0, $w, $h)
        $g.Dispose()
        $png = Join-Path $OutDir ("page_{0:D2}.png" -f $i)
        $bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png)
        $bmp.Dispose()
        $img.Dispose()
        Remove-Item $emf
    }
    Write-Output ("Rendered pages $From-$To of $count")
    $doc.Close($false)
}
finally {
    $word.Quit()
}
