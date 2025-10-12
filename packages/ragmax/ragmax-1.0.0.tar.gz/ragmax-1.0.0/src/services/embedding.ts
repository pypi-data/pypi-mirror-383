export class EmbeddingService {
  private provider: 'cohere' | 'voyage';
  private apiKey: string;

  constructor() {
    // Prefer Voyage AI, fallback to Cohere
    if (process.env.VOYAGE_API_KEY) {
      this.provider = 'voyage';
      this.apiKey = process.env.VOYAGE_API_KEY;
    } else if (process.env.COHERE_API_KEY) {
      this.provider = 'cohere';
      this.apiKey = process.env.COHERE_API_KEY;
    } else {
      throw new Error('No embedding API key configured');
    }
  }

  async embed(text: string): Promise<number[]> {
    if (this.provider === 'voyage') {
      return this.voyageEmbed(text);
    } else {
      return this.cohereEmbed(text);
    }
  }

  async embedBatch(texts: string[]): Promise<number[][]> {
    if (this.provider === 'voyage') {
      return this.voyageEmbedBatch(texts);
    } else {
      return this.cohereEmbedBatch(texts);
    }
  }

  private async voyageEmbed(text: string): Promise<number[]> {
    const response = await fetch('https://api.voyageai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        input: text,
        model: 'voyage-3'
      })
    });

    const data = await response.json();
    return data.data[0].embedding;
  }

  private async voyageEmbedBatch(texts: string[]): Promise<number[][]> {
    const response = await fetch('https://api.voyageai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        input: texts,
        model: 'voyage-3'
      })
    });

    const data = await response.json();
    return data.data.map((item: any) => item.embedding);
  }

  private async cohereEmbed(text: string): Promise<number[]> {
    const response = await fetch('https://api.cohere.ai/v1/embed', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        texts: [text],
        model: 'embed-english-v3.0',
        input_type: 'search_document'
      })
    });

    const data = await response.json();
    return data.embeddings[0];
  }

  private async cohereEmbedBatch(texts: string[]): Promise<number[][]> {
    const response = await fetch('https://api.cohere.ai/v1/embed', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        texts,
        model: 'embed-english-v3.0',
        input_type: 'search_document'
      })
    });

    const data = await response.json();
    return data.embeddings;
  }
}
