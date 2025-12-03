from database import engine, Base
import models as models

Base.metadata.create_all(bind=engine)
print("Tables Created")