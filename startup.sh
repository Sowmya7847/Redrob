#!/bin/bash
# Pre-download and cache model weights
python download_model.py

# Start the Streamlit application
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
