import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

# load dataset
data = pd.read_csv("data/server_data.csv")

# input feature
X = data[["requests"]]

# target
y = data["servers"]

# split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# create model
model = LinearRegression()

# train model
model.fit(X_train, y_train)

# save model
joblib.dump(model, "ml_model/server_scaling_model.pkl")

print("Model trained successfully!")