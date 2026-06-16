import streamlit as st
from utils.style_helper import apply_custom_style
from utils.hf_helper import generate_study_plan
from utils.db_helper import get_study_plan, save_study_plan, get_quiz_history

st.set_page_config(
    page_title="AI Study Planner - AI Study Mentor X",
    page_icon="📅",
    layout="wide"
)

apply_custom_style()

st.markdown("<h1 class='title-main'>📅 Personalized Study Planner</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader-text'>Get a customized, day-by-day learning schedule tailored to your weak topics</p>", unsafe_allow_html=True)

# Check active document
if not st.session_state.get("current_doc_id"):
    st.warning("⚠️ No active study material selected. Please go to the Home page and upload a PDF first.")
else:
    doc_id = st.session_state.current_doc_id
    doc_text = st.session_state.pdf_text
    doc_name = st.session_state.pdf_name
    
    st.markdown(f"<div class='badge'>Targeting Document: {doc_name}</div>", unsafe_allow_html=True)
    
    # Retrieve weak topics for this document from quiz history
    history = get_quiz_history()
    doc_weak_topics = []
    
    for quiz in history:
        if quiz['filename'] == doc_name and quiz['weak_topics']:
            # Split topics and merge
            topics = [t.strip() for t in quiz['weak_topics'].split(",") if t.strip()]
            doc_weak_topics.extend(topics)
            
    # Filter unique weak topics
    unique_weak = list(set(doc_weak_topics))
    weak_topics_str = ", ".join(unique_weak) if unique_weak else "None identified yet (try taking a quiz first!)"
    
    # Display current study profile
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class='glass-container'>
            <h4 style='color: #c084fc; margin-top: 0;'>📝 Study Profile Summary</h4>
            <p>We've analyzed your progress on this document to customize your planner.</p>
        """, unsafe_allow_html=True)
        st.markdown(f"**Document Name:** {doc_name}")
        st.markdown(f"**Struggled Concepts:** `{weak_topics_str}`")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class='glass-container'>
            <h4 style='color: #818cf8; margin-top: 0;'>⚙️ Plan Parameters</h4>
        """, unsafe_allow_html=True)
        days = st.number_input("Days remaining until your exam:", min_value=1, max_value=60, value=7)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Check if plan already exists in database
    cached_plan = get_study_plan(doc_id, days)
    
    if cached_plan:
        st.info("📂 Loaded previously generated study plan for this duration. If you want a fresh plan, click 'Regenerate Study Plan' below.")
        
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown(cached_plan)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🔄 Regenerate Study Plan"):
            if not st.session_state.get("hf_token"):
                st.error("🔑 Hugging Face Token is missing. Please configure your token on the Home page.")
            else:
                with st.spinner("🧠 Generating dynamic study schedule (using Qwen)..."):
                    try:
                        plan_text = generate_study_plan(doc_text, weak_topics_str, days)
                        save_study_plan(doc_id, days, plan_text)
                        st.success("Study plan updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating study plan: {e}")
    else:
        # No plan exists yet
        st.markdown("""
        <div class='glass-container' style='text-align: center; padding: 40px;'>
            <h4 style='color: #a78bfa;'>Ready to Generate Study Plan</h4>
            <p style='color: #94a3b8; max-width: 500px; margin: 0 auto 20px auto;'>
                Click the button below to generate a customized day-by-day study schedule.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Generate Study Plan"):
            if not st.session_state.get("hf_token"):
                st.error("🔑 Hugging Face Token is missing. Please configure your token on the Home page.")
            else:
                with st.spinner("🧠 Generating dynamic study schedule (using Qwen)..."):
                    try:
                        plan_text = generate_study_plan(doc_text, weak_topics_str, days)
                        save_study_plan(doc_id, days, plan_text)
                        st.success("Study plan generated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating study plan: {e}")
