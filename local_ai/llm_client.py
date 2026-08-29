import os

_llm = None
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device_storage", "models")

def get_llm_model():
    global _llm
    if _llm is not None:
        return _llm
        
    os.makedirs(MODELS_DIR, exist_ok=True)
    # Search for any GGUF file in the models folder
    gguf_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".gguf")]
    
    if not gguf_files:
        print("No local GGUF models found in device_storage/models. Using RAG fallback prompt-summarizer.")
        _llm = "fallback"
        return _llm
        
    model_path = os.path.join(MODELS_DIR, gguf_files[0])
    try:
        from llama_cpp import Llama
        print(f"Initializing Llama model from {model_path}...")
        _llm = Llama(model_path=model_path, n_ctx=2048, verbose=False)
        print("Llama GGUF model loaded successfully.")
    except Exception as e:
        print(f"Failed to load llama-cpp-python: {e}. Falling back to RAG prompt-summarizer.")
        _llm = "fallback"
        
    return _llm

def generate_local_response(prompt: str, context_chunks: list) -> str:
    """Generate offline response using local LLM or fallback algorithm."""
    model = get_llm_model()
    
    if model == "fallback":
        # Grounded heuristics to build a readable, fully grounded response from context chunks
        # This simulates local RAG generation in zero-cost/offline hackathon scenarios.
        if not context_chunks:
            return "I don't have this information in my offline knowledge packs. Please verify if you have downloaded the relevant knowledge domain."
            
        # Build clean bullet points or paragraphs from matching chunks
        response = "Based on the loaded offline Knowledge Packs, here is the verified information:\n\n"
        
        for idx, chunk in enumerate(context_chunks):
            filepath = os.path.basename(chunk['filepath'])
            text = chunk['text'].strip()
            
            # Format text nicely
            lines = text.split('\n')
            formatted_text = "\n".join([f"  {line.strip()}" if line.strip() else "" for line in lines])
            
            response += f"### From {filepath} (Source {idx+1}):\n"
            response += f"{text}\n\n"
            
        response += "\n*Note: This response was generated locally and grounded in the offline database.*"
        return response
    else:
        # GGUF model generation
        try:
            # Simple instruction prompt
            system_prompt = "You are GyanSetu AI, an offline assistant. Answer the user's question using ONLY the provided context chunks. Cite sources. If the answer is not in the context, say 'I don't have this information in my offline knowledge packs'."
            full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\nContext:\n"
            
            for chunk in context_chunks:
                full_prompt += f"Source: {chunk['filepath']}\nContent: {chunk['text']}\n---\n"
                
            full_prompt += f"\nQuestion: {prompt}\n<|assistant|>\n"
            
            output = model(
                full_prompt,
                max_tokens=256,
                stop=["<|user|>", "<|system|>", "\n\n\n"],
                echo=False
            )
            return output['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error during local model inference: {e}"
