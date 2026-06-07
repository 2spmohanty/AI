"""
PopChoice — Streamlit Frontend
"""

import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

POP_CHOICE_UI_URL = os.getenv("POP_CHOICE_UI_URL")

st.set_page_config(
    page_title="PopChoice",
    page_icon="🍿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── STYLES ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --card: #1a1a24;
    --border: #2a2a3d;
    --gold: #d4a843;
    --gold-light: #f0c96e;
    --text: #f0ede8;
    --muted: #8a8699;
}

/* ── Global ── */
.stApp { background: var(--bg) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 700px !important; }
h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--text) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    padding: 12px 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(212,168,67,0.15) !important;
}
.stTextInput label, .stTextArea label, .stNumberInput label, .stSlider label {
    color: var(--muted) !important; font-size: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    text-transform: uppercase !important; letter-spacing: 0.8px !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 14px !important;
    padding: 10px 20px !important; width: 100% !important;
    transition: all 0.2s !important; height: 44px !important; line-height: 1 !important;
    background: var(--gold) !important; color: #0a0a0f !important; border: none !important;
}
.stButton > button:hover { background: var(--gold-light) !important; transform: translateY(-1px) !important; }
.stButton > button[kind="secondary"] {
    background: transparent !important; color: var(--muted) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--gold) !important; color: var(--gold) !important; background: transparent !important;
}
[data-testid="stHorizontalBlock"] { gap: 10px !important; align-items: flex-end !important; }

/* ── Slider ── */
.stSlider > div > div > div > div { background: var(--gold) !important; }

/* ── Movie backdrop — FIXED: no clip, full image ── */
.movie-backdrop {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 24px;
    height: 500px;
    display: flex;
    align-items: flex-end;
}
.movie-backdrop-img {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-size: cover;
    background-position: center top;
    background-repeat: no-repeat;
    filter: brightness(0.35);
}
.movie-info {
    position: relative;
    z-index: 1;
    padding: 32px;
    width: 100%;
    background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.3) 60%, transparent 100%);
}
.movie-title {
    font-family: 'Playfair Display', serif;
    font-size: 34px; font-weight: 900; color: #fff;
    line-height: 1.1; margin-bottom: 8px;
}
.movie-meta { font-size: 12px; color: var(--gold); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px; }
.movie-desc { font-size: 13px; color: rgba(255,255,255,0.8); line-height: 1.7; margin-bottom: 14px; }
.match-pill {
    display: inline-block;
    background: rgba(212,168,67,0.15); border: 1px solid rgba(212,168,67,0.3);
    color: var(--gold-light); padding: 6px 14px; border-radius: 20px;
    font-size: 12px; font-style: italic;
}

/* ── Progress dots ── */
.progress-dots { display: flex; justify-content: center; gap: 8px; margin: 20px 0; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--border); display: inline-block; transition: background 0.3s; }
.dot.active { background: var(--gold); }
.dot.done { background: var(--muted); }

/* ── Gold divider ── */
.gold-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--gold), transparent); margin: 24px 0; opacity: 0.4; }

/* ── Person badge ── */
.person-badge {
    display: inline-block; background: rgba(212,168,67,0.1);
    border: 1px solid rgba(212,168,67,0.25); color: var(--gold);
    padding: 4px 12px; border-radius: 20px; font-size: 11px;
    font-family: 'DM Sans', sans-serif; text-transform: uppercase;
    letter-spacing: 0.8px; margin-bottom: 12px;
}

/* ── Movie counter ── */
.movie-counter { text-align: center; font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; }

/* ── Loading screen ── */
.loading-wrap { text-align: center; padding: 60px 20px; }
.loading-icon { font-size: 56px; margin-bottom: 16px; animation: spin 3s linear infinite; display: inline-block; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-title { font-family: 'Playfair Display', serif; font-size: 26px; font-weight: 700; margin-bottom: 10px; color: var(--text); }
.loading-msg { font-size: 14px; color: var(--muted); margin-bottom: 32px; min-height: 22px; transition: opacity 0.4s; }
.loading-bar-wrap { width: 60%; margin: 0 auto; height: 3px; background: var(--border); border-radius: 2px; overflow: hidden; }
.loading-bar { height: 100%; background: linear-gradient(90deg, var(--gold), var(--gold-light)); border-radius: 2px; transition: width 1.2s ease; }

/* ── Alert ── */
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)



def init_state():
    defaults = {
        "page": "landing",
        "num_people": 2,
        "duration": 120,
        "current_person": 0,
        "people_data": [],
        "movies": [],
        "current_movie": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


def go(page):
    st.session_state.page = page
    st.rerun()


def progress_dots(current, total):
    dots = ""
    for i in range(total):
        if i < current:   dots += '<span class="dot done"></span>'
        elif i == current: dots += '<span class="dot active"></span>'
        else:              dots += '<span class="dot"></span>'
    st.markdown(f'<div class="progress-dots">{dots}</div>', unsafe_allow_html=True)


def fetch_recommendations(people_data, duration):
    payload = {"duration_minutes": duration, "people": people_data}
    try:
        resp = requests.post(f"{POP_CHOICE_UI_URL}/recommend", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["suggestions"]
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def fetch_sample():
    try:
        resp = requests.get(f"{POP_CHOICE_UI_URL}/movies/sample", timeout=10)
        resp.raise_for_status()
        return resp.json()["suggestions"]
    except Exception:
        return [
            {"title":"Interstellar","description":"A team of explorers travel through a wormhole in space.","image_url":"https://image.tmdb.org/t/p/original/gEU2QniE6E77NI6lCU6MxlNBvIe.jpg","year":"2014","genre":"Sci-Fi / Drama","duration":"169 min","match_reason":"Epic and thought-provoking."},
            {"title":"The Grand Budapest Hotel","description":"The adventures of Gustave H, a legendary concierge.","image_url":"https://image.tmdb.org/t/p/original/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg","year":"2014","genre":"Comedy / Drama","duration":"99 min","match_reason":"Fun and full of substance."},
            {"title":"Parasite","description":"Greed and class discrimination threaten two families.","image_url":"https://image.tmdb.org/t/p/original/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg","year":"2019","genre":"Thriller / Drama","duration":"132 min","match_reason":"A modern classic."},
        ]


# ── PAGE: LANDING ──────────────────────────────────────────────────────────────

def page_landing():
    st.markdown("""
    <div style="text-align:center; padding: 36px 0 16px;">
        <div style="font-size:52px; margin-bottom:10px;">🍿</div>
        <h1 style="font-size:46px; font-weight:900; margin-bottom:6px; letter-spacing:-1px;">PopChoice</h1>
        <p style="color:#8a8699; font-size:15px; margin-bottom:0;">
            Find the perfect movie for your group.<br/>Everyone's taste, one great pick.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    num_people = st.number_input("How many people are joining?", min_value=1, max_value=5, value=st.session_state.num_people, step=1)
    duration = st.slider("How long is your movie night?", min_value=60, max_value=240, value=st.session_state.duration, step=15, format="%d min")
    st.markdown(f'<p style="color:#8a8699;font-size:12px;margin-top:-8px;margin-bottom:24px;">Up to {duration} minutes — we\'ll suggest movies that fit.</p>', unsafe_allow_html=True)
    if st.button("Let's find your movie →"):
        st.session_state.num_people = int(num_people)
        st.session_state.duration = duration
        st.session_state.current_person = 0
        st.session_state.people_data = []
        go("taste")


# ── PAGE: TASTE ────────────────────────────────────────────────────────────────

def page_taste():
    idx   = st.session_state.current_person
    total = st.session_state.num_people

    progress_dots(idx, total)
    st.markdown(f'<div class="person-badge">Person {idx + 1} of {total}</div>', unsafe_allow_html=True)
    st.markdown("## Tell us your taste")
    st.markdown('<p style="color:#8a8699;font-size:14px;margin-top:-12px;margin-bottom:20px;">Answer honestly — the more specific, the better the recommendation.</p>', unsafe_allow_html=True)

    name      = st.text_input("Your name", placeholder="e.g. Smruti", key=f"name_{idx}")
    favourite = st.text_area("What's your favourite movie and why?", placeholder="e.g. The Dark Knight — the layers, the Joker...", key=f"fav_{idx}", height=100)
    mood      = st.text_input("New or a classic?", placeholder="e.g. Something from the last 5 years...", key=f"mood_{idx}")
    vibe      = st.text_input("Fun or something serious?", placeholder="e.g. Fun and light, I need to laugh...", key=f"vibe_{idx}")

    st.markdown("<br/>", unsafe_allow_html=True)
    is_last   = idx == total - 1
    btn_label = "Find our movies 🍿" if is_last else "Next person →"

    col_back, col_next = st.columns([1, 2])
    with col_back:
        if st.button("← Back", key="back_btn", type="secondary"):
            go("landing") if idx == 0 else (setattr(st.session_state, 'current_person', idx - 1) or st.rerun())
    with col_next:
        if st.button(btn_label, key="next_btn"):
            if not all([name.strip(), favourite.strip(), mood.strip(), vibe.strip()]):
                st.error("Please fill in all fields before continuing.")
                return
            entry = {"name": name.strip(), "favourite_movie": favourite.strip(), "mood": mood.strip(), "vibe": vibe.strip()}
            if idx < len(st.session_state.people_data):
                st.session_state.people_data[idx] = entry
            else:
                st.session_state.people_data.append(entry)
            if is_last:
                go("loading")
            else:
                st.session_state.current_person += 1
                st.rerun()


# ── PAGE: LOADING ──────────────────────────────────────────────────────────────

LOADING_MESSAGES = [
    "Decoding everyone's taste...",
    "Sifting through our movie vault...",
    "Matching vibes to the perfect picks...",
    "Consulting the cinematic oracle...",
    "Running taste compatibility tests...",
    "Bribing the critics for insider picks...",
    "Cross-referencing popcorn preferences...",
    "Almost there — placing the final reel...",
]

def page_loading():
    # Clear the page completely — replace everything with loading screen
    placeholder = st.empty()

    # Animate through messages while fetching
    messages     = LOADING_MESSAGES
    total_msgs   = len(messages)
    msg_idx      = 0
    fetch_done   = False
    movies       = None

    # Kick off the API call using a thread so we can animate while waiting
    import threading
    result_holder = {"movies": None, "done": False}

    people_data = st.session_state.people_data
    duration = st.session_state.duration

    def do_fetch():
        result_holder["movies"] = fetch_recommendations(
            people_data,
            duration
        )
        result_holder["done"] = True

    thread = threading.Thread(target=do_fetch)
    thread.start()

    start = time.time()
    max_wait = 120  # seconds

    while not result_holder["done"] and (time.time() - start) < max_wait:
        elapsed  = time.time() - start
        progress = min(int((elapsed / max_wait) * 90), 90)  # cap at 90% until done
        msg_idx  = int(elapsed / 6) % total_msgs

        with placeholder.container():
            st.markdown(f"""
            <div class="loading-wrap">
                <div class="loading-icon">✨</div>
                <div class="loading-title">Finding your perfect films...</div>
                <div class="loading-msg">{messages[msg_idx]}</div>
                <div class="loading-bar-wrap">
                    <div class="loading-bar" style="width:{progress}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        time.sleep(0.8)

    thread.join(timeout=5)

    # Final flash to 100%
    with placeholder.container():
        st.markdown(f"""
        <div class="loading-wrap">
            <div class="loading-icon">🎬</div>
            <div class="loading-title">Got your picks!</div>
            <div class="loading-msg">Preparing your movie night...</div>
            <div class="loading-bar-wrap">
                <div class="loading-bar" style="width:100%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    time.sleep(0.6)

    placeholder.empty()

    movies = result_holder["movies"]
    st.session_state.movies       = movies if movies else fetch_sample()
    st.session_state.current_movie = 0
    go("results")


# ── PAGE: RESULTS ──────────────────────────────────────────────────────────────

def page_results():
    movies = st.session_state.movies
    idx    = st.session_state.current_movie
    total  = len(movies)

    if not movies:
        st.error("No recommendations found. Please try again.")
        if st.button("Start over"):
            go("landing")
        return

    movie = movies[idx]

    st.markdown(f'<div class="movie-counter">Suggestion {idx + 1} of {total}</div>', unsafe_allow_html=True)

    image_url    = movie.get("image_url") or ""
    title        = movie.get("title", "Unknown")
    description  = movie.get("description", "")
    year         = movie.get("year", "")
    genre        = movie.get("genre", "")
    duration     = movie.get("duration", "")
    match_reason = movie.get("match_reason", "")
    meta_str     = " · ".join([p for p in [year, genre, duration] if p])

    if image_url:
        # Use background-image instead of <img> — avoids Streamlit clipping
        st.markdown(f"""
        <div class="movie-backdrop">
            <div class="movie-backdrop-img" style="background-image: url('{image_url}');"></div>
            <div class="movie-info">
                <div class="movie-title">{title}</div>
                <div class="movie-meta">{meta_str}</div>
                <div class="movie-desc">{description}</div>
                <div class="match-pill">✦ {match_reason}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:36px;margin-bottom:24px;">
            <div class="movie-title" style="color:var(--text)">{title}</div>
            <div class="movie-meta">{meta_str}</div>
            <div class="movie-desc">{description}</div>
            <div class="match-pill">✦ {match_reason}</div>
        </div>
        """, unsafe_allow_html=True)

    has_prev = idx > 0
    has_next = idx < total - 1

    col_home, col_prev, col_next = st.columns(3)

    with col_home:
        if st.button("🏠 Start over", key="startover_btn", type="secondary"):
            for key in ["page","num_people","duration","current_person","people_data","movies","current_movie"]:
                if key in st.session_state: del st.session_state[key]
            init_state()
            go("landing")

    with col_prev:
        if has_prev:
            if st.button("← Previous", key="prev_btn", type="secondary"):
                st.session_state.current_movie -= 1
                st.rerun()

    with col_next:
        if has_next:
            if st.button("Next →", key="next_btn"):
                st.session_state.current_movie += 1
                st.rerun()
        else:
            st.markdown('<p style="text-align:center;color:#8a8699;font-size:12px;padding-top:14px;">Last suggestion 🍿</p>', unsafe_allow_html=True)

    progress_dots(idx, total)


# ── ROUTER ─────────────────────────────────────────────────────────────────────

page = st.session_state.page

if page == "landing":
    page_landing()
elif page == "taste":
    page_taste()
elif page == "loading":
    page_loading()
elif page == "results":
    page_results()
else:
    go("landing")