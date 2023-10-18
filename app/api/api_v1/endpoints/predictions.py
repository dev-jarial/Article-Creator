from fastapi import APIRouter, Depends, UploadFile
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api import deps

from app import crud
from app.core.config import settings
from app.schemas.predictions.prediction import PredictionCreate

from app.models.predictions.prediction import Prediction, File
from datetime import datetime

from app.lib.tools.handler.handle_tool_worker import get_tool_worker

import json

from app.db.session import SessionLocal


router = APIRouter()

# Create a Predictions
@router.post("/", status_code=200)
def create(prediction: PredictionCreate, db: Session = Depends(deps.get_db), api_key: APIKey = Depends(deps.get_api_key)):
    db_prediction = Prediction(
        status = 'starting',
        inputs = prediction.inputs,
        starting_at = datetime.now(),
        tool = prediction.tool,
        created_at = prediction.created_at,
        updated_at = prediction.updated_at
    )
    if prediction.files != None:
        db_files = []
        for f in prediction.files:
            db_files.append(
                            File(
                                file_url = f.file_url,
                                params = f.params,
                                prediction = db_prediction
                            )
                        )   
        db.add_all([db_prediction, *db_files])
    else:
        db.add_all([db_prediction])
    db.commit()
    db.refresh(db_prediction)
    
    pred = db_prediction.__dict__
    pred["inputs"] = json.dumps(pred.get('inputs'))
    pred["name"] = prediction.tool
    pred["id"] = pred.get('id')

    
    parsed_dict = db_prediction.__dict__
    parsed_dict["id"] = pred.get('id')

    # Tool Worker to Mimic
    print(db_prediction.__dict__)
    tw = get_tool_worker(db_prediction.__dict__)
    # Need to Rework here...
    # As I am considering to make all of the resources to progress state

    dbt = SessionLocal()
    sql = "UPDATE predictions SET status = 'processing' WHERE id = '{0}' ".format(pred.get('id'))
    dbt.execute(text(sql))
    dbt.commit()
    

    # Apply
    status = tw.apply()
    
    if status is not None and status["success"] == True:
        # update output url and get latest one
        json_files = status['files']

        id = pred['id']
        dbt = SessionLocal()

        sql = "UPDATE predictions SET status = 'succeeded', outputs = '{0}' WHERE id = '{1}' ".format(json_files, pred.get('id'))
        dbt.execute(text(sql))
        dbt.commit()

        # Refetched

        query = dbt.query(Prediction)
        query = query.filter(Prediction.id == id)
        u_prediction = query.first()
        dbt.close()
        # db.refresh(u_prediction)
        return u_prediction
    
    # Refetched Data
    query = dbt.query(Prediction)
    query = query.filter(Prediction.id == pred['id'])
    db_prediction = query.first()
    dbt.close()
    return db_prediction


@router.get('/{prediction_id}', status_code=200)
def get_prediction(prediction_id: str, db: Session = Depends(deps.get_db), api_key: APIKey = Depends(deps.get_api_key)):
# def get_prediction(prediction_id: str, db: Session = Depends(deps.get_db)):
    query = db.query(Prediction)
    query = query.filter(Prediction.id == prediction_id)

    prediction = query.first()

    return prediction
