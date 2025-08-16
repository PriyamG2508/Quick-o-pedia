"""
Handles the scraping functionality and user input
"""
import streamlit as st
from scraper import scrape_wikipedia
from styling import create_icon_header
from chat_interface import setup_chat_system


def create_scraping_interface():
    """Create the Wikipedia page input interface"""
    st.markdown(create_icon_header("fas fa-search", "Enter Wikipedia Page"), unsafe_allow_html=True)
    
    # Create adjacent input and button using columns
    col1, col2 = st.columns([4, 1])
    
    with col1:
        page_name = st.text_input(
            "Topic:",
            placeholder="e.g., Artificial Intelligence, Python programming language",
            help="Enter the page name as it appears in Wikipedia",
            label_visibility="visible"
        )
    
    with col2:
        # Add label spacing to align with input
        st.markdown('<p style="margin-bottom: 0.5rem; font-size: 0.875rem; color: white;">Action:</p>', unsafe_allow_html=True)
        scrape_clicked = st.button("Scrape Page", type="primary", use_container_width=True)
    
    return page_name, scrape_clicked


def handle_scraping(page_name, scrape_clicked):
    """Handle the scraping process and setup"""
    if scrape_clicked:
        if page_name:
            # Show loading spinner
            with st.spinner(f"🔄 Scraping Wikipedia page: {page_name}..."):
                text_content = scrape_wikipedia(page_name)
            
            if text_content is None:
                st.error(f"❌ Error: Could not find or scrape the page '{page_name}'. Please check the page name and try again.")
                return False
            else:
                st.success(f"✅ Successfully scraped: {page_name}")
                
                # Store in session state
                st.session_state.current_content = text_content
                st.session_state.current_page = page_name
                st.session_state.show_results = True
                
                # Setup chat system
                chat_ready = setup_chat_system(text_content, page_name)
                if chat_ready:
                    # Clear previous chat history for new topic
                    st.session_state.chat_messages = []
                    # Add welcome message
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": f"Hi! I've analyzed the Wikipedia page about '{page_name}'. Feel free to ask me any questions about the content!"
                    })
                
                return True
        else:
            st.warning("⚠️ Please enter a Wikipedia page name")
            return False
    
    return False


def check_and_display_results():
    """Check if results should be displayed and return content if available"""
    if hasattr(st.session_state, 'show_results') and st.session_state.show_results:
        if hasattr(st.session_state, 'current_content') and st.session_state.current_content:
            return st.session_state.current_content, st.session_state.current_page
    
    return None, None