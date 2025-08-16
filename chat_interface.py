"""
Chat interface functionality for the Wikipedia AI app
"""
import streamlit as st
from langchain_rag import populate_vector_store, setup_rag_chain
from styling import create_icon_header


def display_chat_message(role, content):
    """Display a chat message with proper styling"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user">
            <div class="avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant">
            <div class="avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)


def initialize_chat_session():
    """Initialize chat-related session state variables"""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = None
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None


def setup_chat_system(text_content, page_name):
    """Setup the RAG system for chat functionality"""
    try:
        with st.spinner("Setting up AI chat system..."):
            # Just clear the chain, keep vector store for reuse
            st.session_state.qa_chain = None  
            
            # This will reuse cached data if topic exists
            vector_store = populate_vector_store(text_content, page_name)
            qa_chain = setup_rag_chain(vector_store)
            
            # Store in session state
            st.session_state.vector_store = vector_store
            st.session_state.qa_chain = qa_chain
            
        st.success("AI Chat system ready!")
        return True
    except Exception as e:
        st.error(f"Error setting up chat system: {str(e)}")
        return False


def handle_chat_interaction():
    """Handle the chat interface and interactions"""
    st.markdown(create_icon_header("fas fa-comments", "Chat with Wikipedia Content"), unsafe_allow_html=True)
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            display_chat_message(message["role"], message["content"])
    
    # Chat input
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_question = st.text_input(
            "Ask a question about the content:",
            placeholder="e.g., What are the main points? Who is mentioned?",
            key="chat_input",
            label_visibility="visible"
        )
    
    with col2:
        st.markdown('<p style="margin-bottom: 0.5rem; font-size: 0.875rem; color: white;">Send:</p>', unsafe_allow_html=True)
        send_clicked = st.button("🚀 Ask", type="primary", use_container_width=True)
    
    # Handle sending message
    if send_clicked and user_question.strip():
        st.session_state.chat_messages.append({
            "role": "user", 
            "content": user_question
        })
        
        with st.spinner("🤖 AI is thinking..."):
            try:
                result = st.session_state.qa_chain.invoke({"query": user_question})
                ai_response = result["result"]
                
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "content": ai_response
                })
                
                # Rerun to update the display
                st.rerun()
                
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "content": error_message
                })
                st.rerun()
    
    elif send_clicked and not user_question.strip():
        st.warning("⚠️ Please enter a question before sending!")

    # Clear chat button
    if st.session_state.chat_messages:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_messages = []
            st.rerun()