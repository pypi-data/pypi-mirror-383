import os
import asyncio
import json
import httpx

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
API_URL = "https://api.perplexity.ai/chat/completions"

async def test_perplexity_query():
    system_prompt = """You are an expert assistant providing accurate answers using real-time web searches. 
    Your responses must:
    1. Be based on the most relevant web sources
    2. Include source citations for all factual claims
    3. If no relevant results are found, suggest 2-3 alternative search queries
    4. Prioritize technical accuracy, especially for programming-related questions"""
    
    test_query = "Explain the Python GIL in detail"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": system_prompt.strip()},
                        {"role": "user", "content": test_query}
                    ],
                    "stream": True
                },
                timeout=30.0
            )
            response.raise_for_status()

            print("✅ API request successful. Streaming response...")
            
            full_response = ""
            citations = set()
            usage = {}
            
            async for chunk in response.aiter_text():
                for line in chunk.split('\n'):
                    line = line.strip()
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            # Collect citations if present
                            if "citations" in data:
                                for citation in data["citations"]:
                                    citations.add(citation)
                            # Existing content handling
                            if data.get("choices"):
                                content = data["choices"][0]["delta"].get("content", "")
                                full_response += content
                                print(f"Received chunk: {content}")
                            # Add usage tracking
                            if "usage" in data:
                                usage.update(data["usage"])
                        except json.JSONDecodeError:
                            continue
                    elif line == "[DONE]":
                        print("Stream completed")
            
            print("\n📝 Full response:")
            print(full_response)
            
            # Print collected citations
            if citations:
                print("\n🔍 Citations:")
                for idx, citation in enumerate(citations, 1):
                    print(f"{idx}. {citation}")
            else:
                print("\n⚠️ No citations found in response")

            # Add usage display
            print("\n📊 Usage Stats:")
            print(json.dumps(usage, indent=2))

    except Exception as e:
        print(f"❌ API request failed: {str(e)}")

if __name__ == "__main__":
    if not PERPLEXITY_API_KEY:
        print("❌ Missing PERPLEXITY_API_KEY environment variable")
    else:
        asyncio.run(test_perplexity_query()) 