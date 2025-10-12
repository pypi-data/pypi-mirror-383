"""
RAGMax Client
Python client for interacting with the RAGMax memory system
"""

import requests
import json
from typing import List, Dict, Optional

class MemoryClient:
    """Client for RAGMax"""
    
    def __init__(self, endpoint: str = "http://localhost:3000", api_key: Optional[str] = None):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def add_memory(
        self,
        content: str,
        platform: str = "python",
        conversation_id: str = "default",
        role: str = "user",
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Add a memory"""
        payload = {
            "platform": platform,
            "conversationId": conversation_id,
            "content": content,
            "role": role,
            "metadata": metadata or {}
        }
        
        if user_id:
            payload["userId"] = user_id
        
        response = requests.post(
            f"{self.endpoint}/memory",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def search_memory(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
        platform: Optional[str] = None,
        min_score: float = 0.5
    ) -> List[Dict]:
        """Search memories"""
        params = {
            "query": query,
            "limit": limit,
            "minScore": min_score
        }
        
        if user_id:
            params["userId"] = user_id
        if platform:
            params["platform"] = platform
        
        response = requests.get(
            f"{self.endpoint}/memory/search",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_memories(
        self,
        user_id: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get recent memories"""
        params = {"limit": limit}
        
        if user_id:
            params["userId"] = user_id
        if platform:
            params["platform"] = platform
        
        response = requests.get(
            f"{self.endpoint}/memory",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        response = requests.delete(
            f"{self.endpoint}/memory/{memory_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True
    
    def health_check(self) -> Dict:
        """Check system health"""
        response = requests.get(f"{self.endpoint}/health")
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    client = MemoryClient()
    
    # Add memory
    result = client.add_memory(
        content="I love Python and TypeScript",
        platform="python",
        role="user"
    )
    print(f"Added memory: {result['memoryId']}")
    
    # Search
    results = client.search_memory("What do I love?")
    for result in results:
        print(f"Found: {result['chunk']['content']} (score: {result['score']})")
