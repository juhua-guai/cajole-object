"use client";

import { useState } from "react";
import { useChat } from "@/contexts/ChatContext";

export function InputBar() {
  const [text, setText] = useState("");
  const [expanded, setExpanded] = useState(false);
  const { sendMessage, loading } = useChat();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || loading) return;
    sendMessage(text.trim());
    setText("");
  };

  return (
    <div className="border-t border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mx-auto max-w-2xl">
        {!expanded ? (
          <button
            onClick={() => setExpanded(true)}
            className="w-full rounded-lg border border-zinc-300 px-4 py-2 text-left text-sm text-zinc-500 hover:border-zinc-400 dark:border-zinc-700 dark:text-zinc-400 dark:hover:border-zinc-600"
          >
            ✏️ 或者自己输入...
          </button>
        ) : (
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="输入你想说的话..."
              className="flex-1 rounded-lg border border-zinc-300 px-4 py-2 text-sm text-zinc-900 focus:border-blue-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              autoFocus
            />
            <button
              type="submit"
              disabled={!text.trim() || loading}
              className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              发送
            </button>
            <button
              type="button"
              onClick={() => {
                setExpanded(false);
                setText("");
              }}
              className="rounded-lg px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
            >
              ✕
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
