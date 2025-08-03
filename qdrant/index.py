from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


def update_vector_store(
    texts: List[str],
    embeddings: List[List[float]],
    collection_name: str,
    host: str = "localhost",
    port: int = 6333,
    recreate_collection: bool = True,
    file_name: Optional[str] = None
) -> None:
    """
    Update the Qdrant vector store with new text embeddings.
    
    Args:
        texts (List[str]): List of text chunks to store
        embeddings (List[List[float]]): List of corresponding embedding vectors
        collection_name (str): Name of the Qdrant collection to use
        host (str): Qdrant server host (default: "localhost")
        port (int): Qdrant server port (default: 6333)
        recreate_collection (bool): Whether to recreate the collection if it exists
                                   (default: True - will delete existing data)
        file_name (Optional[str]): Name of the source file for metadata tracking
    
    Returns:
        None
    
    Raises:
        ValueError: If texts and embeddings lists have different lengths
        ConnectionError: If unable to connect to Qdrant server
        RuntimeError: If vector store operations fail
        
    Example:
        >>> texts = ["Document 1 content", "Document 2 content"]
        >>> embeddings = [[0.1, 0.2, ...], [0.3, 0.4, ...]]
        >>> update_vector_store(texts, embeddings, "my_collection", file_name="doc.pdf")
        >>> print("Vector store updated successfully")
    """
    try:
        # Validate inputs
        if len(texts) != len(embeddings):
            raise ValueError(
                f"Texts and embeddings must have same length. "
                f"Got {len(texts)} texts and {len(embeddings)} embeddings"
            )
        
        if not texts:
            raise ValueError("Cannot update vector store with empty data")
        
        if not collection_name.strip():
            raise ValueError("Collection name cannot be empty")
        
        # Connect to Qdrant
        print(f"Connecting to Qdrant at {host}:{port}")
        client = QdrantClient(host=host, port=port)
        
        # Get vector dimension from first embedding
        vector_size = len(embeddings[0])
        print(f"Vector dimensions: {vector_size}")
        
        # Create or recreate collection
        if recreate_collection:
            print(f"Recreating collection: {collection_name}")
            client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
        else:
            # Check if collection exists, create if not
            collections = client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if collection_name not in collection_names:
                print(f"Creating new collection: {collection_name}")
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
            else:
                print(f"Using existing collection: {collection_name}")
        
        # Prepare points for upload
        import time
        base_id = int(time.time() * 1000)  # Use timestamp to ensure unique IDs
        
        points = []
        for idx, (text, embedding) in enumerate(zip(texts, embeddings)):
            payload = {"text": text}
            if file_name:
                payload["file_name"] = file_name
            
            points.append({
                "id": base_id + idx,
                "vector": embedding,
                "payload": payload
            })
        
        # Upload to Qdrant
        print(f"Uploading {len(points)} points to vector store...")
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        print(f"✅ Successfully updated vector store '{collection_name}' with {len(points)} vectors")
        
    except Exception as e:
        if "Connection" in str(e) or "connect" in str(e).lower():
            raise ConnectionError(f"Failed to connect to Qdrant server at {host}:{port}. {str(e)}")
        else:
            raise RuntimeError(f"Error updating vector store: {str(e)}")


def search_vector_store(
    query_text: str,
    collection_name: str,
    model_name: str = "all-MiniLM-L6-v2",
    top_k: int = 1,
    host: str = "localhost",
    port: int = 6333
) -> List[Dict[str, Any]]:
    """
    Search the vector store for similar text chunks.
    
    Args:
        query_text (str): The text query to search for
        collection_name (str): Name of the Qdrant collection to search
        model_name (str): Name of the SentenceTransformer model for encoding query
        top_k (int): Number of top results to return (default: 1)
        host (str): Qdrant server host (default: "localhost")
        port (int): Qdrant server port (default: 6333)
    
    Returns:
        List[Dict[str, Any]]: List of search results with text and scores
    
    Raises:
        ValueError: If query_text is empty or collection_name is invalid
        ConnectionError: If unable to connect to Qdrant server
        RuntimeError: If search operation fails
        
    Example:
        >>> results = search_vector_store("financial data", "my_collection", top_k=3)
        >>> for result in results:
        ...     print(f"Score: {result['score']}, Text: {result['text'][:100]}...")
    """
    try:
        # Validate inputs
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")
        
        if not collection_name.strip():
            raise ValueError("Collection name cannot be empty")
        
        # Load model and encode query
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name)
        query_vector = model.encode(query_text).tolist()
        
        # Connect to Qdrant and search
        client = QdrantClient(host=host, port=port)
        
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False
        )
        
        # Format results
        results = [
            {
                "text": result.payload["text"],
                "score": result.score,
                "id": result.id
            }
            for result in search_results
        ]
        
        return results
        
    except Exception as e:
        if "Connection" in str(e) or "connect" in str(e).lower():
            raise ConnectionError(f"Failed to connect to Qdrant server at {host}:{port}. {str(e)}")
        else:
            raise RuntimeError(f"Error searching vector store: {str(e)}")
