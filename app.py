import streamlit as slt
from agents import research
import os

# Set up page configuration
slt.set_page_config(page_title="🔍 Agentic Deep Researcher", layout="wide")

# Initialize session state variables
if "linkup_api_key" not in slt.session_state:
    slt.session_state.linkup_api_key = ""
if "messages" not in slt.session_state:
    slt.session_state.messages = []

def chat_resetter():
    slt.session_state.messages = []

# Sidebar: Linkup Configuration with updated logo link
with slt.sidebar:
    c1, c2 = slt.columns([1, 3])
    with c1:
        slt.write("")
        slt.image(
            "https://avatars.githubusercontent.com/u/175112039?s=200&v=4", width = 65)
    with c2:
        slt.header("LinkUp Configuration")
        slt.write("Deep Web Search")

    slt.markdown("[Get your API key](https://app.linkup.so/sign-up)",
                unsafe_allow_html = True)

    api_key = slt.text_input(
        "Enter your LinkUp API Key here", type = "password")
    if api_key:
        slt.session_state.linkup_api_key = api_key
        # Update the environment variable
        os.environ["API_KEY"] = api_key
        slt.success("API Key saved successfully!")

# Main Chat Interface Header with powered by logos from original code links
c1, c2 = slt.columns([6, 1])
with c1:
    slt.markdown("<h2 style='color: #0066cc;'>🔍 Agentic Deep Researcher</h2>",
                unsafe_allow_html=True)
    powered_by_html = """
    <div style='display: flex; align-items: center; gap: 10px; margin-top: 5px;'>
        <span style='font-size: 20px; color: #666;'>Powered by</span>
        <img src="https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg" width="80"> 
        <span style='font-size: 20px; color: #666;'>and</span>
        <img src="https://framerusercontent.com/images/wLLGrlJoyqYr9WvgZwzlw91A8U.png?scale-down-to=512" width="100">
    </div>
    """
    slt.markdown(powered_by_html, unsafe_allow_html=True)
with c2:
    slt.button("Clear ↺", on_click=chat_resetter)

# Add spacing between header and chat history
slt.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# Display chat history
for msg in slt.session_state.messages:
    with slt.chat_message(msg["role"]):
        slt.markdown(msg["content"])

# Accept user input and process the research query
if user_input := slt.chat_input("Ask any question about your files..."):
    slt.session_state.messages.append({"role": "user", "content": user_input})
    with slt.chat_message("user"):
        slt.markdown(user_input)

    if not slt.session_state.linkup_api_key:
        ai_res = "Please enter your API Key."
    else:
        with slt.spinner("Searching... This will take a few seconds..."):
            try:
                ai_res = run_research(user_input)
            except Exception as err:
                ai_res = f"Error: {str(err)}"

    with slt.chat_message("assistant"):
        slt.markdown(ai_res)
    slt.session_state.messages.append(
        {"role": "assistant", "content": ai_res})