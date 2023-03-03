docker run -it\
 -p 4002:4002\
 -v "$(pwd):/home/app"\
 -e MLFLOW_TRACKING_URI="https://getaroundprojet.herokuapp.com"\ 
 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
 -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY\
 -e ARTIFACT_STORE_URI=$ARTIFACT_STORE_URI\
 -e BACKEND_STORE_URI=$BACKEND_STORE_URI \
 getaround-mlflow python train.py
