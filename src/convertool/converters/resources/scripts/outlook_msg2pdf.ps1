param(
    [Parameter(Mandatory=$true)]
    [ValidateScript({ Test-Path $_ })]
    [String]$ifile,
    [Parameter(Mandatory=$true)]
    [ValidateScript({ Test-Path $_ })]
    [String]$ofile
)

$outlook = New-Object -ComObject Outlook.Application
$word = New-Object -ComObject Word.Application

$docname = $ofile -replace '$', '.tmp.doc'

$msg = $outlook.CreateItemFromTemplate($ifile)
$msg.SaveAs($docname, 4)

$doc = $word.Documents.Open($docname)
$doc.SaveAs($ofile, 17)
$doc.close()
