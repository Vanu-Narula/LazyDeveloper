from model import Topic, UserProfile, ArticleTitle, ArticleContent
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, create_engine
from sqlalchemy import func


class db_wrapper:
    def __init__(self, db_path):
        self.engine = create_engine(db_path)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.metadata = MetaData()

    def add_new_topics(self, topic_list, is_primary=True, parent_topic_id=None):
        new_topics = []
        failed_topics = []

        for topic in topic_list:
            result = self.add_new_topic(topic, is_primary, parent_topic_id)
            if result is not None:
                new_topics.append(result)
            else:
                failed_topics.append(topic)

        return new_topics, failed_topics

    def add_new_topic(self, topic, is_primary, parent_topic_id=None):
        new_topic = Topic(topic_name=topic, parent_topic_id=parent_topic_id, is_linkedin_scanned_skill=is_primary)
        try:
            self.session.add(new_topic)
            self.session.commit()
            return new_topic.to_dict()
        except:
            self.session.rollback()
            return None

    def get_all_topics(self):
        topics = self.session.query(Topic).all()
        if len(topics) > 0:
            topic_dicts = [topic.to_dict() for topic in topics]
            return topic_dicts
        else:
            return None
        
    def get_topic_id(self, topic_name):
        topic = self.session.query(Topic).filter_by(topic_name=topic_name).first()
        self.session.close()
        if topic:
            return topic.id
        else:
            return None
        
    def delete_topic(self, topic_id):
        topic = self.session.query(Topic).filter_by(id=topic_id).first()
        if topic:
            self.session.delete(topic)
            self.session.commit()
            return True
        else:
            return False
    
    def get_user_name(self):
        name = self.session.query(UserProfile).first()
        if name:
            return name.user_name
        else:
            return None
    
    def add_new_profile(self, user_name):
        new_profile = UserProfile(user_name=user_name)
        self.session.add(new_profile)
        self.session.commit()
        self.session.close()
    
    def add_new_article_title(self, topic_name, article_title, is_approved, is_publish):
        # get topic_id from get_topic_id function using topic_name
        topic_id = self.get_topic_id(topic_name)
        if topic_id:
            new_article_title = ArticleTitle(topic_id=topic_id, article_title=article_title, is_approved=is_approved, is_publish=is_publish)
            self.session.add(new_article_title)
            self.session.commit()
        self.session.close()

    def reset_database(self):
        self.metadata.reflect(bind=self.engine)

        # with self.session.begin():
        #     for table in reversed(self.metadata.sorted_tables):
        #         self.session.execute(table.delete())

        self.metadata.drop_all(bind=self.engine)
        self.metadata.bind = self.engine
        self.metadata.create_all(bind=self.engine)


    