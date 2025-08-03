from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer


def get_embeddings(
    text_content: str,
    file_name: Optional[str] = None,
    model_name: str = "all-MiniLM-L6-v2",
    split_delimiter: str = "\n\n"
) -> Tuple[List[str], List[List[float]]]:
    """
    Generate embeddings from text content by splitting it into chunks.
    
    Args:
        text_content (str): The text content to embed
        file_name (Optional[str]): Name of the source file for metadata tracking
        model_name (str): Name of the SentenceTransformer model to use
                         (default: "all-MiniLM-L6-v2")
        split_delimiter (str): Delimiter to split text into chunks
                              (default: "\n\n" for paragraph splits)
    
    Returns:
        Tuple[List[str], List[List[float]]]: A tuple containing:
            - texts: List of text chunks
            - embeddings: List of embedding vectors (as lists of floats)
    
    Raises:
        ValueError: If text_content is empty or None
        RuntimeError: If model loading or embedding generation fails
        
    Example:
        >>> content = "File: doc.pdf\n\nChapter 1\nSome text...\n\nChapter 2\nMore text..."
        >>> texts, embeddings = get_embeddings(content, "doc.pdf")
        >>> print(f"Generated {len(embeddings)} embeddings for {len(texts)} text chunks")
    """
    try:
        # Validate input
        if not text_content or not text_content.strip():
            raise ValueError("Text content cannot be empty or None")
        
        # Load the embedding model
        print(f"Loading embedding model: {model_name}")
        model = SentenceTransformer(model_name)
        
        # Split text into chunks
        texts = text_content.split(split_delimiter)
        
        # Filter out empty chunks
        texts = [text.strip() for text in texts if text.strip()]
        
        if not texts:
            raise ValueError("No valid text chunks found after splitting")
        
        print(f"Splitting text into {len(texts)} chunks")
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = model.encode(texts).tolist()
        
        print(f"✅ Generated {len(embeddings)} embeddings successfully")
        
        return texts, embeddings
        
    except Exception as e:
        raise RuntimeError(f"Error generating embeddings: {str(e)}")
