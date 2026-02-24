import type { Comment } from "../api/client";

const PERSONA_STYLES: Record<string, { label: string; subtitle: string; color: string; avatar: string }> = {
  historian: { label: 'Dr. Margaret "Maggie" Chandrasekaran', subtitle: "Historian · PhD, University of Chicago", color: "bg-amber-50 border-amber-300 text-amber-900", avatar: "/avatars/maggie.png" },
  economist: { label: 'Dr. Timothy "Tim" Brennan', subtitle: "Economist · PhD, London School of Economics", color: "bg-emerald-50 border-emerald-300 text-emerald-900", avatar: "/avatars/tim.png" },
  philosopher: { label: "Sofia Reyes", subtitle: "Philosopher · MA, Columbia University", color: "bg-violet-50 border-violet-300 text-violet-900", avatar: "/avatars/sofia.png" },
};

export default function CommentBlock({ comment }: { comment: Comment }) {
  const style = PERSONA_STYLES[comment.persona] ?? {
    label: comment.persona,
    subtitle: "",
    color: "bg-gray-50 border-gray-300 text-gray-900",
    avatar: "",
  };

  return (
    <div className={`border rounded-lg p-5 ${style.color} flex gap-4`}>
      {style.avatar && (
        <img
          src={style.avatar}
          alt={style.label}
          className="w-36 h-36 rounded-lg object-cover flex-shrink-0"
        />
      )}
      <div className="min-w-0">
        <span className="text-xs font-semibold uppercase tracking-wide">
          {style.label}
        </span>
        {style.subtitle && (
          <span className="block text-xs opacity-70 mt-0.5">
            {style.subtitle}
          </span>
        )}
        <p className="mt-2 text-sm leading-relaxed">{comment.text}</p>
      </div>
    </div>
  );
}
