"use client";
import React, { useEffect, useMemo, useState } from "react";

/** ---------- Types ---------- */
type Post = {
  id: string;
  subreddit: string;
  author: string;
  title: string;
  body: string;
  votes: number;
  comments: number;
  createdAt: string;
  tags: string[];
  saved?: boolean;
  upvoted?: boolean;
};

type SimilarThread = { id: string; title: string; subreddit: string };
type CompanionResp = { text: string; similar: SimilarThread[] };
type ModerateResp = {
  decision: "ALLOW" | "BLOCK" | "REVIEW";
  score: number; // 0..1
  flags: { label: string; match: boolean; note?: string }[];
  suggestedRules: string[];
};
type PersonalizeResp = {
  summary: string;
  picks: { id: string; title: string; subreddit: string }[];
  keywords: string[];
};
type APIResponse = CompanionResp | ModerateResp | PersonalizeResp;
type TabKey = "companion" | "moderation" | "personalize";

/** ---------- Mock data ---------- */
const INITIAL_POSTS: Post[] = [
  {
    id: "p1",
    subreddit: "r/ArtificialIntelligence",
    author: "u/bytebandit",
    title: "We rebuilt Reddit for 2025 with agents — feedback?",
    body:
      "Demo of an AI companion that guides first-time posters, moderates sensitive content, and curates feeds.",
    votes: 482,
    comments: 129,
    createdAt: "2h",
    tags: ["agents", "demo", "ux"],
  },
  {
    id: "p2",
    subreddit: "r/learnprogramming",
    author: "u/dev_dan",
    title: "How to structure agentic workflows for content moderation?",
    body:
      "Looking for examples of triage → rules → escalation using LLM tools + human-in-the-loop.",
    votes: 213,
    comments: 64,
    createdAt: "5h",
    tags: ["moderation", "workflows"],
  },
  {
    id: "p3",
    subreddit: "r/startups",
    author: "u/shipfast",
    title: "Show HN-style weekly: drop your AI-native MVP",
    body:
      "Post a link + 1-liner. The AI concierge will cluster similar posts and route early feedback.",
    votes: 761,
    comments: 301,
    createdAt: "1d",
    tags: ["mvp", "feedback", "launch"],
  },
];

const COMMUNITIES = [
  { name: "r/ArtificialIntelligence", members: "7.2M" },
  { name: "r/MachineLearning", members: "3.4M" },
  { name: "r/learnprogramming", members: "5.1M" },
  { name: "r/startups", members: "1.9M" },
  { name: "r/webdev", members: "3.7M" },
];

/** ---------- Mock API (swap later) ---------- */
async function mockFetch(
  endpoint: "/api/companion" | "/api/moderate" | "/api/personalize",
  payload: Record<string, unknown>
): Promise<APIResponse> {
  await new Promise((r) => setTimeout(r, 250));
  if (endpoint === "/api/companion") {
    return {
      text:
        `Overview for ${payload?.context ?? "this subreddit"}:\n` +
        `• Purpose: share progress, ask focused questions, cross-link prior threads.\n` +
        `• Tips: crisp title + 3–5 bullets + tags.\n` +
        `• I found similar threads — want to view?`,
      similar: [
        { id: "s1", title: "Best practices for agentic moderation", subreddit: "r/ArtificialIntelligence" },
        { id: "s2", title: "How I tuned my AI feed", subreddit: "r/startups" },
      ],
    };
  }
  if (endpoint === "/api/moderate") {
    return {
      decision: "ALLOW",
      score: 0.12,
      flags: [
        { label: "PII", match: false },
        { label: "Harassment", match: false },
        { label: "Spam", match: true, note: "Similar content exists; suggest merge" },
      ],
      suggestedRules: [
        "Require at least 1 topic tag",
        "Block URL-only posts",
        "Auto-reply FAQ for duplicate titles",
      ],
    };
  }
  return {
    summary: "Personalized mix: 80% subs you follow, 20% exploration.",
    picks: [
      { id: "r1", title: "Agentic UX patterns", subreddit: "r/webdev" },
      { id: "r2", title: "Human-in-loop moderation", subreddit: "r/MachineLearning" },
    ],
    keywords: ["agents", "moderation", "UX", "retrieval"],
  };
}

/** ---------- UI ---------- */
function RedditLogo({ className = "h-7 w-7" }: { className?: string }) {
  // reddit orange #FF4500
  return (
    <svg viewBox="0 0 512 512" className={className} aria-hidden="true">
      <circle cx="256" cy="256" r="256" fill="#ff4500" />
      <circle cx="256" cy="280" r="140" fill="#fff" />
      <circle cx="210" cy="270" r="28" fill="#ff4500" />
      <circle cx="302" cy="270" r="28" fill="#ff4500" />
      <path d="M196 330c30 34 90 34 120 0" stroke="#ff4500" strokeWidth="18" strokeLinecap="round" fill="none" />
      <circle cx="338" cy="212" r="22" fill="#fff" stroke="#ff4500" strokeWidth="12" />
      <circle cx="174" cy="212" r="22" fill="#fff" stroke="#ff4500" strokeWidth="12" />
      <path d="M296 160l22-50 60 14" stroke="#fff" strokeWidth="16" strokeLinecap="round" fill="none" />
      <circle cx="380" cy="126" r="20" fill="#fff" />
    </svg>
  );
}

function TopNav({
  onToggleAI,
  search,
  setSearch,
}: {
  onToggleAI: () => void;
  search: string;
  setSearch: (s: string) => void;
}) {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-2">
        <div className="flex items-center gap-2">
          <RedditLogo className="h-8 w-8" />
          <span className="text-lg font-extrabold tracking-tight">
            <span className="text-[#ff4500]">iReddit</span> • Intelligent Reddit

          </span>
        </div>
        <div className="mx-4 flex-1">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border px-3 py-2 text-sm focus:outline-none focus:ring focus:ring-[#ff4500]/30"
            placeholder="Search posts, people, communities…"
          />
        </div>
        <button
          onClick={onToggleAI}
          className="rounded-xl border px-3 py-2 text-sm hover:bg-[#ff4500]/10 border-[#ff4500] text-[#ff4500]"
          title="Toggle AI panel (,)"
        >
          AI Panel
        </button>
        <button className="rounded-xl bg-[#ff4500] px-3 py-2 text-sm font-medium text-white hover:brightness-95">
          Sign in
        </button>
      </div>
    </header>
  );
}

function CommunityList({ onPick }: { onPick: (sub: string | null) => void }) {
  return (
    <aside className="hidden w-64 shrink-0 lg:block">
      <div className="sticky top-16 space-y-3 p-2">
        <h3 className="px-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Communities</h3>
        <div className="space-y-2">
          <button
            onClick={() => onPick(null)}
            className="w-full rounded-xl border px-3 py-2 text-left text-sm hover:bg-gray-50"
          >
            🏠 Home (all)
          </button>
          {COMMUNITIES.map((c) => (
            <button
              key={c.name}
              onClick={() => onPick(c.name)}
              className="flex w-full items-center justify-between rounded-xl border px-3 py-2 text-left text-sm hover:bg-gray-50"
            >
              <span className="truncate">{c.name}</span>
              <span className="text-xs text-gray-500">{c.members}</span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}

function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-md border border-[#ff4500]/30 bg-[#ff4500]/5 px-2 py-0.5 text-xs text-[#ff4500]">
      {children}
    </span>
  );
}

function PostCard({
  post,
  onToggleSave,
  onToggleUpvote,
}: {
  post: Post;
  onToggleSave: (id: string) => void;
  onToggleUpvote: (id: string) => void;
}) {
  return (
    <article className="rounded-2xl border bg-white p-4 shadow-sm transition hover:shadow-md">
      <div className="mb-2 flex items-center gap-2 text-xs text-gray-500">
        <span className="font-medium text-gray-700">{post.subreddit}</span>
        <span>•</span>
        <span>Posted by {post.author}</span>
        <span>•</span>
        <span>{post.createdAt}</span>
      </div>
      <h2 className="mb-1 text-lg font-semibold leading-snug">{post.title}</h2>
      <p className="mb-3 text-sm text-gray-700">{post.body}</p>
      <div className="mb-3 flex flex-wrap gap-2">
        {post.tags.map((t) => (
          <Tag key={t}>{t}</Tag>
        ))}
      </div>
      <div className="flex items-center gap-3 text-sm text-gray-600">
        <button
          onClick={() => onToggleUpvote(post.id)}
          className={`rounded-xl border px-2 py-1 ${post.upvoted ? "border-[#ff4500] text-[#ff4500] bg-[#ff4500]/10" : ""}`}
          aria-pressed={post.upvoted}
        >
          ▲ {post.votes}
        </button>
        <button className="rounded-xl border px-2 py-1">💬 {post.comments}</button>
        <button className="rounded-xl border px-2 py-1">🔗 Share</button>
        <button
          onClick={() => onToggleSave(post.id)}
          className={`ml-auto rounded-xl border px-2 py-1 ${post.saved ? "bg-amber-100 border-amber-300" : ""}`}
          aria-pressed={post.saved}
        >
          {post.saved ? "Saved ✓" : "Save"}
        </button>
      </div>
    </article>
  );
}

function Composer({
  onAdd,
}: {
  onAdd: (title: string, body: string, subreddit: string, tags: string[]) => void;
}) {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [subs, setSubs] = useState("r/ArtificialIntelligence");
  const [tags, setTags] = useState("");

  return (
    <div className="rounded-2xl border bg-white p-3">
      <div className="mb-2 grid grid-cols-1 gap-2 md:grid-cols-[1fr_14rem]">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full rounded-xl border px-3 py-2 text-sm"
          placeholder="Create post title"
        />
        <select
          value={subs}
          onChange={(e) => setSubs(e.target.value)}
          className="rounded-xl border px-3 py-2 text-sm"
        >
          {COMMUNITIES.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
      </div>
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        className="mb-2 h-24 w-full rounded-xl border px-3 py-2 text-sm"
        placeholder="Write something helpful…"
      />
      <div className="flex items-center gap-2">
        <input
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          className="w-full rounded-xl border px-3 py-2 text-sm"
          placeholder="tags (comma separated)"
        />
        <button
          onClick={() => {
            if (!title.trim()) return;
            onAdd(
              title.trim(),
              body.trim(),
              subs,
              tags
                .split(",")
                .map((t) => t.trim())
                .filter(Boolean)
            );
            setTitle("");
            setBody("");
            setTags("");
          }}
          className="rounded-xl bg-[#ff4500] px-3 py-2 text-sm font-medium text-white hover:brightness-95"
        >
          Post
        </button>
      </div>
    </div>
  );
}

function Feed({
  posts,
  onToggleSave,
  onToggleUpvote,
  onAddPost,
}: {
  posts: Post[];
  onToggleSave: (id: string) => void;
  onToggleUpvote: (id: string) => void;
  onAddPost: (title: string, body: string, subreddit: string, tags: string[]) => void;
}) {
  return (
    <main className="mx-auto w-full max-w-2xl space-y-4">
      <Composer onAdd={onAddPost} />
      {posts.map((p) => (
        <PostCard key={p.id} post={p} onToggleSave={onToggleSave} onToggleUpvote={onToggleUpvote} />
      ))}
    </main>
  );
}

function PanelHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="border-b bg-white p-4">
      <h3 className="text-sm font-semibold">{title}</h3>
      {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
    </div>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">{label}</h4>
      {children}
    </section>
  );
}

function AISidePanel({ open, onClose, input, setInput }: {
  open: boolean;
  onClose: () => void;
  input: string;
  setInput: (v: string) => void;
}) {
  const [tab, setTab] = useState<TabKey>("companion");
  const [loading, setLoading] = useState<boolean>(false);
  const [output, setOutput] = useState<APIResponse | null>(null);

  const title = useMemo(() => {
    if (tab === "companion") return "Subreddit Companion";
    if (tab === "moderation") return "Content Moderation";
    return "Personalized Feed";
  }, [tab]);

 useEffect(() => {
  if (!open) return;
  (async () => {
    setLoading(true);
    const endpoint =
      tab === "companion"
        ? "/api/companion"
        : tab === "moderation"
        ? "/api/moderate"
        : "/api/personalize";

    const data = await mockFetch(endpoint, {
      query: "", // ignore input here
      context: "r/ArtificialIntelligence",
    });

    setOutput(data);
    setLoading(false);
  })();
}, [open, tab]); // <--- no input here

  const onAsk = async () => {
    setLoading(true);
    const data = await mockFetch(
      tab === "companion" ? "/api/companion" : tab === "moderation" ? "/api/moderate" : "/api/personalize",
      { query: input, context: "r/ArtificialIntelligence" }
    );
    setOutput(data);
    setLoading(false);
  };

  return (
    <div
      className={`fixed right-0 top-0 z-40 h-screen w-[24rem] transform border-l bg-white shadow-2xl transition-transform duration-300 ${
        open ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <PanelHeader title={`AI • ${title}`} subtitle="Press , (comma) to toggle" />

      <div className="flex items-center gap-1 border-b bg-white p-2">
        {(["companion", "moderation", "personalize"] as const).map((k) => (
          <button
            key={k}
            onClick={() => setTab(k)}
            className={`rounded-xl px-3 py-1 text-sm ${k === tab ? "bg-[#ff4500] text-white" : "border"}`}
          >
            {k.charAt(0).toUpperCase() + k.slice(1)}
          </button>
        ))}
        <button onClick={onClose} className="ml-auto rounded-xl border px-2 py-1 text-sm">
          Close
        </button>
      </div>

      <div className="flex h-[calc(100vh-170px)] flex-col gap-3 overflow-y-auto p-4">
        {/* Companion */}
        {tab === "companion" && (
          <div className="space-y-4">
            <Section label="Overview">
              <p className="text-sm text-gray-700">
                {loading ? "Thinking…" : output && "text" in output ? output.text : "Ask anything about this subreddit."}
              </p>
            </Section>
            <Section label="Similar Threads">
              <ul className="space-y-2 text-sm">
                {output && "similar" in output &&
                  output.similar.map((s) => (
                    <li key={s.id} className="flex items-center justify-between">
                      <span className="truncate pr-2">{s.title}</span>
                      <span className="text-xs text-gray-500">{s.subreddit}</span>
                    </li>
                  ))}
              </ul>
            </Section>
          </div>
        )}

        {/* Moderation */}
        {tab === "moderation" && (
          <div className="space-y-4">
            <Section label="Decision">
              <div className="rounded-xl border p-3 text-sm">
                {loading ? (
                  <span>Evaluating…</span>
                ) : output && "decision" in output ? (
                  <div className="flex items-center gap-2">
                    <span className="rounded-md bg-gray-100 px-2 py-0.5 text-xs">{output.decision}</span>
                    <span className="text-xs text-gray-500">risk={Math.round(output.score * 100)}%</span>
                  </div>
                ) : null}
              </div>
            </Section>
            <Section label="Flags">
              <ul className="space-y-2 text-sm">
                {output && "flags" in output &&
                  output.flags.map((f, i) => (
                    <li key={i} className="flex items-center justify-between rounded-xl border p-2">
                      <span>{f.label}</span>
                      <span className={`text-xs ${f.match ? "text-red-600" : "text-gray-500"}`}>
                        {f.match ? "match" : "clear"}
                      </span>
                    </li>
                  ))}
              </ul>
            </Section>
            <Section label="Suggested Rules">
              <ul className="list-disc space-y-1 pl-5 text-sm text-gray-700">
                {output && "suggestedRules" in output &&
                  output.suggestedRules.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </Section>
          </div>
        )}

        {/* Personalize */}
        {tab === "personalize" && (
          <div className="space-y-4">
            <Section label="Summary">
              <p className="text-sm text-gray-700">
                {loading ? "Crunching…" : output && "summary" in output ? output.summary : ""}
              </p>
            </Section>
            <Section label="Recommended Posts">
              <ul className="space-y-2 text-sm">
                {output && "picks" in output &&
                  output.picks.map((p) => (
                    <li key={p.id} className="flex items-center justify-between">
                      <span className="truncate pr-2">{p.title}</span>
                      <span className="text-xs text-gray-500">{p.subreddit}</span>
                    </li>
                  ))}
              </ul>
            </Section>
            <Section label="Inferred Keywords">
              <div className="flex flex-wrap gap-2">
                {output && "keywords" in output &&
                  output.keywords.map((k) => (
                    <span key={k} className="rounded-md border px-2 py-0.5 text-xs text-gray-700">
                      {k}
                    </span>
                  ))}
              </div>
            </Section>
          </div>
        )}
      </div>

      <div className="border-t bg-white p-3">
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full rounded-xl border px-3 py-2 text-sm"
            placeholder="Ask, paste a draft, or describe interests…"
          />
          <button onClick={onAsk} className="rounded-xl bg-[#ff4500] px-3 py-2 text-sm font-medium text-white">
            Ask
          </button>
        </div>
      </div>
    </div>
  );
}

// NEW
export default function IRedditDemo() {

  const [aiOpen, setAiOpen] = useState<boolean>(true);
  const [posts, setPosts] = useState<Post[]>(INITIAL_POSTS);
  const [search, setSearch] = useState("");
  const [activeSub, setActiveSub] = useState<string | null>(null);
  const [aiInput, setAiInput] = useState("");

  // Ensure the feed stays visible when the AI panel is open on large screens
  // by adding right padding equal to panel width.
  const rightPadding = aiOpen ? "lg:pr-[24rem]" : "";

  useEffect(() => {
    const onKey = (e: WindowEventMap["keydown"]) => {
      if (e.key === ",") setAiOpen((v) => !v);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const visiblePosts = useMemo(() => {
    return posts
      .filter((p) => (activeSub ? p.subreddit === activeSub : true))
      .filter((p) => {
        if (!search.trim()) return true;
        const q = search.toLowerCase();
        return (
          p.title.toLowerCase().includes(q) ||
          p.body.toLowerCase().includes(q) ||
          p.tags.join(" ").toLowerCase().includes(q) ||
          p.subreddit.toLowerCase().includes(q)
        );
      });
  }, [posts, activeSub, search]);

  function toggleSave(id: string) {
    setPosts((arr) =>
      arr.map((p) => (p.id === id ? { ...p, saved: !p.saved } : p))
    );
  }

  function toggleUpvote(id: string) {
    setPosts((arr) =>
      arr.map((p) =>
        p.id === id
          ? {
              ...p,
              upvoted: !p.upvoted,
              votes: p.upvoted ? p.votes - 1 : p.votes + 1,
            }
          : p
      )
    );
  }

  function addPost(title: string, body: string, subreddit: string, tags: string[]) {
    const newPost: Post = {
      id: "p" + (posts.length + 1),
      author: "u/you",
      subreddit,
      title,
      body,
      votes: 1,
      comments: 0,
      createdAt: "now",
      tags: tags.length ? tags : ["new"],
    };
    setPosts((arr) => [newPost, ...arr]);
    setActiveSub(subreddit);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className={`min-h-screen bg-[#fff8f6] text-gray-900 ${rightPadding}`}>
      <TopNav onToggleAI={() => setAiOpen((v) => !v)} search={search} setSearch={setSearch} />

      {/* Content grid */}
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 px-4 py-6 lg:grid-cols-[16rem_minmax(0,1fr)]">
        <CommunityList onPick={setActiveSub} />
        <Feed
          posts={visiblePosts}
          onToggleSave={toggleSave}
          onToggleUpvote={toggleUpvote}
          onAddPost={addPost}
        />
      </div>

      {/* Right AI panel (overlay on small screens; reserved space on lg via padding) */}
      <AISidePanel open={aiOpen} onClose={() => setAiOpen(false)} input={aiInput} setInput={setAiInput} />

      {/* Edge handle when closed */}
      {!aiOpen && (
        <button
          onClick={() => setAiOpen(true)}
          className="fixed right-0 top-1/2 z-30 -translate-y-1/2 rounded-l-xl border bg-white px-2 py-3 text-xs shadow hover:bg-[#ff4500]/10"
          title="Open AI Panel"
        >
          AI
        </button>
      )}
    </div>
  );
}
