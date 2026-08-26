param(
    [Parameter(Mandatory=$true)]
    [ValidateScript({ Test-Path $_ })]
    [String]$ifile,
    [Parameter(Mandatory=$true)]
    [ValidateScript({ Test-Path $_ })]
    [String]$ofile
)

$outlook = New-Object -ComObject Outlook.Application

$outlook.CreateItemFromTemplate($ifile).SaveAs($ofile, 4)