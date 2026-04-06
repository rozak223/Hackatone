# SYNCHAIN AI - Practical Usage Examples

This file contains practical, ready-to-run examples for different use cases.

---

## Example 1: Minimal Prediction (5 lines)

```python
from synchain_advanced import SynChainAI_Advanced

ai = SynChainAI_Advanced()
ai.load_model()
result = ai.get_predictions_with_confidence({'product_id': 5, 'month': 3})
print(f"Prediksi: {result['prediction']:.0f} units")
```

Output:
```
Prediksi: 150 units
```

---

## Example 2: Batch Prediction from CSV

```python
import pandas as pd
from synchain_advanced import SynChainAI_Advanced

# Load model
ai = SynChainAI_Advanced()
ai.load_model()

# Load inventory data
inventory = pd.read_csv('inventory.csv')

# Predict for all products
predictions = []
for _, row in inventory.iterrows():
    pred = ai.get_predictions_with_confidence(row.to_dict())
    predictions.append(pred['prediction'])

# Add to dataframe
inventory['forecast'] = predictions

# Show results
print(inventory[['product_id', 'current_stock', 'forecast']])

# Export
inventory.to_csv('predictions.csv', index=False)
```

---

## Example 3: Restock Analysis

```python
from synchain_advanced import SynChainAI_Advanced
import pandas as pd

ai = SynChainAI_Advanced()
ai.load_model()

# Inventory data
inventory = {
    'product_id': [1, 2, 3, 4, 5],
    'current_stock': [50, 100, 25, 80, 150],
}
df = pd.DataFrame(inventory)

# Get predictions
df['predicted_demand'] = df.apply(
    lambda row: ai._single_prediction({'product_id': row['product_id']}),
    axis=1
)

# Generate recommendations
recommendations = []
for _, row in df.iterrows():
    rec = ai.generate_restock_recommendation(
        current_stock=row['current_stock'],
        predicted_demand=row['predicted_demand'],
        lead_time=7,
        safety_margin=0.2
    )
    recommendations.append({
        'product_id': row['product_id'],
        'action': rec['action'],
        'priority': rec['priority'],
        'restock_qty': rec['restock_quantity']
    })

# Display results
result_df = pd.DataFrame(recommendations)
print(result_df)

# Alert high priority items
alerts = result_df[result_df['priority'] == 'HIGH']
if len(alerts) > 0:
    print(f"\n⚠️  {len(alerts)} products need urgent restock!")
    print(alerts)
```

Output:
```
   product_id           action priority  restock_qty
0           1  RESTOCK NEEDED      HIGH           150
1           2  STOCK SUFFICIENT       LOW             0
2           3  RESTOCK NEEDED     MEDIUM           175
3           4  STOCK SUFFICIENT     MEDIUM             0
4           5  STOCK SUFFICIENT       LOW             0

⚠️  1 products need urgent restock!
   product_id           action priority  restock_qty
0           1  RESTOCK NEEDED      HIGH           150
```

---

## Example 4: Train New Model with Custom Data

```python
import pandas as pd
from synchain_advanced import SynChainAI_Advanced

# Load your data
df = pd.read_csv('sales_data.csv')
print(f"Data shape: {df.shape}")
print(df.head())

# Initialize AI
ai = SynChainAI_Advanced(model_path='my_custom_model.pkl')

# Preprocess
X, y, target_col = ai.preprocess_data(df)
print(f"Preprocessed shape: {X.shape}")

# Train
metrics = ai.train_model(X, y, cv_folds=5)
print(f"Model R² Score: {metrics['r2']:.4f}")

# Show feature importance
print("\nTop Features:")
for feat, score in ai.get_feature_importance(top_n=5):
    print(f"  {feat}: {score:.2f}")

# Save model
ai.save_model()
print("Model saved!")
```

---

## Example 5: Flask REST API

```python
# api_server.py
from flask import Flask, request, jsonify
from synchain_advanced import SynChainAI_Advanced
import pandas as pd

app = Flask(__name__)
ai = SynChainAI_Advanced()
ai.load_model()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'version': '2.0'})

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict demand for a product
    
    POST /predict
    {
        "product_id": 5,
        "category": "Electronics",
        "price": 250,
        "month": 3
    }
    """
    try:
        data = request.json
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
    """
    Get restock recommendation
    
    POST /restock
    {
        "current_stock": 50,
        "predicted_demand": 200,
        "lead_time": 7
    }
    """
    try:
        data = request.json
        rec = ai.generate_restock_recommendation(
            current_stock=data['current_stock'],
            predicted_demand=data['predicted_demand'],
            lead_time=data.get('lead_time', 7),
            safety_margin=data.get('safety_margin', 0.2)
        )
        
        return jsonify({
            'status': 'success',
            'recommendation': rec
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """
    Batch prediction for multiple products
    
    POST /batch-predict
    [
        {"product_id": 1, "category": "A", "price": 100},
        {"product_id": 2, "category": "B", "price": 200}
    ]
    """
    try:
        data = request.json
        results = []
        
        for item in data:
            pred = ai.get_predictions_with_confidence(item)
            results.append({
                'product_id': item.get('product_id'),
                'prediction': pred['prediction']
            })
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

**Usage:**
```bash
# Install Flask
pip install flask

# Run server
python api_server.py

# In another terminal, test endpoints:
curl http://localhost:5000/health

curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"product_id": 5, "category": "Electronics", "price": 250, "month": 3}'
```

---

## Example 6: Scheduled Daily Forecasting

```python
# scheduler.py
import schedule
import time
from datetime import datetime
import pandas as pd
from synchain_advanced import SynChainAI_Advanced
import smtplib
from email.mime.text import MIMEText

ai = SynChainAI_Advanced()
ai.load_model()

def send_alert_email(subject, message):
    """Send email alert"""
    # Configure your email settings
    sender = 'alerts@synchain.ai'
    recipients = ['manager@company.com', 'warehouse@company.com']
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    
    # with smtplib.SMTP('smtp.gmail.com', 587) as server:
    #     server.starttls()
    #     server.login(sender, password)
    #     server.sendmail(sender, recipients, msg.as_string())
    
    print(f"[EMAIL] {subject}")
    print(message)

def daily_forecast_job():
    """Run daily forecast and generate alerts"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*60}")
    print(f"[{timestamp}] Starting daily forecast...")
    
    try:
        # Load inventory
        inventory = pd.read_csv('inventory.csv')
        
        # Generate predictions
        inventory['forecast'] = inventory.apply(
            lambda row: ai._single_prediction(row.to_dict()),
            axis=1
        )
        
        # Get recommendations
        restock_items = []
        for _, row in inventory.iterrows():
            rec = ai.generate_restock_recommendation(
                row['current_stock'],
                row['forecast'],
                lead_time=7
            )
            if rec['action'] == 'RESTOCK NEEDED':
                restock_items.append({
                    'product_id': row['product_id'],
                    'priority': rec['priority'],
                    'qty': rec['restock_quantity']
                })
        
        # Save results
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        inventory.to_csv(f'forecast_{timestamp_str}.csv', index=False)
        
        # Send alerts for high priority items
        high_priority = [r for r in restock_items if r['priority'] == 'HIGH']
        if high_priority:
            alert_msg = f"{len(high_priority)} products need urgent restock:\n\n"
            for item in high_priority:
                alert_msg += f"- Product {item['product_id']}: {item['qty']:.0f} units\n"
            
            send_alert_email(
                f"⚠️ URGENT: {len(high_priority)} items need restock",
                alert_msg
            )
        
        # Summary
        print(f"✅ Forecast complete")
        print(f"   Total items: {len(inventory)}")
        print(f"   Restock needed: {len(restock_items)}")
        print(f"   High priority: {len(high_priority)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        send_alert_email(
            "❌ Forecast Job Failed",
            f"Error: {str(e)}"
        )

# Schedule
print("Scheduler started. Running daily at 8:00 AM...")
schedule.every().day.at("08:00").do(daily_forecast_job)

# Alternative: run every hour for testing
# schedule.every().hour.do(daily_forecast_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Usage:**
```bash
# Install schedule
pip install schedule

# Run scheduler
python scheduler.py
```

---

## Example 7: Data Analysis & Visualization

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from synchain_advanced import SynChainAI_Advanced

# Setup
ai = SynChainAI_Advanced()
ai.load_model()
inventory = pd.read_csv('inventory.csv')

# Add predictions
inventory['forecast'] = inventory.apply(
    lambda row: ai._single_prediction(row.to_dict()),
    axis=1
)

# Calculate metrics
inventory['accuracy_ratio'] = inventory['current_stock'] / inventory['forecast']
inventory['stockout_risk'] = inventory['forecast'] > inventory['current_stock']

# Visualizations
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Forecast vs Current Stock
axes[0, 0].scatter(inventory['current_stock'], inventory['forecast'])
axes[0, 0].set_xlabel('Current Stock')
axes[0, 0].set_ylabel('Forecasted Demand')
axes[0, 0].set_title('Stock vs Forecast')

# 2. Stockout Risk Distribution
axes[0, 1].hist(inventory['accuracy_ratio'], bins=20)
axes[0, 1].set_xlabel('Stock/Forecast Ratio')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].set_title('Inventory Balance')

# 3. Products at Risk
risk_items = inventory[inventory['stockout_risk']]
axes[1, 0].barh(
    range(len(risk_items.head(10))),
    risk_items.head(10)['forecast']
)
axes[1, 0].set_ylabel('Product ID')
axes[1, 0].set_title('Top 10 High-Demand Products (Stockout Risk)')

# 4. Feature Importance
importance = ai.get_feature_importance(top_n=5)
features, scores = zip(*importance)
axes[1, 1].barh(features, scores)
axes[1, 1].set_xlabel('Importance Score')
axes[1, 1].set_title('Top 5 Feature Importance')

plt.tight_layout()
plt.savefig('analysis.png', dpi=300, bbox_inches='tight')
print("Analysis saved to analysis.png")

# Summary statistics
print("\n📊 INVENTORY ANALYSIS SUMMARY")
print("=" * 50)
print(f"Total Products: {len(inventory)}")
print(f"Products at Risk: {len(risk_items)} ({100*len(risk_items)/len(inventory):.1f}%)")
print(f"Average Stock/Forecast Ratio: {inventory['accuracy_ratio'].mean():.2f}")
print(f"Min Ratio: {inventory['accuracy_ratio'].min():.2f}")
print(f"Max Ratio: {inventory['accuracy_ratio'].max():.2f}")
```

---

## Example 8: Integration with Database

```python
# database_integration.py
import sqlite3
import pandas as pd
from synchain_advanced import SynChainAI_Advanced
from datetime import datetime

# Setup
ai = SynChainAI_Advanced()
ai.load_model()

# Connect to database
conn = sqlite3.connect('inventory.db')
c = conn.cursor()

# Create tables if not exist
c.execute('''
    CREATE TABLE IF NOT EXISTS forecasts (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        forecast_value REAL,
        confidence_lower REAL,
        confidence_upper REAL,
        timestamp DATETIME
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        action TEXT,
        restock_qty INTEGER,
        priority TEXT,
        timestamp DATETIME
    )
''')

# Read from database
products = pd.read_sql_query("SELECT * FROM products", conn)

# Generate forecasts
for _, product in products.iterrows():
    result = ai.get_predictions_with_confidence(product.to_dict())
    
    c.execute('''
        INSERT INTO forecasts 
        (product_id, forecast_value, confidence_lower, confidence_upper, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        product['product_id'],
        result['prediction'],
        result['ci_lower'],
        result['ci_upper'],
        datetime.now()
    ))

# Generate recommendations
for _, product in products.iterrows():
    rec = ai.generate_restock_recommendation(
        product['current_stock'],
        result['prediction']  # From above
    )
    
    c.execute('''
        INSERT INTO recommendations
        (product_id, action, restock_qty, priority, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        product['product_id'],
        rec['action'],
        rec['restock_quantity'],
        rec['priority'],
        datetime.now()
    ))

conn.commit()
conn.close()

print("✅ Database updated successfully")
```

---

## Quick Reference: Common Operations

### Load Pre-trained Model
```python
from synchain_advanced import SynChainAI_Advanced
ai = SynChainAI_Advanced()
ai.load_model()
```

### Single Prediction
```python
result = ai.get_predictions_with_confidence({
    'product_id': 5,
    'category': 'Electronics',
    'price': 250
})
print(result['prediction'])
```

### Batch Prediction
```python
predictions = [
    ai._single_prediction(row.to_dict())
    for _, row in df.iterrows()
]
```

### Get Feature Importance
```python
importance = ai.get_feature_importance(top_n=10)
```

### Generate Recommendation
```python
rec = ai.generate_restock_recommendation(
    current_stock=50,
    predicted_demand=200,
    lead_time=7
)
```

### Train New Model
```python
X, y, _ = ai.preprocess_data(df)
metrics = ai.train_model(X, y)
ai.save_model()
```

---

## Performance Tips

1. **Batch predictions** - Process multiple items at once
2. **Cache model** - Load once, reuse
3. **Prune features** - Use only relevant columns
4. **Monitor memory** - For large datasets, process in chunks
5. **Async API** - Use async Flask for concurrent requests

---

**Last Updated:** April 6, 2026  
**Version:** 2.0