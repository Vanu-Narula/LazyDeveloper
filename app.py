import json, time, os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import langChainWrapper
from databaseWrapper import db_wrapper

def add_new_row(row_label):
    new_row = create_new_row(row_label)
    st.session_state.rows.append(new_row)

def create_new_row(label):
    return {
        'label': label,
        'delete': False,
        'write_article': False
    }

def delete_rows(rows, indices):
    return [row for i, row in enumerate(rows) if i not in indices]

def write_article(rows, index):
    if index < len(rows):
        # Call the write_article function in LangChainWrapper class
        # lang_chain_wrapper.write_article(rows[index])
        rows[index]['write_article'] = True

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
    db = db_wrapper(os.environ['SQLite_path'])

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
                        time.sleep(2)
                        success.empty()
                        st.experimental_rerun()

        else:
            reset = st.button("Reset App")
            if reset:
                # Truncate all tables
                db.reset_database()
                st.experimental_rerun()
                
    if user_name is not None:
        topics = db.get_all_topics()
        st.header("Welcome {}".format(user_name))

        if 'rows' not in st.session_state:
            st.session_state.rows = []

        if 'topic_added' not in st.session_state:
            st.session_state.topic_added = False

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Your interests")
        with col2:
            user_topic_name = st.text_input(label="Add topic to list", placeholder="Topic name")
            if user_topic_name is not None and user_topic_name != "":
                new_topic = db.add_new_topic(user_topic_name, False)
                add_new_row(new_topic)
        if topics and not st.session_state.topic_added:
            for topic in topics:
                add_new_row(topic)
                st.session_state.topic_added = True

        # Display rows
        for i, row in enumerate(st.session_state.rows):
            st.divider()
            st.info(row['label']['topic_name'])
            
            delete_button_key = f"delete_{i}"
            write_button_key = f"write_{i}"
            
            delete_button_col, write_button_col = st.columns([1, 1])
            if delete_button_col.button(f"Delete Row", key=delete_button_key):
                st.session_state.rows = delete_rows(st.session_state.rows, [i])
                st.experimental_rerun()
                
            if write_button_col.button("Write Article", key=write_button_key):
                write_article(st.session_state.rows, i)


if __name__ == '__main__':
    main()