#!/usr/bin/env python3
"""
Healthcare RAG Query Interface
=============================
This script implements a complete RAG workflow:
1. Takes user questions from command line
2. Generates embeddings for semantic search
3. Retrieves relevant document chunks
4. Uses GPT-4o-mini to generate contextual answers
5. Provides source attribution and medical disclaimers

Usage:
    python query.py "What are the symptoms of diabetes?"
    python query.py "How often should I check my blood pressure?"
"""

import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

def print_header():
    """Print the application header"""
    print("=" * 70)
    print("🏥 Healthcare RAG Query Interface")
    print("=" * 70)
    print("Powered by Azure OpenAI and AI Search")
    print()

def print_step(step: str):
    """Print a processing step"""
    print(f"🔄 {step}")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")

def load_configuration() -> Dict[str, str]:
    """Load Azure configuration from environment variables"""
    load_dotenv()
    
    config = {
        # Azure OpenAI
        'openai_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
        'openai_api_key': os.getenv('AZURE_OPENAI_API_KEY'),
        'embedding_model': os.getenv('EMBEDDING_MODEL_NAME', 'text-embedding-3-small'),
        'chat_model': 'gpt-4o-mini',  # For answer generation
        
        # Azure AI Search
        'search_endpoint': os.getenv('AZURE_SEARCH_ENDPOINT'),
        'search_api_key': os.getenv('AZURE_SEARCH_API_KEY'),
        'search_index_name': os.getenv('AZURE_SEARCH_INDEX_NAME', 'healthcare-index')
    }
    
    # Validate required configuration
    missing = [key for key, value in config.items() if not value and key != 'chat_model']
    
    if missing:
        print_error("Missing required environment variables:")
        for var in missing:
            print(f"  - {var.upper()}")
        print_info("Please check your .env file")
        return None
    
    return config

def generate_embedding(question: str, config: Dict[str, str]) -> List[float]:
    """
    Generate embedding for the user question using Azure OpenAI.
    
    Args:
        question: User's healthcare question
        config: Configuration dictionary with API credentials
        
    Returns:
        List of floats representing the question embedding
    """
    try:
        from openai import AzureOpenAI
        
        print_step(f"Generating embedding for: '{question}'")
        
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=config['openai_api_key'],
            api_version="2024-10-21",
            azure_endpoint=config['openai_endpoint']
        )
        
        # Generate embedding
        response = client.embeddings.create(
            input=question,
            model=config['embedding_model']
        )
        
        embedding = response.data[0].embedding
        print_success(f"Generated {len(embedding)}-dimensional embedding")
        
        return embedding
        
    except ImportError:
        print_error("OpenAI package not installed")
        print_info("Install with: pip install openai")
        return None
    except Exception as e:
        print_error(f"Failed to generate embedding: {e}")
        return None

def search_documents(question: str, embedding: List[float], config: Dict[str, str], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search Azure AI Search for relevant document chunks.
    
    Args:
        question: Original user question
        embedding: Question embedding vector
        config: Configuration dictionary
        top_k: Number of top results to retrieve
        
    Returns:
        List of relevant document chunks with metadata
    """
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        print_step(f"Searching for top {top_k} relevant documents...")
        
        # Create search client
        credential = AzureKeyCredential(config['search_api_key'])
        search_client = SearchClient(
            endpoint=config['search_endpoint'],
            index_name=config['search_index_name'],
            credential=credential
        )
        
        # Perform vector search
        search_results = search_client.search(
            search_text=None,  # Pure vector search
            vector_queries=[{
                "vector": embedding,
                "k_nearest_neighbors": top_k,
                "fields": "embedding",
                "kind": "vector"
            }],
            select=["id", "content", "source", "page", "chunk_index"],
            top=top_k
        )
        
        results = list(search_results)
        print_success(f"Found {len(results)} relevant document chunks")
        
        return results
        
    except ImportError:
        print_error("Azure Search Documents package not installed")
        print_info("Install with: pip install azure-search-documents")
        return []
    except Exception as e:
        print_error(f"Search failed: {e}")
        return []

def create_rag_prompt(question: str, chunks: List[Dict[str, Any]]) -> str:
    """
    Create a prompt combining the user question with retrieved document chunks.
    
    Args:
        question: User's original question
        chunks: Retrieved document chunks with content and metadata
        
    Returns:
        Enhanced prompt for GPT-4o-mini
    """
    print_step("Creating enhanced prompt with retrieved context...")
    
    # Build context from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get('source', 'Unknown')
        page = chunk.get('page', 'Unknown')
        content = chunk.get('content', '')
        
        context_parts.append(f"Document {i} (Source: {source}, Page: {page}):\n{content}")
    
    context = "\n\n".join(context_parts)
    
    # Create the RAG prompt
    prompt = f"""You are a knowledgeable healthcare assistant. Answer the user's question based on the provided medical documents. Be accurate, helpful, and professional.

IMPORTANT GUIDELINES:
- Base your answer primarily on the provided document context
- If the documents don't contain enough information, acknowledge this limitation
- Use clear, understandable language appropriate for patients
- Include relevant details from the documents
- Always add a medical disclaimer at the end

USER QUESTION:
{question}

RELEVANT MEDICAL DOCUMENTS:
{context}

Please provide a comprehensive answer based on the above medical documents. Include specific information from the sources when relevant."""

    print_success("Enhanced prompt created with medical context")
    return prompt

def generate_answer(prompt: str, config: Dict[str, str]) -> str:
    """
    Generate an answer using GPT-4o-mini with the enhanced prompt.
    
    Args:
        prompt: Enhanced prompt with question and retrieved context
        config: Configuration dictionary with API credentials
        
    Returns:
        Generated answer from GPT-4o-mini
    """
    try:
        from openai import AzureOpenAI
        
        print_step("Generating answer with GPT-4o-mini...")
        
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=config['openai_api_key'],
            api_version="2024-10-21",
            azure_endpoint=config['openai_endpoint']
        )
        
        # Generate response using GPT-4o-mini
        response = client.chat.completions.create(
            model=config['chat_model'],
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful healthcare assistant. Provide accurate, evidence-based information while emphasizing that your responses are for educational purposes only and should not replace professional medical advice."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.3,  # Lower temperature for more consistent medical responses
            top_p=0.8
        )
        
        answer = response.choices[0].message.content.strip()
        print_success("Answer generated successfully")
        
        return answer
        
    except ImportError:
        print_error("OpenAI package not installed")
        return None
    except Exception as e:
        print_error(f"Failed to generate answer: {e}")
        return None

def display_results(question: str, answer: str, chunks: List[Dict[str, Any]]):
    """
    Display the final results with source attribution and disclaimers.
    
    Args:
        question: Original user question
        answer: Generated answer from GPT-4o-mini
        chunks: Retrieved document chunks for source attribution
    """
    print("\n" + "=" * 70)
    print("📋 HEALTHCARE RAG RESPONSE")
    print("=" * 70)
    
    # Display question
    print(f"🔍 Question: {question}")
    print()
    
    # Display answer
    print("💡 Answer:")
    print("-" * 50)
    print(answer)
    print()
    
    # Add medical disclaimer if not already included
    if "educational purposes only" not in answer.lower():
        print("⚠️  Medical Disclaimer:")
        print("This information is for educational purposes only and should not")
        print("replace professional medical advice. Always consult with qualified")
        print("healthcare professionals for medical concerns.")
        print()
    
    # Display source attribution
    print("📚 Sources Used:")
    print("-" * 50)
    for i, chunk in enumerate(chunks, 1):
        score = chunk.get('@search.score', 0)
        source = chunk.get('source', 'Unknown')
        page = chunk.get('page', 'Unknown')
        chunk_id = chunk.get('id', 'Unknown')
        
        print(f"{i}. {source} (Page {page}) - Relevance: {score:.3f}")
        print(f"   Chunk ID: {chunk_id}")
    
    print("\n" + "=" * 70)
    print("✅ Query completed successfully!")
    print("ℹ️  For more information, consult the full documents or healthcare professionals.")

def main():
    """Main function to run the healthcare RAG query interface"""
    print_header()
    
    # Get question from command line arguments
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        print("Usage: python query.py \"your healthcare question\"")
        print("\nExample queries:")
        print("  python query.py \"What are normal blood pressure ranges?\"")
        print("  python query.py \"How do I manage diabetes?\"")
        print("  python query.py \"What are the symptoms of high blood pressure?\"")
        return
    
    print(f"🎯 Processing Question: {question}")
    print()
    
    # Load configuration
    config = load_configuration()
    if not config:
        return
    
    # Step 1: Generate embedding for the question
    embedding = generate_embedding(question, config)
    if not embedding:
        return
    
    # Step 2: Search for relevant documents
    chunks = search_documents(question, embedding, config, top_k=3)
    if not chunks:
        print_warning("No relevant documents found")
        return
    
    # Step 3: Create enhanced prompt with retrieved context
    rag_prompt = create_rag_prompt(question, chunks)
    
    # Step 4: Generate answer using GPT-4o-mini
    answer = generate_answer(rag_prompt, config)
    if not answer:
        return
    
    # Step 5: Display results with source attribution
    display_results(question, answer, chunks)

if __name__ == "__main__":
    main()