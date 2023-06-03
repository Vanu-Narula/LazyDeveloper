import os
from dotenv import load_dotenv
import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper
from langchain.callbacks import get_openai_callback

def generator():
    load_dotenv()

    # App framework
    st.set_page_config(page_title="🦜🔗 Article generator using OpenAI")
    st.header("🦜🔗 Article generator using OpenAI")
    prompt = st.text_input('Plug in your topic here')

    title_template = PromptTemplate(
        input_variables= ['topic'],
        template='Your are expert tutorial title writer, write a short and catchy title about {topic}. The title should represent '
    )

    article_template = PromptTemplate(
        input_variables= ['title', 'wiki_research'],
        template='Your are expert tutorial writer, write an article in form of a detailed tutorial which includes extensive \
            code examples and image urls (if required) for blog on the title {title}. Use this wikipedia research while \
                writing the article, RESEARCH: {wiki_research}'
    )

    # Memory
    title_memory = ConversationBufferMemory(input_key='topic', memory_key='chat_history')
    article_memory = ConversationBufferMemory(input_key='title', memory_key='chat_history')

    #LLM
    llm = OpenAI(temperature=0.9, model_name="gpt-3.5-turbo", max_tokens=2500)
    title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True, output_key='title', memory=title_memory)
    article_chain = LLMChain(llm=llm, prompt=article_template, verbose=True, output_key='article', memory=article_memory)
    
    # sequential_chain = SequentialChain(chains=[title_chain, article_chain], \
    #                     input_variables=['topic'], output_variables=['title', 'article'], verbose=True)

    wiki = WikipediaAPIWrapper()

    # Show st
    if prompt:
        with get_openai_callback() as cb:
            title = title_chain.run(prompt)
            wiki_research = wiki.run(prompt)
            article = article_chain.run(title=title, wiki_research= wiki_research)
            with st.expander('LLM Call Usage'):
                    st.info(cb)
        title = "Title: " + title

        st.write(title)
        st.write(article)

        with st.expander('Title history'):
            st.info(title_memory.buffer)

        with st.expander('Article history'):
            st.info(article_memory.buffer)

        with st.expander('Wikipedia Research'):
            st.info(wiki_research)
