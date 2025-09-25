#!/usr/bin/env python3
"""
Simple Azure Blob Storage Upload Script
=======================================
This script uploads PDF files from the local 'docs/' folder to Azure Blob Storage.
It's designed to be educational and easy to understand.

Prerequisites:
- Azure Storage Account with a container
- Connection string in .env file
- PDFs in the 'docs/' folder

Usage:
    python upload.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def print_step(message):
    """Print a step message with formatting"""
    print(f"\n🔹 {message}")
    print("-" * 60)

def print_success(message):
    """Print a success message in green"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message in red"""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message"""
    print(f"ℹ️  {message}")

def load_azure_config():
    """
    Load Azure configuration from environment variables.
    Returns connection string and container name, or None if missing.
    """
    print_step("Loading Azure Configuration")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get Azure Storage connection details
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'health-docs')
    
    if not connection_string:
        print_error("AZURE_STORAGE_CONNECTION_STRING not found in .env file")
        print_info("Make sure you have run the Azure setup script: pwsh setup_azure_rag.ps1")
        return None, None
    
    print_success("Azure configuration loaded successfully")
    print_info(f"Container name: {container_name}")
    return connection_string, container_name

def find_pdf_files():
    """
    Find all PDF files in the docs/ folder.
    Returns list of PDF file paths.
    """
    print_step("Finding PDF Files")
    
    docs_folder = Path("docs")
    
    # Check if docs folder exists
    if not docs_folder.exists():
        print_error("The 'docs/' folder does not exist")
        print_info("Create the folder or run: python generate_healthcare_pdfs.py")
        return []
    
    # Find all PDF files
    pdf_files = list(docs_folder.glob("*.pdf"))
    
    if not pdf_files:
        print_error("No PDF files found in docs/ folder")
        print_info("Add some PDF files to the docs/ folder first")
        return []
    
    print_success(f"Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        file_size_kb = pdf_file.stat().st_size / 1024
        print_info(f"  📄 {pdf_file.name} ({file_size_kb:.1f} KB)")
    
    return pdf_files

def upload_to_azure_storage(connection_string, container_name, pdf_files):
    """
    Upload PDF files to Azure Blob Storage.
    
    Args:
        connection_string: Azure Storage connection string
        container_name: Name of the storage container
        pdf_files: List of PDF file paths to upload
    
    Returns:
        Number of files successfully uploaded
    """
    print_step("Uploading Files to Azure Storage")
    
    try:
        # Import Azure Storage library
        from azure.storage.blob import BlobServiceClient
        
        # Create a blob service client using the connection string
        print_info("Connecting to Azure Storage...")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)
        
        print_success("Connected to Azure Storage successfully!")
        print_info(f"Uploading to container: {container_name}")
        
        uploaded_count = 0
        
        # Upload each PDF file
        for pdf_file in pdf_files:
            try:
                print_info(f"Uploading: {pdf_file.name}...")
                
                # Read the file content
                with open(pdf_file, 'rb') as file_data:
                    # Upload the blob (overwrite if it already exists)
                    blob_client = container_client.upload_blob(
                        name=pdf_file.name,
                        data=file_data,
                        overwrite=True  # Replace file if it already exists
                    )
                
                # Verify the upload by getting file properties
                blob_properties = container_client.get_blob_client(pdf_file.name).get_blob_properties()
                uploaded_size_kb = blob_properties.size / 1024
                
                print_success(f"✨ {pdf_file.name} uploaded successfully ({uploaded_size_kb:.1f} KB)")
                uploaded_count += 1
                
            except Exception as upload_error:
                print_error(f"Failed to upload {pdf_file.name}: {upload_error}")
                print_info("Continuing with next file...")
        
        return uploaded_count
        
    except ImportError:
        print_error("Azure Storage library not installed")
        print_info("Install it with: pip install azure-storage-blob")
        return 0
    except Exception as azure_error:
        print_error(f"Azure Storage error: {azure_error}")
        print_info("Check your connection string and container name")
        return 0

def main():
    """Main function that orchestrates the upload process"""
    
    print("=" * 60)
    print("🚀 Azure Blob Storage PDF Upload Tool")
    print("=" * 60)
    print("This tool uploads PDF files from docs/ folder to Azure Storage")
    
    # Step 1: Load Azure configuration
    connection_string, container_name = load_azure_config()
    if not connection_string:
        return False
    
    # Step 2: Find PDF files
    pdf_files = find_pdf_files()
    if not pdf_files:
        return False
    
    # Step 3: Upload files
    uploaded_count = upload_to_azure_storage(connection_string, container_name, pdf_files)
    
    # Step 4: Show final results
    print_step("Upload Summary")
    
    if uploaded_count == len(pdf_files):
        print_success(f"🎉 All {uploaded_count} files uploaded successfully!")
        print_info("Your PDFs are now available in Azure Storage")
        print_info("Next steps:")
        print_info("  • Create search indexes for document retrieval")
        print_info("  • Test your RAG application with the uploaded documents")
        
    elif uploaded_count > 0:
        print_info(f"⚠️  {uploaded_count} out of {len(pdf_files)} files uploaded")
        print_info("Some files had errors - check the messages above")
        
    else:
        print_error("No files were uploaded successfully")
        print_info("Please check the error messages and try again")
    
    return uploaded_count > 0

if __name__ == "__main__":
    """
    Script entry point
    This runs when you execute: python upload.py
    """
    try:
        success = main()
        
        # Exit with appropriate code
        if success:
            print("\n✨ Upload completed! Check Azure Portal to verify your files.")
            sys.exit(0)  # Success
        else:
            print("\n❌ Upload failed! Please fix the issues above and try again.")
            sys.exit(1)  # Error
            
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\n⚠️  Upload cancelled by user (Ctrl+C pressed)")
        sys.exit(1)
        
    except Exception as unexpected_error:
        # Handle any unexpected errors
        print(f"\n💥 Unexpected error occurred: {unexpected_error}")
        print("Please report this error if it persists")
        sys.exit(1)