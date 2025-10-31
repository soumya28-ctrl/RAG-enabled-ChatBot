import os
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from typing import List


class YouTubeRAG:
    def __init__(self, openai_api_key: str = None):
        """Initialize the RAG system with OpenAI API key"""
        # Hardcoded API key - replace with your actual key
        if openai_api_key is None:
            openai_api_key = "use-your-own-openai-api-key"
        
        self.openai_api_key = openai_api_key
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.vectorstore = None
        self.qa_chain = None
        self.video_title = None

    def extract_video_id(self, youtube_url: str) -> str:
        """Extract video ID from YouTube URL"""
        try:
            parsed_url = urlparse(youtube_url)
            if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
                if parsed_url.path == '/watch':
                    return parse_qs(parsed_url.query)['v'][0]
                elif parsed_url.path.startswith('/embed/'):
                    return parsed_url.path.split('/')[2]
                elif parsed_url.path.startswith('/v/'):
                    return parsed_url.path.split('/')[2]
            elif parsed_url.hostname == 'youtu.be':
                return parsed_url.path[1:]
            raise ValueError("Invalid YouTube URL format")
        except Exception as e:
            raise Exception(f"Could not extract video ID: {str(e)}")

    def load_youtube_transcript(self, youtube_url: str) -> List[Document]:
        """Load transcript from YouTube video"""
        try:
            video_id = self.extract_video_id(youtube_url)
            
            # Try the NEW API first (version 1.0.0+)
            try:
                ytt_api = YouTubeTranscriptApi()
                fetched_transcript = ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
                
                # Extract text from FetchedTranscript object
                full_text = " ".join([snippet.text for snippet in fetched_transcript.snippets])
                
            except AttributeError:
                # Fallback to OLD API (version 0.x)
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
                full_text = " ".join([entry['text'] for entry in transcript_data])
            
            if not full_text.strip():
                raise Exception("Transcript is empty")
            
            # Create a Document object (LangChain format)
            document = Document(
                page_content=full_text,
                metadata={
                    "source": youtube_url,
                    "video_id": video_id
                }
            )
            
            return [document]
        except Exception as e:
            raise Exception(f"Error loading YouTube transcript: {str(e)}. Make sure the video has captions enabled.")

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into manageable chunks"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_documents(documents)

    def create_vectorstore(self, chunks: List[Document]):
        """Create InMemoryVectorStore from chunks"""
        embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key,
            model="text-embedding-3-small"
        )
        
        # Use InMemoryVectorStore (works with Python 3.13)
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings
        )
        return self.vectorstore

    def format_docs(self, docs: List[Document]) -> str:
        """Format retrieved documents into a single string"""
        return "\n\n".join(doc.page_content for doc in docs)

    def setup_qa_chain(self):
        """Create a RAG QA chain using LCEL"""
        if not self.vectorstore:
            raise Exception("Vectorstore not created yet. Process video first.")

        # Create retriever
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )

        # Prompt template
        template = """You are a helpful assistant that answers questions about YouTube videos based on their transcripts.

Use the following context from the video transcript to answer the question accurately and concisely.
If the answer is not in the context, politely say you don't have that information from the video.

Context from video:
{context}

Question: {question}

Answer:"""

        prompt = ChatPromptTemplate.from_template(template)

        # LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            api_key=self.openai_api_key
        )

        # Build chain using LCEL
        self.qa_chain = (
            {
                "context": retriever | self.format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        return self.qa_chain

    def process_youtube_video(self, youtube_url: str) -> str:
        """End-to-end processing pipeline"""
        try:
            # Load transcript
            docs = self.load_youtube_transcript(youtube_url)
            
            # Split into chunks
            chunks = self.split_documents(docs)
            
            if len(chunks) == 0:
                raise Exception("No content to process from video")
            
            # Create vectorstore
            self.create_vectorstore(chunks)
            
            # Setup QA chain
            self.setup_qa_chain()
            
            return f"✅ Video processed successfully! Total chunks: {len(chunks)}"
        except Exception as e:
            raise Exception(f"Processing failed: {str(e)}")

    def ask_question(self, question: str) -> dict:
        """Ask a question about the processed video"""
        if not self.qa_chain:
            raise Exception("QA chain not ready. Please process a video first.")
        
        if not question or not question.strip():
            raise Exception("Please enter a valid question.")
        
        try:
            answer = self.qa_chain.invoke(question)
            return {"answer": answer}
        except Exception as e:
            raise Exception(f"Error generating answer: {str(e)}")


if __name__ == "__main__":
    # Test the RAG system
    rag = YouTubeRAG()
    link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(rag.process_youtube_video(link))
    print(rag.ask_question("What is the main topic of the video?"))