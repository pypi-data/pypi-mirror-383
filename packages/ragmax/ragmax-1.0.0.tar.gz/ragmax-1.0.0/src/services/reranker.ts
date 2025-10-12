export class RerankerService {
  private apiKey: string;

  constructor() {
    this.apiKey = process.env.COHERE_API_KEY || '';
    if (!this.apiKey) {
      console.warn('No Cohere API key for reranking - will skip reranking');
    }
  }

  async rerank(query: string, documents: string[], topN: number = 10): Promise<Array<{ index: number; relevanceScore: number }>> {
    if (!this.apiKey) {
      // Return original order with dummy scores
      return documents.slice(0, topN).map((_, index) => ({
        index,
        relevanceScore: 1 - (index * 0.1)
      }));
    }

    try {
      const response = await fetch('https://api.cohere.ai/v1/rerank', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          query,
          documents,
          model: 'rerank-english-v3.0',
          top_n: topN,
          return_documents: false
        })
      });

      if (!response.ok) {
        console.error('Rerank API error:', response.status, response.statusText);
        // Fallback to original order
        return documents.slice(0, topN).map((_, index) => ({
          index,
          relevanceScore: 1 - (index * 0.1)
        }));
      }

      const data = await response.json();
      
      if (!data.results || !Array.isArray(data.results)) {
        console.error('Invalid rerank response:', data);
        return documents.slice(0, topN).map((_, index) => ({
          index,
          relevanceScore: 1 - (index * 0.1)
        }));
      }

      return data.results.map((result: any) => ({
        index: result.index,
        relevanceScore: result.relevance_score
      }));
    } catch (error) {
      console.error('Rerank error:', error);
      // Fallback to original order
      return documents.slice(0, topN).map((_, index) => ({
        index,
        relevanceScore: 1 - (index * 0.1)
      }));
    }
  }
}
