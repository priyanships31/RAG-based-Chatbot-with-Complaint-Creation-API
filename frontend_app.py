import streamlit as st
import requests
import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

# Disable unnecessary logging
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["DISABLE_LANGCHAIN_TELEMETRY"] = "true"

def load_rag():
    loader = PyPDFLoader("customer_service_knowledgebase.pdf")
    docs = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="chroma_db"
    )
    return vectordb.as_retriever()

llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")

# Streamlit UI
st.title("🗣️ Customer Complaint Assistant")

# Initialize session state
if "complaint_data" not in st.session_state:
    st.session_state.complaint_data = {
        "name": None,
        "phone": None,
        "email": None,
        "details": None,
        "awaiting_field": None
    }

if "in_complaint_flow" not in st.session_state:
    st.session_state.in_complaint_flow = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("How can I help you today?")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    reply = ""

    # Complaint triggers
    complaint_triggers = [
        "file complaint", "new complaint", "make complaint",
        "raise complaint", "complain about", "report issue",
        "issue with", "problem with", "delayed delivery",
        "wrong item", "received damaged", "not delivered",
        "want to file", "file a complaint", "damaged product",
        "defective", "broken", "poor service", "bad experience",
        "refund", "return", "exchange", "billing issue",
        "overcharged", "charged twice", "wrong charge",
        "missing item", "incomplete order", "late delivery",
        "rude staff", "customer service", "quality issue"
    ]

    # Check for complaint lookup patterns first (before general RAG)
    complaint_lookup_patterns = [
        r"show.*complaint.*([A-Z]{3}\d{3})",
        r"get.*complaint.*([A-Z]{3}\d{3})",
        r"details.*complaint.*([A-Z]{3}\d{3})",
        r"status.*complaint.*([A-Z]{3}\d{3})",
        r"complaint.*([A-Z]{3}\d{3})",
        r"details.*of.*([A-Z]{3}\d{3})",
        r"^([A-Z]{3}\d{3})$"  # Just the ID alone
    ]
    
    # Check for "show all complaints" or similar
    show_all_patterns = [
        "show all complaint", "get all complaint", "list all complaint",
        "show complaint", "all complaint", "list complaint"
    ]

    # === 1. Complaint Creation Flow ===
    if any(trigger in user_input.lower() for trigger in complaint_triggers) and not st.session_state.in_complaint_flow:
        st.session_state.in_complaint_flow = True
        st.session_state.complaint_data["awaiting_field"] = "name"
        reply = "I'm sorry to hear about your issue. Let me help you file a complaint. Please provide your name."

    elif st.session_state.in_complaint_flow:
        current_field = st.session_state.complaint_data["awaiting_field"]

        if current_field == "name":
            st.session_state.complaint_data["name"] = user_input
            st.session_state.complaint_data["awaiting_field"] = "phone"
            reply = f"Thank you, {user_input}. What is your phone number?"

        elif current_field == "phone":
            if not re.match(r"^\d{10}$", user_input):
                reply = "Please enter a valid 10-digit phone number"
            else:
                st.session_state.complaint_data["phone"] = user_input
                st.session_state.complaint_data["awaiting_field"] = "email"
                reply = "Got it. Please provide your email address."

        elif current_field == "email":
            if not re.match(r"[^@]+@[^@]+\.[^@]+", user_input):
                reply = "Please enter a valid email address"
            else:
                st.session_state.complaint_data["email"] = user_input
                st.session_state.complaint_data["awaiting_field"] = "details"
                reply = "Thanks. Please describe your issue or complaint in detail."

        elif current_field == "details":
            st.session_state.complaint_data["details"] = user_input
            
            try:
                response = requests.post(
                    "http://localhost:8000/complaints",
                    json={
                        "name": st.session_state.complaint_data["name"],
                        "phone_number": st.session_state.complaint_data["phone"],
                        "email": st.session_state.complaint_data["email"],
                        "complaint_details": st.session_state.complaint_data["details"]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    complaint_id = data['complaint_id']
                    # Format the complaint ID display exactly as requested
                    reply = f"✅ Your complaint has been registered successfully!\n\n**Complaint ID: {complaint_id}**\n\nYou'll hear back from us soon. Please save this ID for future reference."
                else:
                    reply = f"❌ Error: {response.text}"
            except Exception as e:
                reply = f"❌ Connection error: {str(e)}"

            # Reset flow
            st.session_state.complaint_data = {
                "name": None, "phone": None,
                "email": None, "details": None,
                "awaiting_field": None
            }
            st.session_state.in_complaint_flow = False

    # === 2. Show All Complaints ===
    elif any(pattern in user_input.lower() for pattern in show_all_patterns):
        try:
            reply = "⛔ You are not authorized to view all complaints."
            response = requests.get("http://localhost:8000/complaints")
            if response.status_code == 200:
                complaints = response.json()
                if complaints:
                    reply = "⛔ You are not authorized to view all complaints."
                    # reply = "📋 **All Complaints:**\n\n"
                    # for complaint in complaints:
                    #     reply += f"**Complaint ID: {complaint['complaint_id']}**\n"
                    #     reply += f"**Name:** {complaint['name']}\n"
                    #     reply += f"**Phone:** {complaint['phone_number']}\n"
                    #     reply += f"**Email:** {complaint['email']}\n"
                    #     reply += f"**Details:** {complaint['complaint_details']}\n"
                    #     reply += f"**Created At:** {complaint['created_at']}\n"
                    #     reply += "---\n"
                else:
                    reply = "⛔ You are not authorized to view all complaints."
                    # reply = "No complaints found."
            else:
                reply = "❌ Error fetching complaints."
        except Exception as e:
            reply = f"❌ Server error: {str(e)}"

    # === 3. Complaint Lookup by ID ===
    elif any(re.search(pattern, user_input, re.IGNORECASE) for pattern in complaint_lookup_patterns):
        # Extract complaint ID
        complaint_id = None
        for pattern in complaint_lookup_patterns:
            match = re.search(pattern, user_input.upper(), re.IGNORECASE)
            if match:
                complaint_id = match.group(1) if match.groups() else match.group(0)
                break
        
        if complaint_id:
            try:
                response = requests.get(f"http://localhost:8000/complaints/{complaint_id}")
                if response.status_code == 200:
                    data = response.json()
                    reply = f"""📋 **Complaint Details:**

**Complaint ID: {data['complaint_id']}**
**Name:** {data['name']}
**Phone:** {data['phone_number']}
**Email:** {data['email']}
**Details:** {data['complaint_details']}
**Created At:** {data['created_at']}"""
                else:
                    reply = "❌ Complaint not found. Please check your ID."
            except Exception as e:
                reply = f"❌ Server error: {str(e)}"
        else:
            reply = "🔍 Please include a valid complaint ID (format: ABC123)"

    # === 4. General Questions (RAG) ===
    else:
        try:
            retriever = load_rag()
            prompt = ChatPromptTemplate.from_template(
                """Answer based on this context:
                {context}
                
                Question: {input}"""
            )
            chain = create_retrieval_chain(
                retriever,
                create_stuff_documents_chain(llm, prompt)
            )
            response = chain.invoke({"input": user_input})
            reply = response["answer"]
        except Exception as e:
            reply = f"❌ Error processing your question: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)