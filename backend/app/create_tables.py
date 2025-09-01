from app.db import Base, engine
import backend.app.models.models
 # This single import executes the __init__.py and loads all models

def create_database_tables():
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    create_database_tables()