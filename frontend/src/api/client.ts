const API_BASE =
  import.meta.env.VITE_API_URL ||
  (window.location.hostname === "localhost" ? "http://localhost:8000" : "");

export interface SourceLink {
  url: string;
  title: string;
}

export interface SearchQuery {
  query: string;
  source: string;
  urls?: SourceLink[];
}

export interface Comment {
  id: number;
  persona: string;
  text: string;
  search_queries: SearchQuery[];
  created_at: string;
}

export interface Article {
  id: number;
  guid: string;
  url: string;
  title: string;
  feed: string;
  created_at: string;
  comments: Comment[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  persona?: string;
  content: string;
}

export async function fetchArticles(
  skip = 0,
  limit = 20,
  feed?: string
): Promise<Article[]> {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit),
  });
  if (feed) params.set("feed", feed);
  const res = await fetch(`${API_BASE}/articles?${params}`);
  if (!res.ok) throw new Error(`Failed to fetch articles: ${res.status}`);
  return res.json();
}

export function streamChat(
  articleId: number,
  messages: ChatMessage[],
  onEvent: (event: string, data: Record<string, string>) => void,
  onError: (error: Error) => void
): AbortController {
  const controller = new AbortController();

  fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ article_id: articleId, messages }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        onError(new Error(`Chat request failed: ${res.status}`));
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) {
        onError(new Error("No response body"));
        return;
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        let currentEvent = "";
        for (const line of lines) {
          if (line.startsWith("event: ")) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith("data: ") && currentEvent) {
            try {
              const data = JSON.parse(line.slice(6));
              onEvent(currentEvent, data);
            } catch {
              // skip malformed data
            }
            currentEvent = "";
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        onError(err);
      }
    });

  return controller;
}
