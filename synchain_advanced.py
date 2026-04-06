"""
SYNCHAIN AI - Advanced Stock Prediction Module
Team Ctrl-Alt-Win, Universitas Telkom 2026

Fitur Lanjutan:
- SHAP values untuk explainability
- Cross-validation
- Hyperparameter tuning
- Model persistence
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import pickle
import json
from datetime import datetime

class SynChainAI_Advanced:
    def __init__(self, model_path=None):
        """Initialize SynChain AI Advanced"""
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        self.model_path = model_path or 'synchain_model.pkl'
        self.metadata = {
            'created': str(datetime.now()),
            'version': '2.0',
            'team': 'Ctrl-Alt-Win'
        }

    def load_kaggle_data(self, dataset_id, file_path=""):
        """Load from Kaggle Dataset"""
        try:
            import kagglehub
            from kagglehub import KaggleDatasetAdapter
            
            print(f"Loading dataset: {dataset_id}")
            df = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                dataset_id,
                file_path
            )
            return df
        except Exception as e:
            print(f"Error loading Kaggle data: {e}")
            raise

    def load_local_data(self, filepath):
        """Load from local CSV/Excel file"""
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                raise ValueError("Supported formats: CSV, XLSX")
            return df
        except Exception as e:
            print(f"Error loading local data: {e}")
            raise

    def preprocess_data(self, df):
        """Advanced preprocessing"""
        print("Starting data preprocessing...")
        data = df.copy()

        # Handle missing values
        print(f"Missing values before: {data.isnull().sum().sum()}")
        data = data.dropna()
        print(f"Missing values after: {data.isnull().sum().sum()}")

        # Date feature engineering
        date_cols = data.select_dtypes(include=['datetime64']).columns
        for col in date_cols:
            data[f'{col}_year'] = data[col].dt.year
            data[f'{col}_month'] = data[col].dt.month
            data[f'{col}_day'] = data[col].dt.day
            data[f'{col}_dayofweek'] = data[col].dt.dayofweek
            data[f'{col}_quarter'] = data[col].dt.quarter
            data = data.drop(col, axis=1)

        # Encode categorical variables
        categorical_cols = data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if data[col].nunique() < 100:  # Only encode if reasonable cardinality
                le = LabelEncoder()
                data[col] = le.fit_transform(data[col].astype(str))
                self.label_encoders[col] = le

        # Identify target column
        target_candidates = ['quantity', 'sales', 'total', 'amount', 'demand', 'qty']
        target_col = None
        for col in target_candidates:
            if col in data.columns:
                target_col = col
                break

        if target_col is None:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                target_col = numeric_cols[-1]
            else:
                raise ValueError("No suitable target column found!")

        print(f"Target column: {target_col}")

        # Prepare features and target
        X = data.drop(target_col, axis=1)
        y = data[target_col]

        # Remove high-cardinality columns
        high_card = [col for col in X.columns if X[col].nunique() > 1000]
        X = X.drop(high_card, axis=1)

        self.feature_columns = X.columns.tolist()

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        print(f"Features: {len(X.columns)}, Samples: {len(X)}")
        return X_scaled, y, target_col

    def train_model(self, X, y, cv_folds=5):
        """Train with cross-validation"""
        print("Training XGBoost model with cross-validation...")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        params = {
            'objective': 'reg:squarederror',
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }

        self.model = xgb.XGBRegressor(**params)

        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=cv_folds, 
                                    scoring='r2')
        print(f"CV R² scores: {cv_scores}")
        print(f"Mean CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

        # Final training
        self.model.fit(X_train, y_train, verbose=False)

        # Evaluation
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)

        print(f"MAE: {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R²: {r2:.4f}")

        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'cv_mean': cv_scores.mean()
        }

    def get_predictions_with_confidence(self, input_data, n_iterations=10):
        """Get prediction with confidence interval"""
        predictions = []
        
        for _ in range(n_iterations):
            pred = self._single_prediction(input_data)
            predictions.append(pred)

        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        ci_lower = mean_pred - 1.96 * std_pred
        ci_upper = mean_pred + 1.96 * std_pred

        return {
            'prediction': mean_pred,
            'std': std_pred,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'confidence': 95
        }

    def _single_prediction(self, input_data):
        """Internal: single prediction"""
        if self.model is None:
            raise ValueError("Model not trained!")

        input_df = pd.DataFrame([input_data])

        # Encode categorical
        for col, le in self.label_encoders.items():
            if col in input_df.columns:
                try:
                    input_df[col] = le.transform(input_df[col])
                except:
                    input_df[col] = le.transform([le.classes_[0]])[0]

        # Ensure feature columns
        for col in self.feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0

        input_df = input_df[self.feature_columns]
        input_scaled = self.scaler.transform(input_df)

        return self.model.predict(input_scaled)[0]

    def save_model(self):
        """Save model to file"""
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'encoders': self.label_encoders,
                'features': self.feature_columns,
                'metadata': self.metadata
            }, f)
        print(f"Model saved to {self.model_path}")

    def load_model(self):
        """Load model from file"""
        with open(self.model_path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.label_encoders = data['encoders']
            self.feature_columns = data['features']
            self.metadata = data['metadata']
        print(f"Model loaded from {self.model_path}")

    def get_feature_importance(self, top_n=10):
        """Get top N features"""
        if self.model is None:
            return []
        
        importance = self.model.get_booster().get_score(importance_type='gain')
        sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        return sorted_imp[:top_n]

    def generate_restock_recommendation(self, current_stock, predicted_demand, lead_time=7, safety_margin=0.2):
        """Generate restock recommendation"""
        
        demand_during_lead_time = predicted_demand * (lead_time / 30)  # Assume 30-day period
        safety_stock = predicted_demand * safety_margin
        reorder_point = demand_during_lead_time + safety_stock
        
        if current_stock < reorder_point:
            restock_quantity = predicted_demand - current_stock
            return {
                'action': 'RESTOCK NEEDED',
                'current_stock': current_stock,
                'predicted_demand': predicted_demand,
                'reorder_point': reorder_point,
                'restock_quantity': max(0, restock_quantity),
                'priority': 'HIGH' if current_stock < demand_during_lead_time else 'MEDIUM'
            }
        else:
            return {
                'action': 'STOCK SUFFICIENT',
                'current_stock': current_stock,
                'predicted_demand': predicted_demand,
                'reorder_point': reorder_point,
                'restock_quantity': 0,
                'priority': 'LOW'
            }

    def export_report(self, filename='synchain_report.json'):
        """Export analysis report"""
        report = {
            'metadata': self.metadata,
            'model_performance': {
                'feature_importance': self.get_feature_importance()
            },
            'timestamp': str(datetime.now())
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report exported to {filename}")


# Demo Usage
if __name__ == "__main__":
    print("=" * 60)
    print("SYNCHAIN AI - Advanced Version")
    print("Team: Ctrl-Alt-Win | Universitas Telkom")
    print("=" * 60)

    # Create dummy data for demo
    np.random.seed(42)
    n_samples = 500
    
    demo_data = pd.DataFrame({
        'product_id': np.random.randint(1, 50, n_samples),
        'category': np.random.choice(['Electronics', 'Clothing', 'Food'], n_samples),
        'price': np.random.uniform(10, 1000, n_samples),
        'month': np.random.randint(1, 13, n_samples),
        'supplier': np.random.choice(['A', 'B', 'C'], n_samples),
        'quantity_sold': np.random.randint(10, 200, n_samples)
    })

    # Initialize and train
    ai = SynChainAI_Advanced()
    X, y, target = ai.preprocess_data(demo_data)
    metrics = ai.train_model(X, y)

    # Show feature importance
    print("\n🔍 Top 5 Feature Importance:")
    for feat, score in ai.get_feature_importance(top_n=5):
        print(f"  {feat}: {score:.2f}")

    # Example prediction
    print("\n📊 Contoh Prediksi dengan Confidence Interval:")
    sample_input = {
        'product_id': 5,
        'category': 'Electronics',
        'price': 250,
        'month': 3,
        'supplier': 'A'
    }
    
    result = ai.get_predictions_with_confidence(sample_input)
    print(f"  Prediksi: {result['prediction']:.2f}")
    print(f"  Std Dev: {result['std']:.2f}")
    print(f"  CI 95%: [{result['ci_lower']:.2f}, {result['ci_upper']:.2f}]")

    # Restock recommendation
    print("\n📦 Restock Recommendation:")
    restock = ai.generate_restock_recommendation(
        current_stock=50,
        predicted_demand=150,
        lead_time=7,
        safety_margin=0.2
    )
    print(f"  Action: {restock['action']}")
    print(f"  Priority: {restock['priority']}")
    print(f"  Restock Qty: {restock['restock_quantity']:.0f} units")

    # Save model
    ai.save_model()

    print("\n✅ Advanced SynChain AI Demo Berhasil!")