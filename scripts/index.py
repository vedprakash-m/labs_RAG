#!/usr/bin/env python3
"""
Healthcare RAG Document Indexing Script
=======================================
This script downloads PDFs from Azure Blob Storage, extracts and chunks text,
creates embeddings, and stores everything in Azure AI Search for RAG applications.

Process Flow:
1. Connect to Azure Blob Storage and download PDFs
2. Extract text from PDFs using LangChain's PyPDFLoader
3. Split text into chunks with overlap for better context preservation
4. Generate embeddings using Azure OpenAI
5. Create and populate Azure AI Search index
6. Display progress and summary statistics

Prerequisites:
- Azure Storage with uploaded PDFs
- Azure OpenAI with embedding model deployed
- Azure AI Search service
- All credentials in .env file
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

def print_step(step: int, total: int, message: str):
    """Print formatted step progress"""
    print(f"\n📋 [{step}/{total}] {message}")
    print("=" * 60)

def print_progress(message: str):
    """Print progress message"""
    print(f"🔄 {message}")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")

def load_configuration():
    """
    Load all Azure configuration from environment variables.
    Returns a dictionary with all necessary configuration or None if incomplete.
    """
    print_step(1, 6, "Loading Configuration")
    
    # Load environment variables
    load_dotenv()
    
    config = {
        # Azure Storage
        'storage_connection_string': os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
        'container_name': os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'health-docs'),
        
        # Azure OpenAI
        'openai_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
        'openai_api_key': os.getenv('AZURE_OPENAI_API_KEY'),
        'embedding_model': os.getenv('EMBEDDING_MODEL_NAME', 'text-embedding-3-small'),
        
        # Azure AI Search
        'search_endpoint': os.getenv('AZURE_SEARCH_ENDPOINT'),
        'search_api_key': os.getenv('AZURE_SEARCH_API_KEY'),
        'search_index_name': os.getenv('AZURE_SEARCH_INDEX_NAME', 'healthcare-index')
    }
    
    # Validate required configuration
    missing = [key for key, value in config.items() if not value]
    
    if missing:
        print_error(f"Missing configuration: {', '.join(missing)}")
        print_info("Make sure your .env file has all required Azure credentials")
        return None
    
    print_success("Configuration loaded successfully")
    print_info(f"Storage container: {config['container_name']}")
    print_info(f"Embedding model: {config['embedding_model']}")
    print_info(f"Search index: {config['search_index_name']}")
    
    return config

def download_pdfs_from_storage(config: Dict[str, str]) -> List[Path]:
    """
    Download all PDFs from Azure Blob Storage to temporary directory.
    
    Args:
        config: Configuration dictionary with Azure credentials
        
    Returns:
        List of paths to downloaded PDF files
    """
    print_step(2, 6, "Downloading PDFs from Azure Storage")
    
    try:
        from azure.storage.blob import BlobServiceClient
        
        # Connect to Azure Storage
        print_progress("Connecting to Azure Storage...")
        blob_service_client = BlobServiceClient.from_connection_string(
            config['storage_connection_string']
        )
        container_client = blob_service_client.get_container_client(config['container_name'])
        
        # List all PDF blobs
        print_progress("Finding PDF files...")
        pdf_blobs = [blob for blob in container_client.list_blobs() 
                     if blob.name.lower().endswith('.pdf')]
        
        if not pdf_blobs:
            print_error("No PDF files found in the storage container")
            return []
        
        print_success(f"Found {len(pdf_blobs)} PDF files to download")
        
        # Create temporary directory for downloads
        temp_dir = Path(tempfile.mkdtemp())
        downloaded_files = []
        
        # Download each PDF
        for i, blob in enumerate(pdf_blobs, 1):
            print_progress(f"Downloading {blob.name} ({i}/{len(pdf_blobs)})...")
            
            # Download blob content
            blob_client = container_client.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().readall()
            
            # Save to temporary file
            temp_file = temp_dir / blob.name
            with open(temp_file, 'wb') as f:
                f.write(blob_data)
            
            downloaded_files.append(temp_file)
            print_success(f"Downloaded {blob.name} ({len(blob_data)/1024:.1f} KB)")
        
        print_success(f"All {len(downloaded_files)} PDFs downloaded successfully")
        return downloaded_files
        
    except ImportError:
        print_error("azure-storage-blob package not installed")
        print_info("Install with: pip install azure-storage-blob")
        return []
    except Exception as e:
        print_error(f"Error downloading PDFs: {e}")
        return []

def extract_and_chunk_text(pdf_files: List[Path]) -> List[Dict[str, Any]]:
    """
    Extract text from PDFs and split into chunks with overlap.
    
    Args:
        pdf_files: List of PDF file paths
        
    Returns:
        List of document chunks with metadata
    """
    print_step(3, 6, "Extracting and Chunking Text")
    
    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        # Initialize text splitter with specified chunk size and overlap
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,      # Small chunks for precise retrieval
            chunk_overlap=50,    # Overlap preserves context between chunks
            length_function=len,
            separators=["\n\n", "\n", " ", ""]  # Split on paragraphs, then sentences
        )
        
        all_chunks = []
        total_chunks = 0
        
        # Process each PDF file
        for doc_num, pdf_file in enumerate(pdf_files, 1):
            print_progress(f"Processing doc {doc_num}/{len(pdf_files)}: {pdf_file.name}")
            
            try:
                # Load PDF using LangChain's PyPDFLoader
                loader = PyPDFLoader(str(pdf_file))
                documents = loader.load()
                
                print_info(f"Loaded {len(documents)} pages from {pdf_file.name}")
                
                # Split documents into chunks
                doc_chunks = text_splitter.split_documents(documents)
                
                # Add metadata to each chunk
                for i, chunk in enumerate(doc_chunks):
                    chunk_data = {
                        'id': f"{pdf_file.stem}_chunk_{i:03d}",
                        'content': chunk.page_content,
                        'metadata': {
                            'source': pdf_file.name,
                            'page': chunk.metadata.get('page', 0),
                            'chunk_index': i,
                            'total_chunks': len(doc_chunks)
                        }
                    }
                    all_chunks.append(chunk_data)
                
                total_chunks += len(doc_chunks)
                print_success(f"Created {len(doc_chunks)} chunks from {pdf_file.name}")
                
            except Exception as e:
                print_error(f"Error processing {pdf_file.name}: {e}")
                continue
        
        print_success(f"Text extraction complete: {total_chunks} total chunks created")
        return all_chunks
        
    except ImportError as e:
        print_error(f"Required package not installed: {e}")
        print_info("Install with: pip install langchain langchain-community pypdf")
        return []
    except Exception as e:
        print_error(f"Error during text extraction: {e}")
        return []

def generate_embeddings(chunks: List[Dict[str, Any]], config: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Generate embeddings for text chunks using Azure OpenAI.
    
    Args:
        chunks: List of text chunks with metadata
        config: Configuration dictionary with Azure credentials
        
    Returns:
        List of chunks with embeddings added
    """
    print_step(4, 6, "Generating Embeddings")
    
    try:
        import openai
        
        # Configure Azure OpenAI client
        client = openai.AzureOpenAI(
            api_key=config['openai_api_key'],
            api_version="2024-02-01",
            azure_endpoint=config['openai_endpoint']
        )
        
        print_progress(f"Generating embeddings for {len(chunks)} chunks...")
        print_info(f"Using model: {config['embedding_model']}")
        
        chunks_with_embeddings = []
        batch_size = 10  # Process in small batches to avoid rate limits
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_texts = [chunk['content'] for chunk in batch]
            
            print_progress(f"Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")
            
            try:
                # Generate embeddings for the batch
                response = client.embeddings.create(
                    input=batch_texts,
                    model=config['embedding_model']
                )
                
                # Add embeddings to chunks
                for j, chunk in enumerate(batch):
                    chunk['embedding'] = response.data[j].embedding
                    chunks_with_embeddings.append(chunk)
                
            except Exception as batch_error:
                print_error(f"Error processing batch {i//batch_size + 1}: {batch_error}")
                # Continue with next batch
                continue
        
        print_success(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")
        return chunks_with_embeddings
        
    except ImportError:
        print_error("openai package not installed")
        print_info("Install with: pip install openai")
        return []
    except Exception as e:
        print_error(f"Error generating embeddings: {e}")
        return []

def create_search_index(config: Dict[str, str]) -> bool:
    """
    Create or update Azure AI Search index with proper schema.
    
    Args:
        config: Configuration dictionary with Azure credentials
        
    Returns:
        True if successful, False otherwise
    """
    print_step(5, 6, "Creating Search Index")
    
    try:
        from azure.search.documents.indexes import SearchIndexClient
        from azure.search.documents.indexes.models import (
            SearchIndex, SearchField, SearchFieldDataType, VectorSearch,
            HnswAlgorithmConfiguration, VectorSearchProfile, SemanticConfiguration,
            SemanticSearch, SemanticField
        )
        from azure.core.credentials import AzureKeyCredential
        
        # Create search index client
        credential = AzureKeyCredential(config['search_api_key'])
        index_client = SearchIndexClient(
            endpoint=config['search_endpoint'],
            credential=credential
        )
        
        print_progress("Creating search index schema...")
        
        # Define index fields
        fields = [
            SearchField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
            SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
            SearchField(name="source", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchField(name="page", type=SearchFieldDataType.Int32, filterable=True),
            SearchField(name="chunk_index", type=SearchFieldDataType.Int32, filterable=True),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,  # text-embedding-3-small dimensions
                vector_search_profile_name="healthcare-profile"
            )
        ]
        
        # Configure vector search
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="healthcare-hnsw")
            ],
            profiles=[
                VectorSearchProfile(
                    name="healthcare-profile",
                    algorithm_configuration_name="healthcare-hnsw"
                )
            ]
        )
        
        # Configure semantic search (optional but helpful for better results)
        semantic_search = SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name="healthcare-semantic-config",
                    prioritized_fields={
                        "content_fields": [SemanticField(field_name="content")]
                    }
                )
            ]
        )
        
        # Create the search index
        index = SearchIndex(
            name=config['search_index_name'],
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search
        )
        
        print_progress(f"Creating/updating index: {config['search_index_name']}")
        result = index_client.create_or_update_index(index)
        
        print_success(f"Search index '{result.name}' created successfully")
        return True
        
    except ImportError:
        print_error("azure-search-documents package not installed")
        print_info("Install with: pip install azure-search-documents")
        return False
    except Exception as e:
        print_error(f"Error creating search index: {e}")
        return False

def upload_to_search_index(chunks: List[Dict[str, Any]], config: Dict[str, str]) -> int:
    """
    Upload document chunks with embeddings to Azure AI Search index.
    
    Args:
        chunks: List of chunks with embeddings and metadata
        config: Configuration dictionary with Azure credentials
        
    Returns:
        Number of successfully uploaded documents
    """
    print_step(6, 6, "Uploading to Search Index")
    
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Create search client
        credential = AzureKeyCredential(config['search_api_key'])
        search_client = SearchClient(
            endpoint=config['search_endpoint'],
            index_name=config['search_index_name'],
            credential=credential
        )
        
        print_progress(f"Uploading {len(chunks)} documents to search index...")
        
        # Prepare documents for upload
        documents = []
        for chunk in chunks:
            doc = {
                'id': chunk['id'],
                'content': chunk['content'],
                'source': chunk['metadata']['source'],
                'page': chunk['metadata']['page'],
                'chunk_index': chunk['metadata']['chunk_index'],
                'embedding': chunk['embedding']
            }
            documents.append(doc)
        
        # Upload in batches to avoid request size limits
        batch_size = 50
        uploaded_count = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            print_progress(f"Uploading batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}...")
            
            try:
                result = search_client.upload_documents(documents=batch)
                
                # Count successful uploads
                successful = sum(1 for r in result if r.succeeded)
                uploaded_count += successful
                
                if successful != len(batch):
                    print_error(f"Only {successful}/{len(batch)} documents uploaded in this batch")
                
            except Exception as batch_error:
                print_error(f"Error uploading batch {i//batch_size + 1}: {batch_error}")
                continue
        
        print_success(f"Uploaded {uploaded_count} documents to search index")
        return uploaded_count
        
    except ImportError:
        print_error("azure-search-documents package not installed")
        print_info("Install with: pip install azure-search-documents")
        return 0
    except Exception as e:
        print_error(f"Error uploading to search index: {e}")
        return 0

def cleanup_temp_files(pdf_files: List[Path]):
    """Clean up temporary downloaded files"""
    if pdf_files:
        temp_dir = pdf_files[0].parent
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print_info("Temporary files cleaned up")
        except Exception as e:
            print_info(f"Could not clean up temporary files: {e}")

def main():
    """Main function that orchestrates the entire indexing process"""
    
    print("=" * 60)
    print("🔍 Healthcare RAG Document Indexing")
    print("=" * 60)
    print("This script processes PDFs and creates searchable vector indexes")
    
    pdf_files = []
    
    try:
        # Step 1: Load configuration
        config = load_configuration()
        if not config:
            return False
        
        # Step 2: Download PDFs from Azure Storage
        pdf_files = download_pdfs_from_storage(config)
        if not pdf_files:
            return False
        
        # Step 3: Extract and chunk text
        chunks = extract_and_chunk_text(pdf_files)
        if not chunks:
            return False
        
        # Step 4: Generate embeddings
        chunks_with_embeddings = generate_embeddings(chunks, config)
        if not chunks_with_embeddings:
            return False
        
        # Step 5: Create search index
        if not create_search_index(config):
            return False
        
        # Step 6: Upload to search index
        uploaded_count = upload_to_search_index(chunks_with_embeddings, config)
        
        # Display final summary
        print("\n" + "=" * 60)
        print("📊 INDEXING SUMMARY")
        print("=" * 60)
        
        if uploaded_count > 0:
            print_success(f"🎉 Indexing completed successfully!")
            print_info(f"📄 Processed documents: {len(pdf_files)}")
            print_info(f"📝 Total chunks created: {len(chunks)}")
            print_info(f"🔍 Chunks indexed: {uploaded_count}")
            print_info(f"📊 Average chunks per document: {len(chunks)//len(pdf_files) if pdf_files else 0}")
            
            print("\n🚀 Your healthcare RAG system is ready!")
            print_info("Next steps:")
            print_info("  • Test document search and retrieval")
            print_info("  • Build query interface for healthcare questions")
            print_info("  • Fine-tune chunk size and overlap if needed")
            
        else:
            print_error("❌ Indexing failed - no documents were uploaded")
            print_info("Check the error messages above and try again")
        
        return uploaded_count > 0
        
    finally:
        # Always clean up temporary files
        cleanup_temp_files(pdf_files)

if __name__ == "__main__":
    """
    Script entry point
    Run with: python index.py
    """
    try:
        success = main()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Indexing cancelled by user (Ctrl+C)")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("Please check your configuration and try again")
        sys.exit(1)