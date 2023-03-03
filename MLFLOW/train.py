import argparse
import pandas as pd
import time
import mlflow
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split 
from sklearn.preprocessing import  StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score
from sklearn.compose import ColumnTransformer
import os, joblib
from pickle import dump
import pickle


if __name__ == "__main__":

    # Set your experiment name
    EXPERIMENT_NAME = "getaround Pricing v5"

    # Set tracking URI to your Heroku application
    mlflow.set_tracking_uri("https://getaroundprojet.herokuapp.com")

    # Set experiment's info 
    mlflow.set_experiment(EXPERIMENT_NAME)

    # Get our experiment info
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

    # Call mlflow autolog
    mlflow.sklearn.autolog()

    with mlflow.start_run(experiment_id=experiment.experiment_id):

        # Import dataset

        DATA_URL_prices = ('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv')
        pricing=pd.read_csv(DATA_URL_prices)
        pricing=pricing.iloc[: , 1:]


        # Separate target variable Y from features X
        target_name = 'rental_price_per_day'  
        y = pricing.loc[:,target_name]  
        X = pricing.drop(target_name, axis = 1) # All columns are kept except the target,

        # Train / test split 
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2,random_state=0)

        # Automatically detect names of numeric/categorical columns
        numeric_features = [1,2]
        categorical_features = [0,3,4,8,6,7,8,9,10,11,12]

        # PreProcessing for numeric features  

        numeric_transformer = StandardScaler()  
        
        # PreProcessing for categorical features  
        categorical_transformer = OneHotEncoder(drop='first', handle_unknown='ignore') # dealing with unknown categories which were not part of our training set

        # for both numeric and categorical features, we don't have any null values, so we don't need to use a Simple Imputer
        
        ### Preprocessor 
        preprocessor = ColumnTransformer(  
            transformers=[  
                ('num', numeric_transformer, numeric_features),  
                ('cat', categorical_transformer, categorical_features)  
            ])

        # Create a regressor model
        regressor = LinearRegression()

        model = Pipeline(steps=[("Preprocessing", preprocessor),
                                ("Regressor", regressor)
                                ]) 
        model.fit(X_train, y_train)

        # Make predictions
        predicted_prices = model.predict(X_train)


        mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="getaround_price_prediction",
                registered_model_name="getaround_price_prediction_LineReg",
                signature=infer_signature(X_train, predicted_prices)
                )

        # if we want to save the model to disk
        #filename = 'getaroundpricing_model.sav'
        #joblib.dump(model, filename)
            

