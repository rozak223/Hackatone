# Demo SynChain AI - Versi Sederhana
# Menggunakan data dummy untuk testing

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb

# Generate dummy data
np.random.seed(42)
n_samples = 1000

data = {
    'product_id': np.random.randint(1, 100, n_samples),
    'category': np.random.choice(['A', 'B', 'C'], n_samples),
    'price': np.random.uniform(10, 500, n_samples),
    'month': np.random.randint(1, 13, n_samples),
    'day_of_week': np.random.randint(0, 7, n_samples),
    'quantity_sold': np.random.randint(1, 50, n_samples)  # Target
}

df = pd.DataFrame(data)

# Encode category
df['category'] = df['category'].map({'A': 0, 'B': 1, 'C': 2})

# Features and target
X = df.drop('quantity_sold', axis=1)
y = df['quantity_sold']

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = xgb.XGBRegressor(n_estimators=50, max_depth=4, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("🚀 SYNCHAIN AI Demo")
print("=" * 30)
print(f"MAE: {mae:.2f}")
print(f"R²: {r2:.2f}")
print("\nContoh Prediksi:")
sample = X.iloc[0:1]  # First row
sample_scaled = scaler.transform(sample)
pred = model.predict(sample_scaled)[0]
print(f"Input: {sample.to_dict('records')[0]}")
print(f"Prediksi: {pred:.2f}")
print("\n✅ Demo berhasil!")