# Deploy script for Windows
Write-Host "Deploying OpenShift RAG Demo..." -ForegroundColor Cyan

# Check Azure login
az account show | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to Azure. Running az login..." -ForegroundColor Yellow
    az login
}

$subscription = az account show --query name -o tsv
Write-Host "Using subscription: $subscription" -ForegroundColor Green

# Navigate to terraform
Set-Location terraform

# Initialize and deploy
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# Save outputs to .env
Write-Host "Saving credentials to .env file..." -ForegroundColor Yellow

$envContent = @"
OPENAI_ENDPOINT=$(terraform output -raw openai_endpoint)
OPENAI_KEY=$(terraform output -raw openai_key)
GPT4_DEPLOYMENT=$(terraform output -raw gpt4_deployment_name)
SEARCH_ENDPOINT=$(terraform output -raw search_endpoint)
SEARCH_KEY=$(terraform output -raw search_admin_key)
SEARCH_SERVICE=$(terraform output -raw search_service_name)
"@

$envContent | Out-File -FilePath ..\.env -Encoding UTF8

Write-Host "Deployment complete!" -ForegroundColor Green