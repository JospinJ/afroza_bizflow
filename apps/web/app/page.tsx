import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-center justify-center gap-8 px-6 text-center">
      <div className="space-y-3">
        <p className="text-sm uppercase tracking-widest text-brand-500">
          Afroza BizFlow · Agent IA
        </p>
        <h1 className="text-4xl font-bold">Demo chatbot Salon Aïcha</h1>
        <p className="text-slate-300">
          Interface pour vos collègues : conversation en direct, base RAG Supabase
          visible, intent et contexte injecté à chaque réponse.
        </p>
      </div>

      <Link
        href="/a/salon-aicha"
        className="rounded-xl bg-brand-500 px-8 py-4 text-lg font-semibold text-white shadow-lg shadow-orange-900/30 transition hover:bg-brand-600"
      >
        Ouvrir la demo chat →
      </Link>

      <p className="text-sm text-slate-400">
        API requise : lancer <code className="rounded bg-slate-800 px-2 py-1">services/api/start.ps1</code>
      </p>
    </main>
  );
}
