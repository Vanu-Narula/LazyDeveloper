from model import engine, Topic, UserProfile, ArticleTitle, ArticleContent
from sqlalchemy.orm import sessionmaker


class db_wrapper:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def add_new_topics(self, topic_list):
        for topic in topic_list:
            new_topic = Topic(topic_name=topic, parent_topic_id=None, is_linkedin_scanned_skill=True)
            self.session.add(new_topic)
            self.session.commit()

    def add_new_topic(self, topic, parent_topic_id, is_primary):
        new_topic = Topic(topic_name=topic, parent_topic_id=parent_topic_id, is_linkedin_scanned_skill=is_primary)
        self.session.add(new_topic)
        self.session.commit()

    def get_all_topics(self):
        topics = self.session.query(Topic).all()
        if len(topics) > 0:
            topic_dicts = [topic.to_dict() for topic in topics]
            return topic_dicts
        else:
            return None
    
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

    def get_topic_id(self, topic_name):
        topic = self.session.query(Topic).filter_by(topic_name=topic_name).first()
        self.session.close()
        if topic:
            return topic.id
        else:
            return None
    
    def add_new_article_title(self, topic_name, article_title, is_approved, is_publish):
        # get topic_id from get_topic_id function using topic_name
        topic_id = self.get_topic_id(topic_name)
        if topic_id:
            new_article_title = ArticleTitle(topic_id=topic_id, article_title=article_title, is_approved=is_approved, is_publish=is_publish)
            self.session.add(new_article_title)
            self.session.commit()
        self.session.close()

    
