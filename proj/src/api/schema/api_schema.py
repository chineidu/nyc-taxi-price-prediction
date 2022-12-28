import typing as tp

from pydantic import BaseModel

from src.config.schema import InputSchema


class InputDataSchema(BaseModel):
    """
    Config object for input data.
    """

    inputs: tp.List[InputSchema]

    class Config:
        """Sample Payload"""

        schema_extra = {
            "example": {
                "inputs": [
                    {
                        "DOLocationID": 122,
                        "payment_type": 1,
                        "PULocationID": 236,
                        "RatecodeID": 1.0,
                        "total_amount": 12.36,
                        "tpep_pickup_datetime": "2022-02-01 10:15:17",
                        "trip_distance": 3.17,
                        "VendorID": 2,
                    }
                ]
            }
        }


class ResponsePredictSchema(BaseModel):
    """This schema validates the prediction response."""

    trip_duration: tp.Optional[tp.List[float]]
    model_version: tp.Optional[str]
    errors: tp.Optional[tp.Any]


class APIDetails(BaseModel):
    """This validates the API details"""

    project_name: str
    api_version: str
    model_version: str
