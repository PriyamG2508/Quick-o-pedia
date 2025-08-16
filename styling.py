import streamlit as st

def apply_dark_theme():
    """Apply custom dark theme styling with Font Awesome support"""
    st.markdown("""
    <style>
    /* Font Awesome CDN Import */
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    /* Main app background */
    .stApp {
        background-color: #000000 !important;
        color: white !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: #1a1a1a !important;
        color: white !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: #2b2b2b !important;
        color: white !important;
        border: 1px solid #434343 !important;
    }
    
    /* Text areas */
    .stTextArea > div > div > textarea {
        background-color: #2b2b2b !important;
        color: white !important;
        border: 1px solid #434343 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #434343 !important;
        color: white !important;
        border: 1px solid #666 !important;
    }
    
    .stButton > button:hover {
        background-color: #555 !important;
        border: 1px solid #777 !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #434343 !important;
        color: white !important;
        border: 1px solid #666 !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #555 !important;
        border: 1px solid #777 !important;
    }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        background-color: #2b2b2b !important;
        border: 1px solid #434343 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #1f4e3d !important;
        color: #7fd3b3 !important;
    }
    
    .stError {
        background-color: #4e1f1f !important;
        color: #ff6b6b !important;
    }
    
    .stWarning {
        background-color: #4e4e1f !important;
        color: #ffcc02 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* All text */
    p, div, span, label {
        color: white !important;
    }
    
    /* Custom icon styling */
    .icon-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .icon-header i {
        font-size: 1.5em;
        color: white;
    }
    
    .feature-card {
        background-color: #2b2b2b;
        border: 1px solid #434343;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .feature-card i {
        color: white;
        margin-right: 8px;
    }
    
    .stat-card {
        background-color: #2b2b2b;
        border: 1px solid #434343;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    .stat-card i {
        font-size: 2em;
        color: white;
        margin-bottom: 10px;
    }
    
    .step-item {
        display: flex;
        align-items: center;
        margin: 10px 0;
    }
    
    .step-item i {
        color: #white;
        margin-right: 10px;
        width: 20px;
    }
    
    /* Custom input group styling */
    .input-group {
        display: flex;
        gap: 10px;
        align-items: end;
        margin-bottom: 20px;
    }
    
    .input-group .stTextInput {
        flex: 1;
    }
    
    .input-group .stButton {
        flex: 0 0 auto;
    }
    
    .input-group .stButton > button {
        height: 38px;
        padding: 0 20px;
        margin-top: 27px;
    }

    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    
    .chat-message.user {
        background-color: #2b2b2b;
        border-left: 4px solid #4CAF50;
    }
    
    .chat-message.assistant {
        background-color: #1a1a1a;
        border-left: 4px solid #2196F3;
    }
    
    .chat-message .avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }
    
    .chat-message.user .avatar {
        background-color: #4CAF50;
        color: white;
    }
    
    .chat-message.assistant .avatar {
        background-color: #2196F3;
        color: white;
    }
    
    .chat-message .message-content {
        color: white;
        line-height: 1.6;
    }
    
    /* Chat input styling */
    .chat-input-container {
        position: sticky;
        bottom: 0;
        background-color: #000000;
        padding: 1rem 0;
        border-top: 1px solid #434343;
    }
    </style>
    """, unsafe_allow_html=True)

def create_icon_header(icon_class, text):
    """Create a header with an icon"""
    return f"""
    <div class="icon-header">
        <i class="{icon_class}"></i>
        <h3>{text}</h3>
    </div>
    """


def create_feature_card(icon_class, title, description):
    """Create a feature card with icon"""
    return f"""
    <div class="feature-card">
        <h4><i class="{icon_class}"></i>{title}</h4>
        <p>{description}</p>
    </div>
    """