# LazyDeveloper: Content Generator for Developers

LazyDeveloper is a content generation tool designed for developers. Using the power of Streamlit and LangChain, it provides an intuitive interface for users to generate content based on their interests and skills.

## Features:
- **LinkedIn Profile Upload**: Upload your LinkedIn profile and let the application identify your skills.
- **Dynamic Content Generation**: Add topics of interest and generate articles on-the-fly.
- **Manage Topics**: Easily add, delete, or generate subtopics for your main interests.
- **Database Integration**: All your data, including profiles, topics, and articles, are securely stored and easily retrievable.

## Installation:
1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up your environment variables based on `.env.example`.
4. Run the Streamlit application using `streamlit run app.py`.


## For Migrations
source - https://medium.com/@peytonrunyan/alembic-101-897f322c9334

1. Delete the migration directory and run command - alembic init migrations
2. Check alembic.ini, the sqlalchemy.url should point to your SQLite DB file
3. Run command - alembic revision --autogenerate -m "Create database model"
4. Run command - alembic upgrade head