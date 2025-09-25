# PDF Upload Guide

This guide explains how to use the `upload.py` script to upload PDF files to Azure Blob Storage for your healthcare RAG project.

## 📋 Prerequisites

Before using the upload script, make sure you have:

1. **Azure Storage Account** set up and configured
2. **Connection string** in your `.env` file
3. **PDF files** in the `docs/` folder
4. **Python environment** activated with required packages

## 🚀 Quick Start

### 1. Activate Your Environment
```bash
source healthcare_rag_env/bin/activate
```

### 2. Generate Healthcare PDFs (if needed)
```bash
python generate_healthcare_pdfs.py
```

### 3. Upload PDFs to Azure Storage
```bash
python upload.py
```

## 📖 How It Works

The `upload.py` script follows these steps:

### Step 1: Load Configuration
- Reads Azure Storage connection string from `.env` file
- Gets container name (defaults to `health-docs`)
- Validates that configuration is complete

### Step 2: Find PDF Files
- Scans the `docs/` folder for PDF files
- Shows file names and sizes
- Validates that files exist and are readable

### Step 3: Upload to Azure
- Connects to Azure Blob Storage
- Uploads each PDF file to the container
- Shows progress for each upload
- Overwrites existing files if they already exist

### Step 4: Show Results
- Confirms successful uploads
- Shows any errors that occurred
- Provides next steps

## 🎯 Features

### ✅ **Simple and Educational**
- Well-commented code for learning
- Clear step-by-step process
- Helpful error messages

### ✅ **Robust Error Handling**
- Graceful handling of missing files
- Network error recovery
- Validation of Azure configuration

### ✅ **Progress Tracking**
- Shows upload progress for each file
- File size confirmation
- Success/failure status for each upload

### ✅ **Beginner-Friendly**
- No complex configuration needed
- Uses existing `.env` file
- Clear instructions and feedback

## 📁 File Structure

```
docs/
├── Blood_Pressure_Management_Guide.pdf    # Generated healthcare PDF
├── Diabetes_Management_Fundamentals.pdf   # Generated healthcare PDF
└── Labs_RAG.pdf                          # Original file

.env                                       # Contains Azure credentials
upload.py                                  # Upload script
```

## 🔧 Configuration

The script uses these environment variables from your `.env` file:

```env
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER_NAME=health-docs
```

## 📊 Example Output

```
============================================================
🚀 Azure Blob Storage PDF Upload Tool
============================================================

🔹 Loading Azure Configuration
------------------------------------------------------------
✅ Azure configuration loaded successfully
ℹ️  Container name: health-docs

🔹 Finding PDF Files
------------------------------------------------------------
✅ Found 2 PDF files:
ℹ️    📄 Blood_Pressure_Management_Guide.pdf (7.1 KB)
ℹ️    📄 Diabetes_Management_Fundamentals.pdf (8.1 KB)

🔹 Uploading Files to Azure Storage
------------------------------------------------------------
ℹ️  Connecting to Azure Storage...
✅ Connected to Azure Storage successfully!
ℹ️  Uploading: Blood_Pressure_Management_Guide.pdf...
✅ ✨ Blood_Pressure_Management_Guide.pdf uploaded successfully (7.1 KB)
ℹ️  Uploading: Diabetes_Management_Fundamentals.pdf...
✅ ✨ Diabetes_Management_Fundamentals.pdf uploaded successfully (8.1 KB)

🔹 Upload Summary
------------------------------------------------------------
✅ 🎉 All 2 files uploaded successfully!
```

## ❌ Common Issues

### Issue: "Connection string not found"
**Solution**: Make sure you've run the Azure setup script:
```bash
pwsh setup_azure_rag.ps1
```

### Issue: "No PDF files found"
**Solution**: Generate PDFs first:
```bash
python generate_healthcare_pdfs.py
```

### Issue: "Azure Storage library not installed"
**Solution**: Make sure you're in the virtual environment:
```bash
source healthcare_rag_env/bin/activate
```

## 🔍 Verification

After uploading, verify your files in Azure Portal:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Storage Account (`stvedrag`)
3. Click on "Containers" → "health-docs"
4. You should see your uploaded PDF files

Or use Azure CLI:
```bash
az storage blob list --container-name health-docs --connection-string "$(grep AZURE_STORAGE_CONNECTION_STRING .env | cut -d'=' -f2-)" -o table
```

## 🎯 Next Steps

After uploading your PDFs:

1. **Create search indexes** for document retrieval
2. **Test your RAG application** with the uploaded documents
3. **Add more healthcare documents** as needed
4. **Configure document processing** in your RAG pipeline

## 🔐 Security Notes

- Never commit your `.env` file to version control
- The connection string contains sensitive credentials
- Use Azure managed identities in production environments
- Rotate storage keys regularly for security

Happy uploading! 🚀