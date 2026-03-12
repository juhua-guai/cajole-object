"use client";

import { useState } from "react";
import { BubuConfig, getConfig, getDefaultConfig, saveConfig, resetConfig } from "@/lib/config";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
}

function SettingsModalContent({ onClose, onSave }: Omit<SettingsModalProps, "isOpen">) {
  const [config, setConfig] = useState<BubuConfig>(() => getConfig());

  const handleSave = () => {
    saveConfig(config);
    onSave();
    onClose();
  };

  const handleReset = () => {
    resetConfig();
    setConfig(getDefaultConfig());
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-zinc-900">
        <h2 className="mb-4 text-xl font-bold text-zinc-900 dark:text-zinc-100">
          设置
        </h2>

        <div className="mb-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800 dark:bg-amber-900/30 dark:text-amber-200">
          推荐使用后端服务端配置。若临时输入 API Key，只会保存在当前标签页会话中。
        </div>

        <div className="space-y-4">
          <label className="flex items-start gap-3 rounded-lg border border-zinc-200 p-3 text-sm text-zinc-700 dark:border-zinc-700 dark:text-zinc-300">
            <input
              type="checkbox"
              checked={config.useServerConfig}
              onChange={(e) =>
                setConfig({
                  ...config,
                  useServerConfig: e.target.checked,
                  apiKey: e.target.checked ? "" : config.apiKey,
                })
              }
              className="mt-0.5"
            />
            <span>
              优先使用后端服务端配置
            </span>
          </label>

          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              API Key
            </label>
            <input
              type="password"
              value={config.apiKey}
              onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
              placeholder={config.useServerConfig ? "已交由后端管理" : "输入临时 API Key"}
              disabled={config.useServerConfig}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 focus:border-blue-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              后端 API 地址
            </label>
            <input
              type="text"
              value={config.apiBase}
              onChange={(e) => setConfig({ ...config, apiBase: e.target.value })}
              placeholder="http://localhost:8000/api/chat"
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 focus:border-blue-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Model
            </label>
            <input
              type="text"
              value={config.model}
              onChange={(e) => setConfig({ ...config, model: e.target.value })}
              placeholder={config.useServerConfig ? "由后端服务端配置决定" : "openai/gpt-4o"}
              disabled={config.useServerConfig}
              className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-zinc-900 focus:border-blue-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            />
          </div>
        </div>

        <div className="mt-6 flex justify-between">
          <button
            onClick={handleReset}
            className="rounded-lg px-4 py-2 text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
          >
            重置
          </button>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
            >
              取消
            </button>
            <button
              onClick={handleSave}
              className="rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
            >
              保存
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SettingsModal({ isOpen, onClose, onSave }: SettingsModalProps) {
  if (!isOpen) return null;
  return <SettingsModalContent onClose={onClose} onSave={onSave} />;
}
