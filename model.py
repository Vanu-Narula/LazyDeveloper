from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create the engine to connect to the SQLite database
# engine = create_engine('sqlite:///database.db', echo=False)  # Replace with your database file path

# Create a base class for declarative models
Base = declarative_base()

# Define model classes representing the tables in the database
class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_name = Column(String, unique=True)
    parent_topic_id = Column(Integer)
    is_linkedin_scanned_skill = Column(Boolean)

    def to_dict(self):
        return {
            'id': self.id,
            'topic_name': self.topic_name,
            'parent_topic_id': self.parent_topic_id,
            'is_linkedin_scanned_skill': self.is_linkedin_scanned_skill
        }

class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String)

class ArticleTitle(Base):
    __tablename__ = 'article_title'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer)
    article_title = Column(String)
    is_approved = Column(Boolean)
    is_publish = Column(Boolean)

class ArticleContent(Base):
    __tablename__ = 'article_content'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer)
    content = Column(String)
    is_approved = Column(Boolean)
    is_publish = Column(Boolean)

# Create the tables in the database, if they don't exist
# Base.metadata.create_all(engine)

# Create a session to interact with the database
# Session = sessionmaker(bind=engine)
# session = Session()

# Perform CRUD operations using the session and model classes
# ...

# Example CRUD operations:
# Create
# new_topic = Topic(topic_name='Python', parent_topic_id=None, is_linkedin_scanned_skill=True)
# session.add(new_topic)
# session.commit()

# Read
# topics = session.query(Topic).all()
# for topic in topics:
#     print(topic.id, topic.topic_name)

# Update
# topic_to_update = session.query(Topic).filter_by(id=1).first()
# topic_to_update.is_linkedin_scanned_skill = False
# session.commit()

# Delete
# topic_to_delete = session.query(Topic).filter_by(id=1).first()
# session.delete(topic_to_delete)
# session.commit()

# Close the session
# session.close()
