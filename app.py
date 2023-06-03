import json, time
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import langChainWrapper
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
    user_name = db.get_user_name()

    with st.sidebar:
        if user_name is None:
            st.header("🦥 Upload your linkedIn profile")
            with st.form("my-form", clear_on_submit=True):
                pdf = st.file_uploader(" ", type="pdf")
                submitted = st.form_submit_button("UPLOAD!")

            with st.spinner("Loading..."):
                if pdf is not None:
                    text = extract_pdf_text(pdf)
                    response = langChainWrapper.get_profile_info(text)
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

        else:
            st.button("Reset App")
                
    if user_name != "":
        topics = db.get_all_topics()
        st.header("Welcome {}".format(user_name))
        st.subheader("List of Topics")
        st.divider()
        if topics:
            for topic in topics:
                st.info("**{}**".format(topic['topic_name']))
                st.radio("Actions", ["Create Sub topic", "Delete topic", "Generate Article"], horizontal=True, key=topic['topic_name'])
                st.button("Act Upon", key=topic['id'])
                st.divider()


if __name__ == '__main__':
    main()