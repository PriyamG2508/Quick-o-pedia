"""
Sidebar components for the Wikipedia AI app
"""
import streamlit as st
from styling import create_icon_header


def create_sidebar():
    """Create and populate the sidebar with info and features"""
    with st.sidebar:
        st.markdown(create_icon_header("fas fa-info-circle", "About"), unsafe_allow_html=True)
        
        st.write("A wikipedia scraper with AI assistant for interactive learning.")
        
        # Features section with icons
        st.markdown("**Features:**")
        st.markdown("""
        <div style="margin-left: 10px;">
            <div class="step-item"><i class="fas fa-broom"></i>Clean text extraction</div>
            <div class="step-item"><i class="fas fa-comments"></i>AI-powered chat interface</div>
            <div class="step-item"><i class="fas fa-brain"></i>RAG-based question answering</div>
            <div class="step-item"><i class="fas fa-download"></i>Download functionality</div>
        </div>
        """, unsafe_allow_html=True)
        
        # How to use section
        _create_how_to_use_section()

def _create_how_to_use_section():
    """Create the how-to-use section in sidebar"""
    st.markdown(create_icon_header("fas fa-question-circle", "How to Use"), unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-left: 10px;">
        <div class="step-item"><i class="fas fa-edit"></i>Enter a Wikipedia page name</div>
        <div class="step-item"><i class="fas fa-mouse-pointer"></i>Click 'Scrape Page'</div>
        <div class="step-item"><i class="fas fa-robot"></i>Wait for AI setup completion</div>
        <div class="step-item"><i class="fas fa-comments"></i>Ask questions about the content</div>
        <div class="step-item"><i class="fas fa-file-download"></i>Download the text file</div>
    </div>
    """, unsafe_allow_html=True)
