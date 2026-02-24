import type { Article } from "../api/client";
import ChatPanel from "./ChatPanel";
import CommentBlock from "./CommentBlock";

export default function ArticleCard({ article }: { article: Article }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          {article.title}
        </h2>
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-600 hover:underline"
        >
          Read original article
        </a>
        <p className="text-xs text-gray-400 mt-1">
          {new Date(article.created_at).toLocaleString()}
        </p>
      </div>
      <div className="grid gap-3">
        {article.comments.map((comment) => (
          <CommentBlock key={comment.id} comment={comment} />
        ))}
      </div>
      <ChatPanel articleId={article.id} />
    </div>
  );
}
