import sys
import os

# Include parent directory in search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from local_ai.vector_store import init_store, index_file, search_chunks, remove_pack_indices
from local_ai.rag_pipeline import query_offline_ai

if __name__ == "__main__":
    print("Initializing test vector store...")
    init_store()
    
    # Clean old tests
    remove_pack_indices("test-pack")
    
    # Index mock files
    print("Indexing mock content...")
    index_file(
        pack_id="test-pack", 
        filepath="test-pack/soil_remedy.txt", 
        text_content="For acidic soils, apply agricultural lime (calcium carbonate) to raise pH levels. For alkaline soils, add elemental sulfur."
    )
    index_file(
        pack_id="test-pack", 
        filepath="test-pack/pest_info.txt", 
        text_content="Ladybugs are natural predators that eat aphids. Marigolds planted near tomatoes deter pests with their strong scent."
    )
    
    print("Running vector search query: 'how to fix acidic soil'...")
    results = search_chunks("how to fix acidic soil", top_k=2)
    print("\n--- Search Results ---")
    for r in results:
        print(f"File: {r['filepath']} | Score: {r['score']:.4f}")
        print(f"Content: {r['text']}\n")
        
    print("Running RAG query: 'What eats aphids?'...")
    rag_response = query_offline_ai("What eats aphids?")
    print("\n--- RAG Response ---")
    print(rag_response["answer"])
    print("\nCitations:")
    for cite in rag_response["citations"]:
        print(f"- {cite['title']} ({cite['filepath']}) | Match: {cite['confidence']}%")
        
    # Clean up test
    remove_pack_indices("test-pack")
    print("\nTest completed successfully!")
