const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Comment {
  id: number;
  persona: string;
  text: string;
  created_at: string;
}

export interface Article {
  id: number;
  guid: string;
  url: string;
  title: string;
  created_at: string;
  comments: Comment[];
}

export async function fetchArticles(
  skip = 0,
  limit = 20
): Promise<Article[]> {
  const res = await fetch(
    `${API_BASE}/articles?skip=${skip}&limit=${limit}`
  );
  if (!res.ok) throw new Error(`Failed to fetch articles: ${res.status}`);
  return res.json();
}
