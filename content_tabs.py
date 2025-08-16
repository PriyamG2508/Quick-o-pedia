"""
Content tabs functionality for displaying scraped content
"""
import streamlit as st
from styling import create_icon_header
from chat_interface import handle_chat_interaction


def create_content_tabs(text_content, page_name):
    """Create and handle the main content tabs"""
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📄 Content", "📥 Download"])
    
    with tab1:
        _handle_chat_tab()
    
    with tab2:
        _handle_content_tab(text_content)
    
    with tab3:
        _handle_download_tab(text_content, page_name)


def _handle_chat_tab():
    """Handle the chat tab content"""
    # Chat interface (only show if chat system is ready)
    if hasattr(st.session_state, 'qa_chain') and st.session_state.qa_chain:
        handle_chat_interaction()
    else:
        st.info("🔧 Chat system is being set up. Please wait or refresh the page if this takes too long.")


def _handle_content_tab(text_content):
    """Handle the content preview tab"""
    st.markdown(create_icon_header("fas fa-file-alt", "Text Content"), unsafe_allow_html=True)
    
    # Initialize display option in session state if not exists
    if 'display_option' not in st.session_state:
        st.session_state.display_option = "👀 Preview (first 500 words)"
    
    # Create radio button with icons
    preview_option = st.radio(
        "Choose display option:",
        ["👀 Preview (first 500 words)", "📄 Full text"],
        horizontal=True,
        key='display_option'
    )
    
    # Display text based on option
    if "Preview" in st.session_state.display_option:
        words = text_content.split()
        preview_text = ' '.join(words[:500])
        if len(words) > 500:
            preview_text += "..."
        
        st.text_area(
            "Content Preview:",
            preview_text,
            height=300,
            disabled=True
        )
    else:
        st.text_area(
            "Full Content:",
            text_content,
            height=400,
            disabled=True
        )


def _handle_download_tab(text_content, page_name):
    """Handle the download tab content"""
    st.markdown(create_icon_header("fas fa-cloud-download-alt", "Download Options"), unsafe_allow_html=True)
    
    # Prepare filename
    filename = f"{page_name.replace(' ', '_')}_wikipedia.txt"
    
    # Download button with icon
    st.download_button(
        label="📥 Download Text File",
        data=text_content,
        file_name=filename,
        mime="text/plain",
        help="Download the scraped text as a .txt file"
    )
    
    # Additional info section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 20px;">
        <i class="fas fa-info-circle"></i> 
        Text extracted from Wikipedia and cleaned for your use
    </div>
    """, unsafe_allow_html=True)