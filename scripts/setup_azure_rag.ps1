#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Azure Healthcare RAG Setup Script
.DESCRIPTION
    This PowerShell script sets up all necessary Azure resources for a healthcare RAG application:
    - Resource Group
    - Storage Account with container
    - Azure AI Search service
    - Azure OpenAI with model deployments
    - Generates .env configuration file
.NOTES
    Requires Azure CLI and PowerShell 7+
    Run: pwsh setup_azure_rag.ps1
#>

param(
    [string]$SubscriptionId = "",
    [string]$ResourceGroupName = "rg-ved-rag",
    [string]$Location = "eastus2",
    [string]$StoragePrefix = "stvedrag",
    [string]$SearchPrefix = "srch-ved-rag",
    [string]$OpenAIPrefix = "aoai-ved-rag",
    [string]$ContainerName = "health-docs"
)

# Color functions for better output
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Step {
    param([int]$Step, [int]$Total, [string]$Message)
    Write-Host ""
    Write-Host "[$Step/$Total] $Message" -ForegroundColor Blue -BackgroundColor Black
    Write-Host ("=" * 60) -ForegroundColor Blue
}

function Test-AzureCLI {
    try {
        $null = az version 2>$null
        return $true
    }
    catch {
        return $false
    }
}

function Get-RandomSuffix {
    return Get-Random -Minimum 1000 -Maximum 9999
}

function Get-TimestampSuffix {
    return (Get-Date -Format "MMddHHmm")
}

function Test-ResourceExists {
    param([string]$ResourceName, [string]$ResourceGroup, [string]$ResourceType)
    
    try {
        switch ($ResourceType) {
            "storageAccount" { 
                $result = az storage account show --name $ResourceName --resource-group $ResourceGroup 2>$null
            }
            "searchService" { 
                $result = az search service show --name $ResourceName --resource-group $ResourceGroup 2>$null
            }
            "cognitiveAccount" { 
                $result = az cognitiveservices account show --name $ResourceName --resource-group $ResourceGroup 2>$null
            }
        }
        return $null -ne $result
    }
    catch {
        return $false
    }
}

function Get-UniqueResourceName {
    param([string]$Prefix, [string]$ResourceGroup, [string]$ResourceType)
    
    $baseName = $Prefix
    if (Test-ResourceExists -ResourceName $baseName -ResourceGroup $ResourceGroup -ResourceType $ResourceType) {
        $suffix = Get-RandomSuffix
        $baseName = "$Prefix$suffix"
        Write-Warning "Resource $Prefix already exists, using $baseName instead"
    }
    return $baseName
}

function Wait-ForDeployment {
    param([string]$Message, [int]$Seconds = 30)
    Write-Info "$Message (waiting $Seconds seconds...)"
    Start-Sleep -Seconds $Seconds
}

# Main execution starts here
try {
    Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                Azure Healthcare RAG Setup                    ║
║              Automated Resource Provisioning                 ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Magenta

    Write-Info "This script will create Azure resources for your healthcare RAG project."
    Write-Info "Estimated setup time: 10-15 minutes"
    Write-Info "Estimated monthly cost: $5-20 (Free tier resources where possible)"
    
    $confirmation = Read-Host "`nProceed with Azure resource creation? (y/N)"
    if ($confirmation.ToLower() -ne 'y') {
        Write-Warning "Setup cancelled by user."
        exit 0
    }

    $totalSteps = 8

    # Step 1: Check Prerequisites
    Write-Step 1 $totalSteps "Checking Prerequisites"
    
    if (-not (Test-AzureCLI)) {
        Write-Error "Azure CLI is not installed or not in PATH"
        Write-Info "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    }
    Write-Success "Azure CLI detected"

    # Step 2: Login and Subscription
    Write-Step 2 $totalSteps "Azure Login and Subscription Setup"
    
    Write-Info "Checking current Azure login status..."
    $loginStatus = az account show 2>$null | ConvertFrom-Json
    
    if (-not $loginStatus) {
        Write-Info "Logging into Azure..."
        az login --only-show-errors
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Azure login failed"
            exit 1
        }
    }
    Write-Success "Logged into Azure"

    # List subscriptions
    Write-Info "Available subscriptions:"
    $subscriptions = az account list --query "[].{Name:name, Id:id, IsDefault:isDefault}" -o table
    Write-Host $subscriptions

    if ([string]::IsNullOrEmpty($SubscriptionId)) {
        $currentSub = az account show --query "{Name:name, Id:id}" -o json | ConvertFrom-Json
        Write-Info "Using current subscription: $($currentSub.Name) ($($currentSub.Id))"
        $SubscriptionId = $currentSub.Id
    } else {
        az account set --subscription $SubscriptionId
        Write-Success "Switched to subscription: $SubscriptionId"
    }

    # Step 3: Create Resource Group
    Write-Step 3 $totalSteps "Creating Resource Group"
    
    $rgExists = az group exists --name $ResourceGroupName
    if ($rgExists -eq "true") {
        Write-Warning "Resource group $ResourceGroupName already exists"
    } else {
        Write-Info "Creating resource group: $ResourceGroupName in $Location"
        az group create --name $ResourceGroupName --location $Location --only-show-errors
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Resource group created successfully"
        } else {
            Write-Error "Failed to create resource group"
            exit 1
        }
    }

    # Generate unique names
    $suffix = Get-RandomSuffix
    $StorageAccountName = Get-UniqueResourceName -Prefix $StoragePrefix -ResourceGroup $ResourceGroupName -ResourceType "storageAccount"
    $SearchServiceName = Get-UniqueResourceName -Prefix $SearchPrefix -ResourceGroup $ResourceGroupName -ResourceType "searchService"  
    $OpenAIServiceName = Get-UniqueResourceName -Prefix $OpenAIPrefix -ResourceGroup $ResourceGroupName -ResourceType "cognitiveAccount"

    # Step 4: Create Storage Account
    Write-Step 4 $totalSteps "Creating Storage Account"
    
    Write-Info "Creating storage account: $StorageAccountName"
    az storage account create `
        --name $StorageAccountName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --sku Standard_LRS `
        --kind StorageV2 `
        --access-tier Hot `
        --allow-blob-public-access false `
        --only-show-errors

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Storage account created successfully"
        
        # Get storage connection string
        $storageConnectionString = az storage account show-connection-string `
            --name $StorageAccountName `
            --resource-group $ResourceGroupName `
            --query "connectionString" -o tsv

        # Create container
        Write-Info "Creating container: $ContainerName"
        az storage container create `
            --name $ContainerName `
            --connection-string $storageConnectionString `
            --only-show-errors

        Write-Success "Storage container created successfully"
    } else {
        Write-Error "Failed to create storage account"
        exit 1
    }

    # Step 5: Create Azure AI Search
    Write-Step 5 $totalSteps "Creating Azure AI Search Service"
    
    Write-Info "Creating search service: $SearchServiceName (Free tier)"
    az search service create `
        --name $SearchServiceName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --sku Free `
        --only-show-errors

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Azure AI Search service created successfully"
        
        # Get search admin key
        $searchAdminKey = az search admin-key show `
            --service-name $SearchServiceName `
            --resource-group $ResourceGroupName `
            --query "primaryKey" -o tsv
            
        Write-Success "Retrieved search admin key"
    } else {
        Write-Error "Failed to create Azure AI Search service"
        exit 1
    }

    # Step 6: Create Azure OpenAI
    Write-Step 6 $totalSteps "Creating Azure OpenAI Service"
    
    Write-Info "Creating Azure OpenAI service: $OpenAIServiceName"
    az cognitiveservices account create `
        --name $OpenAIServiceName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --kind OpenAI `
        --sku S0 `
        --yes `
        --only-show-errors

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Azure OpenAI service created successfully"
        
        # Get OpenAI endpoint and key
        $openaiEndpoint = az cognitiveservices account show `
            --name $OpenAIServiceName `
            --resource-group $ResourceGroupName `
            --query "properties.endpoint" -o tsv
            
        $openaiKey = az cognitiveservices account keys list `
            --name $OpenAIServiceName `
            --resource-group $ResourceGroupName `
            --query "key1" -o tsv
            
        Write-Success "Retrieved OpenAI endpoint and key"
    } else {
        Write-Error "Failed to create Azure OpenAI service"
        exit 1
    }

    # Step 7: Deploy AI Models
    Write-Step 7 $totalSteps "Deploying AI Models"
    
    Write-Info "Deploying text-embedding-3-small model..."
    Wait-ForDeployment "Waiting for OpenAI service to be ready" 60
    
    az cognitiveservices account deployment create `
        --name $OpenAIServiceName `
        --resource-group $ResourceGroupName `
        --deployment-name "text-embedding-3-small" `
        --model-name "text-embedding-3-small" `
        --model-version "1" `
        --model-format OpenAI `
        --sku-capacity 1 `
        --sku-name "Standard" `
        --only-show-errors

    if ($LASTEXITCODE -eq 0) {
        Write-Success "text-embedding-3-small model deployed"
    } else {
        Write-Warning "Failed to deploy text-embedding-3-small model (may need manual deployment)"
    }

    Write-Info "Deploying gpt-4o-mini model..."
    Wait-ForDeployment "Waiting between model deployments" 30
    
    az cognitiveservices account deployment create `
        --name $OpenAIServiceName `
        --resource-group $ResourceGroupName `
        --deployment-name "gpt-4o-mini" `
        --model-name "gpt-4o-mini" `
        --model-version "2024-07-18" `
        --model-format OpenAI `
        --sku-capacity 1 `
        --sku-name "Standard" `
        --only-show-errors

    if ($LASTEXITCODE -eq 0) {
        Write-Success "gpt-4o-mini model deployed"
    } else {
        Write-Warning "Failed to deploy gpt-4o-mini model (may need manual deployment)"
    }

    # Step 8: Generate Configuration
    Write-Step 8 $totalSteps "Generating Configuration Files"
    
    # Create updated .env file
    $envContent = @"
# Healthcare RAG Configuration - Generated $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=$storageConnectionString
AZURE_STORAGE_CONTAINER_NAME=$ContainerName
AZURE_STORAGE_ACCOUNT_NAME=$StorageAccountName

# Azure Cognitive Search
AZURE_SEARCH_SERVICE_NAME=$SearchServiceName
AZURE_SEARCH_API_KEY=$searchAdminKey
AZURE_SEARCH_INDEX_NAME=healthcare-index
AZURE_SEARCH_ENDPOINT=https://$SearchServiceName.search.windows.net

# Azure OpenAI
OPENAI_API_KEY=$openaiKey
OPENAI_API_TYPE=azure
OPENAI_API_BASE=$openaiEndpoint
OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_ENDPOINT=$openaiEndpoint
AZURE_OPENAI_API_KEY=$openaiKey

# Model Deployment Names
EMBEDDING_MODEL_NAME=text-embedding-3-small
CHAT_MODEL_NAME=gpt-4o-mini

# Application Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5

# Azure Resource Information
AZURE_SUBSCRIPTION_ID=$SubscriptionId
AZURE_RESOURCE_GROUP=$ResourceGroupName
AZURE_LOCATION=$Location
"@

    $envContent | Out-File -FilePath ".env" -Encoding utf8
    Write-Success "Updated .env file with Azure resource configuration"

    # Create resource summary file
    $resourceSummary = @"
# Azure Healthcare RAG Resources Summary
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Created Resources

### Resource Group
- Name: $ResourceGroupName
- Location: $Location
- Subscription: $SubscriptionId

### Storage Account
- Name: $StorageAccountName
- Container: $ContainerName
- Tier: Standard_LRS (Hot)
- Estimated Monthly Cost: ~$1-5

### Azure AI Search
- Name: $SearchServiceName
- Tier: Free (Limited to 50 MB, 10,000 documents)
- Estimated Monthly Cost: $0 (Free tier)

### Azure OpenAI
- Name: $OpenAIServiceName
- Tier: Standard (S0)
- Models Deployed:
  - text-embedding-3-small (1 unit capacity)
  - gpt-4o-mini (1 unit capacity)
- Estimated Monthly Cost: ~$10-20 (depends on usage)

## Access Information
All connection strings and keys have been saved to .env file.

## Next Steps
1. Verify model deployments in Azure Portal
2. Test connectivity using the generated .env file
3. Upload healthcare documents to the storage container
4. Configure your RAG application

## Cleanup
To delete all resources: az group delete --name $ResourceGroupName --yes --no-wait
"@

    $resourceSummary | Out-File -FilePath "azure_resources_summary.md" -Encoding utf8
    Write-Success "Created resource summary file: azure_resources_summary.md"

    # Final Success Message
    Write-Host ""
    Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                    🎉 SETUP COMPLETED! 🎉                   ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

    Write-Host ""
    Write-Host "✅ RESOURCES CREATED SUCCESSFULLY:" -ForegroundColor Green
    Write-Host "   • Resource Group: $ResourceGroupName" -ForegroundColor White
    Write-Host "   • Storage Account: $StorageAccountName" -ForegroundColor White
    Write-Host "   • Search Service: $SearchServiceName" -ForegroundColor White
    Write-Host "   • OpenAI Service: $OpenAIServiceName" -ForegroundColor White
    Write-Host "   • Container: $ContainerName" -ForegroundColor White

    Write-Host ""
    Write-Host "💰 ESTIMATED MONTHLY COSTS:" -ForegroundColor Yellow
    Write-Host "   • Storage Account: ~$1-5 (depends on usage)" -ForegroundColor White
    Write-Host "   • AI Search: $0 (Free tier)" -ForegroundColor White
    Write-Host "   • OpenAI: ~$10-20 (depends on usage)" -ForegroundColor White
    Write-Host "   • Total: ~$11-25/month" -ForegroundColor White

    Write-Host ""
    Write-Host "📄 CONFIGURATION FILES:" -ForegroundColor Cyan
    Write-Host "   • .env file updated with all connection details" -ForegroundColor White
    Write-Host "   • azure_resources_summary.md created" -ForegroundColor White

    Write-Host ""
    Write-Host "🚀 NEXT STEPS:" -ForegroundColor Blue
    Write-Host "   1. Verify model deployments in Azure Portal" -ForegroundColor White
    Write-Host "   2. Test your healthcare RAG application" -ForegroundColor White
    Write-Host "   3. Upload documents to the storage container" -ForegroundColor White

    Write-Host ""
    Write-Host "🧹 CLEANUP (when needed):" -ForegroundColor Magenta
    Write-Host "   az group delete --name $ResourceGroupName --yes --no-wait" -ForegroundColor Gray

} catch {
    Write-Error "An error occurred during setup: $_"
    Write-Host "Please check the error message above and try again." -ForegroundColor Red
    exit 1
}