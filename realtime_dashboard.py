"""
SYNCHAIN AI - Real-time Stock Monitoring Dashboard
Live stock tracking dengan prediksi AI dan alerts otomatis
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from synchain_advanced import SynChainAI_Advanced
import pandas as pd
import json
import threading
import time
from datetime import datetime
from queue import Queue
import sqlite3

app = Flask(__name__)
CORS(app)

# Initialize AI
ai = SynChainAI_Advanced()
ai.load_model()

# Real-time data store
inventory_data = {}
alerts_queue = Queue()

def initialize_database():
    """Initialize SQLite database for stock tracking"""
    conn = sqlite3.connect('realtime_stock.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_levels (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            product_name TEXT,
            current_stock INTEGER,
            forecast_demand REAL,
            timestamp DATETIME
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            alert_type TEXT,
            message TEXT,
            priority TEXT,
            timestamp DATETIME,
            acknowledged INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def get_real_time_prediction(product_data):
    """Get real-time prediction for a product"""
    try:
        result = ai.get_predictions_with_confidence(product_data)
        
        # Get restock recommendation
        rec = ai.generate_restock_recommendation(
            current_stock=product_data.get('current_stock', 0),
            predicted_demand=result['prediction'],
            lead_time=7
        )
        
        return {
            'prediction': result['prediction'],
            'confidence_lower': result['ci_lower'],
            'confidence_upper': result['ci_upper'],
            'action': rec['action'],
            'priority': rec['priority'],
            'restock_qty': rec['restock_quantity']
        }
    except Exception as e:
        return None

def monitor_stock_levels():
    """Background thread to monitor stock levels"""
    while True:
        try:
            for product_id, product_data in inventory_data.items():
                # Get prediction
                pred = get_real_time_prediction(product_data)
                
                if pred:
                    # Update with prediction
                    inventory_data[product_id]['forecast'] = pred['prediction']
                    inventory_data[product_id]['restock_needed'] = pred['action'] == 'RESTOCK NEEDED'
                    inventory_data[product_id]['priority'] = pred['priority']
                    inventory_data[product_id]['last_update'] = datetime.now().isoformat()
                    
                    # Generate alert if needed
                    if pred['action'] == 'RESTOCK NEEDED':
                        alert = {
                            'product_id': product_id,
                            'product_name': product_data.get('name', f'Product {product_id}'),
                            'alert_type': 'RESTOCK_NEEDED',
                            'priority': pred['priority'],
                            'message': f"Product {product_data.get('name')} needs restock: {pred['restock_qty']:.0f} units",
                            'timestamp': datetime.now().isoformat(),
                            'current_stock': product_data['stock'],
                            'forecast': pred['prediction']
                        }
                        alerts_queue.put(alert)
                    
                    # Save to database
                    save_stock_update(product_id, product_data, pred['prediction'])
            
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            print(f"Error in monitoring: {e}")
            time.sleep(5)

def save_stock_update(product_id, product_data, forecast):
    """Save stock update to database"""
    try:
        conn = sqlite3.connect('realtime_stock.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO stock_levels 
            (product_id, product_name, current_stock, forecast_demand, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            product_id,
            product_data.get('name', f'Product {product_id}'),
            product_data['stock'],
            forecast,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving stock update: {e}")

# ==================== API ENDPOINTS ====================

@app.route('/api/inventory/add', methods=['POST'])
def add_product():
    """Add product to monitoring"""
    data = request.json
    product_id = data.get('product_id')
    
    inventory_data[product_id] = {
        'id': product_id,
        'name': data.get('name', f'Product {product_id}'),
        'stock': data.get('stock', 0),
        'category': data.get('category', 'Unknown'),
        'price': data.get('price', 0),
        'forecast': 0,
        'restock_needed': False,
        'priority': 'LOW',
        'last_update': datetime.now().isoformat()
    }
    
    return jsonify({
        'status': 'success',
        'message': f'Product {product_id} added to monitoring'
    })

@app.route('/api/inventory/update/<int:product_id>', methods=['POST'])
def update_stock(product_id):
    """Update current stock level (real-time input)"""
    data = request.json
    new_stock = data.get('stock')
    
    if product_id not in inventory_data:
        return jsonify({'status': 'error', 'message': 'Product not found'}), 404
    
    # Update stock
    inventory_data[product_id]['stock'] = new_stock
    
    # Get immediate prediction
    pred = get_real_time_prediction({
        'product_id': product_id,
        'current_stock': new_stock,
        'category': inventory_data[product_id].get('category', 'Unknown'),
        'price': inventory_data[product_id].get('price', 0)
    })
    
    if pred:
        inventory_data[product_id]['forecast'] = pred['prediction']
        inventory_data[product_id]['restock_needed'] = pred['action'] == 'RESTOCK NEEDED'
        inventory_data[product_id]['priority'] = pred['priority']
    
    inventory_data[product_id]['last_update'] = datetime.now().isoformat()
    
    return jsonify({
        'status': 'success',
        'product_id': product_id,
        'current_stock': new_stock,
        'prediction': pred['prediction'] if pred else 0,
        'action': pred['action'] if pred else 'UNKNOWN'
    })

@app.route('/api/inventory/list', methods=['GET'])
def get_inventory():
    """Get current inventory status"""
    return jsonify({
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'products': list(inventory_data.values())
    })

@app.route('/api/inventory/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product details"""
    if product_id not in inventory_data:
        return jsonify({'status': 'error', 'message': 'Product not found'}), 404
    
    return jsonify({
        'status': 'success',
        'product': inventory_data[product_id]
    })

@app.route('/api/alerts/list', methods=['GET'])
def get_alerts():
    """Get current alerts"""
    alerts = []
    while not alerts_queue.empty():
        alerts.append(alerts_queue.get())
    
    return jsonify({
        'status': 'success',
        'alerts': alerts,
        'count': len(alerts)
    })

@app.route('/api/alerts/acknowledge/<int:alert_id>', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        conn = sqlite3.connect('realtime_stock.db')
        c = conn.cursor()
        c.execute('UPDATE alerts SET acknowledged = 1 WHERE id = ?', (alert_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Alert acknowledged'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/stats/summary', methods=['GET'])
def get_summary():
    """Get inventory summary statistics"""
    if not inventory_data:
        return jsonify({
            'status': 'success',
            'total_products': 0,
            'restock_needed': 0,
            'high_priority_alerts': 0
        })
    
    total = len(inventory_data)
    restock = sum(1 for p in inventory_data.values() if p.get('restock_needed', False))
    high_priority = sum(1 for p in inventory_data.values() if p.get('priority') == 'HIGH')
    
    return jsonify({
        'status': 'success',
        'total_products': total,
        'restock_needed': restock,
        'high_priority_alerts': high_priority,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get complete dashboard data"""
    total = len(inventory_data)
    restock = sum(1 for p in inventory_data.values() if p.get('restock_needed', False))
    total_stock = sum(p.get('stock', 0) for p in inventory_data.values())
    total_forecast = sum(p.get('forecast', 0) for p in inventory_data.values())
    
    # Get alerts
    alerts_list = []
    try:
        conn = sqlite3.connect('realtime_stock.db')
        c = conn.cursor()
        c.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10')
        for row in c.fetchall():
            alerts_list.append({
                'id': row[0],
                'product_id': row[1],
                'type': row[2],
                'message': row[3],
                'timestamp': row[4] if len(row) > 4 else datetime.now().isoformat()
            })
        conn.close()
    except:
        pass
    
    products_status = [
        {
            'id': p['id'],
            'name': p['name'],
            'stock': int(p['stock']),
            'forecast': float(p['forecast']),  # Convert float32 to float
            'restock_needed': p['restock_needed'],
            'priority': p['priority'],
            'status': '⚠️ LOW' if p['restock_needed'] else '✅ OK'
        }
        for p in sorted(inventory_data.values(), key=lambda x: x['priority'], reverse=True)
    ]
    
    return jsonify({
        'status': 'success',
        'summary': {
            'total_products': int(total),
            'restock_needed': int(restock),
            'alerts_count': int(len(alerts_list)),
            'total_stock': int(total_stock),
            'total_forecast': float(total_forecast),
            'stock_utilization': f"{(total_stock / (total_forecast + 0.01) * 100):.1f}%"
        },
        'products': products_status,
        'alerts': alerts_list,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/inventory/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product from inventory"""
    if product_id in inventory_data:
        del inventory_data[product_id]
        return jsonify({'status': 'success', 'message': 'Product deleted'})
    return jsonify({'status': 'error', 'message': 'Product not found'})

@app.route('/', methods=['GET'])
def dashboard():
    """Serve dashboard HTML"""
    return render_template('dashboard_v2.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'monitored_products': len(inventory_data)
    })

# ==================== INITIALIZATION ====================

if __name__ == '__main__':
    print("🚀 Initializing SYNCHAIN AI Real-time Monitoring...")
    
    # Initialize database
    initialize_database()
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_stock_levels, daemon=True)
    monitor_thread.start()
    print("✅ Monitoring thread started")
    
    # Sample data for demo
    sample_products = [
        {'product_id': 1, 'name': 'Baju Merah', 'stock': 50, 'category': 'Clothing', 'price': 150},
        {'product_id': 2, 'name': 'Celana Biru', 'stock': 30, 'category': 'Clothing', 'price': 200},
        {'product_id': 3, 'name': 'Sepatu Hitam', 'stock': 25, 'category': 'Footwear', 'price': 350},
        {'product_id': 4, 'name': 'Topi Putih', 'stock': 100, 'category': 'Accessories', 'price': 75},
        {'product_id': 5, 'name': 'Sarung Tangan', 'stock': 15, 'category': 'Accessories', 'price': 50},
    ]
    
    for prod in sample_products:
        inventory_data[prod['product_id']] = {
            'id': prod['product_id'],
            'name': prod['name'],
            'stock': prod['stock'],
            'category': prod['category'],
            'price': prod['price'],
            'forecast': 0,
            'restock_needed': False,
            'priority': 'LOW',
            'last_update': datetime.now().isoformat()
        }
    
    print(f"✅ Loaded {len(inventory_data)} sample products")
    print("\n🌐 Dashboard: http://localhost:5000")
    print("📊 API Docs:")
    print("   • GET  /api/dashboard          - Complete dashboard data")
    print("   • GET  /api/inventory/list     - All products")
    print("   • POST /api/inventory/update/1 - Update stock (json: {\"stock\": 50})")
    print("   • GET  /api/alerts/list        - Current alerts")
    print("\n🚀 Starting server...\n")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)