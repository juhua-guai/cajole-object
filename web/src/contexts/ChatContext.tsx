"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { ModeType, Suggestion, ChatResponse, coldStart, sendReply, toggleMode, resetSession, ChoiceType } from "@/lib/api";
import { getConfig, isConfigValid } from "@/lib/config";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  choice?: ChoiceType;
}

interface ChatState {
  messages: Message[];
  suggestions: Suggestion[];
  mode: ModeType;
  desiredMode: ModeType | null;
  loading: boolean;
  error: string | null;
  initialized: boolean;
  modeChangeNotice: string | null;
}

interface ChatContextValue extends ChatState {
  initialize: () => Promise<void>;
  sendSuggestion: (choice: ChoiceType, text: string) => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
  requestModeToggle: () => Promise<void>;
  clearSession: () => Promise<void>;
  clearError: () => void;
  clearModeChangeNotice: () => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ChatState>({
    messages: [],
    suggestions: [],
    mode: "roast",
    desiredMode: null,
    loading: false,
    error: null,
    initialized: false,
    modeChangeNotice: null,
  });

  const handleResponse = useCallback((response: ChatResponse) => {
    setState(prev => {
      const newMessages = [...prev.messages];
      newMessages.push({
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.reply,
      });
      
      let modeChangeNotice: string | null = null;
      if (response.mode_changed) {
        modeChangeNotice = response.mode_changed === "to_survival" 
          ? "布布进入求生模式！🥺 开始卑微认错..." 
          : "布布恢复作死模式！😈 继续阴阳怪气...";
      }
      
      return {
        ...prev,
        messages: newMessages,
        suggestions: response.suggestions,
        mode: response.current_mode,
        loading: false,
        error: null,
        modeChangeNotice,
      };
    });
  }, []);

  const initialize = useCallback(async () => {
    const config = getConfig();
    if (!isConfigValid(config)) {
      setState(prev => ({
        ...prev,
        error: "请先配置后端地址，或关闭“使用后端配置”后输入临时 API Key",
        initialized: false,
      }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await coldStart(config);
      setState(prev => ({
        ...prev,
        messages: [{
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.reply,
        }],
        suggestions: response.suggestions,
        mode: response.current_mode,
        loading: false,
        initialized: true,
        error: null,
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "初始化失败",
      }));
    }
  }, []);

  const sendSuggestion = useCallback(async (choice: ChoiceType, text: string) => {
    const config = getConfig();
    if (!isConfigValid(config)) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      choice,
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      loading: true,
      error: null,
    }));

    try {
      const response = await sendReply(config, text, choice);
      handleResponse(response);
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "发送失败",
      }));
    }
  }, [handleResponse]);

  const sendMessage = useCallback(async (text: string) => {
    const config = getConfig();
    if (!isConfigValid(config)) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      loading: true,
      error: null,
    }));

    try {
      const response = await sendReply(config, text);
      handleResponse(response);
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "发送失败",
      }));
    }
  }, [handleResponse]);

  const requestModeToggle = useCallback(async () => {
    const config = getConfig();
    if (!isConfigValid(config)) return;

    const targetMode: ModeType = state.mode === "roast" ? "survival" : "roast";
    
    try {
      const response = await toggleMode(config, targetMode);
      setState(prev => ({
        ...prev,
        mode: response.current_mode,
        desiredMode: response.accepted ? null : targetMode,
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : "模式切换失败",
      }));
    }
  }, [state.mode]);

  const clearSession = useCallback(async () => {
    const config = getConfig();
    if (!isConfigValid(config)) return;
    await resetSession(config);
    setState({
      messages: [],
      suggestions: [],
      mode: "roast",
      desiredMode: null,
      loading: false,
      error: null,
      initialized: false,
      modeChangeNotice: null,
    });
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const clearModeChangeNotice = useCallback(() => {
    setState(prev => ({ ...prev, modeChangeNotice: null }));
  }, []);

  return (
    <ChatContext.Provider
      value={{
        ...state,
        initialize,
        sendSuggestion,
        sendMessage,
        requestModeToggle,
        clearSession,
        clearError,
        clearModeChangeNotice,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}
