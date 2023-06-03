import pickle, json, time
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

def extract_pdf_text(pdf):
    combined_text = ''
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        combined_text += page.extract_text()
    return combined_text

def get_profile_info(text):
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

def main():
    load_dotenv()
    st.set_page_config(page_title="Content generator for lazy developer",
                       layout='wide',
                        page_icon=':🦥:'
    )

    st.markdown("""
        <style>
            .css-13sdm1b.e16nr0p33 {
            margin-top: -75px;
            }
        </style>
        """, unsafe_allow_html=True)

    user_name = ''
    skills = []


    with st.sidebar:
        st.header("🦥 Upload your linkedIn profile")
        with st.form("my-form", clear_on_submit=True):
            pdf = st.file_uploader(" ", type="pdf")
            submitted = st.form_submit_button("UPLOAD!")

        with st.spinner("Loading..."):
            if pdf is not None:
                text = extract_pdf_text(pdf)
                response = get_profile_info(text)
                success = st.success("Done!")
                json_obj = json.loads(response[0])
                user_name = json_obj["name"]
                skills = list(json_obj["skills"])
                usage = response[1]
                st.subheader("Skills Identified")
                st.divider()
                for s in skills:
                    st.caption(s)
                time.sleep(1)
                success.empty()

    if user_name != '':
        st.header("Welcome {}".format(user_name))


if __name__ == '__main__':
    main()