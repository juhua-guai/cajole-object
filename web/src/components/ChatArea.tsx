"use client";

import { useChat, Message } from "@/contexts/ChatContext";
import { useEffect, useRef, useState } from "react";
import Image from "next/image";

function Avatar({ role, mode }: { role: "user" | "assistant"; mode: string }) {
  const src =
    role === "assistant"
      ? mode === "roast"
        ? "/static/avatars/bubu_roast.jpg"
        : "/static/avatars/bubu_survival.jpg"
      : "/static/avatars/yier.jpg";

  const [imgSrc, setImgSrc] = useState(src);

  useEffect(() => {
    setImgSrc(src);
  }, [src]);

  return (
    <div className="h-10 w-10 flex-shrink-0 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-700">
      <Image
        src={imgSrc}
        alt={role === "assistant" ? "布布" : "一二"}
        width={40}
        height={40}
        className="h-full w-full object-cover"
        onError={() => {
          setImgSrc("/static/placeholder/default_avatar.jpg");
        }}
      />
    </div>
  );
}

function MessageBubble({ message, mode }: { message: Message; mode: string }) {
  const isAssistant = message.role === "assistant";

  return (
    <div className={`flex gap-3 ${isAssistant ? "" : "flex-row-reverse"}`}>
      <Avatar role={message.role} mode={mode} />
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-2 ${
          isAssistant
            ? "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
            : "bg-blue-500 text-white"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </p>
        {message.choice && (
          <span className="mt-1 block text-xs opacity-60">
            选项 {message.choice}
          </span>
        )}
      </div>
    </div>
  );
}

function LoadingBubble({ mode }: { mode: string }) {
  return (
    <div className="flex gap-3">
      <Avatar role="assistant" mode={mode} />
      <div className="rounded-2xl bg-zinc-100 px-4 py-3 dark:bg-zinc-800">
        <div className="flex gap-1">
          <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.3s]"></span>
          <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.15s]"></span>
          <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400"></span>
        </div>
      </div>
    </div>
  );
}

export function ChatArea() {
  const { messages, mode, loading } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="mx-auto max-w-2xl space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} mode={mode} />
        ))}
        {loading && <LoadingBubble mode={mode} />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
