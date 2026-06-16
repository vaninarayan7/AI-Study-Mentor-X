import streamlit as st
import os
from utils.db_helper import init_db, save_document, get_all_documents, get_document, update_document_summary
from utils.pdf_reader import extract_text
from utils.style_helper import apply_custom_style
from utils.hf_helper import generate_summary

# Initialize database
init_db()

# Set page configurations
st.set_page_config(
    page_title="AI Study Mentor X",
    page_icon="🎓",
    layout="wide"
)

# Apply global premium styling
apply_custom_style()

# Ensure uploads directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Session State variables
if "hf_token" not in st.session_state:
    st.session_state.hf_token = ""
if "current_doc_id" not in st.session_state:
    st.session_state.current_doc_id = None
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""
if "pdf_summary" not in st.session_state:
    st.session_state.pdf_summary = ""

# Sidebar Layout
with st.sidebar:
    st.markdown("<h1>🎓 Mentor X</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 1. API Key Input (Hugging Face Token)
    st.markdown("### 🔑 API Configuration")
    env_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_CODELAB_KEY")
    if env_token:
        st.success("HF Token loaded from environment")
        st.session_state.hf_token = env_token
    else:
        token_input = st.text_input("Enter Hugging Face Token", type="password", value=st.session_state.hf_token)
        if token_input:
            st.session_state.hf_token = token_input
            st.success("HF Token saved for session!")
            
    st.markdown("---")
    
    # 2. Document History / Select Active Document
    st.markdown("### 📚 Study Materials")
    docs = get_all_documents()
    
    if docs:
        doc_options = {d['id']: d['filename'] for d in docs}
        selected_id = st.selectbox(
            "Select Study Notes:",
            options=list(doc_options.keys()),
            format_func=lambda x: doc_options[x],
            index=0 if st.session_state.current_doc_id is None else list(doc_options.keys()).index(st.session_state.current_doc_id)
        )
        
        # When user changes selection, load it into session state
        if selected_id != st.session_state.current_doc_id:
            doc_data = get_document(selected_id)
            if doc_data:
                st.session_state.current_doc_id = doc_data['id']
                st.session_state.pdf_text = doc_data['extracted_text']
                st.session_state.pdf_name = doc_data['filename']
                st.session_state.pdf_summary = doc_data['summary'] or ""
                st.rerun()
    else:
        st.info("No documents uploaded yet.")

# Main Page Layout
st.markdown("<h1 class='title-main'>🎓 AI Study Mentor X</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader-text'>Learn Faster • Remember Longer • Score Higher</p>", unsafe_allow_html=True)

# Main Grid Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div class='glass-container'>
        <h3>📤 Upload Study Material</h3>
        <p style='color:#94a3b8;'>Upload your course PDF notes, textbooks, or reference sheets to get started.</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose PDF notes file",
        type=["pdf"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        file_name = uploaded_file.name
        
        # Save file to uploads folder
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("🔍 Reading and processing PDF..."):
            extracted_txt = extract_text(file_path)
            
        if extracted_txt:
            # Check if this filename already exists to avoid redundant saves
            existing_doc = next((d for d in docs if d['filename'] == file_name), None)
            
            if existing_doc:
                st.info("Document already exists in system. Loading it.")
                doc_data = get_document(existing_doc['id'])
                st.session_state.current_doc_id = doc_data['id']
                st.session_state.pdf_text = doc_data['extracted_text']
                st.session_state.pdf_name = doc_data['filename']
                st.session_state.pdf_summary = doc_data['summary'] or ""
            else:
                # Save to database
                doc_id = save_document(file_name, extracted_txt, None)
                st.session_state.current_doc_id = doc_id
                st.session_state.pdf_text = extracted_txt
                st.session_state.pdf_name = file_name
                st.session_state.pdf_summary = ""
                st.success(f"✓ '{file_name}' uploaded and processed successfully!")
                st.rerun()
        else:
            st.error("Could not extract any text from the PDF. Please try a different document.")

with col2:
    st.markdown("""
    <div class='glass-container'>
        <h3>🤖 AI Study Mentor Actions</h3>
        <p style='color:#94a3b8;'>Use the navigation on the sidebar (or pages folder) to access other tools:</p>
        <ul style='color:#cbd5e1;'>
            <li><b>Dashboard</b>: View analytics and weak topics.</li>
            <li><b>AI Tutor</b>: Chat interactively about your notes (Powered by Qwen).</li>
            <li><b>Quiz Generator</b>: Test yourself with 10 customized MCQs.</li>
            <li><b>Study Planner</b>: Generate a day-by-day plan.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Active Document View & Summary
if st.session_state.current_doc_id:
    st.markdown(f"<h2>📚 Active Document: <span style='color:#c084fc;'>{st.session_state.pdf_name}</span></h2>", unsafe_allow_html=True)
    
    # Check if we need to generate summary
    if not st.session_state.pdf_summary:
        if st.button("✨ Generate AI Study Summary"):
            if not st.session_state.hf_token:
                st.warning("Please configure your Hugging Face Token in the sidebar first.")
            else:
                with st.spinner("🧠 Analyzing notes and generating study summary (using Qwen)..."):
                    try:
                        summary_txt = generate_summary(st.session_state.pdf_text)
                        update_document_summary(st.session_state.current_doc_id, summary_txt)
                        st.session_state.pdf_summary = summary_txt
                        st.success("Summary generated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating summary: {e}")
    
    if st.session_state.pdf_summary:
        tab1, tab2 = st.tabs(["📝 Study Summary & Notes", "📄 Full Extracted Text"])
        
        with tab1:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.markdown(st.session_state.pdf_summary)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab2:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.text_area("Raw Extracted Text", st.session_state.pdf_text, height=400, disabled=True)
            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("💡 Get started by uploading a PDF notes file above or selecting an existing document from the sidebar.")
