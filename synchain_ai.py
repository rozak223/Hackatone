# SYNCHAIN AI - Prediksi Stok dan Intelijen Rantai Pasok untuk UMKM
# Team: Ctrl-Alt-Win
# Universitas Telkom, Bandung 2026

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
import kagglehub
from kagglehub import KaggleDatasetAdapter
import warnings
warnings.filterwarnings('ignore')

class SynChainAI:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None

    def load_data(self):
        """Load dataset dari Kaggle"""
        print("Loading dataset dari Kaggle...")
        try:
            df = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                "itexpertfsdpk/retail-sales-dataset-for-prediction",
                ""
            )
            print("Dataset berhasil dimuat!")
            print(f"Jumlah records: {len(df)}")
            return df
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return None

    def preprocess_data(self, df):
        """Preprocessing data"""
        print("Preprocessing data...")

        # Copy dataframe
        data = df.copy()

        # Handle missing values
        data = data.dropna()

        # Convert date columns if any
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            data['year'] = data['date'].dt.year
            data['month'] = data['date'].dt.month
            data['day'] = data['date'].dt.day
            data['day_of_week'] = data['date'].dt.dayofweek

        # Encode categorical variables
        categorical_cols = data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in ['date']:  # Skip date if exists
                le = LabelEncoder()
                data[col] = le.fit_transform(data[col])
                self.label_encoders[col] = le

        # Assume target is 'quantity' or 'sales' - adjust based on dataset
        target_cols = ['quantity', 'sales', 'total', 'amount']
        target_col = None
        for col in target_cols:
            if col in data.columns:
                target_col = col
                break

        if target_col is None:
            # If no standard target, use the last numeric column
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            target_col = numeric_cols[-1]

        print(f"Target column: {target_col}")

        # Features and target
        X = data.drop(target_col, axis=1)
        if 'date' in X.columns:
            X = X.drop('date', axis=1)
        y = data[target_col]

        # Store feature columns
        self.feature_columns = X.columns.tolist()

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        return X_scaled, y, target_col

    def train_model(self, X, y):
        """Train XGBoost model"""
        print("Training XGBoost model...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        X_val, X_test, y_val, y_test = train_test_split(X_test, y_test, test_size=0.5, random_state=42)

        # XGBoost parameters
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
        self.model.fit(X_train, y_train,
                      eval_set=[(X_train, y_train), (X_val, y_val)],
                      early_stopping_rounds=10,
                      verbose=False)

        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"MAE: {mae:.2f}")
        print(f"MSE: {mse:.2f}")
        print(f"R²: {r2:.2f}")
        return mae, mse, r2

    def predict_stock(self, input_data):
        """Predict stock demand"""
        if self.model is None:
            raise ValueError("Model belum ditraining!")

        # Prepare input data
        input_df = pd.DataFrame([input_data])

        # Encode categorical
        for col, le in self.label_encoders.items():
            if col in input_df.columns:
                if input_df[col].iloc[0] not in le.classes_:
                    # Handle unseen categories
                    input_df[col] = le.transform([le.classes_[0]])[0]
                else:
                    input_df[col] = le.transform(input_df[col])

        # Ensure all feature columns are present
        for col in self.feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0  # Default value

        input_df = input_df[self.feature_columns]

        # Scale
        input_scaled = self.scaler.transform(input_df)

        # Predict
        prediction = self.model.predict(input_scaled)[0]

        return prediction

    def get_feature_importance(self):
        """Get feature importance"""
        if self.model is None:
            return None

        importance = self.model.get_booster().get_score(importance_type='gain')
        return sorted(importance.items(), key=lambda x: x[1], reverse=True)

    def plot_feature_importance(self):
        """Plot feature importance"""
        if self.model is None:
            return

        importance = self.get_feature_importance()
        if not importance:
            return

        features, scores = zip(*importance[:10])  # Top 10

        plt.figure(figsize=(10, 6))
        sns.barplot(x=list(scores), y=list(features))
        plt.title('Top 10 Feature Importance')
        plt.xlabel('Gain')
        plt.tight_layout()
        plt.savefig('feature_importance.png')
        plt.show()

def main():
    print("🚀 SYNCHAIN AI - Prediksi Stok untuk UMKM")
    print("=" * 50)

    # Initialize AI
    ai = SynChainAI()

    # Load data
    df = ai.load_data()
    if df is None:
        return

    print("\nDataset Info:")
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Preprocess
    X, y, target = ai.preprocess_data(df)

    # Train model
    mae, mse, r2 = ai.train_model(X, y)

    # Feature importance
    print("\nTop 5 Feature Importance:")
    importance = ai.get_feature_importance()
    if importance:
        for feat, score in importance[:5]:
            print(".4f")

    # Example prediction
    print("\n" + "="*50)
    print("Contoh Prediksi:")

    # Create sample input based on dataset
    sample_input = {}
    for col in ai.feature_columns[:5]:  # Use first 5 features
        if col in df.columns:
            sample_input[col] = df[col].iloc[0]  # Use first row as example

    try:
        prediction = ai.predict_stock(sample_input)
        print(f"Prediksi permintaan: {prediction:.2f}")
    except Exception as e:
        print(f"Error in prediction: {e}")

    print("\n✅ SYNCHAIN AI siap digunakan!")

if __name__ == "__main__":
    main()
