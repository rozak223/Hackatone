# SYNCHAIN AI - Dokumentasi Lengkap

## 📋 Daftar Isi
1. [Ringkasan Eksekutif](#ringkasan-eksekutif)
2. [Teknologi yang Digunakan](#teknologi-yang-digunakan)
3. [Arsitektur Sistem](#arsitektur-sistem)
4. [Panduan Instalasi](#panduan-instalasi)
5. [Cara Menggunakan](#cara-menggunakan)
6. [Model Machine Learning](#model-machine-learning)

---

## 🎯 Ringkasan Eksekutif

**SYNCHAIN AI** adalah sistem prediksi stok dan intelijen rantai pasok berbasis Artificial Intelligence yang dirancang untuk membantu UMKM mengelola inventaris secara lebih efisien.

### Masalah yang Diselesaikan:
- ❌ Overstock (kelebihan stok) → biaya penyimpanan tinggi
- ❌ Stockout (kehabisan stok) → kehilangan penjualan
- ❌ Pengambilan keputusan manual → tidak akurat

### Solusi yang Ditawarkan:
- ✅ Prediksi permintaan berbasis AI (XGBoost)
- ✅ Rekomendasi restock otomatis
- ✅ Insight pengelolaan inventaris yang dapat dijelaskan
- ✅ Automasi workflow dengan n8n

---

## 🛠️ Teknologi yang Digunakan

### Backend & ML:
| Teknologi | Fungsi |
|-----------|--------|
| **Python 3.12** | Bahasa pemrograman utama |
| **Pandas** | Pengolahan dan manipulasi data |
| **NumPy** | Komputasi numerik |
| **XGBoost** | Model machine learning untuk prediksi |
| **Scikit-learn** | Preprocessing dan evaluasi model |
| **Matplotlib/Seaborn** | Visualisasi data |
| **Kagglehub** | Pengambilan dataset publik |

### Workflow Automation:
- **n8n** - Automasi workflow dan notifikasi

### Dataset:
- Kaggle: [Retail Sales Dataset for Prediction](https://www.kaggle.com/datasets/itexpertfsdpk/retail-sales-dataset-for-prediction)
- ~10,000-50,000 baris data penjualan

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA INPUT LAYER                         │
│  (Kaggle Dataset / Excel / Google Sheets / Database)        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              DATA PREPROCESSING LAYER                        │
│  • Handle Missing Values                                    │
│  • Remove Duplicates                                        │
│  • Detect Outliers                                          │
│  • Feature Engineering                                      │
│  • Encoding Categorical Data                                │
│  • Feature Scaling                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│           MODEL TRAINING LAYER (XGBoost)                    │
│  • Train Set (70%)                                          │
│  • Validation Set (15%)                                     │
│  • Test Set (15%)                                           │
│  • Hyperparameter Tuning                                    │
│  • Early Stopping                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│            PREDICTION & ANALYSIS LAYER                      │
│  • Stock Demand Prediction                                  │
│  • Restock Recommendations                                  │
│  • Feature Importance Analysis (Explainability)            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│        WORKFLOW AUTOMATION LAYER (n8n)                       │
│  • Auto Notifications                                       │
│  • Email Alerts                                             │
│  • System Integration                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📥 Panduan Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd Hackatone-main
```

### 2. Setup Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### Requirements:
```
kagglehub>=0.2.0
pandas>=2.0.0
xgboost>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## 🚀 Cara Menggunakan

### Opsi 1: Gunakan Script Demo
```bash
python demo.py
```

Output:
```
🚀 SYNCHAIN AI Demo
==============================
MAE: 13.33
R²: -0.10

Contoh Prediksi:
Input: {'product_id': 52, 'category': 1, 'price': 333.80, 'month': 7}
Prediksi: 26.90

✅ Demo berhasil!
```

### Opsi 2: Gunakan Script Lengkap dengan Kaggle Dataset
```bash
python synchain_ai.py
```

**Catatan:** Anda perlu setup Kaggle API terlebih dahulu:
1. Download API key dari https://www.kaggle.com/settings/account
2. Simpan di `~/.kaggle/kaggle.json`
3. Jalankan script

### Opsi 3: Gunakan sebagai Library Python

```python
from synchain_ai import SynChainAI

# Initialize
ai = SynChainAI()

# Load data
df = ai.load_data()

# Preprocess
X, y, target = ai.preprocess_data(df)

# Train model
mae, mse, r2 = ai.train_model(X, y)

# Predict
prediction = ai.predict_stock({
    'product_id': 5,
    'category': 'A',
    'price': 100,
    'month': 3
})

print(f"Prediksi stok: {prediction:.2f}")
```

---

## 🧠 Model Machine Learning

### Model: XGBoost (Extreme Gradient Boosting)

**Mengapa XGBoost?**
- ✅ Excellent untuk tabular data
- ✅ Akurasi tinggi
- ✅ Handling missing values otomatis
- ✅ Feature importance terintegrasi
- ✅ Fast training & prediction

### Hyperparameter Configuration

```python
params = {
    'objective': 'reg:squarederror',        # Regression task
    'n_estimators': 100,                     # Number of boosting rounds
    'max_depth': 6,                          # Tree depth
    'learning_rate': 0.1,                    # Learning rate
    'subsample': 0.8,                        # Row sampling ratio
    'colsample_bytree': 0.8,                 # Column sampling ratio
    'random_state': 42
}
```

### Data Split:
- **Training Set:** 70% - Untuk melatih model
- **Validation Set:** 15% - Untuk tuning selama training
- **Test Set:** 15% - Untuk evaluasi final

### Metrics Evaluasi:

| Metric | Formula | Interpretasi |
|--------|---------|--------------|
| **MAE** | $\frac{1}{n}\sum\|y - \hat{y}\|$ | Rata-rata error absolut (units) |
| **MSE** | $\frac{1}{n}\sum(y - \hat{y})^2$ | Mean squared error |
| **R²** | $1 - \frac{SS_{res}}{SS_{tot}}$ | Proporsi variance yang dijelaskan (0-1) |

### Feature Importance

XGBoost memberikan score untuk setiap fitur berdasarkan kontribusinya:

```
1. product_id     : 450
2. month          : 380
3. price          : 320
4. day_of_week    : 250
5. category       : 180
```

---

## 📊 Output Sistem

### 1. Prediksi Permintaan
```
Produk: Baju Merah (SKU-001)
Periode: March 2026
Prediksi Quantity: 250 units
Confidence: 87%
```

### 2. Rekomendasi Restock
```
Stok Saat Ini: 50 units
Prediksi Demand: 250 units
Lead Time: 7 hari
REKOMENDASI: Restock 220 units (untuk buffer 20%)
```

### 3. Insight Analisis
```
Top Factors Mempengaruhi Demand:
1. Seasonality (Month) - +45% impact
2. Price Point - -30% impact
3. Product Category - +25% impact
```

---

## 🔐 Keamanan & Privacy

- Data processing dilakukan locally
- Tidak ada data yang diunggah ke cloud
- Support untuk on-premise deployment
- Enkripsi data saat transit (jika terintegrasi)

---

## 🚦 Roadmap Fitur

### Phase 1 (Current)
- ✅ Prediksi permintaan XGBoost
- ✅ Feature importance analysis
- ✅ Basic restock recommendations

### Phase 2
- 🔄 Multi-product demand forecasting
- 🔄 Seasonality pattern detection
- 🔄 Supplier performance tracking

### Phase 3
- 📋 Real-time dashboard
- 📋 Mobile app integration
- 📋 Advanced anomaly detection
- 📋 LSTM/ARIMA time series models

---

## 📞 Support & Contact

**Team Ctrl-Alt-Win**
- Amanda Puja Nur Aini
- Eduardo Rizqi Al Firdaus
- Rozak Gunawan
- Muchammad Miftachur Rizqi
- Muhammad Ghivari Pardiansyah

**Institusi:** Universitas Telkom, Bandung
**Tahun:** 2026

---

## 📜 Lisensi

MIT License - Bebas digunakan untuk kebutuhan komersial dan non-komersial

---

**Last Updated:** April 6, 2026