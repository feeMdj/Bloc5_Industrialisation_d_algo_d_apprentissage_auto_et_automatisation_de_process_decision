#!/usr/bin/env python
import mlflow
import uvicorn
import json
import pandas as pd
import numpy as np
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
from joblib import load
import os

mlflow.set_tracking_uri("https://getaroundprojet.herokuapp.com/")


description = """
Welcome to our getaround API.
Use it to predict the optimal price of your vehicle rental.

# Introduction Endpoints

* Use '/'  for a 'get' request to display the default page
* Use '/predict'  for a 'post' request to call the machine learning app to get the optimal price for your car
"""

# tags meta data definition
tags_metadata = [
    {
        "name": "Introduction Endpoints",
        "description": "Simple endpoints to try the API!"
    },
    {
        "name": "Machine Learning",
        "description": "Prediction price"
    }
]

app = FastAPI(
    title="🚗 getaround Pricing",
    description=description,
    version="0.1",
    contact={
        "name": "🚗 getaround Pricing",
        "url": "https://getaroundprojet.herokuapp.com/",
    },
    openapi_tags=tags_metadata
)

class PredictionFeatures(BaseModel):
    model_key: str = "Citroën"
    mileage: int = 90401
    engine_power: int = 135
    fuel: str = "diesel"
    paint_color: str = "grey"
    car_type: str = "convertible"
    private_parking_available: bool = True
    has_gps: bool = True
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = True
    has_speed_regulator: bool = True
    winter_tires: bool = True


@app.get("/", tags=["Introduction Endpoint"])
async def root():

    """
    Simply returns a welcome message!
    """

    message = "Welcome to the getaround pricing API `/` is the most simple endpoint for the API, for more informations please check the documentation using `/docs`"

    return message

@app.post("/predict", tags = ["Machine Learning"])
async def predict(predictionFeatures: PredictionFeatures):
  
    # Read data 
    df_vehicle = pd.DataFrame(dict(predictionFeatures), index=[0])

    # Log model from mlflow 
    logged_model ='runs:/5e31d4926cc7417eb8e94625f25b66b4/getaround_price_prediction'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(df_vehicle)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)

    