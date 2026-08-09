import streamlit as st
import requests
from datetime import datetime
import time
import os
from concurrent.futures import ThreadPoolExecutor

# Thread pool for background tasks (e.g. logging to Google Sheets)
executor = ThreadPoolExecutor(max_workers=3)

# ============================================================
# PAGE CONFIGURATION (CENTERED CHAT LAYOUT)
# ============================================================
st.set_page_config(
    page_title="AI LLM Router",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# STANDALONE (SERVERLESS) ROUTER IMPORT
# ============================================================
try:
    from app.router.classifier import QueryClassifier
    from app.router.router import LLMRouter
    from app.services.google_sheets import sheets_logger
    import asyncio
    
    def run_async(coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        return asyncio.run_coroutine_threadsafe(coro, loop).result()

    HAS_LOCAL_ROUTER = True
except Exception as e:
    HAS_LOCAL_ROUTER = False

# ============================================================
# DYNAMIC CONNECTION CONFIGURATION
# ============================================================
import sys

# Load dotenv early to read current local configuration
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Sidebar connection section
st.sidebar.markdown("### 🔌 Connection Mode")

mode_selection = st.sidebar.selectbox(
    "Execution Mode",
    [
        "Auto-detect",
        "Standalone Mode (Local)",
        "Render Cloud API (Remote)",
        "Local API Server"
    ],
    index=0,
    help="Auto-detect tries Local API Server first, then Standalone Mode if keys are available, and falls back to Render Cloud API."
)

effective_key_a = os.getenv("PROVIDER_A_API_KEY", "")
effective_key_b = os.getenv("PROVIDER_B_API_KEY", "")

# Resolve connection & execution parameters
LOCAL_API_URL = "http://127.0.0.1:8000/api/v1/chat"
REMOTE_API_URL = "https://ai-llm-router.onrender.com/api/v1/chat"

def resolve_execution_mode(selection):
    if selection == "Render Cloud API (Remote)":
        return "api_remote", REMOTE_API_URL, "Render Cloud API", "🔵"
        
    if selection == "Local API Server":
        return "api_local", LOCAL_API_URL, "Local API Server", "🟢"
        
    if selection == "Standalone Mode (Local)":
        if HAS_LOCAL_ROUTER:
            return "standalone", None, "Standalone Mode (Local)", "⚡"
        else:
            return "api_remote", REMOTE_API_URL, "Render Cloud API (Standalone Unavailable)", "🔴"
            
    # Auto-detect Mode
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=1.0)
        if response.status_code == 200:
            return "api_local", LOCAL_API_URL, "Local API Server", "🟢"
    except requests.RequestException:
        pass
        
    if HAS_LOCAL_ROUTER and (effective_key_a or effective_key_b):
        return "standalone", None, "Standalone Mode (Local)", "⚡"
        
    return "api_remote", REMOTE_API_URL, "Render Cloud API", "🔵"

exec_mode, api_url, mode_label, status_dot = resolve_execution_mode(mode_selection)

# Initialize direct components if running standalone
if exec_mode == "standalone" and "standalone_router" not in st.session_state:
    try:
        for key in ["PROVIDER_A_API_KEY", "PROVIDER_B_API_KEY", "PROVIDER_A_MODEL", "PROVIDER_B_MODEL", "CLASSIFIER_MODEL"]:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
                if key == "PROVIDER_A_API_KEY":
                    if "app.config.settings" in sys.modules:
                        sys.modules["app.config.settings"].PROVIDER_A_API_KEY = st.secrets[key]
                elif key == "PROVIDER_B_API_KEY":
                    if "app.config.settings" in sys.modules:
                        sys.modules["app.config.settings"].PROVIDER_B_API_KEY = st.secrets[key]
                        
        st.session_state.standalone_router = LLMRouter()
        st.session_state.standalone_classifier = QueryClassifier()
    except Exception as e:
        exec_mode = "api_remote"
        api_url = REMOTE_API_URL
        mode_label = "Render Cloud API (Failed Standalone Init)"
        status_dot = "🔴"

# ============================================================
# PREMIUM DARK MINIMALIST CHAT DESIGN (CUSTOM CSS)
# ============================================================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        /* App Background */
        .stApp {
            background: #0b0f19;
            color: #f8fafc;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Centered container */
        .block-container {
            max-width: 800px;
            padding-top: 60px;
            padding-bottom: 80px;
        }
        
        /* App Title */
        .app-title {
            font-size: 38px;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        /* App Subtitle description */
        .app-desc {
            color: #94a3b8;
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 40px;
        }
        
        /* Chat bubble overrides */
        div[data-testid="stChatMessage"] {
            background-color: rgba(30, 41, 59, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.03) !important;
            border-radius: 12px !important;
            padding: 16px !important;
            margin-bottom: 12px !important;
        }
        
        div[data-testid="stChatMessage"] p {
            font-size: 15px !important;
            line-height: 1.6 !important;
        }
        
        /* Sidebar styling overrides */
        section[data-testid="stSidebar"] {
            background-color: #070a12 !important;
            border-right: 1px solid #1e293b !important;
        }
        
        /* Badge styling inside chat */
        .routing-badge {
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 4px;
        }
        .badge-indigo {
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }
        .badge-amber {
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .badge-rose {
            background: rgba(244, 63, 94, 0.15);
            color: #fda4af;
            border: 1px solid rgba(244, 63, 94, 0.3);
        }
        
        /* Hide streamlit default branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background-color: transparent !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# INITIALIZE SESSION STATE FOR CHAT MESSAGES
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================
# SIDEBAR FOR SETTINGS (KEEPING MAIN INTERFACE 100% CLEAN)
# ============================================================
with st.sidebar:
    st.markdown("---")
    st.markdown("### ⚙️ Policy Selection")
    
    # Override Policy
    policy = st.selectbox(
        "Routing Policy",
        [
            "Auto (Intelligent Routing)",
            "Force Provider A (Google Gemini)",
            "Force Provider B (Groq Llama)"
        ],
        index=0
    )
    
    provider_param = "auto"
    if "Force Provider A" in policy:
        provider_param = "provider_a"
    elif "Force Provider B" in policy:
        provider_param = "provider_b"
        
    st.markdown("---")
    st.markdown(f"**Engine:** {mode_label} {status_dot}")
    if exec_mode != "standalone":
         st.caption(f"Endpoint: {api_url}")
         
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================================
# MAIN USER INTERFACE
# ============================================================

# App header
st.markdown('<div class="app-title">🤖 AI LLM Router</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-desc">Welcome! I\'m your Intelligent LLM Router. Ask me anything, and I\'ll route your request to the best LLM provider (Gemini or Groq Llama) with automatic fallback protection!</div>',
    unsafe_allow_html=True
)

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ============================================================
# RUN STANDALONE ROUTER LOGIC
# ============================================================
async def execute_standalone_routing(q_text, prov_override):
    router = st.session_state.standalone_router
    classifier = st.session_state.standalone_classifier
    
    start_time = time.perf_counter()
    
    # 1. Classify
    class_start = time.perf_counter()
    try:
        task, confidence = await classifier.classify(q_text)
    except Exception:
        task, confidence = "general", 0.5
    classification_latency = time.perf_counter() - class_start
    
    # 2. Select Provider
    if prov_override and prov_override.lower() in ["provider_a", "provider_b"]:
        provider_name = prov_override.lower()
        provider = router.providers[provider_name]
    else:
        provider_name, provider = router.select_provider(task)
        
    fallback_used = False
    actual_model = getattr(provider, "model_name", "unknown")
    
    # 3. Generate response with fallback handling
    gen_start = time.perf_counter()
    try:
        response = await provider.generate(q_text)
        generation_latency = time.perf_counter() - gen_start
    except Exception as primary_error:
        fallback_used = True
        fallback_name, fallback_provider = router.get_fallback(provider_name)
        actual_model = getattr(fallback_provider, "model_name", "unknown")
        try:
            response = await fallback_provider.generate(q_text)
            provider_name = fallback_name
            generation_latency = time.perf_counter() - gen_start
        except Exception as fallback_error:
            raise Exception(f"Routing failure: {primary_error} -> {fallback_error}")
            
    total_latency = time.perf_counter() - start_time
    
    # Log to Google Sheets asynchronously in the background using a persistent thread pool
    executor.submit(
        sheets_logger.log_query_sync,
        prompt=q_text,
        category=task,
        confidence=confidence,
        provider=provider_name,
        model=actual_model
    )
    
    return {
        "query": q_text,
        "task": task,
        "confidence": confidence,
        "provider": provider_name,
        "model": actual_model,
        "fallback_used": fallback_used,
        "response": response,
        "metrics": {
            "classification_latency": round(classification_latency, 3),
            "generation_latency": round(generation_latency, 3),
            "total_latency": round(total_latency, 3)
        }
    }

# ============================================================
# CHAT INPUT TRIGGER (BOTTOM FLOATING CHAT INPUT)
# ============================================================
if prompt := st.chat_input("Ask me anything..."):
    # 1. Display user prompt immediately
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Add user prompt to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Query LLM Router and display response
    with st.chat_message("assistant"):
        with st.spinner("Routing..."):
            try:
                if exec_mode == "standalone":
                    data = run_async(execute_standalone_routing(prompt, provider_param))
                else:
                    payload = {
                        "query": prompt,
                        "provider": provider_param
                    }
                    response = requests.post(api_url, json=payload, timeout=60)
                    if response.status_code == 200:
                        data = response.json()
                    else:
                        raise Exception(f"API Error ({response.status_code}): {response.text}")
                
                # Check metrics structure
                if "metrics" not in data:
                    data["metrics"] = {"classification_latency": 0.0, "generation_latency": 0.0, "total_latency": 0.0}
                if "model" not in data:
                    data["model"] = "gemini-3.6-flash" if data.get("provider") == "provider_a" else "llama-3.3-70b-versatile"
                
                response_content = data.get("response", "")
                st.markdown(response_content)
                
                # Metadata tags
                task = data.get("task", "general")
                provider = data.get("provider", "provider_a")
                model = data.get("model", "unknown")
                latency = data["metrics"].get("total_latency", 0.0)
                fallback = data.get("fallback_used", False)
                policy_forced = (provider_param != "auto")
                

                
                # Add response to session state chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_content,
                    "task": task,
                    "provider": provider,
                    "model": model,
                    "latency": latency,
                    "fallback_used": fallback,
                    "policy_forced": policy_forced
                })
            except Exception as e:
                st.error("⚠️ **Routing Execution Failed.** Please verify that your API keys are configured correctly in the environment secrets of your hosting platform (Streamlit Cloud or Render).")