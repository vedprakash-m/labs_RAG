# Azure Healthcare RAG Setup Guide

This guide helps you set up all necessary Azure resources for your healthcare RAG project using automated scripts.

## 🚀 Quick Start

### Prerequisites
1. **Azure CLI** - [Install here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **PowerShell 7+** (recommended) - [Install here](https://github.com/PowerShell/PowerShell#get-powershell)
3. **Active Azure Subscription** with permissions to create resources

### Option 1: PowerShell Script (Recommended)
```bash
# On macOS/Linux
pwsh setup_azure_rag.ps1

# On Windows (Command Prompt)
setup_azure_rag.bat

# On Windows (PowerShell)
.\setup_azure_rag.ps1
```

### Option 2: Manual Parameters
```powershell
.\setup_azure_rag.ps1 -SubscriptionId "your-sub-id" -ResourceGroupName "my-custom-rg" -Location "westus2"
```

## 📋 What Gets Created

### 🗃️ Resource Group
- **Name**: `rg-ved-rag` (or custom name)
- **Location**: `eastus2` (or custom location)
- **Purpose**: Container for all RAG resources

### 💾 Storage Account
- **Name**: `stvedrag[XXXX]` (with random suffix)
- **Type**: Standard_LRS, Hot tier
- **Container**: `health-docs` for storing documents
- **Cost**: ~$1-5/month (depending on usage)

### 🔍 Azure AI Search
- **Name**: `srch-ved-rag[XXXX]` (with random suffix)
- **Tier**: Free (50 MB storage, 10,000 documents limit)
- **Cost**: $0/month (Free tier)
- **Features**: Full-text search, vector search capabilities

### 🤖 Azure OpenAI
- **Name**: `aoai-ved-rag[XXXX]` (with random suffix)
- **Tier**: Standard (S0)
- **Models Deployed**:
  - `text-embedding-3-small` (1 unit capacity)
  - `gpt-4o-mini` (1 unit capacity)
- **Cost**: ~$10-20/month (pay-per-use)

## 💰 Cost Breakdown

| Resource | Tier | Estimated Monthly Cost |
|----------|------|----------------------|
| Storage Account | Standard_LRS | $1-5 |
| AI Search | Free | $0 |
| OpenAI Service | Standard | $10-20 |
| **Total** | | **$11-25/month** |

*Costs are estimates and depend on actual usage*

## 🔧 Script Features

### ✅ Smart Resource Naming
- Automatically adds random suffixes if resources exist
- Prevents naming conflicts
- Uses timestamp fallback if needed

### ✅ Error Handling
- Comprehensive error checking at each step
- Helpful error messages and suggestions
- Graceful failure recovery

### ✅ Progress Tracking
- Clear step-by-step progress indicators
- Color-coded output for easy reading
- Estimated completion times

### ✅ Verification Steps
- Tests Azure CLI availability
- Validates login status
- Checks resource creation success
- Verifies model deployments

### ✅ Configuration Generation
- Automatically updates `.env` file
- Includes all connection strings and keys
- Creates resource summary documentation

## 📄 Generated Files

After successful completion, you'll have:

### `.env` (Updated)
Contains all Azure connection details:
- Storage connection strings
- Search service credentials
- OpenAI API keys and endpoints
- Model deployment names

### `azure_resources_summary.md`
Comprehensive resource documentation:
- All created resource names
- Cost estimates
- Next steps guidance
- Cleanup instructions

## 🛠️ Troubleshooting

### Common Issues

#### "Azure CLI not found"
```bash
# Install Azure CLI
# macOS
brew install azure-cli

# Windows (using winget)
winget install Microsoft.AzureCLI

# Or download from: https://aka.ms/installazurecliwindows
```

#### "PowerShell execution policy" (Windows)
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### "Insufficient permissions"
- Ensure you have Contributor role on the subscription
- Check if your organization has resource creation restrictions
- Contact your Azure administrator

#### "Model deployment failed"
- Models may need manual deployment via Azure Portal
- Check regional availability for OpenAI models
- Verify quota limits in your subscription

### Manual Model Deployment

If automatic model deployment fails:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your OpenAI resource
3. Go to "Model deployments" → "Manage Deployments"
4. Deploy the following models:
   - `text-embedding-3-small` (name: `text-embedding-3-small`)
   - `gpt-4o-mini` (name: `gpt-4o-mini`)

## 🧹 Cleanup

To remove all created resources:
```bash
az group delete --name rg-ved-rag --yes --no-wait
```

⚠️ **Warning**: This will delete ALL resources in the resource group permanently!

## 🔐 Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use Azure Key Vault** for production environments
3. **Rotate keys regularly** (every 90 days recommended)
4. **Use managed identities** where possible
5. **Apply least privilege access** to resources

## 📞 Support

### Script Issues
- Check the detailed error output
- Verify prerequisites are installed
- Ensure you have proper Azure permissions

### Azure Resource Issues
- Check [Azure Status](https://status.azure.com)
- Review [Azure pricing calculator](https://azure.microsoft.com/pricing/calculator/)
- Contact Azure Support for quota increases

### Next Steps After Setup
1. Test connection using your Python RAG application
2. Upload sample healthcare documents to storage
3. Create search indexes for your documents
4. Test OpenAI model responses

## 🎯 Integration with Healthcare RAG

After running the setup script:

1. **Activate your Python environment**:
   ```bash
   source healthcare_rag_env/bin/activate
   ```

2. **Test the connection**:
   ```bash
   python src/healthcare_rag/main.py
   ```

3. **Start building your RAG pipeline** using the generated configuration in `.env`

The script perfectly integrates with your existing Python setup - all credentials are automatically configured!