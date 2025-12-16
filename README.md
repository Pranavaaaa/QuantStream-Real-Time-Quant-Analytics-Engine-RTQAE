# QuantStream - Real-Time Quant Analytics Engine (RTQAE)

<div align="center">

![QuantStream](https://via.placeholder.com/800x200/4f46e5/00d4ff?text=QuantStream+RTQAE)

**A professional real-time quantitative analytics engine for cryptocurrency markets**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61dafb)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5%2B-646cff)](https://vitejs.dev/)

</div>

## 🚀 Features

### Real-Time Data Ingestion
- **WebSocket Integration**: Live data streaming from Binance Futures API
- **Multi-Symbol Support**: Monitor multiple cryptocurrency pairs simultaneously
- **Thread-Safe Buffering**: In-memory circular buffer for high-frequency tick data
- **Automatic Reconnection**: Robust error handling with auto-reconnect logic

### Advanced Analytics
- **Price Statistics**: Real-time calculation of mean, standard deviation, VWAP, volatility
- **Z-Score Analysis**: Statistical outlier detection for anomaly identification
- **Correlation Analysis**: Pearson and Spearman correlation between symbol pairs
- **Pairs Trading**: Spread calculation, linear regression, hedge ratio computation
- **Stationarity Testing**: Augmented Dickey-Fuller (ADF) tests for mean-reversion strategies

### Alert System
- **Rule-Based Alerts**: Configurable thresholds for price, z-score, and volume
- **Severity Levels**: Low, Medium, High, Critical alert classifications
- **Persistent Storage**: All alerts stored in SQLite database

### Modern Architecture
- **Backend**: FastAPI for high-performance async processing
- **Frontend**: React.js + Tailwind CSS for a responsive, modern UI
- **Visualization**: Plotly.js for interactive financial charting

## 📋 Prerequisites

- Python 3.9 or higher
- Node.js 18+ and npm
- Internet connection (for live data)

## 🔧 Installation

1. **Clone or Navigate to the Project Directory**
   ```bash
   cd "d:\QuantStream- Real-Time Quant Analytics Engine (RTQAE)"
   ```

2. **Backend Setup**
   ```bash
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

## 🎯 Quick Start

### Option 1: Using the Run Script (Recommended)

**Windows:**
```bash
.\run.bat
```

This will:
- Start the backend API server on `http://localhost:8000`
- Start the frontend dev server on `http://localhost:5173`
- Open the dashboard in your default browser

### Option 2: Manual Start

**Terminal 1 - Start Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

## 📖 Usage Guide

### 1. Starting Data Ingestion
1. Open the dashboard at `http://localhost:5173`
2. Navigate to the **Controls** page
3. Select symbols to monitor (e.g., BTCUSDT, ETHUSDT)
4. Click **▶️ Start Ingestion**

### 2. Viewing Live Data
- Go to the **Live Data** page to see real-time prices and recent ticks
- Prices update automatically as new data arrives

### 3. Monitoring Statistics
- Visit the **Statistics** page for detailed price metrics
- View current price, mean, standard deviation, VWAP, z-scores
- Color-coded z-score indicators show market conditions

### 4. Analyzing Markets
The **Analytics** page provides detailed interactive charts:
- **Live Price**: Candlestick charts with volume
- **Z-Score**: Real-time gauge charts for outliers
- **Correlation**: Heatmap analysis
- **Pairs Trading**: Spread analysis and Regression
- **ADF Test**: Stationarity testing

### 5. Managing Alerts
- Check the **Alerts** page for triggered notifications
- Filter by severity level
- Export alerts to CSV

## 🏗️ Architecture

```
QuantStream RTQAE
│
├── Backend (Python/FastAPI)
│   ├── Core (Config, Logger, Utils)
│   ├── Storage (SQLite, Models, Resampler)
│   ├── Ingestion (WebSocket, Buffer, Router)
│   ├── Analytics (Stats, Z-Score, Correlation, Regression, ADF)
│   ├── Alerts (Rules, Engine, Notifier)
│   └── API (Server, Routes)
│
├── Database (SQLite)
│   ├── Ticks (Raw trade data)
│   ├── OHLCV (Candlestick data)
│   ├── Analytics (Computed metrics)
│   └── Alerts (Alert history)
│
└── Frontend (React + Vite)
    ├── src/
    │   ├── api/        # Axios API client
    │   ├── components/ # Reusable UI components
    │   ├── pages/      # Application pages
    │   └── App.jsx     # Main entry point
    └── public/         # Static assets
```

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🛠️ Configuration

Edit `backend/core/config.py` to customize:
- **Window Sizes**: Adjust rolling calculation windows
- **Alert Thresholds**: Configure alert trigger conditions
- **API Settings**: Modify host, port, CORS settings

## 📂 Project Structure

```
QuantStream- Real-Time Quant Analytics Engine (RTQAE)/
├── backend/           # Python FastAPI Backend
│   ├── app.py         # Entry point
│   └── ...
├── frontend/          # React Frontend
│   ├── src/           # Source code
│   ├── index.html     # Entry HTML
│   └── package.json   # NPM dependencies
├── data/              # Database storage
├── logs/              # Application logs
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 📝 License

This project is provided as-is for educational and research purposes.

<div align="center">

**Built with ❤️ using Python, FastAPI, React, and Vite**

</div>
