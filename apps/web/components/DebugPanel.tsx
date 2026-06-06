"use client";

import type { AgentChatResponse } from "@/lib/types";

type DebugPanelProps = {
  lastResponse: AgentChatResponse | null;
  conversationId?: string;
};

export function DebugPanel({ lastResponse, conversationId }: DebugPanelProps) {
  const meta = lastResponse?.metadata ?? {};
  const ragItems = (meta.rag_items as Array<{ type: string; title: string; content: string }>) ?? [];
  const ragTypes = (meta.rag_matched_types as string[]) ?? [];
  const contextPreview = (meta.rag_context_preview as string) ?? "";

  return (
    <div className="space-y-4 lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto">
      <div className="rounded-2xl border border-slate-700 bg-slate-900/60 p-4 shadow-xl">
        <h2 className="font-semibold">🔍 Pipeline IA (dernière réponse)</h2>
        <p className="mt-1 text-xs text-slate-400">
          Ce que vos collègues Data/IA doivent comprendre : intent → filtre RAG → prompt LLM.
        </p>

        {!lastResponse ? (
          <p className="mt-6 text-sm text-slate-500">
            Envoyez un message pour voir le détail technique.
          </p>
        ) : (
          <dl className="mt-4 space-y-3 text-sm">
            <Row label="Intent" value={lastResponse.intent} highlight />
            <Row
              label="Confiance"
              value={`${(lastResponse.confidence * 100).toFixed(0)}%`}
            />
            <Row label="Storage" value={String(meta.storage ?? "—")} />
            <Row label="Source RAG" value={String(meta.rag_source ?? "—")} />
            <Row label="Latence" value={`${meta.latency_ms ?? "—"} ms`} />
            <Row label="Modèle" value={String(meta.model ?? "—")} />
            {conversationId && (
              <Row label="Conversation" value={conversationId} mono small />
            )}
          </dl>
        )}
      </div>

      {lastResponse && (
        <>
          <div className="rounded-2xl border border-slate-700 bg-slate-900/60 p-4 shadow-xl">
            <h3 className="text-sm font-semibold">Filtre RAG par intent</h3>
            <p className="mt-1 text-xs text-slate-400">
              Types recherchés pour <code>{lastResponse.intent}</code> :
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {ragTypes.map((t) => (
                <span
                  key={t}
                  className="rounded-full bg-slate-700 px-2 py-1 text-xs text-slate-200"
                >
                  {t}
                </span>
              ))}
            </div>
            <p className="mt-3 text-xs text-slate-400">
              {ragItems.length} item(s) sélectionné(s) sur la base complète.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-900/60 p-4 shadow-xl">
            <h3 className="text-sm font-semibold">Contexte injecté au LLM</h3>
            <pre className="mt-3 max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-3 text-xs text-slate-300">
              {contextPreview || "(vide)"}
            </pre>
          </div>

          {lastResponse.actions.length > 0 && (
            <div className="rounded-2xl border border-slate-700 bg-slate-900/60 p-4 shadow-xl">
              <h3 className="text-sm font-semibold">Actions agent</h3>
              <pre className="mt-3 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-300">
                {JSON.stringify(lastResponse.actions, null, 2)}
              </pre>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function Row({
  label,
  value,
  highlight,
  mono,
  small,
}: {
  label: string;
  value: string;
  highlight?: boolean;
  mono?: boolean;
  small?: boolean;
}) {
  return (
    <div className="flex flex-col gap-0.5 border-b border-slate-800 pb-2 last:border-0">
      <dt className="text-xs text-slate-500">{label}</dt>
      <dd
        className={`${highlight ? "text-brand-400 font-medium" : "text-slate-200"} ${
          mono ? "font-mono break-all" : ""
        } ${small ? "text-xs" : ""}`}
      >
        {value}
      </dd>
    </div>
  );
}
