import streamlit as st
from utils.style_helper import apply_custom_style
from utils.hf_helper import tutor_answer

st.set_page_config(
    page_title="AI Tutor - AI Study Mentor X",
    page_icon="🤖",
    layout="wide"
)

apply_custom_style()

st.markdown("<h1 class='title-main'>🤖 Interactive AI Tutor</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader-text'>Ask questions and get explanations directly from your uploaded notes</p>", unsafe_allow_html=True)

# Check if document is selected
if not st.session_state.get("current_doc_id"):
    st.warning("⚠️ No active study material selected. Please go to the Home page and upload a PDF first.")
else:
    # Set up active document info
    st.markdown(f"<div class='badge'>Reading Context: {st.session_state.pdf_name}</div>", unsafe_allow_html=True)
    
    # Initialize Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    # Sidebar control to clear chat
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Tutor Settings")
        if st.button("🧹 Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
            
    # Display Chat Messages
    for msg in st.session_state.chat_history:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            
    # Accept Student Question
    question = st.chat_input("Ask your AI Tutor about these notes...")
    
    if question:
        # Check API key (Hugging Face Token)
        if not st.session_state.get("hf_token"):
            st.error("🔑 Hugging Face Token is missing. Please configure your token on the Home page sidebar.")
        else:
            # Display user question
            with st.chat_message("user", avatar="👤"):
                st.markdown(question)
            st.session_state.chat_history.append({"role": "user", "content": question})
            
            # Generate tutor answer
            with st.spinner("🤖 Thinking (Powered by Qwen)..."):
                try:
                    answer = tutor_answer(
                        st.session_state.pdf_text,
                        question,
                        st.session_state.chat_history
                    )
                    
                    # Display tutor answer
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"Error communicating with AI Tutor: {e}")
                    # Remove the last user query to prevent saving error loops
                    st.session_state.chat_history.pop()
