import type { Comment } from "../api/client";

const PERSONA_STYLES: Record<string, { label: string; color: string }> = {
  historian: { label: "Historian", color: "bg-amber-50 border-amber-300 text-amber-900" },
  economist: { label: "Economist", color: "bg-emerald-50 border-emerald-300 text-emerald-900" },
  philosopher: { label: "Philosopher", color: "bg-violet-50 border-violet-300 text-violet-900" },
};

export default function CommentBlock({ comment }: { comment: Comment }) {
  const style = PERSONA_STYLES[comment.persona] ?? {
    label: comment.persona,
    color: "bg-gray-50 border-gray-300 text-gray-900",
  };

  return (
    <div className={`border rounded-lg p-4 ${style.color}`}>
      <span className="text-xs font-semibold uppercase tracking-wide">
        {style.label}
      </span>
      <p className="mt-2 text-sm leading-relaxed">{comment.text}</p>
    </div>
  );
}
