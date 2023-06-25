import pickle
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.utilities import WikipediaAPIWrapper
from langchain.tools import DuckDuckGoSearchResults
from logging import Logger


class LangChainWrapper:
    def __init__(self):
        load_dotenv()
        self.logger = Logger(name=__name__)

    def get_profile_info(self, text):
        """
        Get profile information using OpenAI Language models.
        """
        try:
            self.logger.info("Getting profile information...")
            
            # Split text into chunks
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=200,
                chunk_overlap=40,
                length_function=len
            )
            chunks = text_splitter.split_text(text)

            # Create embeddings and knowledge base
            embeddings = OpenAIEmbeddings()
            knowledge_base = FAISS.from_texts(chunks, embeddings)

            # Save vectorstore
            with open("vectorstore.pkl", "wb") as f:
                pickle.dump(knowledge_base, f)

            to_be_searched = "What is the name and skills of the person?"
            prompt_query = "Return the full name and skills of the person in JSON format. Don't add any extra sentence, response should be just JSON."

            # Load QA chain and run the query
            chain = load_qa_chain(ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0),
                                 chain_type="stuff")  # we are going to stuff all the docs in at once
            docs = knowledge_base.similarity_search(to_be_searched)
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=prompt_query)

            self.logger.info("Profile information retrieved successfully.")
            return (response, cb)
        except Exception as e:
            self.logger.error("Error occurred while getting profile information.")
            self.logger.exception(str(e))
            return (None, str(e))

    def create_sub_topics(self, topic_name):
        """
        Generate sub-topics for a given topic using OpenAI Language models.
        """
        try:
            self.logger.info("Creating sub-topics...")
            
            output_parser = CommaSeparatedListOutputParser()
            format_instructions = output_parser.get_format_instructions()

            # Define the prompt template for generating sub-topics
            topics_gen_template = PromptTemplate(
                input_variables=['topic_name'],
                template="""Your are expert tutorial writer, write five to ten short sub topics about {topic_name}. Remember
                         the sub topics should be about latest trends and on which tutorial could be further written. \n{format_instructions}
                         """,
                partial_variables={"format_instructions": format_instructions}
            )

            llm = OpenAI(temperature=0.9, model_name="gpt-3.5-turbo", max_tokens=300)
            topic_chain = LLMChain(llm=llm, prompt=topics_gen_template, verbose=True)

            # Run the topic chain to generate sub-topics
            sub_topics = topic_chain.run(topic_name)

            self.logger.info("Sub-topics created successfully.")
            # print(list(output_parser.parse(sub_topics)))
            return list(output_parser.parse(sub_topics))
        except Exception as e:
            self.logger.error("Error occurred while creating sub-topics.")
            self.logger.exception(str(e))
            return str(e)
        

    def article_generator(self, topic):
        """
        Generate article for a given topic, contains two chains: title chain and article chain.
        The title chain will generate the suitable title and then article chain will generate a
        full article on that title.
        """
        title_template = PromptTemplate(
            input_variables= ['topic'],
            template='Your are expert tutorial title writer, write a short and catchy title about {topic}. Title should make readers want to click and read' 
        )

        article_template = PromptTemplate(
            input_variables= ['title', 'wiki_research', 'search_results'],
            template='Your are expert tutorial writer, write an article in form of a detailed tutorial in markdown text which includes extensive \
                code examples, image urls (if required) and subheading for blog on the title {title}. Use this wikipedia research  and search results while \
                    writing the article, RESEARCH: {wiki_research} \nSEARCH RESULTS: {search_results}'
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
        duck=DuckDuckGoSearchResults()

        # Show st
        if topic:
            with get_openai_callback() as cb:
                title = title_chain.run(topic)
                wiki_research = wiki.run(topic)
                duck_search = duck.run(topic)
                article = article_chain.run(title=title, wiki_research= wiki_research, search_results=duck_search)

                return title, article
            #     with st.expander('LLM Call Usage'):
            #             st.info(cb)
            # title = "Title: " + title

            # st.write(title)
            # st.write(article)

            # with st.expander('Title history'):
            #     st.info(title_memory.buffer)

            # with st.expander('Article history'):
            #     st.info(article_memory.buffer)

            # with st.expander('Wikipedia Research'):
            #     st.info(wiki_research)