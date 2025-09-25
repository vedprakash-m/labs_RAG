#!/usr/bin/env python3
"""
Healthcare RAG Search Test
==========================
This script demonstrates how to search the indexed healthcare documents.
It performs both semantic vector search and keyword search on the indexed content.

Usage:
    python search_test.py "What are the symptoms of high blood pressure?"
"""

import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

def print_result(result: Dict, index: int):
    """Print a search result in a formatted way"""
    score = result.get('@search.score', 0)
    source = result.get('source', 'Unknown')
    doc_id = result.get('id', 'Unknown')
    content = result.get('content', '')
    
    print(f"\n📄 Result {index + 1} (Score: {score:.3f})")
    print(f"📋 Source: {source}")
    print(f"🔗 ID: {doc_id}")
    print(f"📝 Content:")
    print(f"   {content[:200]}{'...' if len(content) > 200 else ''}")
    print("-" * 60)

def search_documents(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search the healthcare documents using vector similarity and return top results.
    
    Args:
        query: Search query string
        top_k: Number of top results to return
        
    Returns:
        List of search results with metadata
    """
    try:
        # Import Azure Search modules
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        from openai import AzureOpenAI
        
        # Load configuration
        load_dotenv()
        
        # Azure OpenAI client for query embedding
        openai_client = AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version="2024-10-21",
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        )
        
        # Generate embedding for the query
        print(f"🔄 Generating embedding for query: '{query}'")
        response = openai_client.embeddings.create(
            input=query,
            model=os.getenv('EMBEDDING_MODEL_NAME', 'text-embedding-3-small')
        )
        query_embedding = response.data[0].embedding
        print(f"✅ Generated {len(query_embedding)}-dimensional embedding")
        
        # Create search client
        credential = AzureKeyCredential(os.getenv('AZURE_SEARCH_API_KEY'))
        search_client = SearchClient(
            endpoint=os.getenv('AZURE_SEARCH_ENDPOINT'),
            index_name=os.getenv('AZURE_SEARCH_INDEX_NAME', 'healthcare-index'),
            credential=credential
        )
        
        # Perform vector search
        print(f"🔍 Searching for top {top_k} results...")
        search_results = search_client.search(
            search_text=None,  # Pure vector search
            vector_queries=[{
                "vector": query_embedding,
                "k_nearest_neighbors": top_k,
                "fields": "embedding",
                "kind": "vector"
            }],
            select=["id", "content", "source", "page"],
            top=top_k
        )
        
        results = list(search_results)
        print(f"✅ Found {len(results)} results")
        return results
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("ℹ️  Make sure azure-search-documents and openai packages are installed")
        return []
    except Exception as e:
        print(f"❌ Search error: {e}")
        return []

def search_with_keywords(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search using traditional keyword search.
    
    Args:
        query: Search query string
        top_k: Number of top results to return
        
    Returns:
        List of search results with metadata
    """
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Load configuration
        load_dotenv()
        
        # Create search client
        credential = AzureKeyCredential(os.getenv('AZURE_SEARCH_API_KEY'))
        search_client = SearchClient(
            endpoint=os.getenv('AZURE_SEARCH_ENDPOINT'),
            index_name=os.getenv('AZURE_SEARCH_INDEX_NAME', 'healthcare-index'),
            credential=credential
        )
        
        # Perform keyword search
        print(f"🔍 Performing keyword search for: '{query}'")
        search_results = search_client.search(
            search_text=query,
            select=["id", "content", "source", "page"],
            top=top_k
        )
        
        results = list(search_results)
        print(f"✅ Found {len(results)} keyword results")
        return results
        
    except Exception as e:
        print(f"❌ Keyword search error: {e}")
        return []

def main():
    """Main function to run search tests"""
    print("=" * 60)
    print("🔍 Healthcare RAG Search Test")
    print("=" * 60)
    
    # Default query if none provided
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "What are the normal blood pressure ranges?"
    
    print(f"🎯 Query: {query}")
    print()
    
    # Perform vector search
    print("🚀 VECTOR SEARCH RESULTS")
    print("=" * 60)
    vector_results = search_documents(query, top_k=3)
    
    if vector_results:
        for i, result in enumerate(vector_results):
            print_result(result, i)
    else:
        print("❌ No vector search results found")
    
    print("\n" + "=" * 60)
    print("🔍 KEYWORD SEARCH RESULTS")
    print("=" * 60)
    
    # Perform keyword search
    keyword_results = search_with_keywords(query, top_k=3)
    
    if keyword_results:
        for i, result in enumerate(keyword_results):
            print_result(result, i)
    else:
        print("❌ No keyword search results found")
    
    print("\n" + "=" * 60)
    print("✅ Search test completed!")
    print("ℹ️  Try different queries:")
    print("ℹ️    python search_test.py 'diabetes management'")
    print("ℹ️    python search_test.py 'high blood pressure symptoms'")
    print("ℹ️    python search_test.py 'blood glucose monitoring'")

if __name__ == "__main__":
    main()