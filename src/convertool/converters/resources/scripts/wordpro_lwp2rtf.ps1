param(
    [Parameter(Mandatory = $true)]
    [ValidateScript({ Test-Path $_ })]
    [String]$ifile,
    [Parameter(Mandatory = $true)]
    [String]$ofile
)

$ofileDir = Split-Path -Path $ofile
$ofileName = Split-Path -Name $ofile -Leaf

$app = New-Object -ComObject WordPro.Application

$openResult = $app.OpenDocument($ifile)
if (-not $openResult)
{
    throw "OpenDocument rejected '$ifile'."
}

$app.SaveAs($ofileName, $ofileDir, 'Rich Text Format', $false, $false, $true)

while ($true)
{
    try
    {
        $saveResult = $app.SaveAs($ofileName, $ofileDir, 'Rich Text Format', $false, $false, $true)
        break
    }
    catch
    {
        $cause = $_.Exception
        while ($cause -and $cause.HResult -notin @(-2147418111, -2147417846))
        {
            $cause = $cause.InnerException
        }
        if (-not $cause)
        {
            throw
        }
        if ($wait.Elapsed.TotalSeconds -ge 60)
        {
            throw "Word Pro still rejects SaveAs after 60 seconds for '$fileName'. $( $cause.Message )"
        }
        if (-not $notified -and $wait.Elapsed.TotalSeconds -ge 3)
        {
            Write-Warning "Word Pro is busy. Check its window for a dialog for '$fileName'. Export will retry automatically."
            $notified = $true
        }
        Start-Sleep -Milliseconds 500
    }
}