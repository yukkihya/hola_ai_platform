"""
Real LLM-powered RAG Chatbot
Backend function: rag_chatbot_backend
"""
import os
from typing import Dict
#from langchain_community.llms import Ollama
#from langchain_community.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_groq import ChatGroq
from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredURLLoader, PyPDFLoader


from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# Load environment variables
load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY")

'''
# Example KB
docs = [
    Document(page_content="Flask is a Python web framework. It is lightweight and easy to use."),
    Document(page_content="LangChain helps developers build applications with large language models."),
    Document(page_content="CrewAI can orchestrate multiple AI agents to collaborate on a task.")
]

# Create vector store in memory
embeddings = OllamaEmbeddings(model="llama3")
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
split_docs = splitter.split_documents(docs)
vectorstore = FAISS.from_documents(split_docs, embeddings)

# LLM
llm = Ollama(model="llama3")

def rag_chatbot_backend(request) -> Dict:
    context = {}
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if not query:
            context["response"] = "Please enter a question."
            return context

        # Retrieve relevant docs
        matches = vectorstore.similarity_search(query, k=2)
        retrieved_text = "\n".join([m.page_content for m in matches])

        prompt = f"Answer the question based on the following context:\n{retrieved_text}\n\nQuestion: {query}\nAnswer:"
        answer = llm.invoke(prompt)
        context["response"] = answer

    return context
'''


def rag_chatbot_backend(request) -> Dict:

    context = {}
    if request.method == 'POST':
        url_input = request.form.get('url')
        pdf_file = request.files.get('pdf')
        model_selected = request.form.get('model')
        user_prompt = request.form.get('prompt')
        question =  user_prompt
        # Step 1: Load document
        
        documents = []
        if url_input:
            loader = UnstructuredURLLoader(urls=[url_input])
            documents.extend(loader.load())
        elif pdf_file and pdf_file.filename:
            pdf_path = f"/tmp/{pdf_file.filename}"
            pdf_file.save(pdf_path)
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())

        # Step 2: Embed with FAISS


        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)

        embeddings = OllamaEmbeddings(model="nomic-embed-text")  #model=model_selected
        vectorstore = FAISS.from_documents(docs, embeddings)
        print( f"vectorstore {vectorstore}")
        # Step 3: RAG retrieval QA
        llm = OllamaLLM(model=model_selected)
        llm1 = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=150,  # Limiting max tokens for brevity in response
            timeout=10,  # Optional: setting a timeout in case of slow responses
            max_retries=2,
        )
        print( f"llm {llm}")
        '''
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            chain_type="stuff"
        )
        resp = qa.run(user_prompt)
        print(f"resp {resp}")
        context["response"] =  resp
        return context
        '''

        retriever = vectorstore.as_retriever()
    
        #perform the RAG 
        
        after_rag_template = """Figure out the important features or concepts or content from the source provided:
        {context}
        Question: {question}
        """
        after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
        after_rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | after_rag_prompt
            | llm
            | StrOutputParser()
        )
        #return after_rag_chain.invoke(user_prompt) 
        resp = after_rag_chain.invoke(question)
        print(f"resp {resp}")
        context["response"] =  resp
        return context
        