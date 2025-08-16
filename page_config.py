"""
Page configuration and initialization functions
"""
import streamlit as st
from styling import apply_dark_theme


def setup_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="Quick o Pedia AI",
        page_icon="📚",
        layout="wide"
    )
    
    # Add Font Awesome favicon
    st.markdown("""
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 448 512'><path fill='%23ffffff' d='M96 0C43 0 0 43 0 96V416c0 53 43 96 96 96H384h32c17.7 0 32-14.3 32-32s-14.3-32-32-32V384c17.7 0 32-14.3 32-32V32c0-17.7-14.3-32-32-32H384 96zm0 384H352v64H96c-17.7 0-32-14.3-32-32s14.3-32 32-32zm32-240c0-8.8 7.2-16 16-16H336c8.8 0 16 7.2 16 16s-7.2 16-16 16H144c-8.8 0-16-7.2-16-16zm16 48H336c8.8 0 16 7.2 16 16s-7.2 16-16 16H144c-8.8 0-16-7.2-16-16s7.2-16 16-16z'/></svg>">
    """, unsafe_allow_html=True)
    
    # Apply dark theme
    apply_dark_theme()


def create_main_header():
    """Create the main header for the application"""
    st.markdown("""
    <div class="icon-header">
        <i class="fas fa-book-open"></i>
        <h1>Quick o Pedia AI</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p><i class="fas fa-download"></i> Extract, download, and chat with any Wikipedia page</p>', 
                unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all session state variables"""
    # Chat-related session state
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = None
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    
    # Content-related session state
    if 'current_content' not in st.session_state:
        st.session_state.current_content = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False