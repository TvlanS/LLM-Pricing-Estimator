
import gradio as gr
import json
from utils.classes import TableEmbedding   

print("Using gradio version:", gr.__version__)

# ---------- Initialize your embedding ----------
embed = TableEmbedding()
embed.create_database()
json_path = embed.create_json()

# ---------- Custom CSS ----------
CUSTOM_CSS = """
body { background: #0b0f1a; font-family: Inter, sans-serif; color: #e6eef8; }
.gradio-container { background: transparent; }

#chat-window {
  background: #0b0f1a;
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 12px;
  max-height: 70vh;
  overflow-y: auto;
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}
.message-wrap { display: flex; margin: 10px 0; animation: fadeIn 0.3s ease; }
.message-bubble {
  max-width: 78%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 0.95rem;
  line-height: 1.5;
  box-shadow: 0 4px 14px rgba(0,0,0,0.3);
  white-space: pre-wrap;
}
.user-bubble {
  background: linear-gradient(180deg,#2563eb,#1d4ed8);
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 6px;
}
.assistant-bubble {
  background: #1a1e2d;
  color: #e6eef8;
  margin-right: auto;
  border-bottom-left-radius: 6px;
}
#controls {
  margin-top: 12px;
}
.gr-button {
  border-radius: 10px !important;
  font-weight: 600;
  padding: 6px 16px;
}
#raw-panel {
  margin-top: 16px;
  background: #111827;
  border-radius: 12px;
  padding: 10px;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.4);
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
"""

# ---------- Helper: Convert Markdown tables to HTML ----------
def markdown_to_html_block(text):
    """Render a single block: table OR text"""
    if "|" in text and "---" in text:  # crude check for markdown table
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        headers = [h.strip() for h in lines[0].split("|")[1:-1]]
        html = "<table style='border-collapse: collapse; width: 100%; margin-top:6px;'>"
        html += "<tr>"
        for h in headers:
            html += f"<th style='border:1px solid #444;padding:6px;text-align:left;background:#1f2937;'>{h}</th>"
        html += "</tr>"
        for line in lines[2:]:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            html += "<tr>"
            for c in cells:
                html += f"<td style='border:1px solid #444;padding:6px;'>{c}</td>"
            html += "</tr>"
        html += "</table>"
        return html
    else:
        return f"<p style='margin:6px 0;'>{text.replace(chr(10), '<br>')}</p>"

# ---------- Generate response ----------
def generate_reply(prompt_text, n_results=10):
    try:
        result , embedding = embed.LLM_output(prompt_text,n_results)
        # If ChatCompletion-like → extract message content
        if hasattr(result, "choices") and result.choices:
            reply = result.choices[0].message.content
            raw_output = embedding
        else:
            reply = str(result)
            raw_output = str(result)
    except Exception as e:
        reply = f"[Error] {e}"
        raw_output = f"[Error] {e}"
    return reply, raw_output

# ---------- Chat handling ----------
def respond(message, history):
    history = history or []
    reply, raw = generate_reply(message, 10)
    embed.history(message, reply, json_path)
    history.append((message, reply))
    return history, "", render_chat(history), raw

def get_initial():
    return [("Hello!","Enter the desired service , ensure each work is separated by a comma (,)")]

# ---------- Chat rendering ----------
def render_chat(history):
    if not history:
        return ""
    html = ""
    for user_msg, bot_msg in history:
        if user_msg:
            html += f"<div class='message-wrap'><div class='message-bubble user-bubble'>{user_msg}</div></div>"
        if bot_msg:
            # split message into sections (tables, paragraphs, notes)
            parts = [p.strip() for p in bot_msg.split("\n\n") if p.strip()]
            bot_html = ""
            for part in parts:
                bot_html += markdown_to_html_block(part)
            html += f"<div class='message-wrap'><div class='message-bubble assistant-bubble'>{bot_html}</div></div>"
    return html

# ---------- Gradio app ----------
def build_demo():
    with gr.Blocks(css=CUSTOM_CSS, title="LM Studio Style Chat (Production)") as demo:
        state = gr.State(get_initial())

        with gr.Column():
            chat_display = gr.HTML(value=render_chat(get_initial()), elem_id="chat-window")
            message_box = gr.Textbox(
                placeholder="Type a message and hit enter...",
                show_label=False,
                lines=2,
                elem_id="message_box"
            )

            with gr.Row(elem_id="controls"):
                send_btn = gr.Button("Send", elem_classes="gr-button")
                clear_btn = gr.Button("Clear", elem_classes="gr-button")

            with gr.Accordion("🔎 Embedding Raw Output", open=False, elem_id="raw-panel"):
                raw_output_box = gr.Textbox(
                    label=None,
                    interactive=False,
                    lines=14
                )

        # Events
        message_box.submit(respond, [message_box, state], [state, message_box, chat_display, raw_output_box])
        send_btn.click(respond, [message_box, state], [state, message_box, chat_display, raw_output_box])
        clear_btn.click(lambda: ([], "", "", ""), outputs=[state, message_box, chat_display, raw_output_box])

    return demo

if __name__ == "__main__":
    demo = build_demo()
    demo.launch(share=False)
