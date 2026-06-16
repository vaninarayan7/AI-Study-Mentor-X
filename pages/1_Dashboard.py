import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from utils.db_helper import get_document_count, get_average_score, get_quiz_history, get_weak_topics_list
from utils.style_helper import apply_custom_style, render_metric_card

st.set_page_config(
    page_title="Analytics Dashboard - AI Study Mentor X",
    page_icon="📊",
    layout="wide"
)

apply_custom_style()

st.markdown("<h1 class='title-main'>📊 Study Analytics & Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader-text'>Track your academic progress, quiz scores, and focus areas</p>", unsafe_allow_html=True)

# Fetch stats from DB
doc_count = get_document_count()
avg_score = get_average_score()
quiz_history = get_quiz_history()
weak_topics_list = get_weak_topics_list()

# Unique weak topics count
unique_weak_topics = set(weak_topics_list)
weak_topics_count = len(unique_weak_topics)

# Display High-Level Metric Cards
st.markdown("### 📈 Performance at a Glance")
m1, m2, m3, m4 = st.columns(4)

with m1:
    render_metric_card("PDFs Uploaded", str(doc_count), "Total textbooks & notes", "📚", "#818cf8")
with m2:
    render_metric_card("Average Quiz Score", f"{avg_score:.1f}%", "All completed tests", "🎯", "#c084fc")
with m3:
    render_metric_card("Quizzes Completed", str(len(quiz_history)), "Total assessments taken", "📝", "#f472b6")
with m4:
    render_metric_card("Focus Topics", str(weak_topics_count), "Identified weak areas", "⚠️", "#fb923c")

st.markdown("---")

# Visual Charts
if not quiz_history:
    st.info("💡 Complete a practice quiz in the 'Quiz Generator' page to populate your performance charts.")
else:
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.markdown("### 📈 Score Progression Over Time")
        # Build DataFrame for line chart
        df_quizzes = pd.DataFrame(quiz_history)
        df_quizzes['score_pct'] = (df_quizzes['score'] / df_quizzes['total_questions']) * 100.0
        
        # Sort chronologically
        df_quizzes['completed_at'] = pd.to_datetime(df_quizzes['completed_at'])
        df_quizzes = df_quizzes.sort_values('completed_at')
        df_quizzes['Test Number'] = range(1, len(df_quizzes) + 1)
        df_quizzes['Test Label'] = df_quizzes.apply(lambda row: f"Q{row['Test Number']}: {row['filename'][:15]}...", axis=1)
        
        # Plotly Line Chart
        fig = px.line(
            df_quizzes,
            x="Test Number",
            y="score_pct",
            markers=True,
            labels={"score_pct": "Score (%)", "Test Number": "Test Number"},
            title="Practice Test Scores (%)"
        )
        # Style Plotly Chart
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#cbd5e1',
            xaxis=dict(showgrid=False, color='#64748b', tickmode='linear'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#64748b', range=[0, 105]),
            title_font_size=16,
            margin=dict(l=10, r=10, t=40, b=10),
            hovermode="x"
        )
        fig.update_traces(
            line_color='#a78bfa',
            line_width=3,
            marker=dict(color='#ec4899', size=8)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("### 🚨 Top Weak Topics")
        if not weak_topics_list:
            st.success("No weak topics identified yet! Perfect score?")
        else:
            # Count weak topics frequencies
            counts = Counter(weak_topics_list)
            df_topics = pd.DataFrame(counts.items(), columns=["Topic", "Frequency"]).sort_values("Frequency", ascending=True)
            
            # Plotly Horizontal Bar Chart
            fig_bar = px.bar(
                df_topics.tail(8),  # Show top 8
                x="Frequency",
                y="Topic",
                orientation='h',
                title="Struggled Concepts (Frequency)"
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#cbd5e1',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#64748b', tickmode='linear'),
                yaxis=dict(showgrid=False, color='#64748b'),
                title_font_size=16,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            fig_bar.update_traces(
                marker_color='#fb923c',
                marker_line_color='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    
    # Detailed Table
    st.markdown("### 📋 Quiz Attempt Logs")
    # Format dataframe for display
    df_table = pd.DataFrame(quiz_history)
    df_table['Score'] = df_table.apply(lambda r: f"{r['score']} / {r['total_questions']}", axis=1)
    df_table['Percentage'] = (df_table['score'] / df_table['total_questions'] * 100.0).round(1).astype(str) + "%"
    df_table['Date'] = pd.to_datetime(df_table['completed_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    df_display = df_table[['filename', 'Date', 'Score', 'Percentage', 'weak_topics']].rename(columns={
        'filename': 'Notes Name',
        'weak_topics': 'Identified Weak Areas'
    })
    
    st.dataframe(df_display, use_container_width=True)
