from sklearn.linear_model import LinearRegression
import numpy as np

def train_model(historical_data):
    X = np.array(historical_data['features'])
    y = np.array(historical_data['prices'])
    model = LinearRegression().fit(X, y)
    return model

def predict_price(model, current_data):
    prediction = model.predict([current_data])
    return prediction[0]