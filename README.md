# Bloc_5
## Industrialisation d'un algorithme d'apprentissage automatique et automatisation des processus de décision.

## Vidéo:
[LIEN VIDEO DE PRESENTATION](https://share.vidyard.com/watch/nhd9YyZH4vu7t8A29bKyxg?)

-------------

![image](https://user-images.githubusercontent.com/115455973/222815123-3a30e9ee-7a2e-413a-b1f0-ee8d4f3b21d1.png)

GetAround is the Airbnb for cars. You can rent cars from any person for a few hours to a few days! Founded in 2009, this company has known rapid growth. In 2019, they count over 5 million users and about 20K available cars worldwide.


## Scope of the Project 🚧

When renting a car, users have to complete a checkin flow at the beginning of the rental and a checkout flow at the end of the rental in order to:

    Assess the state of the car and notify other parties of pre-existing damages or damages that occurred during the rental.
    Compare fuel levels.
    Measure how many kilometers were driven.

The checkin and checkout of rentals can be done with three distinct flows:

    📱 Mobile rental agreement on native apps: driver and owner meet and both sign the rental agreement on the owner’s smartphone
    Connect: the driver doesn’t meet the owner and opens the car with his smartphone
    📝 Paper contract (negligible)

For this project we had to:

- Create a streamlit dashboard to help staff people to find the threshold of time delta between twe rentals
- Study price dataset to create a machine learning model to predict the optimal price for a vehicle
- Create an API to get the price prediction for a specific car


## MLFLOW

Here is the mlflow url: https://getaroundprojet.herokuapp.com

In this folder you'll find everything regarding the prediction model and the mlflow tracking server:
secrets.sh+Dockerfile + requirements.txt + run.sh
You'll have to put your credentials in the secrets.sh
commands:
    To save your envirnoment variables: ./secrets.sh
    To build the image: docker build . -t getaroundprojet
    To run the image: ./run.sh (this file will also run app.py)

To deploy on heroku: you'll have to feed your variables on heroku postgresql and follow the commands:
    heroku login
    heroku container:login
    heroku create getaroundprojet
    heroku container:push web -a getaroundprojet
    heroku container:release web -a getaroundprojet

The app.py will lunch the model on mlflow trackin and save the experiment, parameters and metrics

## API

The API url: https://getaround-api-f.herokuapp.com/docs

You have to follow the same steps than before for the image

On heroku, no need to add other variables

To deploy change the name of the app by the name of the API, here, getaround-api-f 

You can request the API using the file: test._pred.ipynb you

predict image is the result of the API request

## Dashboard Streamlit

Here is the url: https://getaround-dashboard-f.herokuapp.com/

Please notice that the file config.toml is to add on a folder .streamlit

You have to build the image using the following command: docker build . -t getaround-stream
And run the command: docker run -it -v "$(pwd):/home/app" -e PORT=80 -p 4000:80 getaround-stream

To deply, it's the same steps, just change the app name, for example here: getaround-dashboard-f
