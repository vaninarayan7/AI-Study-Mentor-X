import streamlit as st

def apply_custom_style():
    """
    Applies custom CSS styling for a modern, high-quality dark theme dashboard.
    All colors meet WCAG AA contrast on a dark background.
    Opacity: 1.0 everywhere. No semi-transparent text or backgrounds.
    """
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        /* ── Global font ── */
        html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6,
        li, span, label, button, input, select, textarea {
            font-family: 'Outfit', sans-serif !important;
        }

        /* ── App background ── */
        .stApp {
            background: linear-gradient(135deg, #0e0a1f 0%, #150f30 50%, #1c1240 100%) !important;
            color: #E5E7EB !important;
        }

        /* ── Main heading gradient ── */
        h1.title-main {
            font-weight: 800;
            background: linear-gradient(45deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            font-size: 3rem;
            letter-spacing: -1px;
        }

        /* ── All headings: full white ── */
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
        }

        /* ── Body text minimum brightness ── */
        p, li, span, label {
            color: #E5E7EB;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background-color: #110d26 !important;
            border-right: 2px solid #2d2060;
        }

        section[data-testid="stSidebar"] .stMarkdown h1 {
            color: #c4b5fd !important;
            font-size: 1.8rem;
            font-weight: 700;
        }

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {
            color: #E5E7EB !important;
        }

        /* ── Glass card containers ── */
        .glass-container {
            background: #1e1740;
            border: 1px solid #3b2f7a;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.5);
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        .glass-container:hover {
            border-color: #7c3aed;
            box-shadow: 0 12px 40px 0 rgba(124, 58, 237, 0.35);
        }

        .glass-container h3,
        .glass-container h4 {
            color: #FFFFFF !important;
        }

        .glass-container p,
        .glass-container li {
            color: #E5E7EB !important;
        }

        /* ── Buttons ── */
        div.stButton > button {
            background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.5) !important;
            transition: all 0.25s ease !important;
            width: 100%;
            opacity: 1 !important;
        }

        div.stButton > button:hover {
            background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 22px rgba(99, 102, 241, 0.7) !important;
        }

        div.stButton > button:active {
            transform: translateY(0px) !important;
        }

        /* ── Text inputs ── */
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea,
        .stSelectbox [data-baseweb="select"] {
            background-color: #1a1535 !important;
            color: #FFFFFF !important;
            border: 1px solid #4c3d9e !important;
            border-radius: 8px !important;
        }

        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stTextArea textarea:focus {
            border-color: #8b5cf6 !important;
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.4) !important;
        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: #9ca3af !important;
        }

        /* ── Tabs ── */
        button[data-baseweb="tab"] {
            color: #c4b5fd !important;
            font-weight: 500 !important;
            opacity: 1 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #FFFFFF !important;
            border-bottom-color: #c084fc !important;
        }

        /* ── Subheader text ── */
        .subheader-text {
            color: #E5E7EB !important;
            font-size: 1.1rem;
            margin-bottom: 25px;
            opacity: 1 !important;
        }

        /* ── Badge ── */
        .badge {
            background-color: #2d1f6e;
            color: #e9d5ff;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid #6d28d9;
            display: inline-block;
            margin-bottom: 12px;
            opacity: 1 !important;
        }

        /* ── Chat messages ── */
        [data-testid="stChatMessage"] {
            background: #1e1740 !important;
            border: 1px solid #3b2f7a !important;
            border-radius: 12px !important;
            color: #E5E7EB !important;
            opacity: 1 !important;
        }

        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] span {
            color: #E5E7EB !important;
            opacity: 1 !important;
        }

        /* ── Streamlit native text elements ── */
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown span {
            color: #E5E7EB !important;
        }

        /* ── Metric labels and values ── */
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            opacity: 1 !important;
        }

        /* ── Selectbox, radio labels ── */
        .stRadio label,
        .stSelectbox label,
        .stCheckbox label {
            color: #E5E7EB !important;
            opacity: 1 !important;
        }

        /* ── Dataframe/table text ── */
        .stDataFrame, [data-testid="stDataFrameResizable"] {
            color: #E5E7EB !important;
        }

        /* ── Section headers ── */
        .stSidebar h1,
        .stSidebar h2,
        .stSidebar h3 {
            color: #FFFFFF !important;
        }

        /* ── Info / warning / success / error messages ── */
        .stAlert p {
            color: #FFFFFF !important;
        }

        /* ── Divider ── */
        hr {
            border-color: #3b2f7a !important;
        }

        </style>
    """, unsafe_allow_html=True)


def render_metric_card(title, value, subtitle="", icon="🎓", border_color="#8b5cf6"):
    """
    Renders a high-contrast metric card with solid background and full opacity.
    """
    card_html = f"""
    <div style="
        background: #1e1740;
        border: 1px solid #3b2f7a;
        border-left: 4px solid {border_color};
        border-radius: 12px;
        padding: 20px;
        color: #FFFFFF;
        box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.5);
        margin-bottom: 15px;
        position: relative;
        overflow: hidden;
        opacity: 1;
    ">
        <div style="
            font-size: 26px;
            position: absolute;
            top: 14px;
            right: 16px;
            opacity: 1;
        ">{icon}</div>
        <div style="
            font-size: 11px;
            color: #c4b5fd;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.2px;
        ">{title}</div>
        <div style="
            font-size: 30px;
            font-weight: 800;
            margin: 8px 0 4px 0;
            background: linear-gradient(45deg, #a78bfa, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.1;
        ">{value}</div>
        <div style="
            font-size: 12px;
            color: #E5E7EB;
            font-weight: 500;
        ">{subtitle}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
