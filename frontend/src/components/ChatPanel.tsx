import { useRef, useState } from "react";
import { streamChat, type ChatMessage } from "../api/client";

const PERSONA_STYLES: Record<
  string,
  { label: string; color: string; avatar: string }
> = {
  historian: {
    label: "Dr. Maggie Chandrasekaran — Historian",
    color: "bg-amber-50 border-amber-300 text-amber-900",
    avatar: "/avatars/maggie.png",
  },
  economist: {
    label: "Dr. Tim Brennan — Economist",
    color: "bg-emerald-50 border-emerald-300 text-emerald-900",
    avatar: "/avatars/tim.png",
  },
  philosopher: {
    label: "Sofia Reyes — Philosopher",
    color: "bg-violet-50 border-violet-300 text-violet-900",
    avatar: "/avatars/sofia.png",
  },
};

interface DisplayMessage {
  role: "user" | "assistant";
  persona?: string;
  content: string;
}

export default function ChatPanel({ articleId }: { articleId: number }) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingPersona, setStreamingPersona] = useState<string | null>(null);
  const [streamingText, setStreamingText] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    setTimeout(() => {
      scrollRef.current?.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }, 50);
  };

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;

    const userMessage: DisplayMessage = { role: "user", content: trimmed };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setIsStreaming(true);
    setStreamingPersona(null);
    setStreamingText("");
    scrollToBottom();

    const apiMessages: ChatMessage[] = updatedMessages.map((m) => ({
      role: m.role,
      persona: m.persona,
      content: m.content,
    }));

    let currentPersona = "";
    let currentText = "";

    abortRef.current = streamChat(
      articleId,
      apiMessages,
      (event, data) => {
        if (event === "persona_start") {
          currentPersona = data.persona;
          currentText = "";
          setStreamingPersona(data.persona);
          setStreamingText("");
          scrollToBottom();
        } else if (event === "token") {
          currentText += data.token;
          setStreamingText((prev) => prev + data.token);
          scrollToBottom();
        } else if (event === "persona_end") {
          // Snapshot values before React batches — the next persona_start
          // may overwrite currentPersona/currentText before the updater runs
          const completedMsg: DisplayMessage = {
            role: "assistant",
            persona: currentPersona,
            content: currentText,
          };
          setMessages((prev) => [...prev, completedMsg]);
          setStreamingPersona(null);
          setStreamingText("");
          scrollToBottom();
        } else if (event === "done") {
          setIsStreaming(false);
          setStreamingPersona(null);
          setStreamingText("");
          abortRef.current = null;
        }
      },
      (error) => {
        console.error("Chat stream error:", error);
        setIsStreaming(false);
        setStreamingPersona(null);
        abortRef.current = null;
      }
    );
  };

  const renderMessage = (msg: DisplayMessage, idx: number) => {
    if (msg.role === "user") {
      return (
        <div key={idx} className="flex justify-end">
          <div className="bg-gray-200 text-gray-900 rounded-lg px-4 py-2 max-w-[80%]">
            <p className="text-sm">{msg.content}</p>
          </div>
        </div>
      );
    }

    const style = PERSONA_STYLES[msg.persona || ""] ?? {
      label: msg.persona || "Unknown",
      color: "bg-gray-50 border-gray-300 text-gray-900",
      avatar: "",
    };

    return (
      <div
        key={idx}
        className={`border rounded-lg p-3 ${style.color} flex gap-3`}
      >
        {style.avatar && (
          <img
            src={style.avatar}
            alt={style.label}
            className="w-10 h-10 rounded-full object-cover flex-shrink-0"
          />
        )}
        <div className="min-w-0">
          <span className="text-xs font-semibold uppercase tracking-wide">
            {style.label}
          </span>
          <p className="mt-1 text-sm leading-relaxed">{msg.content}</p>
        </div>
      </div>
    );
  };

  const renderStreamingMessage = () => {
    if (!streamingPersona) return null;

    const style = PERSONA_STYLES[streamingPersona] ?? {
      label: streamingPersona,
      color: "bg-gray-50 border-gray-300 text-gray-900",
      avatar: "",
    };

    return (
      <div className={`border rounded-lg p-3 ${style.color} flex gap-3`}>
        {style.avatar && (
          <img
            src={style.avatar}
            alt={style.label}
            className="w-10 h-10 rounded-full object-cover flex-shrink-0"
          />
        )}
        <div className="min-w-0">
          <span className="text-xs font-semibold uppercase tracking-wide">
            {style.label}
          </span>
          <p className="mt-1 text-sm leading-relaxed">
            {streamingText}
            <span className="inline-block w-1.5 h-4 bg-current opacity-75 animate-pulse ml-0.5 align-text-bottom" />
          </p>
        </div>
      </div>
    );
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="w-full text-sm text-gray-500 hover:text-gray-700 py-3 border-t border-gray-100 transition-colors"
      >
        Chat with the panel about this article...
      </button>
    );
  }

  return (
    <div className="border-t border-gray-200 pt-4 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-700">
          Chat with the Panel
        </h4>
        <button
          onClick={() => setIsOpen(false)}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          Close
        </button>
      </div>

      {/* Messages */}
      <div
        ref={scrollRef}
        className="max-h-96 overflow-y-auto space-y-3 pr-1"
      >
        {messages.length === 0 && !streamingPersona && (
          <p className="text-sm text-gray-400 text-center py-4">
            Ask Maggie, Tim, and Sofia about this article. Mention a name to get
            their response first.
          </p>
        )}
        {messages.map(renderMessage)}
        {renderStreamingMessage()}
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
        className="flex gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isStreaming}
          placeholder={
            isStreaming ? "Waiting for responses..." : "Type a message..."
          }
          className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400 disabled:opacity-50 disabled:bg-gray-50"
        />
        <button
          type="submit"
          disabled={isStreaming || !input.trim()}
          className="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-800 disabled:opacity-50 disabled:hover:bg-gray-900 transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  );
}
