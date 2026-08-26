param(
    [ValidateScript({ Test-Path $_ })]
    [String]$ifile,
    [ValidateScript({ Test-Path $_ })]
    [String]$ofile
)

$outlook = New-Object -ComObject Outlook.Application

$outlook.CreateItemFromTemplate($ifile).SaveAs($ofile, 4)