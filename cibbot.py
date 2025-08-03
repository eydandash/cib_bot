from email.mime import message
import chainlit as cl
import httpx
import logging
import json
import requests
from vectorDB.qdrant_scripts import search_qdrant
from generation.llm import build_contextual_prompt, call_mistral_stream
from qdrant_client import QdrantClient

# ------------------ Logging Setup ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
# ---------------------------------------------------

# ------------------ Configuration ------------------
OLLAMA_URL = "http://host.docker.internal:11434/api/chat"
OLLAMA_HEALTH_URL = "http://host.docker.internal:11434/api/tags"

# Qdrant configuration - use host.docker.internal for Docker environment
QDRANT_HOST = "host.docker.internal"  # Changed from localhost for Docker
QDRANT_PORT = 6333
COLLECTION_NAME = "cib_financial_statements"

# Initialize Qdrant client
try:
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
except Exception as e:
    # Fallback to localhost if Docker internal host fails
    logger.warning(f"Failed to connect to {QDRANT_HOST}, trying localhost: {e}")
    qdrant_client = QdrantClient(host="localhost", port=QDRANT_PORT)

WELCOME_MSG = (
    "👋 Hello and welcome! I'm your assistant here to help you explore and understand CIB's financial statements. "
    "Whether you're looking for specific figures, trends, or just trying to make sense of the reports — I'm here to support you every step of the way.\n\n"
    "Feel free to ask me any questions in English or Arabic. Just type what you’re curious about!\n\n"
    "مرحبًا بك! أنا مساعدك هنا لمساعدتك في استكشاف وفهم البيانات المالية للبنك التجاري الدولي. "
    "سواء كنت تبحث عن أرقام محددة، أو اتجاهات عامة، أو تحاول فقط فهم التقارير — أنا هنا لمساعدتك.\n\n"
    "لا تتردد في طرح أي سؤال، بالعربية أو بالإنجليزية. فقط اكتب ما يدور في ذهنك!"
)

@cl.on_chat_start
async def start():
    # Check Ollama/Mistral connectivity
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(OLLAMA_HEALTH_URL)
            response.raise_for_status()
        logger.info("✅ Mistral/Ollama is up and reachable.")
    except httpx.RequestError as e:
        logger.error("❌ Could not connect to Mistral/Ollama!")
        await cl.Message(content="⚠️ Mistral (Ollama) is not reachable. Please make sure the model is running.").send()
        return

    # Check Qdrant connectivity
    try:
        collections = qdrant_client.get_collections()
        collection_exists = any(col.name == COLLECTION_NAME for col in collections.collections)
        if collection_exists:
            collection_info = qdrant_client.get_collection(COLLECTION_NAME)
            logger.info(f"✅ Qdrant is up and collection '{COLLECTION_NAME}' has {collection_info.points_count} documents.")
        else:
            logger.warning(f"⚠️ Collection '{COLLECTION_NAME}' not found. Please make sure to run the data processing pipeline first.")
            await cl.Message(content=f"⚠️ Collection '{COLLECTION_NAME}' not found. Please process your financial documents first using the notebook.").send()
    except Exception as e:
        logger.error(f"❌ Could not connect to Qdrant: {e}")
        await cl.Message(content="⚠️ Vector database is not reachable. Some features may be limited.").send()

    await cl.Message(content=WELCOME_MSG).send()

async def ask_ollama_with_context_stream(user_query: str):
    """
    Search vector database for relevant context and stream response from Mistral.
    
    Args:
        user_query (str): The user's question
        
    Yields:
        str: Tokens from the streaming response
    """
    try:
        # Step 1: Search for relevant context
        logger.info(f"� Searching vector database for: {user_query}")
        
        try:
            search_results = search_qdrant(
                query=user_query,
                client=qdrant_client,
                collection_name=COLLECTION_NAME,
                top_k=3
            )
            
            if search_results:
                # Extract text from top results
                context_chunks = [result.payload["text"] for result in search_results]
                
                # Log source files for debugging
                source_files = [result.payload.get("file_name", "Unknown") for result in search_results]
                logger.info(f"📄 Found context from files: {source_files}")
                
                # Step 2: Build contextual prompt
                prompt = build_contextual_prompt(user_query, context_chunks)
                logger.info(f"📝 Built contextual prompt with {len(context_chunks)} chunks")
                
            else:
                # Fallback: answer without context
                logger.warning("⚠️ No relevant context found, answering without context")
                prompt = f"""You are a financial assistant for the Commercial International Bank in Egypt. 
                
Question: {user_query}

Answer: I don't have specific information about that in my current database. Could you please rephrase your question or ask about CIB's financial statements, performance metrics, or other banking-related topics?"""
                
        except Exception as search_error:
            logger.error(f"❌ Vector search failed: {search_error}")
            # Fallback: answer without context
            prompt = f"""You are a financial assistant for the Commercial International Bank in Egypt. 
            
Question: {user_query}

Answer: I'm experiencing some technical difficulties accessing the financial database. Could you please try again or ask a general question about CIB?"""
        
        # Step 3: Stream response from Mistral
        logger.info(f"🤖 Streaming response from Mistral...")
        async for token in async_call_mistral_stream(prompt):
            yield token
            
    except Exception as e:
        logger.error(f"❌ Error in ask_ollama_with_context_stream: {e}")
        yield f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"


async def async_call_mistral_stream(prompt: str):
    """
    Async wrapper for the streaming Mistral function.
    
    Args:
        prompt (str): The prompt to send to Mistral
        
    Yields:
        str: Tokens from the streaming response
    """
    import asyncio
    import concurrent.futures
    
    # Run the synchronous streaming function in a thread with correct URL
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: list(call_mistral_stream(prompt, OLLAMA_URL)))
        
        # Get the result and yield tokens
        try:
            tokens = await asyncio.wrap_future(future)
            for token in tokens:
                yield token
        except Exception as e:
            logger.error(f"❌ Async streaming error: {e}")
            yield "Error generating response. Please try again."

@cl.on_message
async def handle_message(message: cl.Message):
    logger.info(f"💬 User message: {message.content}")

    # Initialize history if it doesn't exist
    if not hasattr(cl.user_session, "history"):
        cl.user_session.history = []

    cl.user_session.history.append({"role": "user", "content": message.content})

    # Stream response with vector search context
    msg = cl.Message(content="")
    async for token in ask_ollama_with_context_stream(message.content):
        await msg.stream_token(token)
    
    cl.user_session.history.append({"role": "assistant", "content": msg.content})
    await msg.send()
