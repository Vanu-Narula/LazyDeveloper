import json, time
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import langChainHelper
from databaseWrapper import db_wrapper


def extract_pdf_text(pdf):
    combined_text = ''
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        combined_text += page.extract_text()
    return combined_text

def main():
    load_dotenv()
    st.set_page_config(page_title="Content generator for lazy developer",
                       layout='wide',
                        page_icon=':🦥:'
    )
    db = db_wrapper()

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
                response = langChainHelper.get_profile_info(text)
                success = st.success("Done!")
                json_obj = json.loads(response[0])
                user_name = json_obj["name"]
                if user_name:
                    db.add_new_profile(user_name)
                skills = list(json_obj["skills"])
                usage = response[1]
                st.subheader("Skills Identified")
                st.divider()
                if len(skills) > 0:
                    for skill in skills:
                        st.caption(skill)
                    db.add_new_topics(skills)
                    time.sleep(1)
                    success.empty()
                
    if user_name != '':
        st.header("Welcome {}".format(user_name))


if __name__ == '__main__':
    main()