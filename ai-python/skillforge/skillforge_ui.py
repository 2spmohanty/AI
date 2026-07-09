"""
SkillForge — Test UI for Stages 1-3
⚠️ AI GENERATED — Test harness only. Not production UI.
Purpose: Validate interview subgraph, summarisation, and evaluation pipeline.
"""

import uuid
import hashlib
import ipywidgets as widgets
from IPython.display import display, clear_output
from langgraph.types import Command


# ──────────────────────────────────────────────
# UI FACTORY
# ──────────────────────────────────────────────

def build_skillforge_ui(parent_graph):
    """
    Accepts the compiled parent_graph and renders a self-contained test UI.
    Call this from any notebook cell: build_skillforge_ui(parent_graph)
    """

    # ── Session memory ──
    session = {"config": None, "running": False}
    log_lines = []

    # ── Layout constants ──
    FULL = widgets.Layout(width="100%")
    HALF = widgets.Layout(width="50%")

    # ── Header ──
    header = widgets.HTML("""
        <div style='background:#1e3a8a;padding:12px 16px;border-radius:6px;margin-bottom:10px'>
            <span style='color:white;font-size:16px;font-weight:bold'>🛠️ SkillForge — Stage 1-3 Test Harness</span>
            <span style='color:#93c5fd;font-size:11px;margin-left:10px'>⚠️ For Backend validation only</span>
        </div>
    """)

    # ── Form ──
    name_input    = widgets.Text(description="Name:", placeholder="e.g. Smruti", layout=HALF)
    skills_input  = widgets.Text(description="Skills:", placeholder="e.g. python, kafka, spark", layout=FULL)
    start_btn     = widgets.Button(description="Start Session", button_style="success",
                                   icon="play", layout=widgets.Layout(width="180px"))
    form_box      = widgets.VBox([name_input, skills_input, start_btn])

    # ── Chat log ──
    chat_log = widgets.HTML(
        value="<div style='color:#6b7280;font-style:italic'>Session not started.</div>",
        layout=widgets.Layout(
            width="100%", height="420px",
            border="1px solid #e5e7eb", padding="12px",
            overflow_y="auto", background_color="#f9fafb"
        )
    )

    # ── Input row ──
    reply_input = widgets.Text(placeholder="Type your answer here...", layout=widgets.Layout(width="80%"))
    send_btn    = widgets.Button(description="Send", button_style="primary",
                                 icon="paper-plane", layout=widgets.Layout(width="18%"))
    reply_input.disabled = True
    send_btn.disabled    = True
    input_row = widgets.HBox([reply_input, send_btn])

    # ── Status bar ──
    status_bar = widgets.HTML(value=_status("Idle", "gray"))

    # ── Full app ──
    app = widgets.VBox(
        [header, form_box,
         widgets.HTML("<hr style='margin:10px 0'>"),
         input_row, chat_log, status_bar],
        layout=widgets.Layout(display='flex', flex_flow='column', width='100%')
    )
    display(app)

    # ──────────────────────────────────────────
    # LOGGING HELPERS
    # ──────────────────────────────────────────

    def log(sender: str, text: str, color="#111827", badge_color="#1e3a8a"):
        line = (
            f"<div style='margin:6px 0;padding:8px 10px;border-left:3px solid {badge_color};"
            f"background:white;border-radius:0 4px 4px 0'>"
            f"<span style='color:{badge_color};font-weight:bold;font-size:11px'>{sender}</span>"
            f"<div style='color:{color};margin-top:3px;font-size:13px'>{text.replace(chr(10), '<br>')}</div>"
            f"</div>"
        )
        log_lines.append(line)
        visible = log_lines[-4:]  # Show last 4 entries (2 exchanges = question + answer)
        chat_log.value = (
                "<div style='line-height:1.6'>" + "".join(visible) + "</div>"
        )

    def set_status(msg, color="gray"):
        status_bar.value = _status(msg, color)

    # ──────────────────────────────────────────
    # START SESSION
    # ──────────────────────────────────────────

    def on_start(b):
        name   = name_input.value.strip()
        skills = skills_input.value.strip()

        if not name or not skills:
            set_status("⚠️  Please enter both name and skills.", "orange")
            return

        interests = [s.strip() for s in skills.split(",") if s.strip()]
        thread_id = "sf_" + hashlib.sha256(name.encode()).hexdigest()[:12]
        config    = {"configurable": {"thread_id": thread_id}}
        session["config"] = config

        # Lock form
        name_input.disabled  = True
        skills_input.disabled = True
        start_btn.disabled   = True

        log("⚙️ System", f"Thread: <code>{thread_id}</code>", color="#6b7280", badge_color="#6b7280")
        set_status("Starting session...", "blue")

        existing = parent_graph.get_state(config)

        if existing.values:
            prev_gaps = existing.values.get("detected_gaps", [])
            prev_known = existing.values.get("known_gaps", [])

            # Carry forward all known gaps into long-term memory
            carried_known_gaps = list(set(prev_known + prev_gaps))

            log("⚙️ System",
                f"Welcome back <b>{name}</b>! Carrying {len(carried_known_gaps)} known gaps forward.",
                color="#6b7280", badge_color="#6b7280")

            # Fresh state with carried memory
            fresh_state = {
                "learner_profile": {
                    "interests": interests,
                    "known_gaps": carried_known_gaps,
                    "learning_paths": []
                },
                "interview_summary": [],
                "known_gaps": carried_known_gaps,
                "detected_gaps": [],
                "gap_confidence_score": 1.0,
                "approval_status": "pending"
            }

            try:
                for _, _ in parent_graph.stream(fresh_state, config, subgraphs=True):
                    pass
                _show_last_question(config)
            except Exception as e:
                log("❌ Error", str(e), color="red", badge_color="red")
                return
        else:
            log("⚙️ System", f"New session for <b>{name}</b>. Interests: {', '.join(interests)}", color="#6b7280", badge_color="#6b7280")

            initial_state = {
                "learner_profile": {
                    "interests": interests,
                    "known_gaps": [],
                    "learning_paths": []
                },
                "interview_summary": [],
                "known_gaps":        [],
                "detected_gaps":     [],
                "gap_confidence_score": 1.0,
                "approval_status":   "pending"
            }

            try:
                for _, _ in parent_graph.stream(initial_state, config, subgraphs=True):
                    pass
                _show_last_question(config)
            except Exception as e:
                log("❌ Error", str(e), color="red", badge_color="red")
                set_status("Error during start.", "red")
                return

        reply_input.disabled = False
        send_btn.disabled    = False
        set_status("Session active — waiting for your answer.", "green")

    start_btn.on_click(on_start)

    # ──────────────────────────────────────────
    # SEND REPLY
    # ──────────────────────────────────────────

    def on_send(b):
        user_text = reply_input.value.strip()
        config    = session["config"]

        if not user_text or not config:
            return

        log("📝 You", user_text, color="#065f46", badge_color="#059669")
        reply_input.value    = ""
        reply_input.disabled = True
        send_btn.disabled    = True
        set_status("Processing...", "blue")

        try:
            for namespace, event in parent_graph.stream(
                Command(resume=user_text), config=config, subgraphs=True
            ):
                _process_event(namespace, event)

        except Exception as e:
            log("❌ Error", str(e), color="red", badge_color="red")
            set_status("Error during send.", "red")
            reply_input.disabled = False
            send_btn.disabled    = False
            return

        # Check terminal state
        snap       = parent_graph.get_state(config)
        next_nodes = getattr(snap, "next", None)
        values     = getattr(snap, "values", {}) or {}

        if not next_nodes:
            log("🏁 Complete", "Interview pipeline finished.", color="#1e3a8a", badge_color="#1e3a8a")
            _show_final_summary(values)
            set_status("Pipeline complete.", "green")
        else:
            reply_input.disabled = False
            send_btn.disabled    = False
            set_status("Waiting for your answer.", "green")

    send_btn.on_click(on_send)
    reply_input.on_submit(on_send)  # Enter key also sends

    # ──────────────────────────────────────────
    # EVENT PROCESSOR
    # ──────────────────────────────────────────

    def _process_event(namespace, event):
        for node_name, payload in event.items():
            if not isinstance(payload, dict):
                continue

            # New mentor question
            msgs = payload.get("interview_messages", [])
            if msgs:
                last = msgs[-1]
                if getattr(last, "type", "") in ["ai", "AIMessage"]:
                    log("🤖 Mentor", last.content, color="#1e3a8a", badge_color="#1e3a8a")

            # Summarisation complete
            if "interview_summary" in payload or "detected_gaps" in payload:
                gaps = payload.get("detected_gaps", [])
                if gaps:
                    log("📊 Gaps Detected",
                        "<br>".join(f"• {g}" for g in gaps),
                        color="#7c3aed", badge_color="#7c3aed")

            # Evaluation result
            if node_name == "evaluation_node":
                score  = payload.get("gap_confidence_score", 1.0)
                status = payload.get("approval_status", "pending")
                if score == 0.0:
                    log("⚖️ Judge",
                        "⚠️ Low confidence detected. Dynamic breakpoint triggered.",
                        color="#d97706", badge_color="#d97706")
                elif status == "approved":
                    log("⚖️ Judge",
                        f"✅ High confidence ({score:.2f}). Evaluation passed.",
                        color="#059669", badge_color="#059669")

    # ──────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────

    def _show_last_question(config):
        """Extract and display the last mentor question from state."""
        try:
            for entry in parent_graph.get_state_history(config):
                values = getattr(entry, "values", {}) or {}
                msgs   = values.get("interview_messages", [])
                if msgs:
                    last = msgs[-1]
                    if getattr(last, "type", "") in ["ai", "AIMessage"]:
                        log("🤖 Mentor", last.content, color="#1e3a8a", badge_color="#1e3a8a")
                        return
        except Exception:
            pass
        log("🤖 Mentor", "Welcome! Let's begin. What's your current experience level?",
            color="#1e3a8a", badge_color="#1e3a8a")

    def _show_final_summary(values):
        """Display final gaps and summary after pipeline completes."""
        gaps    = values.get("detected_gaps", [])
        summary = values.get("interview_summary", [])

        if gaps:
            log("🎯 Detected Gaps",
                "<br>".join(f"• {g}" for g in gaps),
                color="#7c3aed", badge_color="#7c3aed")
        if summary:
            log("📋 Interview Summary",
                "<br>".join(f"• {s}" for s in summary),
                color="#0369a1", badge_color="#0369a1")


def _status(msg, color):
    colors = {
        "gray":   "#6b7280",
        "green":  "#059669",
        "blue":   "#2563eb",
        "orange": "#d97706",
        "red":    "#dc2626"
    }
    hex_color = colors.get(color, "#6b7280")
    return (
        f"<div style='margin-top:6px;padding:4px 10px;border-radius:4px;"
        f"background:#f3f4f6;font-size:11px;color:{hex_color}'>"
        f"● {msg}</div>"
    )