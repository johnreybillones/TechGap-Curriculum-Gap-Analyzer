from fastapi import APIRouter, HTTPException, Depends
from typing_extensions import Annotated
from typing import Literal, Union, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm import Session
import json
from app.database import SessionLocal
from app.models import MatchResult, Embedding
from model.model_runtime import run_inference

router = APIRouter(tags=["Predict"])  # main.py applies /predict

EXPECTED_FEATURES = 384
MODEL_TYPES = Literal["nb", "siamese"]
DEFAULT_MODEL_TYPE: MODEL_TYPES = "siamese"


class PredictIn(BaseModel):
    model_type: MODEL_TYPES = DEFAULT_MODEL_TYPE
    text: Optional[str] = None
    features: Annotated[
        Optional[List[float]],
        Field(default=None, min_length=EXPECTED_FEATURES, max_length=EXPECTED_FEATURES),
    ] = None

    @field_validator("features")
    @classmethod
    def _check_len(cls, v):
        if v is not None and len(v) != EXPECTED_FEATURES:
            raise ValueError(f"features must have length {EXPECTED_FEATURES}")
        return v

    @model_validator(mode="after")
    def _check_required(self):
        if self.model_type == "nb":
            if not self.text or not self.text.strip():
                raise ValueError("text is required when model_type is 'nb'")
        elif self.features is None:
            raise ValueError("features are required when model_type is 'siamese'")
        return self


class PredictAndSaveIn(PredictIn):
    curriculum_id: int
    job_id: Optional[int] = None
    model_name: Optional[str] = None
    save_embedding: bool = False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", summary="Run model inference")
def predict(payload: PredictIn):
    try:
        result = run_inference(
            payload.model_type, text=payload.text, features=payload.features
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}")
    return result


@router.post("/save", summary="Run inference, store MatchResult, optionally store embedding")
def predict_and_save(payload: PredictAndSaveIn, db: Session = Depends(get_db)):
    try:
        result = run_inference(
            payload.model_type, text=payload.text, features=payload.features
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}")

    if "score" not in result:
        raise HTTPException(status_code=500, detail="Inference did not return a score")

    score = float(result["score"])
    model_label = payload.model_name or payload.model_type

    match_row = MatchResult(
        curriculum_id=payload.curriculum_id,
        job_id=payload.job_id,
        score=score,
        rank_small=1,
        model=model_label,
    )
    db.add(match_row)

    if payload.save_embedding:
        embedding_vector = result.get("embedding")
        if embedding_vector is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Selected model does not produce an embedding to save; "
                    "disable save_embedding or use the siamese model."
                ),
            )

        # We currently always save embeddings under the curriculum owner
        embedding_row = Embedding(
            owner_type="curriculum",  # must be 'curriculum' | 'job_role' | 'skill'
            owner_id=payload.curriculum_id,
            model=model_label,
            embedding_json=json.dumps(embedding_vector),
            vector_dim=len(embedding_vector),
        )
        db.add(embedding_row)

    db.commit()
    db.refresh(match_row)
    return {"match_result": match_row, "inference": result}
