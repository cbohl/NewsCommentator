import { useEffect, useState } from "react";
import { fetchArticles, type Article } from "../api/client";
import ArticleCard from "../components/ArticleCard";

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchArticles()
      .then(setArticles)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-gray-500">Loading articles...</p>;
  }

  if (error) {
    return <p className="text-red-600">Error: {error}</p>;
  }

  if (articles.length === 0) {
    return (
      <p className="text-gray-500">
        No articles yet. The pipeline runs every hour, or trigger it manually
        via <code className="bg-gray-100 px-1 rounded">POST /trigger</code>.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      {articles.map((article) => (
        <ArticleCard key={article.id} article={article} />
      ))}
    </div>
  );
}
