"""Streamlit UI for AI News Aggregator."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.state_manager import StateManager
from src.discovery import NewsDiscovery
from src.scoring import NewsScorer
from src.tagger import NewsTagger
from src.obsidian_writer import ObsidianWriter
from src.researcher import Researcher
from src.content_creator import ContentCreator


st.set_page_config(
    page_title="AI News Aggregator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Component initialisation (cached across reruns)
# ---------------------------------------------------------------------------

@st.cache_resource
def load_components():
    config = Config("config/config.yaml")
    state = StateManager(prune_after_weeks=config.get('state.archive_after_weeks', 12))
    discovery = NewsDiscovery(config, state)
    scorer = NewsScorer(config)
    tagger = NewsTagger(config)
    obsidian = ObsidianWriter(config)
    researcher = Researcher(config, discovery)
    content_creator = ContentCreator(config)
    return config, state, discovery, scorer, tagger, obsidian, researcher, content_creator


try:
    config, state, discovery, scorer, tagger, obsidian, researcher, content_creator = load_components()
except Exception as e:
    st.error(f"**Initialisation failed:** {e}")
    st.info("Make sure `config/config.yaml` exists. Copy `config/config.example.yaml` and fill in your settings.")
    st.stop()


# ---------------------------------------------------------------------------
# Session-state defaults
# ---------------------------------------------------------------------------

defaults = {
    "news_items": [],
    "shortlist": [],
    "deep_dive_items": [],
    "selected_for_deep_dive": [],
    "presentation_file": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🤖 AI News Aggregator")
    st.divider()

    # Always read fresh state from disk
    state.weekly_state = state._load_weekly_state()
    weekly_state = state.weekly_state

    if weekly_state:
        st.metric("Current Week", weekly_state.week)
        stage_label = weekly_state.stage.replace("_", " ").title()
        st.metric("Stage", stage_label)

        c1, c2, c3 = st.columns(3)
        c1.metric("Found", weekly_state.items_discovered)
        c2.metric("Selected", weekly_state.items_shortlisted)
        c3.metric("Deep Dived", weekly_state.items_deep_dived)
    else:
        st.info("No active week. Use the **Dashboard** tab to start.")

    st.divider()

    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()


# ---------------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------------

tab_dash, tab_discover, tab_review, tab_deepdive = st.tabs(
    ["📊 Dashboard", "🔍 Discover", "✅ Review", "🔬 Deep Dive"]
)


# ── Tab 1: Dashboard ────────────────────────────────────────────────────────

with tab_dash:
    st.header("Weekly Workflow")

    STAGES = [
        ("🔍", "Discovery",        "Fetch articles from RSS feeds, websites, and searches"),
        ("🏷️", "Scoring & Tagging", "Score by relevance and auto-generate tags with Claude"),
        ("✅", "Review",            "Pick the best articles for deeper research"),
        ("🔬", "Deep Dive",         "Multi-source research on selected articles"),
        ("📊", "Presentation",      "Generate a narration-ready slide deck (.pptx)"),
    ]

    current_stage = weekly_state.stage if weekly_state else ""

    for icon, name, desc in STAGES:
        col_icon, col_text = st.columns([1, 8])
        col_icon.markdown(f"## {icon}")
        col_text.markdown(f"**{name}**  \n{desc}")

    st.divider()

    if st.button("🚀 Start New Week", type="primary", use_container_width=False):
        state.init_new_week()
        for key, value in defaults.items():
            st.session_state[key] = value
        # Clear any per-article checkbox state
        for key in list(st.session_state.keys()):
            if key.startswith("select_"):
                del st.session_state[key]
        st.success("New week initialised. Head to the **Discover** tab.")
        st.rerun()


# ── Tab 2: Discover ─────────────────────────────────────────────────────────

with tab_discover:
    st.header("News Discovery")

    col_btn, col_hint = st.columns([2, 8])
    run_clicked = col_btn.button("🔍 Run Discovery", type="primary", use_container_width=True)

    if not weekly_state:
        col_hint.warning("Start a new week first (Dashboard tab).")
    else:
        col_hint.caption(f"Will fetch, score, tag, and export all articles to Obsidian.")

    if run_clicked:
        if not weekly_state:
            st.warning("Please start a new week first.")
        else:
            with st.status("Running discovery pipeline…", expanded=True) as status:
                st.write("Fetching articles from all sources…")
                items = discovery.discover_all()

                if not items:
                    status.update(label="No articles found. Check your sources.", state="error")
                    st.stop()

                st.write(f"Found **{len(items)}** articles. Scoring…")
                items = scorer.score_all(items)

                st.write("Generating tags with Claude…")
                min_tag_score = config.get("selection.min_score", 40)
                tagger.tag_all(items, min_score=min_tag_score)

                st.write("Exporting to Obsidian…")
                for item in items:
                    state.mark_url_processed(item.url, "scanned", item.week)
                    state.add_discovered_url(item.url)
                obsidian.export_scanned_items(items)
                state.update_stage("scoring_complete")

                shortlist_size = config.get("selection.shortlist_size", 10)
                st.session_state.news_items = items
                st.session_state.shortlist = scorer.get_shortlist(items, shortlist_size)

                status.update(
                    label=f"✅ Done — {len(items)} articles found, top {len(st.session_state.shortlist)} shortlisted.",
                    state="complete",
                )

    # Article list
    items = st.session_state.news_items
    if items:
        st.divider()

        f1, f2, f3 = st.columns([3, 2, 2])
        search_q = f1.text_input("Search title", placeholder="e.g. GPT, agent…")
        min_score = f2.slider("Min score", 0.0, 100.0, 0.0, step=5.0)
        sort_by = f3.selectbox("Sort by", ["Score ↓", "Score ↑", "Date (newest)", "Date (oldest)"])

        filtered = [
            i for i in items
            if (not search_q or search_q.lower() in i.title.lower())
            and i.score >= min_score
        ]
        sort_map = {
            "Score ↓":       (lambda x: x.score, True),
            "Score ↑":       (lambda x: x.score, False),
            "Date (newest)": (lambda x: x.discovered, True),
            "Date (oldest)": (lambda x: x.discovered, False),
        }
        key_fn, reverse = sort_map[sort_by]
        filtered.sort(key=key_fn, reverse=reverse)

        st.caption(f"Showing {len(filtered)} of {len(items)} articles")

        for item in filtered:
            with st.expander(f"**{item.title}** — Score {item.score:.1f}"):
                left, right = st.columns([5, 1])
                with left:
                    st.caption(f"📰 {item.source}  ·  📅 {item.discovered.strftime('%Y-%m-%d')}")
                    if item.summary:
                        st.write(item.summary[:300] + ("…" if len(item.summary) > 300 else ""))
                    if item.tags:
                        st.write("  ".join(f"`{t}`" for t in item.tags[:6]))
                with right:
                    st.link_button("Open →", item.url, use_container_width=True)
    else:
        st.info("Run discovery to populate articles.")


# ── Tab 3: Review ────────────────────────────────────────────────────────────

with tab_review:
    st.header("Select Articles for Deep Dive")

    shortlist = st.session_state.shortlist
    deep_dive_count = config.get("selection.deep_dive_count", 3)

    if not shortlist:
        st.info("Run **Discovery** first to get the shortlist.")
    else:
        # Count selections from checkbox session state
        selected_urls = {
            item.url
            for item in shortlist
            if st.session_state.get(f"select_{item.url}", False)
        }
        n_selected = len(selected_urls)

        header_left, header_right = st.columns([6, 2])
        header_left.caption(f"Top {len(shortlist)} articles — recommended: choose {deep_dive_count}")
        header_right.metric("Selected", f"{n_selected} / {deep_dive_count}")

        st.divider()

        for item in shortlist:
            with st.container(border=True):
                card_left, card_right = st.columns([6, 1])

                with card_left:
                    st.checkbox(
                        f"**{item.title}**",
                        key=f"select_{item.url}",
                    )
                    m1, m2, m3 = st.columns(3)
                    m1.caption(f"📰 {item.source}")
                    m2.caption(f"🎯 Score: {item.score:.1f}")
                    m3.caption(f"📅 {item.discovered.strftime('%Y-%m-%d')}")
                    if item.summary:
                        st.caption(item.summary[:220] + "…")
                    if item.tags:
                        st.write("  ".join(f"`{t}`" for t in item.tags[:5]))

                with card_right:
                    st.link_button("Open →", item.url, use_container_width=True)

        st.divider()

        confirm_disabled = n_selected == 0
        if st.button(
            f"🔬 Confirm Selection ({n_selected} articles)",
            type="primary",
            disabled=confirm_disabled,
        ):
            selected_items = [i for i in shortlist if st.session_state.get(f"select_{i.url}", False)]
            for item in selected_items:
                state.add_shortlisted_url(item.url)
            state.update_stage("review_complete")
            st.session_state.selected_for_deep_dive = selected_items
            st.success(f"✅ {len(selected_items)} articles confirmed. Head to the **Deep Dive** tab.")


# ── Tab 4: Deep Dive ─────────────────────────────────────────────────────────

with tab_deepdive:
    st.header("Deep Dive Research & Presentation")

    selected_for_dive = st.session_state.selected_for_deep_dive

    if not selected_for_dive:
        st.info("Confirm your selection in the **Review** tab first.")
    else:
        st.write(f"**{len(selected_for_dive)} articles queued for research:**")
        for item in selected_for_dive:
            st.write(f"- {item.title}")

        st.divider()

        action_left, action_right = st.columns(2)

        # Deep dive
        with action_left:
            if st.button("🔬 Run Deep Dive", type="primary", use_container_width=True):
                with st.status("Researching articles…", expanded=True) as status:
                    deep_dive_items = researcher.deep_dive_all(selected_for_dive)

                    st.write("Exporting research to Obsidian…")
                    for item in deep_dive_items:
                        state.add_deep_dive_url(item.url)
                        state.mark_url_processed(item.url, "deep-dive", item.week)
                        obsidian.export_deep_dive(item)
                    state.update_stage("deep_dive_complete")
                    st.session_state.deep_dive_items = deep_dive_items

                    status.update(label="✅ Deep dive complete!", state="complete")

        # Presentation
        with action_right:
            dive_done = bool(st.session_state.deep_dive_items)
            if st.button(
                "📊 Create Presentation",
                type="secondary",
                use_container_width=True,
                disabled=not dive_done,
            ):
                with st.spinner("Generating .pptx…"):
                    output_dir = Path("output") / state.get_current_week()
                    output_dir.mkdir(parents=True, exist_ok=True)
                    pptx = content_creator.create_presentation(
                        st.session_state.deep_dive_items,
                        state.get_current_week(),
                        output_dir,
                    )
                    for item in st.session_state.deep_dive_items:
                        obsidian.export_deep_dive(item)
                    state.update_stage("complete")
                    if pptx:
                        st.session_state.presentation_file = pptx
                        st.success(f"Presentation saved: `{pptx}`")
                    else:
                        st.error("Presentation generation failed — see terminal logs.")

        # Research results
        if st.session_state.deep_dive_items:
            st.divider()
            st.subheader("Research Results")
            for item in st.session_state.deep_dive_items:
                with st.expander(f"📄 {item.title}"):
                    if item.narrative:
                        st.markdown(item.narrative)
                    if item.research_sources:
                        st.markdown("**Sources**")
                        for src in item.research_sources:
                            st.write(f"- {src}")

        # Download presentation
        pptx_path = st.session_state.presentation_file
        if pptx_path and Path(pptx_path).exists():
            st.divider()
            with open(pptx_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Presentation (.pptx)",
                    data=f,
                    file_name=Path(pptx_path).name,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=False,
                )
