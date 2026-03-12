"use client";

import { useState, useEffect } from "react";
import { ChatProvider, useChat } from "@/contexts/ChatContext";
import { Header } from "@/components/Header";
import { ChatArea } from "@/components/ChatArea";
import { SuggestionBar } from "@/components/SuggestionBar";
import { InputBar } from "@/components/InputBar";
import { SettingsModal } from "@/components/SettingsModal";
import { Toast } from "@/components/Toast";
import { getConfig, isConfigValid } from "@/lib/config";

function ChatApp() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const { initialize, initialized, error, clearError, modeChangeNotice, clearModeChangeNotice } = useChat();
  const isSettingsOpen = settingsOpen || !!error;

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- SSR hydration requires client-side state init
    setMounted(true);
    const config = getConfig();
    if (isConfigValid(config)) {
      initialize();
    } else {
      setSettingsOpen(true);
    }
  }, [initialize]);

  const handleSettingsSave = () => {
    initialize();
  };

  if (!mounted) {
    return (
      <div className="flex h-screen flex-col bg-zinc-50 dark:bg-zinc-950">
        <div className="flex flex-1 items-center justify-center">
          <div className="text-zinc-400">加载中...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-zinc-50 dark:bg-zinc-950">
      <Header onSettingsClick={() => setSettingsOpen(true)} />

      {modeChangeNotice && (
        <Toast
          message={modeChangeNotice}
          type="info"
          onClose={clearModeChangeNotice}
        />
      )}

      {error && (
        <div className="mx-4 mt-2 rounded-lg bg-red-100 p-3 text-sm text-red-800 dark:bg-red-900/30 dark:text-red-200">
          <div className="flex items-center justify-between">
            <span>❌ {error}</span>
            <button onClick={clearError} className="text-red-600 hover:text-red-800">
              ✕
            </button>
          </div>
        </div>
      )}

      {!initialized && !error && (
        <div className="flex flex-1 items-center justify-center">
          <div className="text-center">
            <p className="mb-4 text-zinc-600 dark:text-zinc-400">
              请先配置后端，或在设置中输入临时 API Key
            </p>
            <button
              onClick={() => setSettingsOpen(true)}
              className="rounded-lg bg-blue-500 px-6 py-2 text-white hover:bg-blue-600"
            >
              打开设置
            </button>
          </div>
        </div>
      )}

      {initialized && (
        <>
          <ChatArea />
          <SuggestionBar />
          <InputBar />
        </>
      )}

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setSettingsOpen(false)}
        onSave={handleSettingsSave}
      />
    </div>
  );
}

export default function Home() {
  return (
    <ChatProvider>
      <ChatApp />
    </ChatProvider>
  );
}
