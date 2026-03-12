const STORAGE_KEY = "bubu-config";
const SESSION_API_KEY_KEY = "bubu-session-api-key";

export interface BubuConfig {
  apiBase: string;
  apiKey: string;
  model: string;
  useServerConfig: boolean;
}

const DEFAULT_CONFIG: BubuConfig = {
  apiBase: "http://localhost:8000/api/chat",
  apiKey: "",
  model: "openai/gpt-4o",
  useServerConfig: true,
};

export function getDefaultConfig(): BubuConfig {
  return { ...DEFAULT_CONFIG };
}

export function getConfig(): BubuConfig {
  if (typeof window === "undefined") {
    return getDefaultConfig();
  }
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      const useServerConfig = parsed.useServerConfig ?? DEFAULT_CONFIG.useServerConfig;
      return {
        apiBase: parsed.apiBase || DEFAULT_CONFIG.apiBase,
        apiKey: useServerConfig ? "" : sessionStorage.getItem(SESSION_API_KEY_KEY) || "",
        model: parsed.model || DEFAULT_CONFIG.model,
        useServerConfig,
      };
    }
  } catch {
    // 解析失败时返回默认值
  }
  
  return getDefaultConfig();
}

export function saveConfig(config: BubuConfig): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      apiBase: config.apiBase,
      model: config.model,
      useServerConfig: config.useServerConfig,
    })
  );

  if (config.useServerConfig || !config.apiKey.trim()) {
    sessionStorage.removeItem(SESSION_API_KEY_KEY);
    return;
  }

  sessionStorage.setItem(SESSION_API_KEY_KEY, config.apiKey);
}

export function resetConfig(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(STORAGE_KEY);
  sessionStorage.removeItem(SESSION_API_KEY_KEY);
}

export function isConfigValid(config: BubuConfig): boolean {
  if (!config.apiBase) {
    return false;
  }

  if (config.useServerConfig) {
    return true;
  }

  return !!config.apiKey && !!config.model;
}
