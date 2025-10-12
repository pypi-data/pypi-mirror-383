#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
    CallToolRequest,
} from '@modelcontextprotocol/sdk/types.js';
import { MemoryManager } from './memory-manager.js';
import { createHash } from 'crypto';
import { hostname } from 'os';

// Get or create a consistent default userId
const getDefaultUserId = (): string => {
    // Priority 1: Environment variable
    if (process.env.DEFAULT_USER_ID) {
        return process.env.DEFAULT_USER_ID;
    }
    
    // Priority 2: Use machine hostname hash for consistency
    const machineId = hostname();
    const hash = createHash('sha256').update(machineId).digest('hex').substring(0, 16);
    return `user_${hash}`;
};

const DEFAULT_USER_ID = getDefaultUserId();
console.error(`Using default userId: ${DEFAULT_USER_ID}`);

const manager = new MemoryManager();

const server = new Server(
    {
        name: 'universal-ai-memory',
        version: '1.0.0',
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: 'search_memory',
                description: 'Search through all user memories across platforms using hybrid semantic and keyword search. Returns highly relevant context tailored to the query.',
                inputSchema: {
                    type: 'object',
                    properties: {
                        query: {
                            type: 'string',
                            description: 'The search query to find relevant memories'
                        },
                        userId: {
                            type: 'string',
                            description: 'User identifier to search memories for (optional, defaults to current user)'
                        },
                        limit: {
                            type: 'number',
                            description: 'Maximum number of results to return (default: 10)',
                            default: 10
                        },
                        platform: {
                            type: 'string',
                            description: 'Filter by specific platform (claude, chatgpt, gemini, perplexity)',
                            enum: ['claude', 'chatgpt', 'gemini', 'perplexity', 'other']
                        },
                        minScore: {
                            type: 'number',
                            description: 'Minimum relevance score (0-1)',
                            default: 0.5
                        }
                    },
                    required: ['query']
                }
            },
            {
                name: 'add_to_memory',
                description: 'Add new content to user memory. Automatically chunks, embeds, and stores across hot/warm/cold storage layers for optimal retrieval.',
                inputSchema: {
                    type: 'object',
                    properties: {
                        userId: {
                            type: 'string',
                            description: 'User identifier (optional, defaults to current user)'
                        },
                        platform: {
                            type: 'string',
                            description: 'Platform where this interaction occurred',
                            enum: ['claude', 'chatgpt', 'gemini', 'perplexity', 'other']
                        },
                        conversationId: {
                            type: 'string',
                            description: 'Unique conversation identifier'
                        },
                        content: {
                            type: 'string',
                            description: 'The content to store in memory'
                        },
                        role: {
                            type: 'string',
                            description: 'Role of the message sender',
                            enum: ['user', 'assistant']
                        },
                        metadata: {
                            type: 'object',
                            description: 'Additional metadata to store with the memory',
                            additionalProperties: true
                        }
                    },
                    required: ['platform', 'conversationId', 'content', 'role']
                }
            }
        ]
    };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request: CallToolRequest) => {
    const { name, arguments: args } = request.params;

    if (!args) {
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify({ error: 'No arguments provided' })
                }
            ],
            isError: true
        };
    }

    try {
        if (name === 'search_memory') {
            const userId = (args.userId as string) || DEFAULT_USER_ID;
            const results = await manager.searchMemory({
                query: args.query as string,
                userId: userId,
                limit: args.limit as number | undefined,
                platform: args.platform as string | undefined,
                minScore: args.minScore as number | undefined
            });

            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(results, null, 2)
                    }
                ]
            };
        }

        if (name === 'add_to_memory') {
            const userId = (args.userId as string) || DEFAULT_USER_ID;
            const result = await manager.addMemory({
                userId: userId,
                platform: args.platform as string,
                conversationId: args.conversationId as string,
                content: args.content as string,
                role: args.role as 'user' | 'assistant',
                metadata: args.metadata as Record<string, any> | undefined
            });

            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({ success: true, memoryId: result.id }, null, 2)
                    }
                ]
            };
        }

        throw new Error(`Unknown tool: ${name}`);
    } catch (error) {
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify({ error: (error as Error).message })
                }
            ],
            isError: true
        };
    }
});

async function main() {
    await manager.initialize();

    const transport = new StdioServerTransport();
    await server.connect(transport);

    console.error('Universal AI Memory MCP server running on stdio');
}

main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
});
