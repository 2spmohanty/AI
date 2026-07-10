"""
SkillForge — Test UI for Stages 1-3
⚠️ AI GENERATED — Test harness only. Not production UI.
Purpose: Validate interview subgraph, summarisation, evaluation, and gap confirmation pipeline.
"""

import uuid
import hashlib
import ipywidgets as widgets
from IPython.display import display, clear_output
from langgraph.types import Command
from langgraph.errors import GraphInterrupt


# ──────────────────────────────────────────────────────────────────────────────
# INTERRUPT MESSAGE EXTRACTOR
# ──────────────────────────────────────────────────────────────────────────────

def _extract_interrupt_message(interrupt_exception: GraphInterrupt) -> str:
    try:
        # Try direct string
        raw = interrupt_exception.args[0]

        # LangGraph wraps in tuple of Interrupt namedtuples
        if isinstance(raw, (list, tuple)):
            for item in raw:
                # item.value contains the actual message
                if hasattr(item, 'value'):
                    return str(item.value)
                return str(item)

        # Direct string case
        if isinstance(raw, str):
            return raw

        # Pydantic or dataclass
        if hasattr(raw, 'value'):
            return str(raw.value)

        return str(raw)

    except Exception as e:
        print(f"DEBUG extract failed: {e} args={interrupt_exception.args}")
        return "Please confirm how you would like to proceed."


# ──────────────────────────────────────────────────────────────────────────────
# STATUS HELPER
# ──────────────────────────────────────────────────────────────────────────────

def _status(msg: str, color: str) -> str:
    colors = {
        "gray":   "#6b7280",
        "green":  "#059669",
        "blue":   "#2563eb",
        "orange": "#d97706",
        "red":    "#dc2626"
    }
    hex_color = colors.get(color, "#6b7280")
    return (
        f"<div style='padding:4px 10px;border-radius:4px;"
        f"background:#f3f4f6;font-size:11px;color:{hex_color}'>"
        f"● {msg}</div>"
    )


# ──────────────────────────────────────────────────────────────────────────────
# MAIN UI FACTORY
# ──────────────────────────────────────────────────────────────────────────────

def build_skillforge_ui(parent_graph):
    """
    Accepts the compiled parent_graph and renders a self-contained test UI.
    Usage: build_skillforge_ui(parent_graph)
    """

    # ── Session memory ──
    session = {"config": None}
    log_lines = []

    # ── Layout helpers ──
    FULL = widgets.Layout(width="100%")
    HALF = widgets.Layout(width="50%")

    # ── Header ──
    header = widgets.HTML("""
        <div style='background:#1e3a8a;padding:12px 16px;border-radius:6px;margin-bottom:8px'>
            <span style='color:white;font-size:16px;font-weight:bold'>🛠️ SkillForge</span>
            <span style='color:#93c5fd;font-size:11px;margin-left:10px'>
                ⚠️ Backend validation only
            </span>
        </div>
    """)

    # ── Form ──
    name_input   = widgets.Text(
        description="Name:",
        placeholder="e.g. Smruti",
        layout=HALF
    )
    skills_input = widgets.Text(
        description="Skills:",
        placeholder="e.g. python, kafka, spark — comma separated",
        layout=FULL
    )
    start_btn = widgets.Button(
        description="Start Session",
        button_style="success",
        icon="play",
        layout=widgets.Layout(width="180px", margin="6px 0 0 0")
    )
    debug_btn = widgets.Button(
        description="Debug State",
        button_style="warning",
        icon="bug",
        layout=widgets.Layout(width="150px", margin="6px 0 0 6px")
    )

    form_box = widgets.VBox([name_input, skills_input,
                             widgets.HBox([start_btn, debug_btn])])

    # ── Input row ──
    reply_input = widgets.Textarea(
        placeholder=(
            "Type your answer here...\n"
            "Commands: DONE = finish interview | YES = proceed | MORE = more questions"
        ),
        layout=widgets.Layout(width="80%", height="80px")
    )
    send_btn = widgets.Button(
        description="Send",
        button_style="primary",
        icon="paper-plane",
        layout=widgets.Layout(width="18%", height="80px")
    )
    reply_input.disabled = True
    send_btn.disabled    = True
    input_row = widgets.HBox([reply_input, send_btn])

    # ── Status bar ──
    status_bar = widgets.HTML(
        value=_status("Idle — start a session above.", "gray"),
        layout=widgets.Layout(width="100%", height="24px", margin="2px 0 2px 0")
    )

    # ── Chat log ──
    chat_log = widgets.HTML(
        value="<div style='color:#6b7280;font-style:italic;padding:8px'>Session not started.</div>",
        layout=widgets.Layout(
            width="100%",
            min_height="300px",
            border="1px solid #e5e7eb",
            padding="8px",
            overflow_y="scroll",
            background_color="#f9fafb"
        )
    )

    # ── App layout ──
    # Order: header → form → divider → input → status → chat log
    app = widgets.VBox(
        [
            header,
            form_box,
            widgets.HTML("<hr style='margin:8px 0;border-color:#e5e7eb'>"),
            input_row,
            status_bar,
            chat_log
        ],
        layout=widgets.Layout(width="100%")
    )
    display(app)

    # ──────────────────────────────────────────────────────────────────────────
    # LOGGING
    # ──────────────────────────────────────────────────────────────────────────

    def log(sender: str, text: str, color: str = "#111827", badge_color: str = "#1e3a8a"):
        line = (
            f"<div style='margin:5px 0;padding:8px 10px;"
            f"border-left:3px solid {badge_color};"
            f"background:white;border-radius:0 4px 4px 0'>"
            f"<span style='color:{badge_color};font-weight:bold;font-size:11px'>{sender}</span>"
            f"<div style='color:{color};margin-top:3px;font-size:13px'>"
            f"{text.replace(chr(10), '<br>')}"
            f"</div></div>"
        )
        log_lines.append(line)
        # Show last 6 entries to avoid overflow
        visible = log_lines[-6:]
        chat_log.value = (
            "<div style='line-height:1.6'>"
            + "".join(visible)
            + "</div>"
        )

    def set_status(msg: str, color: str = "gray"):
        status_bar.value = _status(msg, color)

    def enable_input(status_msg: str, status_color: str = "green"):
        reply_input.disabled = False
        send_btn.disabled    = False
        set_status(status_msg, status_color)

    def disable_input(status_msg: str, status_color: str = "blue"):
        reply_input.disabled = True
        send_btn.disabled    = True
        set_status(status_msg, status_color)

    # ──────────────────────────────────────────────────────────────────────────
    # EVENT PROCESSOR
    # Node-name guarded — each node owns its own display output
    # No namespace depth guard — preserves subgraph messages
    # ──────────────────────────────────────────────────────────────────────────

    def _process_event(namespace, event):
        for node_name, payload in event.items():

            # Skip non-dict payloads and internal root re-emissions
            if not isinstance(payload, dict):
                continue
            if node_name == "__root__":
                continue

            # ── System status per node ──
            system_labels = {
                "parent_init":           ("⚙️ System", "Initialising session...",       "#6b7280"),
                "summarisation_node":    ("📝 System", "Summarising your responses...", "#6b7280"),
                "evaluation_node":       ("⚖️ System", "Evaluating your responses...",  "#6b7280"),
                "gap_confirmation_node": ("🌱 System", "Preparing your gap report...",  "#6b7280"),
            }
            if node_name in system_labels:
                label, msg, color = system_labels[node_name]
                log(label, msg, color=color, badge_color=color)

            # ── Mentor question — from subgraph question generator only ──
            if node_name == "question_generator":
                msgs = payload.get("interview_messages", [])
                if msgs:
                    last = msgs[-1]
                    if getattr(last, "type", "") in ["ai", "AIMessage"]:
                        log("🤖 Mentor", last.content,
                            color="#1e3a8a", badge_color="#1e3a8a")

            # ── Gaps detected — from summarisation only ──
            if node_name == "summarisation_node":
                gaps = payload.get("detected_gaps", [])
                if gaps:
                    log("📊 Gaps Detected",
                        "<br>".join(f"• {g}" for g in gaps),
                        color="#7c3aed", badge_color="#7c3aed")

            # ── Evaluation result — from evaluation_node only ──
            if node_name == "evaluation_node":
                score  = payload.get("gap_confidence_score", 1.0)
                status = payload.get("approval_status", "pending")
                if score == 0.0:
                    log("⚖️ Judge",
                        "⚠️ Low confidence detected — requesting more information.",
                        color="#d97706", badge_color="#d97706")
                elif status == "approved":
                    log("⚖️ Judge",
                        f"✅ Confidence {score:.2f} — We have identified your growth areas.<br>"
                        f"Type <b>YES</b> to generate your personalised learning plan<br>"
                        f"Type <b>MORE</b> to answer additional questions and refine the assessment.",
                        color="#059669", badge_color="#059669")

    # ──────────────────────────────────────────────────────────────────────────
    # GRAPH STATE INSPECTOR
    # ──────────────────────────────────────────────────────────────────────────

    def _check_next_state(config):
        snap = parent_graph.get_state(config)
        next_nodes = getattr(snap, "next", None) or []
        values = getattr(snap, "values", {}) or {}

        if not next_nodes:
            log("🏁 Complete", "Session complete!",
                color="#1e3a8a", badge_color="#1e3a8a")
            _show_final_summary(values)
            disable_input("Session complete.", "gray")

        elif any("interview" in str(n) for n in next_nodes):
            # Don't call _show_last_question here —
            # _process_event already displayed the new question from the stream
            enable_input(
                "Answer the question above — type DONE to finish interview.",
                "green"
            )
        else:
            enable_input("Waiting for your response.", "green")

    # ──────────────────────────────────────────────────────────────────────────
    # INTERRUPT HANDLER — single source of truth for all GraphInterrupt events
    # ──────────────────────────────────────────────────────────────────────────

    def _handle_interrupt(interrupt_exception: GraphInterrupt):
        print(f"DEBUG raw args: {interrupt_exception.args}")
        msg = _extract_interrupt_message(interrupt_exception)
        print(f"DEBUG extracted: {repr(msg)}")
        log("🌱 SkillForge", msg.replace("\n", "<br>"),
            color="#1e3a8a", badge_color="#065f46")
        enable_input(
            "Type YES to generate your plan  |  MORE for additional questions.",
            "orange"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────────

    def _show_last_question(config):
        """Extract and display the last mentor question from state history."""
        try:
            for entry in parent_graph.get_state_history(config):
                values = getattr(entry, "values", {}) or {}
                msgs   = values.get("interview_messages", [])
                if msgs:
                    last = msgs[-1]
                    if getattr(last, "type", "") in ["ai", "AIMessage"]:
                        log("🤖 Mentor", last.content,
                            color="#1e3a8a", badge_color="#1e3a8a")
                        return
        except Exception:
            pass
        log("🤖 Mentor",
            "Welcome! Let's begin. Tell me about your background with this skill.",
            color="#1e3a8a", badge_color="#1e3a8a")

    def _show_final_summary(values):
        """Display final gaps and summary after pipeline completes."""
        gaps    = values.get("detected_gaps", [])
        summary = values.get("interview_summary", [])
        if gaps:
            log("🎯 Your Growth Areas",
                "<br>".join(f"• {g}" for g in gaps),
                color="#7c3aed", badge_color="#7c3aed")
        if summary:
            log("📋 Session Summary",
                "<br>".join(f"• {s}" for s in summary),
                color="#0369a1", badge_color="#0369a1")

    def _stream_graph(input_or_command, config):
        try:
            for namespace, event in parent_graph.stream(
                    input_or_command, config, subgraphs=True
            ):
                _process_event(namespace, event)
            print("DEBUG: stream completed normally")
            return True

        except GraphInterrupt as i:
            print(f"DEBUG: GraphInterrupt caught: {type(i)} {i.args}")
            _handle_interrupt(i)
            return False

        except Exception as e:
            print(f"DEBUG: Exception caught: {type(e)} {e}")
            log("❌ Error", str(e), color="red", badge_color="red")
            enable_input("Error occurred — try again.", "red")
            return False
    # ──────────────────────────────────────────────────────────────────────────
    # ACTION: START SESSION
    # ──────────────────────────────────────────────────────────────────────────

    def on_start(b):
        name   = name_input.value.strip()
        skills = skills_input.value.strip()

        if not name or not skills:
            set_status("⚠️ Please enter both name and skills.", "orange")
            return

        interests = [s.strip() for s in skills.split(",") if s.strip()]
        thread_id = "sf_" + hashlib.sha256(name.encode()).hexdigest()[:12]
        config    = {"configurable": {"thread_id": thread_id}}
        session["config"] = config

        # Lock form
        name_input.disabled   = True
        skills_input.disabled = True
        start_btn.disabled    = True

        log("⚙️ System",
            f"Thread: <code>{thread_id}</code>",
            color="#6b7280", badge_color="#6b7280")
        disable_input("Starting session...", "blue")

        existing = parent_graph.get_state(config)

        if existing.values:
            print(f"DEBUG existing gap_confirmation: {existing.values.get('gap_confirmation')}")
            # ── Returning learner — carry gaps forward, fresh interview ──
            prev_gaps  = existing.values.get("detected_gaps", [])
            prev_known = existing.values.get("known_gaps", [])
            carried    = list(set(prev_known + prev_gaps))

            log("⚙️ System",
                f"Welcome back <b>{name}</b>! "
                f"Carrying {len(carried)} known gaps into this session.",
                color="#6b7280", badge_color="#6b7280")

            fresh_state = {
                "learner_profile": {
                    "interests":      interests,
                    "known_gaps":     carried,
                    "learning_paths": []
                },
                "interview_summary":    [],
                "known_gaps":           carried,
                "detected_gaps":        [],
                "gap_confidence_score": 1.0,
                "approval_status":      "pending",
                "gap_confirmation":     "pending",
                "evaluation_rationale": ""
            }
            completed = _stream_graph(fresh_state, config)
            if completed:
                _show_last_question(config)  # Returning learner — show resumed question
                enable_input("Answer the question above — type DONE to finish interview.", "green")

        else:
            # ── New learner ──
            log("⚙️ System",
                f"New session for <b>{name}</b>. "
                f"Interests: {', '.join(interests)}",
                color="#6b7280", badge_color="#6b7280")

            fresh_state = {
                "learner_profile": {
                    "interests":      interests,
                    "known_gaps":     [],
                    "learning_paths": []
                },
                "interview_summary":    [],
                "known_gaps":           [],
                "detected_gaps":        [],
                "gap_confidence_score": 1.0,
                "approval_status":      "pending",
                "gap_confirmation":     "pending",
                "evaluation_rationale": ""
            }

            completed = _stream_graph(fresh_state, config)
            if completed:
                enable_input("Answer the question above — type DONE to finish interview.", "green")

    # If not completed, _handle_interrupt already updated UI

    start_btn.on_click(on_start)



    # ──────────────────────────────────────────────────────────────────────────
    # ACTION: SEND REPLY
    # ──────────────────────────────────────────────────────────────────────────

    def on_send(b):
        user_text = reply_input.value.strip()
        config    = session["config"]

        if not user_text or not config:
            return

        log("📝 You", user_text, color="#065f46", badge_color="#059669")
        reply_input.value = ""
        disable_input("Processing...", "blue")

        completed = _stream_graph(Command(resume=user_text), config)

        if completed:
            _check_next_state(config)
        # If not completed, _handle_interrupt already updated UI

    send_btn.on_click(on_send)

    def on_debug(b):
        config = session["config"]
        if not config:
            log("⚙️ Debug", "No active session.", color="gray", badge_color="gray")
            return

        snap = parent_graph.get_state(config)
        values = getattr(snap, "values", {}) or {}

        log("⚙️ Debug",
            f"<b>next:</b> {snap.next}<br>"
            f"<b>approval_status:</b> {values.get('approval_status')}<br>"
            f"<b>gap_confirmation:</b> {values.get('gap_confirmation')}<br>"
            f"<b>confidence:</b> {values.get('gap_confidence_score')}<br>"
            f"<b>detected_gaps:</b> {values.get('detected_gaps')}<br>"
            f"<b>interview_summary:</b> {values.get('interview_summary')}",
            color="#374151", badge_color="#d97706")

    debug_btn.on_click(on_debug)