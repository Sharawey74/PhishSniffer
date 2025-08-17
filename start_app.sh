#!/bin/bash
echo "Starting PhishSniffer Web Application..."
echo ""
echo "Open your web browser to http://localhost:8501 once the server starts"
echo "Press Ctrl+C to stop the server"
echo ""
streamlit run app_streamlit.py --server.port=8501 --server.address=localhost
