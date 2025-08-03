import requests
import json
import httpx

def build_contextual_prompt(user_question, chunks):
    import re
    
    # Clean up the chunks to remove excessive whitespace and line breaks
    cleaned_chunks = []
    for chunk in chunks:
        # Remove excessive line breaks and single character lines
        cleaned = re.sub(r'\n\s*\n', '\n', chunk)  # Replace multiple newlines with single
        cleaned = re.sub(r'\n\s*([a-zA-Z])\s*\n', r' \1 ', cleaned)  # Fix single character lines
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Replace multiple spaces with single
        cleaned = cleaned.strip()
        if cleaned:  # Only add non-empty chunks
            cleaned_chunks.append(cleaned)
    
    context = "\n\n".join(cleaned_chunks)
    prompt = f"""You are a financial assistant who only knows information about the Commercial International Bank in Egypt and cannot detail any information about other entities unless mentioned in the context provided to you. Use the following context to answer the question.
    Context:
    {context}

    Question: {user_question}

    Answer (extract the key information directly from the context):"""
    return prompt

def call_mistral(prompt, ollama_url=None):
    """
    Non-streaming call to Mistral via Ollama API.
    
    Args:
        prompt (str): The prompt to send to Mistral
        ollama_url (str, optional): Custom Ollama URL. Defaults to Docker-compatible URL.
        
    Returns:
        str: The complete response from Mistral
    """
    # Use provided URL or default to Docker-compatible URL
    if ollama_url is None:
        OLLAMA_CHAT_URL = "http://host.docker.internal:11434/api/chat"
    else:
        OLLAMA_CHAT_URL = ollama_url
        
    payload = {
        "model": "mistral",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=320)
        print("🔄 Streaming response...")
        print(type(response))
        print("response.status_code:", response.status_code)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", e)
        return "Error: Failed to connect to Ollama server. Please ensure Ollama is running."
    except Exception as ex:
        print("❌ Parsing failed:", ex)
        return "Error: Failed to parse response from Ollama server."


def call_mistral_stream(prompt, ollama_url=None):
    """
    Stream response from Mistral via Ollama API.
    
    Args:
        prompt (str): The prompt to send to Mistral
        ollama_url (str, optional): Custom Ollama URL. Defaults to Docker-compatible URL.
        
    Yields:
        str: Tokens from the streaming response
        
    Example:
        >>> for token in call_mistral_stream("What is the capital of France?"):
        ...     print(token, end="")
    """
    # Use provided URL or default to Docker-compatible URL
    if ollama_url is None:
        OLLAMA_CHAT_URL = "http://host.docker.internal:11434/api/chat"
    else:
        OLLAMA_CHAT_URL = ollama_url
        
    payload = {
        "model": "mistral",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    try:
        with requests.post(OLLAMA_CHAT_URL, json=payload, stream=True, timeout=320) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = line.decode("utf-8")
                        # Ollama streams JSON objects per line
                        try:
                            obj = json.loads(chunk)
                        except json.JSONDecodeError:
                            continue
                            
                        token = obj.get("message", {}).get("content", "")
                        if token:
                            yield token
                            
                    except Exception as e:
                        print(f"❌ Streaming parse error: {e}")
                        continue
                        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        yield "Error: Failed to connect to Ollama server. Please ensure Ollama is running."
    except Exception as ex:
        print(f"❌ Parsing failed: {ex}")
        yield "Error: Failed to parse response from Ollama server."


