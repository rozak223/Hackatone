# 🚀 SYNCHAIN AI

### Teknologi Prediksi Stok & Intelijen Rantai Pasok Berbasis AI untuk UMKM

---

## 🧠 Deskripsi Singkat

**SYNCHAIN AI** adalah sistem berbasis Artificial Intelligence yang dirancang untuk membantu UMKM dalam mengelola stok dan rantai pasok secara lebih cerdas, efisien, dan adaptif.

Dengan memanfaatkan data penjualan historis, sistem ini mampu:

* 📊 Memprediksi permintaan produk di masa depan
* 📦 Memberikan rekomendasi restock otomatis
* 🔍 Menyediakan insight berbasis data untuk pengambilan keputusan

---

## ⚠️ Permasalahan

Banyak UMKM masih mengalami:

* Overstock (kelebihan stok) → biaya tinggi
* Stockout (kehabisan stok) → kehilangan pelanggan
* Pengambilan keputusan berbasis intuisi, bukan data

---

## 💡 Solusi

SYNCHAIN AI menghadirkan solusi berbasis AI dengan fitur utama:

### 🔮 1. Prediksi Permintaan

Menggunakan model Machine Learning (**XGBoost**) untuk memprediksi kebutuhan stok berdasarkan data historis.

### 📦 2. Rekomendasi Restock

Memberikan jumlah optimal barang yang perlu disediakan untuk menghindari overstock & stockout.

### 🔍 3. Explainable AI (Explainability)

Setiap prediksi dilengkapi dengan penjelasan:

* Faktor utama yang mempengaruhi hasil
* Arah pengaruh (positif/negatif)

👉 Transparan, bukan black-box

### ⚙️ 4. Automasi Workflow

Integrasi dengan automation tools (n8n) untuk:

* Notifikasi stok
* Monitoring supply chain

---

## 🧩 Arsitektur Sistem

```bash
User Input (CSV / Data Penjualan)
        ↓
Data Preprocessing
        ↓
Model AI (XGBoost)
        ↓
Prediction + Explainability (SHAP)
        ↓
Dashboard (Streamlit)
```

---

## 🛠️ Tech Stack

### 🤖 AI & Data

* Python
* XGBoost
* Pandas
* Scikit-learn
* SHAP (Explainability)

### 🌐 Application

* Streamlit (Dashboard UI)
* FastAPI (Optional Backend)

### ⚙️ Automation

* n8n

---

## 📊 Dataset

Dataset yang digunakan berasal dari:

* Dataset publik (Retail / Sales Dataset)
* Data simulasi UMKM

Struktur data:

* Tanggal transaksi
* Produk
* Jumlah penjualan
* Harga
* Stok

---

## 🚀 Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/your-repo/synchain-ai.git
cd synchain-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan Training Model

```bash
jupyter notebook training.ipynb
```

### 4. Jalankan Inference / App

```bash
streamlit run app.py
```

---

## 📈 Output Sistem

* Prediksi permintaan produk
* Status stok (aman / tidak aman)
* Rekomendasi restock
* Insight faktor yang mempengaruhi prediksi

---

## 🎯 Keunggulan

✅ Berbasis AI (data-driven decision)
✅ Explainable (transparan & dapat dipercaya)
✅ Ringan & dapat berjalan offline
✅ Relevan untuk UMKM Indonesia

---

## 🔐 Compliance Hackathon

* ✅ Offline inference (tanpa API eksternal)
* ✅ Model ringan & efisien
* ✅ Explainability wajib tersedia
* ✅ Reproducible environment

---

## 🌍 Dampak

Dengan SYNCHAIN AI, UMKM dapat:

* Mengurangi biaya operasional
* Meningkatkan efisiensi stok
* Mengambil keputusan berbasis data

---

## 💬 Tagline

> “From Guessing to Predicting — Empowering UMKM with Intelligent Supply Chain”

---

## 📌 Future Development

* Integrasi POS & WhatsApp API
* Multi-store analytics
* Fraud detection pada supply chain
* Real-time forecasting

---

## 🤝 Kontribusi

Project ini dikembangkan dalam rangka Hackathon 2026.

---

## ⭐ Penutup

SYNCHAIN AI bukan sekadar tools, tetapi langkah menuju digitalisasi UMKM berbasis kecerdasan buatan yang adaptif dan berkelanjutan.
