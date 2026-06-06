"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  fetchBusiness,
  fetchHealth,
  getApiUrl,
  sendChatMessage,
} from "@/lib/api";
import type { AgentChatResponse, BusinessProfile, ChatMessage } from "@/lib/types";
import { ChatPanel } from "./ChatPanel";
import { RagKnowledgePanel } from "./RagKnowledgePanel";
import { DebugPanel } from "./DebugPanel";

const SUGGESTIONS = [
  "Bonjour, c'est combien pour des braids ?",
  "Vous ouvrez à quelle heure le samedi ?",
  "Je voudrais prendre rendez-vous pour demain",
  "Vous acceptez Mobile Money ?",
];

type ChatDemoProps = {
  slug: string;
};

export function ChatDemo({ slug }: ChatDemoProps) {
  const [business, setBusiness] = useState<BusinessProfile | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [lastResponse, setLastResponse] = useState<AgentChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [supabaseOk, setSupabaseOk] = useState<boolean | null>(null);

  const loadBusiness = useCallback(async () => {
    try {
      const profile = await fetchBusiness(slug);
      setBusiness(profile);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Impossible de charger le salon");
    }
  }, [slug]);

  useEffect(() => {
    loadBusiness();
    fetchHealth()
      .then((h) => {
        setApiOk(true);
        setSupabaseOk(h.supabase);
      })
      .catch(() => setApiOk(false));
  }, [loadBusiness]);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text.trim(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const res = await sendChatMessage({
        business_slug: slug,
        message: text.trim(),
        conversation_id: conversationId,
      });

      setConversationId(res.conversation_id);
      setLastResponse(res);

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: res.reply,
        intent: res.intent,
        confidence: res.confidence,
        metadata: res.metadata,
        actions: res.actions,
        escalated: res.escalated,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur lors de l'envoi");
    } finally {
      setLoading(false);
    }
  };

  const highlightedTitles = new Set(
    ((lastResponse?.metadata?.rag_items as Array<{ title: string }>) ?? []).map(
      (i) => i.title
    )
  );

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-slate-700/80 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-4 px-4 py-4">
          <div>
            <Link href="/" className="text-xs text-slate-400 hover:text-white">
              ← Accueil
            </Link>
            <h1 className="text-xl font-bold">
              {business?.name ?? slug}{" "}
              <span className="text-sm font-normal text-slate-400">
                · demo Agent IA
              </span>
            </h1>
            {business && (
              <p className="text-sm text-slate-400">
                {business.sector} · {business.city} · ton {business.tone} ·{" "}
                {business.knowledge_count} items RAG · source{" "}
                <span className="text-brand-500">{business.storage}</span>
              </p>
            )}
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <StatusBadge ok={apiOk} label={`API ${getApiUrl()}`} />
            <StatusBadge ok={supabaseOk} label="Supabase" />
          </div>
        </div>
      </header>

      <main className="mx-auto grid w-full max-w-[1600px] flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-12">
        <section className="lg:col-span-3">
          <RagKnowledgePanel
            items={business?.knowledge_items ?? []}
            highlightedTitles={highlightedTitles}
            loading={!business && !error}
            error={error}
          />
        </section>

        <section className="flex flex-col lg:col-span-5">
          <ChatPanel
            messages={messages}
            loading={loading}
            suggestions={SUGGESTIONS}
            onSend={handleSend}
            error={error}
          />
        </section>

        <section className="lg:col-span-4">
          <DebugPanel lastResponse={lastResponse} conversationId={conversationId} />
        </section>
      </main>
    </div>
  );
}

function StatusBadge({ ok, label }: { ok: boolean | null; label: string }) {
  const color =
    ok === null ? "bg-slate-700 text-slate-300" : ok ? "bg-emerald-900/60 text-emerald-300" : "bg-red-900/60 text-red-300";
  return (
    <span className={`rounded-full px-3 py-1 ${color}`}>
      {ok === null ? "…" : ok ? "●" : "○"} {label}
    </span>
  );
}
