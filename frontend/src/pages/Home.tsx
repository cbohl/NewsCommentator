import { useEffect, useState } from "react";
import { fetchArticles, type Article } from "../api/client";
import ArticleCard from "../components/ArticleCard";

const FEEDS = ["business", "technology", "world"] as const;

const FEED_LABELS: Record<string, string> = {
  business: "Business",
  technology: "Technology",
  world: "World",
};

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFeed, setActiveFeed] = useState<string>("business");

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchArticles(0, 20, activeFeed)
      .then(setArticles)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [activeFeed]);

  return (
    <div>
      <div className="flex border-b border-gray-200 mb-6">
        {FEEDS.map((feed) => (
          <button
            key={feed}
            onClick={() => setActiveFeed(feed)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeFeed === feed
                ? "border-b-2 border-blue-600 text-blue-600 font-bold"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {FEED_LABELS[feed]}
          </button>
        ))}
      </div>

      {loading && <p className="text-gray-500">Loading articles...</p>}

      {error && <p className="text-red-600">Error: {error}</p>}

      {!loading && !error && articles.length === 0 && (
        <p className="text-gray-500">
          No articles yet for {FEED_LABELS[activeFeed]}. The pipeline runs every
          hour, or trigger it manually via{" "}
          <code className="bg-gray-100 px-1 rounded">POST /trigger</code>.
        </p>
      )}

      {!loading && !error && articles.length > 0 && (
        <div className="space-y-6">
          {articles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}
    </div>
  );
}
