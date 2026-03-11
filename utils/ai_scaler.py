import joblib
import os

# get project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# build correct path to model
model_path = os.path.join(BASE_DIR, "ml_model", "server_scaling_model.pkl")

# load model
model = joblib.load(model_path)


def predict_servers(requests):

    prediction = model.predict([[requests]])

    servers_needed = round(prediction[0])

    if servers_needed < 1:
        servers_needed = 1

    return servers_needed