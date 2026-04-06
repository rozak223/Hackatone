"""
SYNCHAIN AI - Mobile-Optimized Real-time Monitor
Simple API untuk quick checks from anywhere
"""

from flask import Flask, jsonify, request
from datetime import datetime
import json

app = Flask(__name__)

# Shared inventory data (in-memory for demo)
inventory = {}

@app.route('/mobile/status', methods=['GET'])
def mobile_status():
    """Quick status for mobile - minimal data"""
    if not inventory:
        return jsonify({
            'status': 'ok',
            'message': 'No products monitored',
            'products': 0,
            'alerts': 0
        })
    
    alerts = sum(1 for p in inventory.values() if p.get('alert'))
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'total_products': len(inventory),
        'need_restock': sum(1 for p in inventory.values() if p.get('restock_needed')),
        'alerts': alerts,
        'last_update': datetime.now().isoformat()
    })

@app.route('/mobile/quick/<int:product_id>', methods=['GET'])
def quick_check(product_id):
    """Quick check for one product"""
    if product_id not in inventory:
        return jsonify({'error': 'Product not found'}), 404
    
    p = inventory[product_id]
    return jsonify({
        'id': product_id,
        'name': p.get('name', f'Product {product_id}'),
        'stock': p.get('stock', 0),
        'status': '🟢 OK' if not p.get('restock_needed') else '🔴 ACTION NEEDED',
        'action': p.get('action', 'None'),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/mobile/alerts', methods=['GET'])
def mobile_alerts():
    """Get alerts for mobile"""
    alerts = [
        {
            'product': p.get('name'),
            'action': p.get('action'),
            'stock': p.get('stock'),
            'needed': p.get('forecast', 0)
        }
        for p in inventory.values()
        if p.get('alert')
    ]
    
    return jsonify({
        'count': len(alerts),
        'alerts': alerts
    })

@app.route('/mobile/update/<int:product_id>/<int:new_stock>', methods=['POST'])
def mobile_update(product_id, new_stock):
    """Quick update from mobile"""
    if product_id not in inventory:
        return jsonify({'error': 'Product not found'}), 404
    
    inventory[product_id]['stock'] = new_stock
    
    return jsonify({
        'status': 'updated',
        'product_id': product_id,
        'new_stock': new_stock,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/mobile/all', methods=['GET'])
def mobile_all():
    """Get all products for mobile view"""
    products = []
    for pid, p in inventory.items():
        products.append({
            'id': pid,
            'name': p.get('name'),
            'stock': p.get('stock'),
            'forecast': round(p.get('forecast', 0)),
            'status': '🟡 WARNING' if p.get('restock_needed') else '🟢 OK',
            'action': '🔴 RESTOCK' if p.get('alert') else '✅ OK'
        })
    
    return jsonify({
        'count': len(products),
        'products': products,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Demo data
    inventory = {
        1: {'name': 'Baju Merah', 'stock': 45, 'forecast': 150, 'restock_needed': True, 'alert': True, 'action': 'Order 105 units'},
        2: {'name': 'Celana Biru', 'stock': 60, 'forecast': 80, 'restock_needed': False, 'alert': False, 'action': 'None'},
        3: {'name': 'Sepatu', 'stock': 20, 'forecast': 100, 'restock_needed': True, 'alert': True, 'action': 'Order 80 units'},
    }
    
    print("📱 Mobile API running on port 5001")
    print("Quick access:")
    print("  /mobile/status          - Quick overview")
    print("  /mobile/quick/1         - Check product 1")
    print("  /mobile/alerts          - All alerts")
    print("  /mobile/all             - All products")
    
    app.run(debug=False, host='0.0.0.0', port=5001)