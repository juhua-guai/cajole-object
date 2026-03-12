import { BubuConfig } from "./config";

export type ModeType = "roast" | "survival";
export type ChoiceType = "A" | "B" | "C";

export interface Suggestion {
  label: string;
  text: string;
}

export interface ChatResponse {
  reply: string;
  suggestions: Suggestion[];
  current_mode: ModeType;
  mode_changed?: string | null;
}

export interface ModeToggleResponse {
  accepted: boolean;
  current_mode: ModeType;
  reason: "already_in_mode" | "pending_emotion_confirm" | "emotion_supported";
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

function buildConfigPayload(config: BubuConfig): Record<string, string> {
  if (config.useServerConfig) {
    return {};
  }

  return {
    api_key: config.apiKey,
    model: config.model,
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(response.status, data.detail || "请求失败");
  }
  return response.json();
}

export async function coldStart(config: BubuConfig): Promise<ChatResponse> {
  const response = await fetch(`${config.apiBase}/cold-start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(buildConfigPayload(config)),
  });
  return handleResponse<ChatResponse>(response);
}

export async function sendReply(
  config: BubuConfig,
  text: string,
  choice?: ChoiceType
): Promise<ChatResponse> {
  const response = await fetch(`${config.apiBase}/reply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...buildConfigPayload(config),
      text,
      choice: choice || null,
    }),
  });
  return handleResponse<ChatResponse>(response);
}

export async function toggleMode(
  config: BubuConfig,
  targetMode: ModeType
): Promise<ModeToggleResponse> {
  const response = await fetch(`${config.apiBase}/mode-toggle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_mode: targetMode }),
  });
  return handleResponse<ModeToggleResponse>(response);
}

export async function resetSession(config: BubuConfig): Promise<void> {
  await fetch(`${config.apiBase}/reset`, { method: "POST" });
}
