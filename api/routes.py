from fastapi import APIRouter, FastAPI, status

from config import settings


api_router = APIRouter()

@api_router.post(response_model=None, status_code=status.HTTP_200_OK)
def predict_trip_duration():
    """This endpoint is used for predicting the trip
    duration in minutes.
    """