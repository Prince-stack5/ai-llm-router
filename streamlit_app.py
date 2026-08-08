import streamlit as st
import requests
import html


API_URL = "https://ai-llm-router.onrender.com/api/v1/chat"


st.set_page_config(
    page_title="AI LLM Router",
    page_icon="🤖",
    layout="centered",
)


st.markdown(
    """
    <style>
        .main {
            max-width: 900px;
            margin: auto;
        }

        .title {
            text-align: center;
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .subtitle {
            text-align: center;
            color: #666666;
            margin-bottom: 30px;
        }

        .result-box {
            padding: 20px;
            border-radius: 12px;
            background: #f7f7f8;
            border: 1px solid #e5e5e5;
            margin-top: 20px;
        }

        .response-text {
            color: #222222;
            font-size: 16px;
            line-height: 1.7;
            white-space: pre-wrap;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="title">🤖 AI LLM Router</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Send your prompt and let the router choose the right AI provider.</div>',
    unsafe_allow_html=True,
)


query = st.text_area(
    "Your prompt",
    placeholder="Example: Write a professional email asking my manager for one day of leave...",
    height=150,
)


if st.button("🚀 Send Request", use_container_width=True):

    if not query.strip():
        st.warning("Please enter a prompt first.")

    else:

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    API_URL,
                    json={"query": query},
                    timeout=90,
                )

                if response.status_code == 200:

                    data = response.json()

                    st.success("Request completed")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Task",
                            data.get("task", "Unknown"),
                        )

                    with col2:
                        st.metric(
                            "Provider",
                            data.get("provider", "Unknown"),
                        )

                    st.markdown("### Response")

                    response_text = data.get(
                        "response",
                        "No response received.",
                    )

                    safe_response = html.escape(response_text)

                    st.markdown(
                        f"""
                        <div class="result-box">
                            <div class="response-text">{safe_response}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                else:

                    st.error(
                        f"API returned an error: {response.status_code}"
                    )

                    try:
                        error_data = response.json()
                        st.json(error_data)
                    except Exception:
                        st.code(response.text)

            except requests.exceptions.Timeout:

                st.error(
                    "The server took too long to respond. "
                    "The Render free instance may be waking up."
                )

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not connect to the API: {e}"
                )