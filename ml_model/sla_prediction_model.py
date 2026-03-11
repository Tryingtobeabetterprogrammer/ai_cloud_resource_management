import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os

class SLAViolationPredictor:
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'requests', 'servers', 'capacity', 'response_time', 
            'cpu_usage', 'memory_usage', 'network_io', 'disk_io',
            'task_priority', 'cost_per_hour', 'uptime_percentage'
        ]
        
    def load_data(self, data_path):
        """Load and preprocess the enhanced dataset"""
        data = pd.read_csv(data_path)
        
        # Feature engineering
        data['utilization'] = data['requests'] / data['capacity']
        data['server_efficiency'] = data['requests'] / data['servers']
        data['cost_efficiency'] = data['requests'] / data['cost_per_hour']
        
        # Add engineered features to feature list
        self.feature_columns.extend(['utilization', 'server_efficiency', 'cost_efficiency'])
        
        X = data[self.feature_columns]
        y = data['sla_violation']
        
        return X, y
    
    def train_model(self, data_path):
        """Train the SLA violation prediction model"""
        print("Loading and preprocessing data...")
        X, y = self.load_data(data_path)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print("Training Random Forest model...")
        # Use Random Forest for better performance on classification
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        print(feature_importance)
        
        return accuracy
    
    def predict_sla_violation(self, input_data):
        """Predict SLA violation for new data"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Ensure input has all required features
        if isinstance(input_data, dict):
            # Convert dict to DataFrame and add engineered features
            df = pd.DataFrame([input_data])
            df['utilization'] = df['requests'] / df['capacity']
            df['server_efficiency'] = df['requests'] / df['servers']
            df['cost_efficiency'] = df['requests'] / df['cost_per_hour']
            input_data = df[self.feature_columns]
        
        prediction = self.model.predict(input_data)
        probability = self.model.predict_proba(input_data)
        
        return {
            'sla_violation': int(prediction[0]),
            'violation_probability': float(probability[0][1]),
            'normal_probability': float(probability[0][0])
        }
    
    def save_model(self, model_path):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'feature_columns': self.feature_columns
        }, model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path):
        """Load a pre-trained model"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        data = joblib.load(model_path)
        self.model = data['model']
        self.feature_columns = data['feature_columns']
        print(f"Model loaded from {model_path}")

# Training function
def train_sla_model():
    """Train and save the SLA violation prediction model"""
    predictor = SLAViolationPredictor()
    
    # Train the model
    accuracy = predictor.train_model("data/enhanced_server_data.csv")
    
    # Save the model
    predictor.save_model("ml_model/sla_violation_model.pkl")
    
    return predictor, accuracy

if __name__ == "__main__":
    predictor, accuracy = train_sla_model()
    print(f"\nSLA Violation Prediction Model trained with accuracy: {accuracy:.4f}")
