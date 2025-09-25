#!/usr/bin/env python3
"""
Upload Healthcare PDFs to Azure Storage
=======================================
Uploads the generated healthcare PDFs to Azure Blob Storage for RAG processing.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def print_success(message):
    print(f"✓ {message}")

def print_error(message):
    print(f"✗ {message}")

def print_info(message):
    print(f"ℹ {message}")

def print_step(step, total, message):
    print(f"\n[{step}/{total}] {message}")
    print("=" * 50)

def upload_pdfs_to_azure():
    """Upload healthcare PDFs to Azure Storage"""
    
    # Load environment variables
    load_dotenv()
    
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'health-docs')
    
    if not connection_string:
        print_error("AZURE_STORAGE_CONNECTION_STRING not found in .env file")
        return False
    
    try:
        from azure.storage.blob import BlobServiceClient
        
        # Initialize blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get container client
        container_client = blob_service_client.get_container_client(container_name)
        
        # Find PDF files
        docs_dir = Path("docs")
        pdf_files = list(docs_dir.glob("*.pdf"))
        healthcare_pdfs = [f for f in pdf_files if f.name != "Labs_RAG.pdf"]  # Exclude the original
        
        if not healthcare_pdfs:
            print_error("No healthcare PDFs found to upload")
            return False
        
        print_info(f"Found {len(healthcare_pdfs)} healthcare PDFs to upload")
        
        uploaded_count = 0
        
        for pdf_file in healthcare_pdfs:
            try:
                print_info(f"Uploading: {pdf_file.name}")
                
                # Read file content
                with open(pdf_file, 'rb') as data:
                    # Upload blob
                    blob_client = container_client.upload_blob(
                        name=pdf_file.name,
                        data=data,
                        overwrite=True,
                        content_settings={
                            'content_type': 'application/pdf'
                        }
                    )
                
                # Get blob properties to verify
                blob_props = container_client.get_blob_client(pdf_file.name).get_blob_properties()
                size_kb = blob_props.size / 1024
                
                print_success(f"Uploaded {pdf_file.name} ({size_kb:.1f} KB)")
                uploaded_count += 1
                
            except Exception as e:
                print_error(f"Failed to upload {pdf_file.name}: {e}")
        
        return uploaded_count == len(healthcare_pdfs)
        
    except ImportError:
        print_error("azure-storage-blob package not available")
        print_info("Make sure you're in the virtual environment: source healthcare_rag_env/bin/activate")
        return False
    except Exception as e:
        print_error(f"Azure Storage error: {e}")
        return False

def main():
    print("Healthcare PDFs Azure Upload")
    print("=" * 50)
    
    total_steps = 3
    
    # Check environment
    print_step(1, total_steps, "Checking Environment Setup")
    env_file = Path(".env")
    if not env_file.exists():
        print_error(".env file not found")
        print_info("Run the Azure setup script first: pwsh setup_azure_rag.ps1")
        return False
    print_success("Environment file found")
    
    # Check for PDF files
    print_step(2, total_steps, "Checking for Healthcare PDFs")
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print_error("docs/ directory not found")
        return False
    
    pdf_files = list(docs_dir.glob("*.pdf"))
    healthcare_pdfs = [f for f in pdf_files if f.name != "Labs_RAG.pdf"]
    
    if not healthcare_pdfs:
        print_error("No healthcare PDFs found in docs/ directory")
        print_info("Run the PDF generator first: python generate_healthcare_pdfs.py")
        return False
    
    print_success(f"Found {len(healthcare_pdfs)} healthcare PDFs ready for upload")
    for pdf in healthcare_pdfs:
        size_kb = pdf.stat().st_size / 1024
        print_info(f"  • {pdf.name} ({size_kb:.1f} KB)")
    
    # Upload to Azure
    print_step(3, total_steps, "Uploading to Azure Storage")
    success = upload_pdfs_to_azure()
    
    if success:
        print_success("🎉 All healthcare PDFs uploaded to Azure Storage successfully!")
        print_info("Documents are now available for RAG processing")
        print_info("Next steps:")
        print_info("  1. Create search indexes for the uploaded documents")
        print_info("  2. Test document retrieval in your RAG application")
    else:
        print_error("❌ Upload process encountered errors")
        print_info("Check the error messages above and verify your Azure configuration")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Upload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)