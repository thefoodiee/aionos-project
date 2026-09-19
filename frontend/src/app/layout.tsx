// app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "AI Team Builder - Agentic AI + RAG System",
  description:
    "Intelligent project team composition utilizing hybrid RAG retrieval and multi-agent LangGraph workflow.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased flex flex-col">
        <Navbar />
        <main className="flex-1 pb-16">{children}</main>
      </body>
    </html>
  );
}
