from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Embedding
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/embedding", tags=["Embedding"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ SCHEMAS ------------------
class EmbeddingBase(BaseModel):
    owner_type: str
    owner_id: int
    model: str
    vector_dim: int

class EmbeddingCreate(EmbeddingBase):
    embedding_json: str

class EmbeddingOut(EmbeddingBase):
    embedding_json: str

    class Config:
        from_attributes = True

# ------------------ ROUTES ------------------

@router.post("/", response_model=EmbeddingOut)
def create_embedding(data: EmbeddingCreate, db: Session = Depends(get_db)):
    new_embedding = Embedding(**data.dict())
    db.add(new_embedding)
    db.commit()
    db.refresh(new_embedding)
    return new_embedding

@router.get("/", response_model=List[EmbeddingOut])
def get_all_embeddings(db: Session = Depends(get_db)):
    return db.query(Embedding).all()

@router.get("/{embedding_id}", response_model=EmbeddingOut)
def get_embedding(embedding_id: int, db: Session = Depends(get_db)):
    embedding = db.query(Embedding).filter(Embedding.id == embedding_id).first()
    if not embedding:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return embedding

@router.put("/{embedding_id}", response_model=EmbeddingOut)
def update_embedding(embedding_id: int, data: EmbeddingBase, db: Session = Depends(get_db)):
    embedding = db.query(Embedding).filter(Embedding.id == embedding_id).first()
    if not embedding:
        raise HTTPException(status_code=404, detail="Embedding not found")
    for key, value in data.dict().items():
        setattr(embedding, key, value)
    db.commit()
    db.refresh(embedding)
    return embedding

@router.delete("/{embedding_id}")
def delete_embedding(embedding_id: int, db: Session = Depends(get_db)):
    embedding = db.query(Embedding).filter(Embedding.id == embedding_id).first()
    if not embedding:
        raise HTTPException(status_code=404, detail="Embedding not found")
    db.delete(embedding)
    db.commit()
    return {"message": "Embedding deleted successfully"}