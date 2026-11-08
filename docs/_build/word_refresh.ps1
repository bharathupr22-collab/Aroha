param(
    [Parameter(Mandatory = $true)][string]$Docx,
    [Parameter(Mandatory = $true)][string]$Pdf
)
# Opens a .docx in Word, refreshes all fields (TOC page numbers), saves, and exports a PDF for checking.
$ErrorActionPreference = "Stop"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($Docx)
    $doc.Repaginate()
    $null = $doc.Fields.Update()
    $doc.Repaginate()
    $null = $doc.Fields.Update()
    foreach ($s in $doc.Sections) {
        foreach ($f in $s.Footers) { $null = $f.Range.Fields.Update() }
    }
    $doc.Save()
    $doc.ExportAsFixedFormat($Pdf, 17)
    Write-Output ("Pages: " + $doc.ComputeStatistics(2))
    $doc.Close($false)
}
finally {
    $word.Quit()
}
