import type { Comment, SearchQuery, SourceLink } from "../api/client";

const PERSONA_STYLES: Record<string, { label: string; subtitle: string; color: string; avatar: string }> = {
  historian: { label: 'Dr. Margaret "Maggie" Chandrasekaran', subtitle: "Historian · PhD, University of Chicago", color: "bg-amber-50 border-amber-300 text-amber-900", avatar: "/avatars/maggie.png" },
  economist: { label: 'Dr. Timothy "Tim" Brennan', subtitle: "Economist · PhD, London School of Economics", color: "bg-emerald-50 border-emerald-300 text-emerald-900", avatar: "/avatars/tim.png" },
  philosopher: { label: "Sofia Reyes", subtitle: "Philosopher · MA, Columbia University", color: "bg-violet-50 border-violet-300 text-violet-900", avatar: "/avatars/sofia.png" },
};

function SourceLinkItem({ link }: { link: SourceLink }) {
  return (
    <a href={link.url} target="_blank" rel="noopener noreferrer" className="underline hover:opacity-80">
      {link.title}
    </a>
  );
}

function SearchFootnote({ sq }: { sq: SearchQuery }) {
  const urls = sq.urls ?? [];
  if (urls.length === 0) {
    return <>&ldquo;{sq.query}&rdquo; ({sq.source})</>;
  }
  if (urls.length === 1) {
    return (
      <a href={urls[0].url} target="_blank" rel="noopener noreferrer" className="underline hover:opacity-80">
        &ldquo;{sq.query}&rdquo; ({sq.source}: {urls[0].title})
      </a>
    );
  }
  return (
    <>
      &ldquo;{sq.query}&rdquo; ({sq.source}:{" "}
      {urls.map((link, j) => (
        <span key={j}>
          {j > 0 && ", "}
          <SourceLinkItem link={link} />
        </span>
      ))}
      )
    </>
  );
}

export default function CommentBlock({ comment }: { comment: Comment }) {
  const style = PERSONA_STYLES[comment.persona] ?? {
    label: comment.persona,
    subtitle: "",
    color: "bg-gray-50 border-gray-300 text-gray-900",
    avatar: "",
  };

  const footnotes = comment.search_queries.length > 0 && (
    <p className="mt-1 text-xs italic opacity-60">
      Researched:{" "}
      {comment.search_queries.map((sq, i) => (
        <span key={i}>
          {i > 0 && ", "}
          <SearchFootnote sq={sq} />
        </span>
      ))}
    </p>
  );

  return (
    <div className={`border rounded-lg p-5 ${style.color}`}>
      {/* Mobile: circle avatar + name header */}
      <div className="flex items-center gap-3 sm:hidden">
        {style.avatar && (
          <img
            src={style.avatar}
            alt={style.label}
            className="w-11 h-11 rounded-full object-cover object-top flex-shrink-0"
          />
        )}
        <div>
          <span className="text-sm font-semibold">{style.label}</span>
          {style.subtitle && (
            <span className="block text-xs opacity-70">{style.subtitle}</span>
          )}
        </div>
      </div>
      <p className="mt-3 text-sm leading-relaxed sm:hidden">{comment.text}</p>
      <div className="sm:hidden">{footnotes}</div>

      {/* Desktop: big image side-by-side with text */}
      <div className="hidden sm:flex gap-4">
        {style.avatar && (
          <img
            src={style.avatar}
            alt={style.label}
            className="w-32 h-40 rounded-lg object-cover object-top flex-shrink-0"
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
          {footnotes}
        </div>
      </div>
    </div>
  );
}
