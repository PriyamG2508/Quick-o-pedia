import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

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

def create_stat_card(icon_class, value, label):
    """Create a stat card with icon"""
    return f"""
    <div class="stat-card">
        <i class="{icon_class}"></i>
        <h3>{value}</h3>
        <p>{label}</p>
    </div>
    """

def scrape_wikipedia_page(page_name):
    """
    Scrape Wikipedia page and return cleaned text
    
    Args:
        page_name (str): Name of the Wikipedia page
        
    Returns:
        tuple: (text_content, error_message)
    """
    try:
        # Format the page name for URL
        formatted_name = page_name.replace(' ', '_')
        url = f"https://en.wikipedia.org/wiki/{formatted_name}"
        
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Make the request
        response = requests.get(url, headers=headers)
        
        # Check if page exists
        if response.status_code == 404:
            return None, "Page not found. Please check the page name."
        
        if response.status_code != 200:
            return None, f"Error: Status code {response.status_code}"
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from paragraphs
        text_content = ""
        for paragraph in soup.find_all('p'):
            text_content += paragraph.get_text() + "\n"
        
        # Clean the text
        text_content = clean_text(text_content)
        
        return text_content, None
        
    except requests.RequestException as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def clean_text(text):
    """Clean and format the scraped text"""
    # Remove citation numbers [1], [2], etc.
    text = re.sub(r'\[\d+\]', '', text)
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def get_text_stats(text):
    """Calculate statistics for the text"""
    if not text:
        return {}
    
    stats = {
        'characters': len(text),
        'words': len(text.split()),
        'paragraphs': len([p for p in text.split('\n\n') if p.strip()]),
        'sentences': len([s for s in text.split('.') if s.strip()])
    }
    
    return stats

def main():
    # Page configuration with Font Awesome favicon
    st.set_page_config(
        page_title="Quick o Pedia",
        page_icon="📚",
        layout="wide"
    )
    
    # Add Font Awesome favicon
    st.markdown("""
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 448 512'><path fill='%23ffffff' d='M96 0C43 0 0 43 0 96V416c0 53 43 96 96 96H384h32c17.7 0 32-14.3 32-32s-14.3-32-32-32V384c17.7 0 32-14.3 32-32V32c0-17.7-14.3-32-32-32H384 96zm0 384H352v64H96c-17.7 0-32-14.3-32-32s14.3-32 32-32zm32-240c0-8.8 7.2-16 16-16H336c8.8 0 16 7.2 16 16s-7.2 16-16 16H144c-8.8 0-16-7.2-16-16zm16 48H336c8.8 0 16 7.2 16 16s-7.2 16-16 16H144c-8.8 0-16-7.2-16-16s7.2-16 16-16z'/></svg>">
    """, unsafe_allow_html=True)
    
    # Apply dark theme
    apply_dark_theme()
    
    # Header with icon
    st.markdown("""
    <div class="icon-header">
        <i class="fas fa-book-open"></i>
        <h1>Quick o Pedia</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p><i class="fas fa-download"></i> Extract and download clean text from any Wikipedia page</p>', 
                unsafe_allow_html=True)
    
    # Sidebar with info
    with st.sidebar:
        st.markdown(create_icon_header("fas fa-info-circle", "About"), unsafe_allow_html=True)
        
        st.write("This app scrapes Wikipedia pages and extracts clean text content.")
        
        # Features section with icons
        st.markdown("**Features:**")
        st.markdown("""
        <div style="margin-left: 10px;">
            <div class="step-item"><i class="fas fa-broom"></i>Clean text extraction</div>
            <div class="step-item"><i class="fas fa-chart-bar"></i>Text statistics</div>
            <div class="step-item"><i class="fas fa-download"></i>Download functionality</div>
            <div class="step-item"><i class="fas fa-shield-alt"></i>Error handling</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(create_icon_header("fas fa-question-circle", "How to Use"), unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-left: 10px;">
            <div class="step-item"><i class="fas fa-edit"></i>Enter a Wikipedia page name</div>
            <div class="step-item"><i class="fas fa-mouse-pointer"></i>Click 'Scrape Page'</div>
            <div class="step-item"><i class="fas fa-eye"></i>View statistics and content</div>
            <div class="step-item"><i class="fas fa-file-download"></i>Download the text file</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Input section
    st.markdown(create_icon_header("fas fa-search", "Enter Wikipedia Page"), unsafe_allow_html=True)
    
    # Create adjacent input and button using columns
    col1, col2 = st.columns([4, 1])
    
    with col1:
        page_name = st.text_input(
            "Page Name:",
            placeholder="e.g., Artificial Intelligence, Python programming language",
            help="Enter the page name as it appears in Wikipedia",
            label_visibility="visible"
        )
    
    with col2:
        # Add label spacing to align with input
        st.markdown('<p style="margin-bottom: 0.5rem; font-size: 0.875rem; color: white;">Action:</p>', unsafe_allow_html=True)
        scrape_clicked = st.button("🔍 Scrape Page", type="primary", use_container_width=True)
    
    # Handle scraping
    if scrape_clicked:
        if page_name:
            # Show loading spinner
            with st.spinner(f"🔄 Scraping Wikipedia page: {page_name}..."):
                text_content, error = scrape_wikipedia_page(page_name)
            
            if error:
                st.error(f"{error}")
            else:
                st.success(f"✅ Successfully scraped: {page_name}")
                
                # Store in session state
                st.session_state.current_content = text_content
                st.session_state.current_page = page_name
                st.session_state.show_results = True
                
        else:
            st.warning("⚠️ Please enter a Wikipedia page name")
    
    # Show results if available in session state
    if hasattr(st.session_state, 'show_results') and st.session_state.show_results:
        if hasattr(st.session_state, 'current_content') and st.session_state.current_content:
            text_content = st.session_state.current_content
            page_name = st.session_state.current_page
            
            # Statistics section with icons
            st.markdown(create_icon_header("fas fa-chart-line", "Text Statistics"), unsafe_allow_html=True)
            
            # Get statistics
            stats = get_text_stats(text_content)
            
            # Display stats in columns with custom cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(create_stat_card("fas fa-font", f"{stats['characters']:,}", "Characters"), 
                           unsafe_allow_html=True)
            with col2:
                st.markdown(create_stat_card("fas fa-align-left", f"{stats['words']:,}", "Words"), 
                           unsafe_allow_html=True)
            with col3:
                st.markdown(create_stat_card("fas fa-paragraph", str(stats['paragraphs']), "Paragraphs"), 
                           unsafe_allow_html=True)
            with col4:
                st.markdown(create_stat_card("fas fa-list-ol", str(stats['sentences']), "Sentences"), 
                           unsafe_allow_html=True)
            
            # Text preview options
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
            
            # Download section
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

if __name__ == "__main__":
    main()
