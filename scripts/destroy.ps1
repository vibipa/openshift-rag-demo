# Cleanup script for Windows
Write-Host "WARNING: This will destroy all Azure resources!" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Type 'yes' to confirm"

if ($confirm -ne "yes") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Set-Location terraform
terraform destroy -auto-approve

Write-Host "All resources destroyed" -ForegroundColor Green

if (Test-Path ..\.env) {
    Remove-Item ..\.env
    Write-Host "Removed .env file" -ForegroundColor Green
}