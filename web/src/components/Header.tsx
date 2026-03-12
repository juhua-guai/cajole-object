"use client";

import { useChat } from "@/contexts/ChatContext";

interface HeaderProps {
  onSettingsClick: () => void;
}

export function Header({ onSettingsClick }: HeaderProps) {
  const { mode, desiredMode, requestModeToggle, clearSession } = useChat();

  const modeText = mode === "roast" ? "作死模式" : "求生模式";
  const modeEmoji = mode === "roast" ? "😈" : "🥺";
  const modeColor = mode === "roast" ? "bg-red-500" : "bg-blue-500";

  return (
    <header className="sticky top-0 z-40 flex items-center justify-between border-b border-zinc-200 bg-white/80 px-4 py-3 backdrop-blur-sm dark:border-zinc-800 dark:bg-zinc-900/80">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
          布布的嘴替日常
        </h1>
        <button
          onClick={requestModeToggle}
          className={`flex items-center gap-1 rounded-full px-3 py-1 text-sm font-medium text-white transition-all ${modeColor}`}
        >
          <span>{modeEmoji}</span>
          <span>{modeText}</span>
        </button>
        {desiredMode && (
          <span className="text-xs text-amber-600 dark:text-amber-400">
            (等待切换中...)
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={clearSession}
          className="rounded-lg px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
          title="清空会话"
        >
          🗑️
        </button>
        <button
          onClick={onSettingsClick}
          className="rounded-lg px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
          title="设置"
        >
          ⚙️
        </button>
      </div>
    </header>
  );
}
