from app.database import engine, Base
from app import models as models

Base.metadata.create_all(bind=engine)
print("Tables Created")