#!/bin/bash
echo "=== Redrob Platform Production Startup ==="

# 1. Ensure Python dependencies are up to date
echo "Verifying Python dependencies..."
pip install -r requirements.txt

# 2. Verify and cache embedding model offline
echo "Validating model cache..."
python download_model.py

# 3. Check and recover missing cache/submission assets
echo "Performing startup auto-recovery checks..."
python -c "
import os, json, csv
workspace_dir = os.path.dirname(os.path.abspath('__file__'))
cache_path = os.path.join(workspace_dir, 'data_cache.json')
sub_path = os.path.join(workspace_dir, 'submission.csv')

if not os.path.exists(cache_path) or not os.path.exists(sub_path):
    print('Starting auto-recovery: building cache and submission...')
    from sample_data_loader import build_data_cache
    build_data_cache()
    
    # Generate submission CSV from generated cache
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    candidates = cache_data.get('candidates', [])
    
    with open(sub_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])
        for idx, item in enumerate(candidates[:100]):
            writer.writerow([item['candidate_id'], idx+1, f'{float(item[\"score\"]):.4f}', item['reasoning']])
    print('Auto-recovery completed successfully.')
else:
    print('All data and submission caches present.')
"

# 4. Launch Streamlit application
echo "Launching Streamlit application..."
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
