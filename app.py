"""
Nexus Research: a mission-control UI for the multi-agent research pipeline.

Run with:  streamlit run app.py
Keep this file next to agents.py (and pipeline.py).
"""

import html
import re
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # reads TAVILY_API_KEY / GEMINI_API_KEY from .env

# langchain-google-genai looks for GOOGLE_API_KEY, so accept GEMINI_API_KEY too.
import os

if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

st.set_page_config(
    page_title="Nexus Research",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# Design tokens + CSS
# ──────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --void: #000000;
  --deep: #030a1f;
  --panel: rgba(4, 12, 36, 0.62);
  --line: rgba(92, 184, 255, 0.14);
  --ice: #5cb8ff;
  --plasma: #2f6bff;
  --ember: #ffb454;
  --ok: #5ef2b0;
  --err: #ff6b81;
  --text: #e6ebff;
  --muted: #8fa6d9;
}

html, body, [class*="css"], .stApp {
  font-family: 'Space Grotesk', system-ui, sans-serif;
  color: var(--text);
}
.stApp {
  background:
    radial-gradient(1100px 600px at 12% -10%, rgba(20, 80, 255, 0.34), transparent 60%),
    radial-gradient(900px 500px at 95% 10%, rgba(92, 184, 255, 0.13), transparent 60%),
    radial-gradient(1000px 500px at 50% 115%, rgba(20, 80, 255, 0.28), transparent 65%),
    var(--void);
}
/* moving star-grid */
.stApp::before {
  content: "";
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(92,184,255,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(92,184,255,.05) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse at 50% 20%, #000 20%, transparent 75%);
  -webkit-mask-image: radial-gradient(ellipse at 50% 20%, #000 20%, transparent 75%);
  animation: gridDrift 24s linear infinite;
}
@keyframes gridDrift { to { background-position: 56px 56px, 56px 56px; } }

header[data-testid="stHeader"], footer, #MainMenu { visibility: hidden; height: 0; }
.block-container { padding-top: 2.2rem; max-width: 1180px; position: relative; z-index: 1; }

/* ── Hero ── */
.hero { margin-bottom: 1.6rem; }
.hero h1 {
  font-size: clamp(2.2rem, 5vw, 3.6rem); font-weight: 700; letter-spacing: -0.03em;
  line-height: 1.02; margin: 0.5rem 0 0.6rem 0;
  background: linear-gradient(100deg, #fff 10%, var(--ice) 40%, var(--plasma) 65%, #fff 90%);
  background-size: 250% 100%;
  -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: shimmer 7s ease-in-out infinite;
}
@keyframes shimmer { 0%,100% { background-position: 0% 0; } 50% { background-position: 100% 0; } }
.hero p { color: var(--muted); font-size: 1.05rem; max-width: 58ch; margin: 0; }
.chip {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 5px 12px; border-radius: 999px;
  border: 1px solid var(--line); background: rgba(2, 8, 26, 0.85);
  font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: var(--ice);
}
.chip .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--ok);
  box-shadow: 0 0 0 0 rgba(94,242,176,.6); animation: ping 2s infinite; }
@keyframes ping { 70% { box-shadow: 0 0 0 9px rgba(94,242,176,0); } 100% { box-shadow: 0 0 0 0 rgba(94,242,176,0); } }

/* ── Input form ── */
[data-testid="stForm"] {
  border: 1px solid var(--line); border-radius: 18px; padding: 1.1rem 1.2rem 0.4rem;
  background: var(--panel); backdrop-filter: blur(14px);
  box-shadow: 0 0 0 1px rgba(47,107,255,.08), 0 20px 60px -30px rgba(47,107,255,.6);
}
.stTextInput input {
  background: rgba(0, 0, 0, 0.85) !important; color: var(--text) !important;
  border: 1px solid var(--line) !important; border-radius: 12px !important;
  font-size: 1.05rem !important; padding: 0.85rem 1rem !important;
  transition: border-color .2s, box-shadow .2s;
}
.stTextInput input:focus {
  border-color: var(--ice) !important;
  box-shadow: 0 0 0 3px rgba(92,184,255,.18), 0 0 30px rgba(92,184,255,.15) !important;
}
.stTextInput label p { color: var(--muted) !important; }
.stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button {
  border: 0 !important; border-radius: 12px !important; font-weight: 600 !important;
  color: #05081a !important; padding: 0.7rem 1.6rem !important;
  background: linear-gradient(110deg, var(--ice), #2f6bff 55%, var(--ice)) !important;
  background-size: 200% 100% !important;
  transition: transform .15s, box-shadow .25s, background-position .6s !important;
}
.stButton button:hover, .stDownloadButton button:hover, [data-testid="stFormSubmitButton"] button:hover {
  transform: translateY(-2px); background-position: 100% 0 !important;
  box-shadow: 0 10px 30px -8px rgba(92,184,255,.55) !important;
}
.stButton button:focus-visible, [data-testid="stFormSubmitButton"] button:focus-visible {
  outline: 2px solid #fff !important; outline-offset: 2px;
}

/* ── Pipeline relay ── */
.relay {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 1.6rem 1.2rem 1.3rem; margin: 1.4rem 0 0.8rem;
  border: 1px solid var(--line); border-radius: 18px; background: var(--panel);
  backdrop-filter: blur(14px); overflow-x: auto; gap: 4px;
}
.node { flex: 0 0 158px; text-align: center; }
.orb {
  position: relative; width: 74px; height: 74px; margin: 0 auto 0.8rem; border-radius: 50%;
  display: grid; place-items: center; font-size: 1.85rem;
  background: radial-gradient(circle at 30% 25%, #0f2a6e, #020818);
  border: 1.5px solid rgba(139, 150, 201, 0.35); transition: all .5s;
}
.node .t { font-weight: 600; font-size: 1.02rem; }
.node .s { color: var(--muted); font-size: 0.84rem; margin-top: 2px; min-height: 2.4em; }
.node .st { margin-top: 6px; font-family: 'IBM Plex Mono', monospace; font-size: 0.76rem; color: var(--muted); }

.node.pending .orb { filter: grayscale(.8) opacity(.6); }

.node.running .orb {
  border-color: var(--ember); box-shadow: 0 0 34px rgba(255,180,84,.45);
  animation: breathe 1.6s ease-in-out infinite;
}
.node.running .orb::before {          /* rotating scanner ring */
  content: ""; position: absolute; inset: -9px; border-radius: 50%;
  border: 2px solid transparent; border-top-color: var(--ember); border-right-color: rgba(255,180,84,.3);
  animation: spin 1.1s linear infinite;
}
.node.running .orb::after {           /* expanding pulse */
  content: ""; position: absolute; inset: 0; border-radius: 50%;
  border: 2px solid var(--ember); animation: pulse 1.6s ease-out infinite;
}
.node.running .st { color: var(--ember); }

.node.done .orb { border-color: var(--ok); box-shadow: 0 0 26px rgba(94,242,176,.32); }
.node.done .orb::after {
  content: "✓"; position: absolute; right: -4px; bottom: -4px; width: 24px; height: 24px;
  border-radius: 50%; background: var(--ok); color: #04150d; font-size: .85rem; font-weight: 700;
  display: grid; place-items: center; animation: pop .45s cubic-bezier(.2,1.6,.4,1);
}
.node.done .st { color: var(--ok); }

.node.error .orb { border-color: var(--err); box-shadow: 0 0 26px rgba(255,107,129,.4); }
.node.error .st { color: var(--err); }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes breathe { 50% { transform: scale(1.06); } }
@keyframes pulse { from { transform: scale(1); opacity: .7; } to { transform: scale(1.7); opacity: 0; } }
@keyframes pop { from { transform: scale(0); } to { transform: scale(1); } }

.link {
  flex: 1 1 30px; min-width: 24px; height: 3px; margin-top: 36px; border-radius: 3px;
  background: rgba(139,150,201,.22); position: relative; overflow: hidden;
}
.link.on { background: linear-gradient(90deg, var(--ok), var(--ice)); }
.link.flow::after {
  content: ""; position: absolute; top: 0; left: -40%; width: 40%; height: 100%;
  background: linear-gradient(90deg, transparent, var(--ember), transparent);
  animation: flow 1.1s linear infinite;
}
@keyframes flow { to { left: 100%; } }

/* ── Progress ── */
.bar { height: 6px; border-radius: 6px; background: rgba(139,150,201,.18); overflow: hidden; margin: 0 0 1.2rem; }
.bar > span {
  display: block; height: 100%; border-radius: 6px; transition: width .7s cubic-bezier(.2,.8,.2,1);
  background: linear-gradient(90deg, var(--plasma), var(--ice), var(--plasma)); background-size: 200% 100%;
  animation: barflow 2.4s linear infinite;
}
@keyframes barflow { to { background-position: 200% 0; } }

/* ── Live console ── */
.console {
  border: 1px solid var(--line); border-radius: 14px; background: rgba(0, 0, 0, .9);
  font-family: 'IBM Plex Mono', monospace; font-size: 0.83rem; overflow: hidden;
}
.console .top { padding: 8px 14px; border-bottom: 1px solid var(--line); color: var(--muted); display: flex; gap: 6px; align-items: center; }
.console .top i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.console .body { padding: 12px 14px; max-height: 210px; overflow-y: auto; }
.console .ln { padding: 2px 0; color: #b9c3f5; }
.console .ln b { color: var(--muted); font-weight: 400; margin-right: 10px; }
.console .ln.ok { color: var(--ok); }
.console .ln.run { color: var(--ember); }
.console .ln.err { color: var(--err); }
.console .cursor { display: inline-block; width: 8px; height: 14px; background: var(--ice); vertical-align: middle; animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* ── Metrics ── */
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin: 1.4rem 0 0.6rem; }
.metric { border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px; background: var(--panel); }
.metric .v { font-size: 1.7rem; font-weight: 700; color: var(--ice); letter-spacing: -0.02em; }
.metric .l { color: var(--muted); font-size: 0.85rem; }

/* ── Results ── */
button[data-baseweb="tab"] { color: var(--muted) !important; font-weight: 500; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--ice) !important; }
div[data-baseweb="tab-highlight"] { background-color: var(--ice) !important; }
[data-testid="stTabsContent"], div[role="tabpanel"] { animation: reveal .7s ease both; }
@keyframes reveal { from { opacity: 0; transform: translateY(14px); filter: blur(4px); } to { opacity: 1; transform: none; filter: none; } }
.paper {
  border: 1px solid var(--line); border-radius: 16px; padding: 1.4rem 1.6rem;
  background: rgba(2, 8, 26, .72); line-height: 1.7;
}
.paper h1, .paper h2, .paper h3 { color: #fff; letter-spacing: -0.01em; }
.paper a { color: var(--ice); }
.rawbox { font-family: 'IBM Plex Mono', monospace; font-size: .83rem; white-space: pre-wrap; color: #b9c3f5; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .001s !important; animation-iteration-count: 1 !important; }
}
@media (max-width: 720px) { .node { flex-basis: 132px; } }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Pipeline definition
# ──────────────────────────────────────────────────────────────────────────────
STEPS = [
    {"icon": "🛰️", "title": "Search agent", "sub": "Scans the web for recent, reliable sources"},
    {"icon": "🕸️", "title": "Reader agent", "sub": "Opens the best link and pulls deep content"},
    {"icon": "✍️", "title": "Writer chain", "sub": "Drafts the full research report"},
    {"icon": "🧠", "title": "Critic chain", "sub": "Reviews the report and scores its quality"},
]
STATUS_LABEL = {"pending": "standby", "running": "working…", "done": "complete", "error": "failed"}


def text_of(x) -> str:
    """Normalise whatever an agent / chain returns into plain text."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    content = getattr(x, "content", x)
    if isinstance(content, list):  # content-block style responses
        return "\n".join(
            b.get("text", "") if isinstance(b, dict) else str(b) for b in content
        )
    return str(content)


URL_RE = re.compile(r"https?://[^\s\)\]>\"']+")


def log_tool_calls(run: dict, messages) -> None:
    """Show which tools the LangChain agent actually called."""
    for m in messages:
        for call in getattr(m, "tool_calls", None) or []:
            args = call.get("args", {}) or {}
            arg = str(next(iter(args.values()), ""))[:70]
            log(run, "", f"  ↳ tool {call.get('name')}({arg})")


def fresh_run(topic: str = "") -> dict:
    return {
        "topic": topic,
        "status": ["pending"] * 4,
        "secs": [None] * 4,
        "logs": [],
        "result": None,
        "total": None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Renderers
# ──────────────────────────────────────────────────────────────────────────────
def relay_html(run: dict) -> str:
    parts = ['<div class="relay">']
    for i, step in enumerate(STEPS):
        s = run["status"][i]
        secs = run["secs"][i]
        label = STATUS_LABEL[s] + (f" · {secs:.1f}s" if secs is not None and s in ("done", "error") else "")
        parts.append(
            f'<div class="node {s}"><div class="orb">{step["icon"]}</div>'
            f'<div class="t">{step["title"]}</div><div class="s">{step["sub"]}</div>'
            f'<div class="st">{label}</div></div>'
        )
        if i < len(STEPS) - 1:
            cls = "link"
            if run["status"][i] == "done":
                cls += " on"
            if run["status"][i] == "done" and run["status"][i + 1] == "running":
                cls += " flow"
            parts.append(f'<div class="{cls}"></div>')
    parts.append("</div>")

    done = sum(1 for s in run["status"] if s == "done")
    running = any(s == "running" for s in run["status"])
    pct = min(100, done * 25 + (12 if running else 0))
    parts.append(f'<div class="bar"><span style="width:{pct}%"></span></div>')
    return "".join(parts)


def console_html(run: dict, live: bool) -> str:
    lines = "".join(
        f'<div class="ln {lvl}"><b>{ts}</b>{html.escape(msg)}</div>'
        for ts, lvl, msg in run["logs"][-14:]
    )
    if not lines:
        lines = '<div class="ln"><b>--:--:--</b>Waiting for a topic…</div>'
    cursor = '<span class="cursor"></span>' if live else ""
    return (
        '<div class="console"><div class="top">'
        '<i style="background:#ff6b81"></i><i style="background:#ffb454"></i><i style="background:#5ef2b0"></i>'
        '<span style="margin-left:8px">mission log</span></div>'
        f'<div class="body">{lines}{cursor}</div></div>'
    )


def paint(run: dict, pipe_ph, log_ph, live: bool = True):
    pipe_ph.markdown(relay_html(run), unsafe_allow_html=True)
    log_ph.markdown(console_html(run, live), unsafe_allow_html=True)


def log(run: dict, level: str, msg: str):
    run["logs"].append((datetime.now().strftime("%H:%M:%S"), level, msg))


# ──────────────────────────────────────────────────────────────────────────────
# Pipeline execution (same 4 steps as pipeline.py, but observable one by one)
# ──────────────────────────────────────────────────────────────────────────────
def execute(topic: str, pipe_ph, log_ph) -> dict:
    run = fresh_run(topic)
    st.session_state["run"] = run
    started = time.perf_counter()
    state: dict = {}

    def begin(i, msg):
        run["status"][i] = "running"
        log(run, "run", msg)
        paint(run, pipe_ph, log_ph)
        return time.perf_counter()

    def finish(i, t0, msg):
        run["secs"][i] = time.perf_counter() - t0
        run["status"][i] = "done"
        log(run, "ok", msg)
        paint(run, pipe_ph, log_ph)

    def fail(i, t0, exc):
        run["secs"][i] = time.perf_counter() - t0
        run["status"][i] = "error"
        log(run, "err", f"{STEPS[i]['title']} failed: {exc}")
        paint(run, pipe_ph, log_ph, live=False)

    # Import lazily so a missing dependency shows up in the console, not as a crash.
    log(run, "", "Booting agents…")
    paint(run, pipe_ph, log_ph)
    try:
        from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain
    except Exception as exc:  # noqa: BLE001
        run["status"][0] = "error"
        log(run, "err", f"Could not import agents.py: {exc}")
        import sys
        log(run, "", f"Python in use: {sys.executable}")
        log(run, "", f"Fix: run  \"{sys.executable}\" -m pip install langchain langchain-google-genai tavily-python beautifulsoup4 requests python-dotenv")
        paint(run, pipe_ph, log_ph, live=False)
        return run

    # 1 ── Search
    t0 = begin(0, f"Search agent scanning the web for “{topic}”")
    try:
        search_agent = build_search_agent()
        res = search_agent.invoke(
            {"messages": [("user", f"Find the recent and reliable information about {topic}")]}
        )
        log_tool_calls(run, res["messages"])
        state["search_result"] = text_of(res["messages"][-1])
        raw_tool_output = "\n".join(text_of(m) for m in res["messages"] if getattr(m, "type", "") == "tool")
        state["n_sources"] = len(set(URL_RE.findall(raw_tool_output + "\n" + state["search_result"])))
        finish(0, t0, f"Search complete, {state['n_sources']} source link(s) found")
    except Exception as exc:  # noqa: BLE001
        fail(0, t0, exc)
        return run

    # 2 ── Read / scrape
    t0 = begin(1, "Reader agent picking the strongest source and scraping it")
    try:
        reader = build_reader_agent()
        res = reader.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search results: \n {state['search_result'][:800]}",
                    )
                ]
            }
        )
        log_tool_calls(run, res["messages"])
        state["scraped_content"] = text_of(res["messages"][-1])
        finish(1, t0, f"Deep read complete, {len(state['scraped_content']):,} characters captured")
    except Exception as exc:  # noqa: BLE001
        fail(1, t0, exc)
        return run

    # 3 ── Write
    t0 = begin(2, "Writer chain drafting the report")
    try:
        combined = (
            f"SEARCH_RESULTS : \n {state['search_result']}\n\n"
            f"DETAILED_INFORMATION : \n {state['scraped_content']}"
        )
        state["report"] = text_of(writer_chain.invoke({"topic": topic, "research": combined}))
        finish(2, t0, f"Report drafted, {len(state['report'].split()):,} words")
    except Exception as exc:  # noqa: BLE001
        fail(2, t0, exc)
        return run

    # 4 ── Critique
    t0 = begin(3, "Critic chain reviewing the report")
    try:
        state["feedback"] = text_of(critic_chain.invoke({"report": state["report"]}))
        finish(3, t0, "Review complete")
    except Exception as exc:  # noqa: BLE001
        fail(3, t0, exc)
        return run

    run["total"] = time.perf_counter() - started
    log(run, "ok", f"Mission complete in {run['total']:.1f}s")
    run["result"] = state
    paint(run, pipe_ph, log_ph, live=False)
    return run


# ──────────────────────────────────────────────────────────────────────────────
# Page
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
  <span class="chip"><span class="dot"></span>4 agents online</span>
  <h1>Ask a question.<br>Four agents build the answer.</h1>
  <p>Enter any topic. Nexus searches the web, reads the best source, writes a full report,
  and then has a critic grade it. You can watch every step as it happens.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.form("query", border=True):
    topic_in = st.text_input(
        "Research topic",
        placeholder="e.g. Solid-state batteries in electric vehicles",
    )
    go = st.form_submit_button("Launch research")

pipe_ph = st.empty()
log_ph = st.empty()

if go:
    if not topic_in.strip():
        st.warning("Enter a topic first, then press Launch research.")
    else:
        run = execute(topic_in.strip(), pipe_ph, log_ph)
elif "run" in st.session_state:
    run = st.session_state["run"]
    paint(run, pipe_ph, log_ph, live=False)
else:
    run = fresh_run()
    paint(run, pipe_ph, log_ph, live=False)

# ── Results ──
result = run.get("result") if run else None
if result:
    words = len(result["report"].split())
    sources = result.get("n_sources", len(set(URL_RE.findall(result["search_result"]))))
    st.markdown(
        '<div class="metrics">'
        f'<div class="metric"><div class="v">{run["total"]:.1f}s</div><div class="l">Total run time</div></div>'
        f'<div class="metric"><div class="v">{sources}</div><div class="l">Sources found</div></div>'
        f'<div class="metric"><div class="v">{len(result["scraped_content"]):,}</div><div class="l">Characters read in depth</div></div>'
        f'<div class="metric"><div class="v">{words:,}</div><div class="l">Words in the report</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    tab_report, tab_feedback, tab_search, tab_scrape = st.tabs(
        ["Report", "Critic feedback", "Search results", "Scraped content"]
    )
    with tab_report:
        st.markdown('<div class="paper">', unsafe_allow_html=True)
        st.markdown(result["report"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Dual format downloads (.md and .txt)
        st.write("")
        col_md, col_txt = st.columns(2)
        file_prefix = re.sub(r"\W+", "_", run["topic"]).strip("_").lower()[:60]

        with col_md:
            st.download_button(
                "Download report (.md)",
                data=result["report"],
                file_name=f"{file_prefix}_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_txt:
            st.download_button(
                "Download report (.txt)",
                data=result["report"],
                file_name=f"{file_prefix}_report.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with tab_feedback:
        st.markdown('<div class="paper">', unsafe_allow_html=True)
        st.markdown(result["feedback"])
        st.markdown("</div>", unsafe_allow_html=True)
    with tab_search:
        st.markdown(
            f'<div class="paper rawbox">{html.escape(result["search_result"])}</div>',
            unsafe_allow_html=True,
        )
    with tab_scrape:
        st.markdown(
            f'<div class="paper rawbox">{html.escape(result["scraped_content"])}</div>',
            unsafe_allow_html=True,
        )