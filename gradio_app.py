import gradio as gr
import requests
import time
import json
from typing import List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

# Firebase setup for listening to updates
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth

# Initialize Firebase
if not firebase_admin._apps:
    firebase_cert_path = os.getenv("FIREBASE_ADMIN_CERT_PATH", "firebase_adminsdk.json")
    cred = credentials.Certificate(firebase_cert_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Global state
current_user_id = "demo_user"  # For hackathon, using a single demo user
BASE_URL = "http://127.0.0.1:8000"
FIREBASE_ID_TOKEN = os.getenv("FIREBASE_ID_TOKEN")


def _build_headers(include_json: bool = False) -> dict:
    """Compose request headers with optional Firebase auth."""
    headers = {}
    if FIREBASE_ID_TOKEN:
        headers["Authorization"] = f"Bearer {FIREBASE_ID_TOKEN}"
    if include_json:
        headers["Content-Type"] = "application/json"
    return headers

def get_session_data():
    """Fetch current session data from Firestore"""
    doc = db.collection('users').document(current_user_id).get()
    if doc.exists:
        return doc.to_dict()
    return None

def send_message(message: str, history: List[Tuple[str, str]]):
    """Send message to chat API"""
    if not message.strip():
        return history, ""

    # Add user message to history
    history.append((message, "🤔 Thinking..."))

    # Send to backend
    try:
        if not FIREBASE_ID_TOKEN:
            raise RuntimeError("FIREBASE_ID_TOKEN is not set. Provide a valid Firebase ID token in the environment.")

        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": message},
            headers=_build_headers(include_json=True)
        )

        # Wait a bit for backend to process
        time.sleep(2)

        # Fetch updated messages from Firestore
        session_data = get_session_data()
        if session_data and 'messages' in session_data:
            messages = session_data['messages']
            if messages:
                # Get the last assistant message
                last_assistant_msg = next((m['content'] for m in reversed(messages) if m['role'] == 'assistant'), None)
                if last_assistant_msg:
                    history[-1] = (message, last_assistant_msg)

    except Exception as e:
        history[-1] = (message, f"❌ Error: {str(e)}")

    return history, ""

def get_customer_info():
    """Display customer information"""
    session_data = get_session_data()
    if not session_data or 'customerInfo' not in session_data:
        return "ℹ️ No customer information collected yet."

    info = session_data['customerInfo']
    return f"""
### 📋 Customer Information

**Name:** {info.get('name', 'N/A')}
**Phone:** {info.get('phone', 'N/A')}
**Current Address:** {info.get('current_address', 'N/A')}
**Destination:** {info.get('destination_address', 'N/A')}
**Move Out Date:** {info.get('move_out_date', 'N/A')}
**Move In Date:** {info.get('move_in_date', 'N/A')}
**Apartment Size:** {info.get('apartment_size', 'N/A')}
**Packing Assistance:** {'Yes' if info.get('packing_assistance') else 'No'}
**Special Items:** {info.get('special_items', 'None')}
**Inventory:** {', '.join(info.get('inventory', []))}
"""

def get_movers_info():
    """Display filtered movers"""
    session_data = get_session_data()
    if not session_data or 'movers' not in session_data:
        return "ℹ️ No movers selected yet."

    movers = session_data['movers']
    rationale = session_data.get('moverRationale', '')

    output = f"### 🚚 Selected Movers\n\n**Selection Rationale:**\n{rationale}\n\n---\n\n"

    for mover in movers:
        output += f"""
**{mover['name']}**
📞 {mover['phone']}
✨ Specialties: {mover.get('specialties', 'N/A')}
💰 Price Range: ${mover.get('base_price_range', 'N/A')}

---
"""

    return output

def get_strategy_info():
    """Display negotiation strategy"""
    session_data = get_session_data()
    if not session_data or 'strategy' not in session_data:
        return "ℹ️ Strategy not created yet."

    strategy = session_data['strategy']
    return f"""
### 🎯 Negotiation Strategy

{strategy}
"""

def get_calls_info():
    """Display call summaries and status"""
    session_data = get_session_data()
    if not session_data:
        return "ℹ️ No call data available."

    status = session_data.get('status', 'unknown')
    call_summaries = session_data.get('callSummaries', [])
    movers = session_data.get('movers', [])

    output = f"### 📞 Call Status: `{status.upper()}`\n\n"

    if status == 'negotiating':
        output += "🔄 **Currently making calls to movers...**\n\n"

    for i, mover in enumerate(movers):
        output += f"**{mover['name']}** - {mover['phone']}\n\n"

        if i < len(call_summaries):
            output += f"{call_summaries[i]}\n\n"
        elif status == 'negotiating':
            output += "⏳ Waiting to call...\n\n"
        else:
            output += "❌ No call data\n\n"

        output += "---\n\n"

    return output

def get_recommendation():
    """Display final recommendation"""
    session_data = get_session_data()
    if not session_data or 'recommendation' not in session_data:
        return "ℹ️ Final recommendation not ready yet."

    recommendation = session_data['recommendation']
    return f"""
### 🏆 Final Recommendation

{recommendation}
"""

def get_status():
    """Get current status"""
    session_data = get_session_data()
    if not session_data:
        return "❓ Unknown"

    status = session_data.get('status', 'unknown')
    status_map = {
        'info_collection': '💬 Collecting Information',
        'strategizing': '🧠 Creating Strategy',
        'negotiating': '📞 Negotiating with Movers',
        'analyzing': '📊 Analyzing Results',
        'completed': '✅ Completed'
    }
    return status_map.get(status, status)

def refresh_all():
    """Refresh all components"""
    return (
        get_status(),
        get_customer_info(),
        get_movers_info(),
        get_strategy_info(),
        get_calls_info(),
        get_recommendation()
    )

def start_new_session():
    """Start a new quote session"""
    try:
        if not FIREBASE_ID_TOKEN:
            raise RuntimeError("FIREBASE_ID_TOKEN is not set. Provide a valid Firebase ID token in the environment.")

        response = requests.get(
            f"{BASE_URL}/api/chat/new",
            headers=_build_headers()
        )
        time.sleep(1)
        return [], *refresh_all()
    except Exception as e:
        return [], f"❌ Error: {str(e)}", "", "", "", "", ""

# Build Gradio Interface
with gr.Blocks(title="MoveScout - AI Moving Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🚚 MoveScout - AI Moving Assistant

    Your AI-powered moving negotiation assistant. Chat to get started!
    """)

    with gr.Row():
        status_display = gr.Textbox(label="Current Status", value=get_status(), interactive=False)
        refresh_btn = gr.Button("🔄 Refresh", scale=0)
        new_session_btn = gr.Button("🆕 New Session", scale=0)

    with gr.Tab("💬 Chat"):
        chatbot = gr.Chatbot(label="Chat with MoveScout", height=400)
        msg_input = gr.Textbox(
            label="Your Message",
            placeholder="Tell me about your move (addresses, dates, apartment size, etc.)",
            lines=2
        )
        send_btn = gr.Button("Send", variant="primary")

        gr.Markdown("""
        **Example message:**
        *"I want to move from San Francisco to Miami. My current address is 825 Menlo Ave, Menlo Park, CA 94002,
        and I'm moving to 200 First Street, Miami. Moving on Dec 10, 2024. I have a studio apartment (500 sq ft),
        no special items. Need help with packing. My name is Alex and my phone is 650-321-4321."*
        """)

    with gr.Tab("📋 Customer Info"):
        customer_info_display = gr.Markdown(value=get_customer_info())

    with gr.Tab("🚚 Movers"):
        movers_display = gr.Markdown(value=get_movers_info())

    with gr.Tab("🎯 Strategy"):
        strategy_display = gr.Markdown(value=get_strategy_info())

    with gr.Tab("📞 Calls"):
        calls_display = gr.Markdown(value=get_calls_info())

    with gr.Tab("🏆 Recommendation"):
        recommendation_display = gr.Markdown(value=get_recommendation())

    # Event handlers
    send_btn.click(
        send_message,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input]
    ).then(
        refresh_all,
        outputs=[status_display, customer_info_display, movers_display,
                strategy_display, calls_display, recommendation_display]
    )

    msg_input.submit(
        send_message,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input]
    ).then(
        refresh_all,
        outputs=[status_display, customer_info_display, movers_display,
                strategy_display, calls_display, recommendation_display]
    )

    refresh_btn.click(
        refresh_all,
        outputs=[status_display, customer_info_display, movers_display,
                strategy_display, calls_display, recommendation_display]
    )

    new_session_btn.click(
        start_new_session,
        outputs=[chatbot, status_display, customer_info_display, movers_display,
                strategy_display, calls_display, recommendation_display]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
