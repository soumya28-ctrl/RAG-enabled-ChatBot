import streamlit as st
from youtube_rag import YouTubeRAG
import traceback

# Set up Streamlit page config
st.set_page_config(page_title="🎥 YouTube RAG Chatbot", layout="wide")

# Initialize session state if not already initialized
if "rag" not in st.session_state:
    # Initialize RAG with API key from youtube_rag.py (it has a default hardcoded key)
    st.session_state.rag = YouTubeRAG()
if "processed" not in st.session_state:
    st.session_state.processed = False
if "chat" not in st.session_state:
    st.session_state.chat = []
if "current_video" not in st.session_state:
    st.session_state.current_video = None

# Display title and description
st.title("🎥 YouTube Video RAG Chatbot")
st.markdown("Ask questions about any YouTube video using AI-powered retrieval!")

# Sidebar for YouTube URL input
with st.sidebar:
    st.header("⚙️ Settings")
    link = st.text_input("📺 YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("🔄 Process Video"):
        if not link:
            st.error("Please paste a YouTube link!")
        else:
            try:
                with st.spinner("Processing video... please wait"):
                    # Process the video and store the result
                    msg = st.session_state.rag.process_youtube_video(link)
                    st.session_state.processed = True
                    st.session_state.current_video = link
                    # Clear chat history when processing new video
                    st.session_state.chat = []
                    st.success(msg)
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("Show detailed error"):
                    st.code(traceback.format_exc())

    # Add reset button
    if st.session_state.processed:
        if st.button("🗑️ Clear & Start New"):
            st.session_state.processed = False
            st.session_state.chat = []
            st.session_state.current_video = None
            st.session_state.rag = YouTubeRAG()  # Reset RAG instance
            st.rerun()

# Show chat interface if video is processed
if st.session_state.processed:
    st.subheader("💬 Chat about the video")
    
    # Display current video info
    if st.session_state.current_video:
        st.info(f"📹 Currently chatting about: {st.session_state.current_video}")
    
    # Display previous chat history
    for idx, chat in enumerate(st.session_state.chat):
        with st.container():
            st.markdown(f"**🙋 You:** {chat['q']}")
            st.markdown(f"**🤖 Assistant:** {chat['a']}")
            st.divider()

    # Question input - using form to handle Enter key properly
    with st.form(key="question_form", clear_on_submit=True):
        q = st.text_input("Ask a question", placeholder="What is this video about?", key="question_input")
        submit_button = st.form_submit_button("🚀 Ask")
        
        if submit_button and q:
            try:
                with st.spinner("Thinking..."):
                    # Get the answer from the RAG system
                    res = st.session_state.rag.ask_question(q)
                    st.session_state.chat.append({"q": q, "a": res['answer']})
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("Show detailed error"):
                    st.code(traceback.format_exc())
else:
    st.info("👈 Enter a YouTube link in the sidebar and click 'Process Video' to begin.")
    
    # Show helpful tips
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Paste a YouTube URL** in the sidebar (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
        2. **Click "Process Video"** to analyze the video transcript
        3. **Ask questions** about the video in natural language
        4. The AI will answer based on the video's content!
        
        **Note:** The video must have captions/transcript available.
        """)