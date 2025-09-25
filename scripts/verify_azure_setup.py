#!/usr/bin/env python3
"""
Azure Healthcare RAG - Resource Verification Script
==================================================
This script verifies that all Azure resources are properly configured
and accessible using the credentials in the .env file.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import json

def print_success(message):
    print(f"✓ {message}")

def print_error(message):
    print(f"✗ {message}")

def print_info(message):
    print(f"ℹ {message}")

def print_step(step, message):
    print(f"\n[{step}] {message}")
    print("=" * 50)

def test_azure_storage():
    """Test Azure Storage connection"""
    try:
        from azure.storage.blob import BlobServiceClient
        
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        
        if not connection_string:
            print_error("AZURE_STORAGE_CONNECTION_STRING not found in .env")
            return False
            
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Test connection by listing containers
        containers = list(blob_service_client.list_containers())
        print_success(f"Connected to storage account")
        print_info(f"Found {len(containers)} containers")
        
        # Check if our container exists
        container_exists = any(c.name == container_name for c in containers)
        if container_exists:
            print_success(f"Container '{container_name}' found")
        else:
            print_error(f"Container '{container_name}' not found")
            return False
            
        return True
        
    except ImportError:
        print_error("azure-storage-blob package not installed")
        print_info("Run: pip install azure-storage-blob")
        return False
    except Exception as e:
        print_error(f"Storage connection failed: {e}")
        return False

def test_azure_search():
    """Test Azure AI Search connection"""
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        service_name = os.getenv('AZURE_SEARCH_SERVICE_NAME')
        api_key = os.getenv('AZURE_SEARCH_API_KEY')
        
        if not service_name or not api_key:
            print_error("Azure Search credentials not found in .env")
            return False
            
        # Test connection with management endpoint
        search_endpoint = f"https://{service_name}.search.windows.net"
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Get service statistics
        response = requests.get(f"{search_endpoint}/servicestats?api-version=2023-11-01", headers=headers)
        
        if response.status_code == 200:
            stats = response.json()
            print_success(f"Connected to search service: {service_name}")
            print_info(f"Storage used: {stats['storageSize']:,} bytes")
            print_info(f"Documents: {stats['documentCount']:,}")
            return True
        else:
            print_error(f"Search service connection failed: {response.status_code}")
            return False
            
    except ImportError:
        print_error("azure-search-documents package not installed")
        print_info("Run: pip install azure-search-documents")
        return False
    except Exception as e:
        print_error(f"Search connection failed: {e}")
        return False

def test_azure_openai():
    """Test Azure OpenAI connection"""
    try:
        import openai
        
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = os.getenv('OPENAI_API_BASE') or os.getenv('AZURE_OPENAI_ENDPOINT')
        api_version = os.getenv('OPENAI_API_VERSION', '2024-02-01')
        
        if not api_key or not endpoint:
            print_error("Azure OpenAI credentials not found in .env")
            return False
            
        # Configure OpenAI client for Azure
        client = openai.AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        # Test with a simple completion
        try:
            embedding_model = os.getenv('EMBEDDING_MODEL_NAME', 'text-embedding-3-small')
            response = client.embeddings.create(
                input="Test healthcare RAG setup",
                model=embedding_model
            )
            
            if response.data:
                print_success(f"Connected to Azure OpenAI")
                print_success(f"Embedding model '{embedding_model}' is working")
                print_info(f"Embedding dimensions: {len(response.data[0].embedding)}")
        except Exception as e:
            print_error(f"Embedding model test failed: {e}")
            return False
        
        # Test chat model
        try:
            chat_model = os.getenv('CHAT_MODEL_NAME', 'gpt-4o-mini')
            response = client.chat.completions.create(
                model=chat_model,
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10
            )
            
            if response.choices:
                print_success(f"Chat model '{chat_model}' is working")
                return True
        except Exception as e:
            print_error(f"Chat model test failed: {e}")
            return False
            
    except ImportError:
        print_error("openai package not installed")
        print_info("Run: pip install openai")
        return False
    except Exception as e:
        print_error(f"OpenAI connection failed: {e}")
        return False

def main():
    print("Azure Healthcare RAG - Resource Verification")
    print("=" * 50)
    
    # Load environment variables
    env_path = Path.cwd() / '.env'
    if not env_path.exists():
        print_error(".env file not found in current directory")
        print_info("Make sure you're in the project root and have run the Azure setup script")
        return False
    
    load_dotenv(env_path)
    print_info(f"Loaded environment from: {env_path}")
    
    results = []
    
    # Test each service
    print_step(1, "Testing Azure Storage Connection")
    results.append(("Azure Storage", test_azure_storage()))
    
    print_step(2, "Testing Azure AI Search Connection") 
    results.append(("Azure AI Search", test_azure_search()))
    
    print_step(3, "Testing Azure OpenAI Connection")
    results.append(("Azure OpenAI", test_azure_openai()))
    
    # Summary
    print_step("SUMMARY", "Verification Results")
    
    all_passed = True
    for service, passed in results:
        if passed:
            print_success(f"{service}: Connected and working")
        else:
            print_error(f"{service}: Failed or not configured")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print_success("🎉 All Azure services verified successfully!")
        print_info("Your healthcare RAG environment is ready to use.")
        print_info("Next steps:")
        print_info("  1. Upload documents to your storage container")
        print_info("  2. Create search indexes for your documents") 
        print_info("  3. Start building your RAG application")
    else:
        print_error("❌ Some services failed verification")
        print_info("Please check the error messages above and:")
        print_info("  1. Verify your .env file has correct credentials")
        print_info("  2. Check if resources were created successfully in Azure Portal")
        print_info("  3. Ensure all required packages are installed")
        print_info("  4. Try re-running the Azure setup script if needed")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)