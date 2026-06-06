"use client";

import type { KnowledgeItem } from "@/lib/types";

const TYPE_COLORS: Record<string, string> = {
  service: "bg-violet-900/50 text-violet-200",
  faq: "bg-sky-900/50 text-sky-200",
  policy: "bg-amber-900/50 text-amber-200",
  hours: "bg-emerald-900/50 text-emerald-200",
  tone: "bg-pink-900/50 text-pink-200",
};

type RagKnowledgePanelProps = {
  items: KnowledgeItem[];
  highlightedTitles: Set<string>;
  loading: boolean;
  error?: string | null;
};

export function RagKnowledgePanel({
  items,
  highlightedTitles,
  loading,
  error,
}: RagKnowledgePanelProps) {
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-900/60 p-4 shadow-xl lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto">
      <h2 className="font-semibold">📚 Base RAG Supabase</h2>
      <p className="mt-1 text-xs text-slate-400">
        Tous les <code className="text-slate-300">knowledge_items</code> du salon.
        Les items <span className="text-brand-400">surlignés</span> ont été injectés
        dans le prompt de la dernière réponse.
      </p>

      {loading && (
        <p className="mt-6 text-sm text-slate-500">Chargement…</p>
      )}

      {error && (
        <div className="mt-4 rounded-lg border border-red-800 bg-red-950/50 p-3 text-xs text-red-200">
          Impossible de charger la base RAG : {error}
          <br />
          <span className="text-red-300/80">
            Redémarrez l&apos;API (<code>services/api/start.ps1</code>) puis rafraîchissez la page.
          </span>
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <p className="mt-6 text-sm text-slate-500">Aucune donnée — vérifiez Supabase.</p>
      )}

      <ul className="mt-4 space-y-3">
        {items.map((item) => {
          const active = highlightedTitles.has(item.title);
          return (
            <li
              key={`${item.type}-${item.title}`}
              className={`rounded-xl border p-3 transition ${
                active
                  ? "border-brand-500 bg-brand-950/40 ring-1 ring-brand-500/50"
                  : "border-slate-700 bg-slate-800/50"
              }`}
            >
              <div className="mb-2 flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-medium uppercase ${
                    TYPE_COLORS[item.type] ?? "bg-slate-700 text-slate-300"
                  }`}
                >
                  {item.type}
                </span>
                <span className="text-sm font-medium">{item.title}</span>
                {active && (
                  <span className="ml-auto text-[10px] text-brand-400">utilisé</span>
                )}
              </div>
              <p className="text-xs leading-relaxed text-slate-300">{item.content}</p>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
