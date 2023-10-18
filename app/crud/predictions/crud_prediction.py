from app.crud.base import CRUDBase
from app.models.predictions.prediction import Prediction
from app.schemas.predictions.prediction import PredictionCreate, PredictionUpdate


class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    ...

prediction = CRUDPrediction(Prediction)