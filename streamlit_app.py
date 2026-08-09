import streamlit as st
import requests
from datetime import datetime
import time
import os

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="AI LLM Router",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# STANDALONE (SERVERLESS) ROUTER IMPORT
# ============================================================
try:
    from app.router.classifier import QueryClassifier
    from app.router.router import LLMRouter
    import asyncio
    
    # Helper to run async code inside synchronous Streamlit
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
# API ENDPOINT / EXECUTION MODE AUTO-DETECTION
# ============================================================
LOCAL_API_URL = "http://127.0.0.1:8000/api/v1/chat"

@st.cache_data(ttl=2)
def detect_execution_mode():
    # 1. Try to connect to local FastAPI server first
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=0.3)
        if response.status_code == 200:
            return "api_local", LOCAL_API_URL, "Local API Server", "🟢"
    except requests.RequestException:
        pass
        
    # 2. If no API server, check if standalone router modules are imported
    if HAS_LOCAL_ROUTER:
        # Check if API keys are set in environment/secrets
        has_keys = os.getenv("PROVIDER_A_API_KEY") is not None or "PROVIDER_A_API_KEY" in st.secrets
        if has_keys:
            return "standalone", None, "Standalone Mode (Cloud)", "⚡"
            
    # 3. Fallback to hosted Render API
    return "api_remote", "https://ai-llm-router.onrender.com/api/v1/chat", "Render Cloud API", "🔵"

exec_mode, api_url, mode_label, status_dot = detect_execution_mode()

# Initialize direct components if running standalone
if exec_mode == "standalone" and "standalone_router" not in st.session_state:
    try:
        # Ensure env variables are loaded if using local settings
        from dotenv import load_dotenv
        load_dotenv()
        
        # Override env with streamlit secrets if available
        for key in ["PROVIDER_A_API_KEY", "PROVIDER_B_API_KEY", "PROVIDER_A_MODEL", "PROVIDER_B_MODEL", "CLASSIFIER_MODEL"]:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
                
        st.session_state.standalone_router = LLMRouter()
        st.session_state.standalone_classifier = QueryClassifier()
    except Exception as e:
        # Fallback to remote API if initialization fails
        exec_mode = "api_remote"
        api_url = "https://ai-llm-router.onrender.com/api/v1/chat"
        mode_label = "Render Cloud API (Failed Standalone Init)"
        status_dot = "🔴"

# ============================================================
# PREMIUM DARK MINIMALIST DESIGN (CUSTOM CSS)
# ============================================================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        .stApp {
            background: #090d16;
            color: #f8fafc;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .block-container {
            max-width: 800px;
            padding-top: 40px;
            padding-bottom: 40px;
        }
        
        .premium-card {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .gradient-title {
            background: linear-gradient(135deg, #a5b4fc, #6366f1, #4f46e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 34px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 4px;
            letter-spacing: -1px;
        }
        
        .subtitle {
            color: #94a3b8;
            font-size: 14px;
            text-align: center;
            margin-bottom: 30px;
        }
        
        textarea {
            background-color: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            font-size: 14px !important;
        }
        textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        }
        
        .custom-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        
        .badge-indigo {
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }
        .badge-emerald {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
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
        
        div[data-baseweb="select"] > div {
            background-color: #0f172a !important;
            border: 1px solid #334155 !important;
            color: #f8fafc !important;
            border-radius: 10px;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
if "history" not in st.session_state:
    st.session_state.history = []

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if "last_response" not in st.session_state:
    st.session_state.last_response = None

# ============================================================
# MAIN HEADER
# ============================================================
st.markdown('<div class="gradient-title">🤖 AI LLM Router</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">Engine: <b>{mode_label}</b> {status_dot}</div>', 
    unsafe_allow_html=True
)

# ============================================================
# INTERACTIVE CHAT SANDBOX CARD
# ============================================================
st.markdown('<div class="premium-card">', unsafe_allow_html=True)

# Preset chips
presets = [
    ("💻 Code", "Write a python function to find the nth Fibonacci number."),
    ("📝 Writing", "Draft a polite email asking for an extension on the project deadline."),
    ("📄 Summarize", "Summarize the key differences between SQL and NoSQL databases."),
    ("🌐 Translate", "Translate to German: 'Artificial intelligence is changing software development'"),
    ("🧠 Logic", "If a farmer has 35 heads and 94 legs of chickens and rabbits, how many of each does he have?")
]

st.markdown('<div style="color: #64748b; font-size: 11px; margin-bottom: 6px; font-weight: 500;">Quick Test:</div>', unsafe_allow_html=True)
cols = st.columns(len(presets))
for idx, (label, text) in enumerate(presets):
    with cols[idx]:
        if st.button(label, key=f"chip_{idx}", use_container_width=True):
            st.session_state.last_query = text
            st.session_state.preset_prompt = text
            st.rerun()

# Prompt loading logic
default_text = st.session_state.get("preset_prompt", "")
query = st.text_area(
    "Query input",
    value=st.session_state.get("last_query", default_text),
    placeholder="Enter your prompt here or click a preset above...",
    height=130,
    label_visibility="collapsed"
)
if "preset_prompt" in st.session_state:
    del st.session_state.preset_prompt
st.session_state.last_query = query

# Selection dropdown and trigger button
ctrl_col1, ctrl_col2 = st.columns([2, 1])
with ctrl_col1:
    policy = st.selectbox(
        "Routing Policy",
        [
            "Auto (Intelligent Routing)",
            "Force Provider A (Google Gemini)",
            "Force Provider B (Groq Llama)"
        ],
        index=0,
        label_visibility="collapsed"
    )
    
with ctrl_col2:
    provider_param = "auto"
    if "Force Provider A" in policy:
        provider_param = "provider_a"
    elif "Force Provider B" in policy:
        provider_param = "provider_b"
        
    send_req = st.button("🚀 Route Request", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ROUTER WORKER EXECUTION
# ============================================================
async def execute_standalone_routing(q_text, prov_override):
    # Standalone execution running directly in-process
    router = st.session_state.standalone_router
    classifier = st.session_state.standalone_classifier
    
    start_time = time.perf_counter()
    
    # 1. Classification
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
# API SEND TRIGGER
# ============================================================
if send_req:
    if not query.strip():
        st.warning("Please enter a query first.")
    else:
        with st.spinner("Routing..."):
            try:
                # Execution routing selection
                if exec_mode == "standalone":
                    # Standalone execution
                    data = run_async(execute_standalone_routing(query.strip(), provider_param))
                else:
                    # Server execution
                    payload = {
                        "query": query.strip(),
                        "provider": provider_param
                    }
                    response = requests.post(api_url, json=payload, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                    else:
                        raise Exception(f"API Error ({response.status_code}): {response.text}")
                
                # Check for metrics
                if "metrics" not in data:
                    data["metrics"] = {"classification_latency": 0.0, "generation_latency": 0.0, "total_latency": 0.0}
                    
                st.session_state.last_response = data
                
                # Store in session history
                st.session_state.history.insert(0, {
                    "query": query.strip(),
                    "response": data.get("response", ""),
                    "task": data.get("task", "general"),
                    "confidence": data.get("confidence", 1.0),
                    "provider": data.get("provider", "provider_a"),
                    "model": data.get("model", "unknown"),
                    "fallback_used": data.get("fallback_used", False),
                    "metrics": data.get("metrics", {}),
                    "time": datetime.now().strftime("%I:%M %p")
                })
                st.rerun()
            except Exception as e:
                st.error(f"Execution Error: {e}")

# ============================================================
# ROUTER RESPONSE & MINI STATUS BAR
# ============================================================
if st.session_state.last_response:
    res = st.session_state.last_response
    metrics = res.get("metrics", {})
    task = res.get("task", "general")
    confidence = res.get("confidence", 1.0)
    provider = res.get("provider", "provider_a")
    model = res.get("model", "unknown")
    fallback_used = res.get("fallback_used", False)
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    
    # Compact horizontal status row
    st.markdown(
        f"""
        <div style="margin-bottom: 16px;">
            <span class="custom-badge badge-indigo">Task: {task.upper()} ({confidence:.0%})</span>
            <span class="custom-badge badge-emerald">Routed to: {provider.upper()}</span>
            <span class="custom-badge badge-indigo">Model: {model}</span>
            <span class="custom-badge badge-indigo">Latency: {metrics.get('total_latency', 0):.2f}s</span>
            {"<span class='custom-badge badge-rose'>Fallback Triggered</span>" if fallback_used else ""}
            {"<span class='custom-badge badge-amber'>Policy Forced</span>" if provider_param != "auto" else ""}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div style="font-weight:700; font-size:13px; color:#a5b4fc; margin-bottom:8px;">✨ Response:</div>', unsafe_allow_html=True)
    st.markdown(res.get("response", ""))
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# CONVERSATION HISTORY LOGS
# ============================================================
if st.session_state.history:
    st.markdown('<h4 style="color:#f8fafc; font-size:16px; font-weight:700; margin-top:24px; margin-bottom:12px;">🕘 Session History</h4>', unsafe_allow_html=True)
    
    for index, item in enumerate(st.session_state.history):
        title_text = item["query"].replace("\n", " ").strip()
        if len(title_text) > 75:
            title_text = title_text[:75] + "..."
            
        fallback_str = " (Fallback)" if item.get("fallback_used", False) else ""
        
        with st.expander(
            f"#{len(st.session_state.history)-index}: {title_text} [{item['task'].upper()} ⚡ {item['provider'].upper()}{fallback_str}]"
        ):
            st.markdown(
                f"""
                <div style="font-size: 12px; color: #94a3b8; margin-bottom: 10px; line-height: 1.5;">
                    <b>Model:</b> {item['model']} &nbsp;|&nbsp; 
                    <b>Latency:</b> {item['metrics'].get('total_latency', 0):.2f}s (Class: {item['metrics'].get('classification_latency', 0):.2f}s, Gen: {item['metrics'].get('generation_latency', 0):.2f}s) &nbsp;|&nbsp;
                    <b>Time:</b> {item['time']}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("**Prompt:**")
            st.code(item["query"])
            st.markdown("**Response:**")
            st.write(item["response"])
            
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Session History", use_container_width=True):
        st.session_state.history = []
        st.session_state.last_response = None
        st.session_state.last_query = ""
        st.rerun()