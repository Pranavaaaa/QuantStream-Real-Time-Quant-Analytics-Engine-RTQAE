#!/bin/bash

echo "========================================"
echo "QuantStream RTQAE - Starting Services"
echo "========================================"
echo ""

echo "[1/3] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi
echo "Python found!"
echo ""

echo "[2/3] Starting Backend API Server..."
cd backend && python3 app.py &
BACKEND_PID=$!
sleep 3
echo "Backend started on http://localhost:8000 (PID: $BACKEND_PID)"
echo ""

echo "[3/3] Starting Frontend Dashboard..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!
echo ""

echo "========================================"
echo " QuantStream RTQAE is now running!"
echo "========================================"
echo ""
echo " Backend API: http://localhost:8000"
echo " API Docs:    http://localhost:8000/docs"
echo " Dashboard:   http://localhost:5173"
echo ""
echo " Press Ctrl+C to stop all services..."
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
