"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import type { ChatMessage } from "@/lib/types";

type ChatPanelProps = {
  messages: ChatMessage[];
  loading: boolean;
  suggestions: string[];
  onSend: (text: string) => void;
  error: string | null;
};

export function ChatPanel({
  messages,
  loading,
  suggestions,
  onSend,
  error,
}: ChatPanelProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col rounded-2xl border border-slate-700 bg-slate-900/60 shadow-xl">
      <div className="border-b border-slate-700 px-4 py-3">
        <h2 className="font-semibold">💬 Chat client</h2>
        <p className="text-xs text-slate-400">
          Comme une cliente sur WhatsApp / web — réponses basées sur Supabase + Groq
        </p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-600 p-6 text-center text-sm text-slate-400">
            Posez une question ou cliquez une suggestion ci-dessous.
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[90%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-brand-600 text-white"
                  : "border border-slate-600 bg-slate-800 text-slate-100"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.role === "assistant" && msg.intent && (
                <p className="mt-2 border-t border-slate-600/50 pt-2 text-xs text-slate-400">
                  intent: <span className="text-brand-400">{msg.intent}</span>
                  {msg.confidence != null && (
                    <> · confiance {(msg.confidence * 100).toFixed(0)}%</>
                  )}
                  {msg.escalated && <> · escalade</>}
                </p>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl border border-slate-600 bg-slate-800 px-4 py-3 text-sm text-slate-400">
              L&apos;agent réfléchit…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && (
        <div className="mx-4 mb-2 rounded-lg bg-red-900/40 px-3 py-2 text-sm text-red-200">
          {error}
        </div>
      )}

      <div className="flex flex-wrap gap-2 border-t border-slate-700 px-4 py-2">
        {suggestions.map((s) => (
          <button
            key={s}
            type="button"
            disabled={loading}
            onClick={() => onSend(s)}
            className="rounded-full border border-slate-600 px-3 py-1 text-xs text-slate-300 transition hover:border-brand-500 hover:text-white disabled:opacity-50"
          >
            {s}
          </button>
        ))}
      </div>

      <form onSubmit={submit} className="flex gap-2 border-t border-slate-700 p-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Votre message…"
          disabled={loading}
          className="flex-1 rounded-xl border border-slate-600 bg-slate-800 px-4 py-3 text-sm outline-none ring-brand-500 focus:ring-2 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="rounded-xl bg-brand-500 px-5 py-3 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
        >
          Envoyer
        </button>
      </form>
    </div>
  );
}
