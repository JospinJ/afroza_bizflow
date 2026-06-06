export type KnowledgeItem = {
  type: string;
  title: string;
  content: string;
  active?: boolean;
};

export type BusinessProfile = {
  id: string;
  name: string;
  sector?: string | null;
  city?: string | null;
  tone?: string | null;
  language?: string | null;
  public_slug: string;
  knowledge_items: KnowledgeItem[];
  storage: string;
  knowledge_count: number;
};

export type AgentAction = {
  type: string;
  payload: Record<string, unknown>;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  intent?: string;
  confidence?: number;
  metadata?: Record<string, unknown>;
  actions?: AgentAction[];
  escalated?: boolean;
};

export type AgentChatResponse = {
  conversation_id: string;
  reply: string;
  intent: string;
  confidence: number;
  actions: AgentAction[];
  escalated: boolean;
  metadata: Record<string, unknown>;
};

export type RagPreview = {
  intent: string;
  matched_types: string[];
  available_intents: string[];
  selected_items: KnowledgeItem[];
  context_preview: string;
};
