"use client";

import { useChat } from "@/contexts/ChatContext";
import { ChoiceType } from "@/lib/api";

const EMOTION_CONFIG: Record<string, { icon: string; color: string; hoverColor: string }> = {
  A: {
    icon: "😊",
    color: "border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-900/30",
    hoverColor: "hover:border-green-400 hover:bg-green-100 dark:hover:border-green-600 dark:hover:bg-green-900/50",
  },
  B: {
    icon: "😐",
    color: "border-zinc-300 bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-800/50",
    hoverColor: "hover:border-zinc-400 hover:bg-zinc-100 dark:hover:border-zinc-600 dark:hover:bg-zinc-800",
  },
  C: {
    icon: "😡",
    color: "border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-900/30",
    hoverColor: "hover:border-red-400 hover:bg-red-100 dark:hover:border-red-600 dark:hover:bg-red-900/50",
  },
};

export function SuggestionBar() {
  const { suggestions, loading, sendSuggestion } = useChat();

  if (suggestions.length === 0) return null;

  const handleClick = (choice: ChoiceType, text: string) => {
    if (loading) return;
    sendSuggestion(choice, text);
  };

  return (
    <div className="border-t border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <div className="mx-auto max-w-2xl space-y-2">
        <p className="mb-2 text-xs text-zinc-500 dark:text-zinc-400">
          选择一个回复：
        </p>
        <div className="grid gap-2 sm:grid-cols-3">
          {suggestions.map((suggestion) => {
            const label = suggestion.label as ChoiceType;
            const config = EMOTION_CONFIG[label] || EMOTION_CONFIG.B;

            return (
              <button
                key={label}
                onClick={() => handleClick(label, suggestion.text)}
                disabled={loading}
                className={`flex items-start gap-2 rounded-xl border p-3 text-left transition-all ${config.color} ${config.hoverColor} ${
                  loading ? "cursor-not-allowed opacity-50" : "cursor-pointer"
                }`}
              >
                <span className="text-lg">{config.icon}</span>
                <span className="flex-1 text-sm text-zinc-800 dark:text-zinc-200">
                  {suggestion.text}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
