import pickle
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback


def get_profile_info(text):
    load_dotenv()
    # split into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=200,
        chunk_overlap=40,
        length_function=len
    )
    
    chunks = text_splitter.split_text(text)
    
    # create embeddings
    embeddings = OpenAIEmbeddings()
    knowledge_base = FAISS.from_texts(chunks, embeddings)
    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(knowledge_base, f)

    to_be_searched = "What is the name and skills of the person?"
    prompt_query = "Return the full name and skills of the person in JSON format."
    chain = load_qa_chain(ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0), 
                chain_type="stuff") # we are going to stuff all the docs in at once
    docs = knowledge_base.similarity_search(to_be_searched)
    with get_openai_callback() as cb:
        response = chain.run(input_documents=docs, question=prompt_query)
    return (response, cb)