/**
 * Intelligence Layer - Decides what to store and extracts key information
 */

export interface ExtractedInfo {
  shouldStore: boolean;
  importance: 'high' | 'medium' | 'low';
  facts: string[];
  preferences: string[];
  context: string[];
  summary?: string;
}

export class IntelligenceService {
  private apiKey: string;

  constructor() {
    // Use Cohere or OpenAI for intelligence
    this.apiKey = process.env.COHERE_API_KEY || process.env.OPENAI_API_KEY || '';
  }

  /**
   * Analyze content and decide what to store
   */
  async analyzeContent(content: string, conversationContext?: string[]): Promise<ExtractedInfo> {
    if (!this.apiKey) {
      // Fallback: store everything
      return {
        shouldStore: true,
        importance: 'medium',
        facts: [],
        preferences: [],
        context: []
      };
    }

    try {
      const prompt = this.buildAnalysisPrompt(content, conversationContext);
      const analysis = await this.callLLM(prompt);
      return this.parseAnalysis(analysis);
    } catch (error) {
      console.error('Intelligence analysis failed:', error);
      // Fallback: store everything
      return {
        shouldStore: true,
        importance: 'medium',
        facts: [],
        preferences: [],
        context: []
      };
    }
  }

  private buildAnalysisPrompt(content: string, context?: string[]): string {
    return `Analyze this conversation message and extract key information worth remembering long-term.

${context && context.length > 0 ? `Recent context:\n${context.join('\n')}\n` : ''}

Message to analyze:
"${content}"

Extract:
1. FACTS: Concrete information about the user (name, location, job, etc.)
2. PREFERENCES: User likes, dislikes, habits, style preferences
3. CONTEXT: Important context for future conversations
4. IMPORTANCE: Rate as high/medium/low
5. SHOULD_STORE: true if worth remembering, false if just casual chat

Respond in JSON:
{
  "shouldStore": boolean,
  "importance": "high" | "medium" | "low",
  "facts": ["fact1", "fact2"],
  "preferences": ["pref1", "pref2"],
  "context": ["context1"],
  "summary": "brief summary if long"
}

Examples:
- "My favorite food is biryani" → shouldStore: true, importance: high, preferences: ["favorite food is biryani"]
- "I live in Paris" → shouldStore: true, importance: high, facts: ["lives in Paris"]
- "What's the weather?" → shouldStore: false, importance: low
- "I'm working on a TypeScript project" → shouldStore: true, importance: medium, context: ["working on TypeScript project"]
- "Tell me about famous places in France" → shouldStore: false (just a question), but infer: context: ["interested in France"]

Respond with JSON only:`;
  }

  private async callLLM(prompt: string): Promise<string> {
    // Use Cohere or OpenAI
    if (this.apiKey.startsWith('sk-')) {
      // OpenAI
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          messages: [{ role: 'user', content: prompt }],
          temperature: 0.1,
          response_format: { type: 'json_object' }
        })
      });
      const data = await response.json();
      return data.choices[0].message.content;
    } else {
      // Cohere
      const response = await fetch('https://api.cohere.ai/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          message: prompt,
          model: 'command-r',
          temperature: 0.1
        })
      });
      const data = await response.json();
      return data.text;
    }
  }

  private parseAnalysis(response: string): ExtractedInfo {
    try {
      const json = JSON.parse(response);
      return {
        shouldStore: json.shouldStore ?? true,
        importance: json.importance ?? 'medium',
        facts: json.facts ?? [],
        preferences: json.preferences ?? [],
        context: json.context ?? [],
        summary: json.summary
      };
    } catch (error) {
      console.error('Failed to parse analysis:', error);
      return {
        shouldStore: true,
        importance: 'medium',
        facts: [],
        preferences: [],
        context: []
      };
    }
  }

  /**
   * Infer facts from conversation
   * Example: "Tell me about Paris" → might mean user is interested in Paris
   */
  inferFacts(content: string, analysis: ExtractedInfo): string[] {
    const inferred: string[] = [];

    // Location inference
    if (content.toLowerCase().includes('famous places in france') || 
        content.toLowerCase().includes('things to do in france')) {
      inferred.push('interested in France');
    }

    // Add more inference rules here
    
    return inferred;
  }

  /**
   * Decide if we should store based on importance and relevance
   */
  shouldStoreMessage(analysis: ExtractedInfo): boolean {
    // Store if:
    // 1. Explicitly marked as should store
    // 2. Has facts or preferences
    // 3. High importance
    return analysis.shouldStore || 
           analysis.facts.length > 0 || 
           analysis.preferences.length > 0 ||
           analysis.importance === 'high';
  }
}
