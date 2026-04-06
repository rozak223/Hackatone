# SYNCHAIN AI - API Documentation & Integration Guide

## 📚 Table of Contents
1. [Quick Start](#quick-start)
2. [API Reference](#api-reference)
3. [Integration Examples](#integration-examples)
4. [n8n Workflow Setup](#n8n-workflow-setup)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Basic Usage
```python
from synchain_advanced import SynChainAI_Advanced
import pandas as pd

# Load data
ai = SynChainAI_Advanced()
df = pd.read_csv('sales_data.csv')

# Train model
X, y, target = ai.preprocess_data(df)
metrics = ai.train_model(X, y)

# Make prediction
result = ai.get_predictions_with_confidence({
    'product_id': 5,
    'category': 'Electronics',
    'price': 250,
    'month': 3
})

print(f"Prediksi: {result['prediction']:.2f}")
```

---

## 🔌 API Reference

### Class: `SynChainAI_Advanced`

#### Constructor
```python
SynChainAI_Advanced(model_path=None)
```

**Parameters:**
- `model_path` (str, optional): Path to save/load model. Default: `'synchain_model.pkl'`

**Example:**
```python
ai = SynChainAI_Advanced(model_path='my_model.pkl')
```

---

### Method: `load_kaggle_data()`

Load dataset from Kaggle API.

```python
def load_kaggle_data(self, dataset_id, file_path="")
```

**Parameters:**
- `dataset_id` (str): Kaggle dataset ID (format: `username/dataset-name`)
- `file_path` (str): Specific file in dataset to load

**Returns:**
- `pd.DataFrame`: Loaded dataset

**Example:**
```python
df = ai.load_kaggle_data(
    "itexpertfsdpk/retail-sales-dataset-for-prediction",
    ""
)
```

**Requirements:**
- Install Kaggle: `pip install kagglehub`
- Setup API key: https://www.kaggle.com/settings/account
- Place `kaggle.json` in `~/.kaggle/`

---

### Method: `load_local_data()`

Load from local CSV or Excel files.

```python
def load_local_data(self, filepath)
```

**Parameters:**
- `filepath` (str): Path to CSV or XLSX file

**Returns:**
- `pd.DataFrame`: Loaded dataset

**Supported Formats:**
- `.csv` - Comma-separated values
- `.xlsx`, `.xls` - Excel spreadsheets

**Example:**
```python
# CSV
df = ai.load_local_data('sales_data.csv')

# Excel
df = ai.load_local_data('inventory.xlsx')
```

---

### Method: `preprocess_data()`

Preprocess and prepare data for training.

```python
def preprocess_data(self, df)
```

**Parameters:**
- `df` (pd.DataFrame): Raw dataset

**Returns:**
- `tuple`: `(X_scaled, y, target_col_name)`
  - `X_scaled`: Scaled feature matrix (numpy array)
  - `y`: Target values (pandas Series)
  - `target_col_name`: Name of target column (str)

**Processing Steps:**
1. Handle missing values (dropna)
2. Feature engineering from date columns
3. Encode categorical variables
4. Identify target column automatically
5. Scale features using StandardScaler

**Example:**
```python
X, y, target = ai.preprocess_data(df)
print(f"Features shape: {X.shape}")
print(f"Target column: {target}")
```

---

### Method: `train_model()`

Train XGBoost model with cross-validation.

```python
def train_model(self, X, y, cv_folds=5)
```

**Parameters:**
- `X` (numpy array): Feature matrix (from preprocess_data)
- `y` (pandas Series): Target values
- `cv_folds` (int): Number of cross-validation folds. Default: 5

**Returns:**
- `dict`: Performance metrics
  ```python
  {
      'mae': float,      # Mean Absolute Error
      'mse': float,      # Mean Squared Error
      'rmse': float,     # Root Mean Squared Error
      'r2': float,       # R² Score (0-1)
      'cv_mean': float   # Mean CV R² Score
  }
  ```

**Example:**
```python
metrics = ai.train_model(X, y, cv_folds=5)
print(f"Model R² Score: {metrics['r2']:.4f}")
print(f"RMSE: {metrics['rmse']:.2f}")
```

---

### Method: `get_predictions_with_confidence()`

Get prediction with 95% confidence interval.

```python
def get_predictions_with_confidence(self, input_data, n_iterations=10)
```

**Parameters:**
- `input_data` (dict): Feature values for prediction
- `n_iterations` (int): Number of iterations for CI calculation. Default: 10

**Returns:**
- `dict`: Prediction with confidence interval
  ```python
  {
      'prediction': float,    # Point estimate
      'std': float,           # Standard deviation
      'ci_lower': float,      # 95% CI lower bound
      'ci_upper': float,      # 95% CI upper bound
      'confidence': int       # Confidence level (95)
  }
  ```

**Example:**
```python
result = ai.get_predictions_with_confidence({
    'product_id': 10,
    'category': 'Electronics',
    'price': 500,
    'month': 6,
    'supplier': 'B'
})

print(f"Prediksi: {result['prediction']:.2f}")
print(f"Range: [{result['ci_lower']:.2f}, {result['ci_upper']:.2f}]")
```

---

### Method: `get_feature_importance()`

Get top N important features.

```python
def get_feature_importance(self, top_n=10)
```

**Parameters:**
- `top_n` (int): Number of top features. Default: 10

**Returns:**
- `list`: List of tuples `(feature_name, importance_score)`

**Example:**
```python
importance = ai.get_feature_importance(top_n=5)
for feat, score in importance:
    print(f"{feat}: {score:.2f}")
```

**Output:**
```
f2: 1904.14
f4: 1559.54
f0: 1497.35
f3: 1481.53
f1: 1080.81
```

---

### Method: `generate_restock_recommendation()`

Generate restock recommendation based on prediction.

```python
def generate_restock_recommendation(self, current_stock, predicted_demand, 
                                    lead_time=7, safety_margin=0.2)
```

**Parameters:**
- `current_stock` (int): Current inventory level
- `predicted_demand` (float): Predicted demand from model
- `lead_time` (int): Lead time in days. Default: 7
- `safety_margin` (float): Safety stock margin (0-1). Default: 0.2

**Returns:**
- `dict`: Restock recommendation
  ```python
  {
      'action': str,              # 'RESTOCK NEEDED' or 'STOCK SUFFICIENT'
      'current_stock': int,
      'predicted_demand': float,
      'reorder_point': float,
      'restock_quantity': int,    # Qty to restock (0 if not needed)
      'priority': str             # 'HIGH', 'MEDIUM', or 'LOW'
  }
  ```

**Example:**
```python
rec = ai.generate_restock_recommendation(
    current_stock=50,
    predicted_demand=200,
    lead_time=7,
    safety_margin=0.2
)

if rec['action'] == 'RESTOCK NEEDED':
    print(f"⚠️ RESTOCK: {rec['restock_quantity']} units")
    print(f"Priority: {rec['priority']}")
```

---

### Method: `save_model()` & `load_model()`

Persist model to disk.

```python
def save_model(self)
def load_model(self)
```

**Example:**
```python
# Save after training
ai.save_model()  # Saves to 'synchain_model.pkl'

# Load later
ai_loaded = SynChainAI_Advanced()
ai_loaded.load_model()  # Loads from 'synchain_model.pkl'

# Make predictions
result = ai_loaded.get_predictions_with_confidence({'product_id': 5})
```

---

## 🔗 Integration Examples

### Example 1: Flask API Server

```python
# app.py
from flask import Flask, request, jsonify
from synchain_advanced import SynChainAI_Advanced

app = Flask(__name__)
ai = SynChainAI_Advanced()
ai.load_model()

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for predictions"""
    data = request.json
    
    try:
        result = ai.get_predictions_with_confidence(data)
        return jsonify({
            'status': 'success',
            'prediction': result['prediction'],
            'confidence_interval': {
                'lower': result['ci_lower'],
                'upper': result['ci_upper']
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/restock', methods=['POST'])
def restock():
    """API endpoint for restock recommendations"""
    data = request.json
    
    recommendation = ai.generate_restock_recommendation(
        current_stock=data['current_stock'],
        predicted_demand=data['predicted_demand'],
        lead_time=data.get('lead_time', 7)
    )
    
    return jsonify({
        'status': 'success',
        'recommendation': recommendation
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

**Usage:**
```bash
python app.py

# In another terminal:
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"product_id": 5, "category": "Electronics", "price": 250}'
```

---

### Example 2: Pandas Integration

```python
# Process entire dataset
import pandas as pd
from synchain_advanced import SynChainAI_Advanced

ai = SynChainAI_Advanced()
ai.load_model()

# Load inventory data
inventory = pd.read_csv('inventory.csv')

# Add predictions
inventory['predicted_demand'] = inventory.apply(
    lambda row: ai._single_prediction(row.to_dict()), axis=1
)

# Add restock recommendations
inventory['restock_needed'] = inventory.apply(
    lambda row: ai.generate_restock_recommendation(
        row['current_stock'], 
        row['predicted_demand']
    )['action'] == 'RESTOCK NEEDED',
    axis=1
)

# Export results
inventory.to_csv('predictions.csv', index=False)
```

---

### Example 3: Scheduled Batch Processing

```python
# batch_process.py
import schedule
import time
from datetime import datetime
from synchain_advanced import SynChainAI_Advanced
import pandas as pd

ai = SynChainAI_Advanced()
ai.load_model()

def daily_forecast():
    """Run forecasting at 8 AM daily"""
    print(f"[{datetime.now()}] Running daily forecast...")
    
    # Load today's data
    df = pd.read_csv('today_sales.csv')
    
    # Generate predictions
    predictions = []
    for _, row in df.iterrows():
        pred = ai.get_predictions_with_confidence(row.to_dict())
        predictions.append(pred['prediction'])
    
    # Save results
    df['forecast'] = predictions
    df.to_csv(f'forecast_{datetime.now().date()}.csv', index=False)
    
    # Send alerts
    alert_count = (df['forecast'] > 500).sum()
    if alert_count > 0:
        print(f"⚠️  {alert_count} items need restock")

# Schedule
schedule.every().day.at("08:00").do(daily_forecast)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 🔄 n8n Workflow Setup

### Prerequisite
- n8n instance running (local or cloud)
- Flask API server (from Example 1)

### Workflow Configuration

**Trigger:** Webhook or Timer

**Step 1: Read Inventory Data**
```
Node Type: SQLite / CSV File Reader
Output: Inventory records
```

**Step 2: Call SynChain AI API**
```
Node Type: HTTP Request
URL: http://localhost:5000/predict
Method: POST
Body: {
  "product_id": "{{ $json.product_id }}",
  "category": "{{ $json.category }}",
  "price": "{{ $json.price }}"
}
```

**Step 3: Generate Alert**
```
Node Type: Condition
IF: prediction > reorder_point
THEN: Send notification
```

**Step 4: Send Email/Slack Alert**
```
Node Type: Email / Slack
Template: 
"⚠️ RESTOCK ALERT
Product: {{ $json.product_id }}
Predicted Demand: {{ $json.prediction }}
Current Stock: {{ $json.current_stock }}"
```

**Step 5: Log to Database**
```
Node Type: SQLite / PostgreSQL
Query: INSERT INTO predictions (product_id, forecast, timestamp)
VALUES (?, ?, NOW())
```

---

## 🔧 Troubleshooting

### Issue 1: "Model not trained"
```python
# ❌ Wrong
result = ai.get_predictions_with_confidence({'product_id': 5})

# ✅ Correct
X, y, _ = ai.preprocess_data(df)
ai.train_model(X, y)
result = ai.get_predictions_with_confidence({'product_id': 5})
```

### Issue 2: Kaggle API error
```bash
# Setup Kaggle API
pip install kagglehub
# Download key from https://www.kaggle.com/settings/account
mkdir ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Issue 3: Memory error with large datasets
```python
# Process in chunks
chunk_size = 10000
chunks = [df[i:i+chunk_size] for i in range(0, len(df), chunk_size)]

for chunk in chunks:
    X, y, _ = ai.preprocess_data(chunk)
    # Process...
    del X, y  # Free memory
```

### Issue 4: Low model accuracy
```python
# Try more data
# Try different hyperparameters:
params = {
    'n_estimators': 200,  # More trees
    'max_depth': 8,       # Deeper trees
    'learning_rate': 0.05 # Lower learning rate
}
```

---

## 📊 Performance Optimization

### Data Size Recommendations
| Data Size | Training Time | Prediction Time |
|-----------|---------------|-----------------|
| < 10K     | < 10s         | < 100ms         |
| 10K-100K  | 10-30s        | 100-200ms       |
| > 100K    | 30s+          | 200ms+          |

### Model Deployment
```python
# Production setup
from flask import Flask
import joblib

app = Flask(__name__)
model = joblib.load('synchain_model.pkl')

# Use pre-loaded model for faster predictions
@app.route('/predict', methods=['POST'])
def predict():
    # < 50ms response time
    ...
```

---

## 📞 Support
- **Email:** contact@ctrl-alt-win.dev
- **Documentation:** https://docs.synchain.ai
- **Issues:** https://github.com/ctrl-alt-win/synchain-ai/issues

---

**Last Updated:** April 6, 2026
**Version:** 2.0