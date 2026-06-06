import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Afroza BizFlow — Demo Agent IA",
  description: "Chatbot demo Salon Aïcha avec visualisation RAG Supabase",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body className="antialiased">{children}</body>
    </html>
  );
}
