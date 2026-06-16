import streamlit as st
import json
from utils.style_helper import apply_custom_style, render_metric_card
from utils.hf_helper import generate_quiz, analyze_weak_topics
from utils.db_helper import save_quiz

st.set_page_config(
    page_title="AI Quiz Generator - AI Study Mentor X",
    page_icon="📝",
    layout="wide"
)

apply_custom_style()

st.markdown("<h1 class='title-main'>📝 Practice Quiz Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader-text'>Test your knowledge with 10 dynamically generated multiple-choice questions</p>", unsafe_allow_html=True)

# Check active document
if not st.session_state.get("current_doc_id"):
    st.warning("⚠️ No active study material selected. Please go to the Home page and upload a PDF first.")
else:
    doc_id = st.session_state.current_doc_id
    doc_text = st.session_state.pdf_text
    doc_name = st.session_state.pdf_name
    
    st.markdown(f"<div class='badge'>Testing on: {doc_name}</div>", unsafe_allow_html=True)
    
    # Initialize Quiz states
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = None
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "quiz_doc_id" not in st.session_state:
        st.session_state.quiz_doc_id = None
    if "quiz_weak_analysis" not in st.session_state:
        st.session_state.quiz_weak_analysis = ""
    if "user_choices" not in st.session_state:
        st.session_state.user_choices = {}
        
    # Reset quiz state if document changed
    if st.session_state.quiz_doc_id != doc_id:
        st.session_state.quiz_questions = None
        st.session_state.quiz_submitted = False
        st.session_state.quiz_weak_analysis = ""
        st.session_state.user_choices = {}
        st.session_state.quiz_doc_id = doc_id
        
    # Sidebar actions
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🛠️ Quiz Tools")
        generate_btn = st.button("🔄 Generate New Quiz")
        if generate_btn:
            if not st.session_state.get("hf_token"):
                st.error("🔑 Hugging Face Token is missing. Configure it on the Home page.")
            else:
                with st.spinner("🧠 Generating 10 MCQs from notes (using Qwen)..."):
                    try:
                        quiz_data = generate_quiz(doc_text)
                        st.session_state.quiz_questions = quiz_data
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_weak_analysis = ""
                        st.session_state.user_choices = {}
                        st.success("Successfully generated new practice test!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate quiz: {e}")
                        
    # Main Quiz Flow
    if st.session_state.quiz_questions is None:
        st.markdown("""
        <div class='glass-container' style='text-align: center; padding: 40px;'>
            <h4 style='color: #c084fc;'>No Practice Test Loaded</h4>
            <p style='color: #94a3b8; max-width: 500px; margin: 0 auto 20px auto;'>
                Click the <b>Generate New Quiz</b> button on the sidebar to analyze your active document and create an interactive practice test.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        questions = st.session_state.quiz_questions
        submitted = st.session_state.quiz_submitted
        
        # Display questions
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        
        # We will collect responses
        for i, q in enumerate(questions):
            st.markdown(f"**Question {q.get('question_num', i+1)} of 10**")
            st.markdown(f"#### {q.get('question')}")
            
            # Options format list
            options = q.get('options', [])
            
            # Map choice index to option label
            saved_choice = st.session_state.user_choices.get(i, None)
            
            # Determine starting index for radio button
            choice_idx = None
            if saved_choice is not None:
                for idx, opt in enumerate(options):
                    if opt.strip().startswith(saved_choice):
                        choice_idx = idx
                        break
                        
            # Render radio buttons
            selected_option = st.radio(
                label=f"Options for Q{i+1}",
                options=options,
                index=choice_idx,
                key=f"radio_q_{i}",
                disabled=submitted,
                label_visibility="collapsed"
            )
            
            # Save selection to session state
            if selected_option and not submitted:
                choice_letter = selected_option.split(")")[0].strip()
                st.session_state.user_choices[i] = choice_letter
                
            # Render validation details if submitted
            if submitted:
                correct = q.get('correct_answer', '').strip()
                student_choice = st.session_state.user_choices.get(i, '').strip()
                
                if student_choice == correct:
                    st.success(f"✓ Correct! (Answer: {correct})")
                else:
                    st.error(f"✗ Incorrect. Your choice: {student_choice or 'None'} | Correct Answer: {correct}")
                    
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            st.markdown("---")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Submit / Score Section
        if not submitted:
            if st.button("📤 Submit & Grade Quiz"):
                # Grade quiz
                score = 0
                wrong_answers = []
                weak_topics_list = []
                
                for idx, q in enumerate(questions):
                    correct = q.get('correct_answer', '').strip()
                    student_choice = st.session_state.user_choices.get(idx, '').strip()
                    topic = q.get('topic', 'General').strip()
                    
                    if student_choice == correct:
                        score += 1
                    else:
                        wrong_answers.append({
                            "question": q.get('question'),
                            "correct_answer": correct,
                            "student_choice": student_choice or "Unanswered",
                            "topic": topic
                        })
                        weak_topics_list.append(topic)
                        
                # Log to DB
                weak_topics_str = ", ".join(set(weak_topics_list))
                save_quiz(doc_id, score, len(questions), weak_topics_str)
                
                st.session_state.quiz_submitted = True
                
                # If there are wrong answers, analyze weak topics
                if wrong_answers:
                    with st.spinner("🤖 Analyzing performance and weak topics (using Qwen)..."):
                        try:
                            analysis = analyze_weak_topics(wrong_answers)
                            st.session_state.quiz_weak_analysis = analysis
                        except Exception as e:
                            st.session_state.quiz_weak_analysis = f"Failed to analyze weak topics: {e}"
                else:
                    st.session_state.quiz_weak_analysis = "🎉 Perfect score! You have shown excellent command over all topics in this quiz."
                    
                st.rerun()
        else:
            # Show Score Report
            score = 0
            for idx, q in enumerate(questions):
                correct = q.get('correct_answer', '').strip()
                student_choice = st.session_state.user_choices.get(idx, '').strip()
                if student_choice == correct:
                    score += 1
                    
            st.markdown("### 📊 Quiz Result Report")
            c1, c2 = st.columns([1, 2])
            
            with c1:
                pct = (score / len(questions)) * 100
                border_col = "#22c55e" if pct >= 70 else ("#fb923c" if pct >= 40 else "#ef4444")
                render_metric_card(
                    "Practice Test Score",
                    f"{score} / {len(questions)}",
                    f"Percentage: {pct:.0f}%",
                    "🎯",
                    border_col
                )
                
                if st.button("🔄 Retake Quiz"):
                    st.session_state.quiz_submitted = False
                    st.session_state.user_choices = {}
                    st.session_state.quiz_weak_analysis = ""
                    st.rerun()
                    
            with c2:
                st.markdown("""
                <div class='glass-container'>
                    <h4 style='color: #fb923c; margin-top: 0;'>⚠️ Weak Topics & Review Guide</h4>
                """, unsafe_allow_html=True)
                st.markdown(st.session_state.quiz_weak_analysis)
                st.markdown("</div>", unsafe_allow_html=True)
