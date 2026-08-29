import os

_llm = None
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device_storage", "models")

def get_llm_model():
    global _llm
    if _llm is not None:
        return _llm
        
    os.makedirs(MODELS_DIR, exist_ok=True)
    gguf_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".gguf")]
    
    if not gguf_files:
        _llm = "fallback"
        return _llm
        
    model_path = os.path.join(MODELS_DIR, gguf_files[0])
    try:
        from llama_cpp import Llama
        _llm = Llama(model_path=model_path, n_ctx=2048, verbose=False)
    except Exception as e:
        _llm = "fallback"
        
    return _llm

def generate_local_response(prompt: str, context_chunks: list) -> str:
    """Generate offline response using local LLM or grounded context summarizer."""
    model = get_llm_model()
    
    if model == "fallback":
        if not context_chunks:
            return "I don't have this information in my offline knowledge packs. Please verify if you have downloaded the relevant agricultural or government pack in the Knowledge Packs tab."
            
        # Top chunk contains the most relevant grounded content
        top_chunk = context_chunks[0]
        text = top_chunk['text'].strip()
        
        # Build clean formatted response
        response = f"Based on the verified offline knowledge database, here is the official guidance:\n\n{text}"
        
        # If there are additional secondary chunks that add context, mention them
        if len(context_chunks) > 1 and context_chunks[1]['filepath'] != top_chunk['filepath']:
            sec_chunk = context_chunks[1]
            sec_text = sec_chunk['text'].strip()
            # If text is too long, take the first 300 characters
            if len(sec_text) > 300:
                sec_text = sec_text[:300] + "..."
            response += f"\n\n**Additional Cross-Referenced Advisory ({os.path.basename(sec_chunk['filepath'])}):**\n{sec_text}"
            
        return response
    else:
        try:
            system_prompt = "You are GyanSetu AI, an offline assistant. Answer the user's question using ONLY the provided context chunks. Cite sources."
            full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\nContext:\n"
            for chunk in context_chunks:
                full_prompt += f"Source: {chunk['filepath']}\nContent: {chunk['text']}\n---\n"
            full_prompt += f"\nQuestion: {prompt}\n<|assistant|>\n"
            
            output = model(full_prompt, max_tokens=256, stop=["<|user|>", "<|system|>"], echo=False)
            return output['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error during local model inference: {e}"
