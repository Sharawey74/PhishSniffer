# 🚀 Streamlit Cloud Deployment Guide for PhishSniffer

## 📋 Pre-Deployment Checklist

### ✅ Files Added/Modified for Cloud Deployment:

1. **requirements.txt** - Added `nltk>=3.8.0` and `seaborn>=0.11.0`
2. **packages.txt** - System-level dependencies (if needed)
3. **.streamlit/config.toml** - Streamlit configuration
4. **setup_cloud.py** - Cloud initialization script
5. **streamlit_app.py** - Cloud-optimized entry point
6. **model/__init__.py** - Error-safe imports
7. **model/features.py** - NLTK optional import handling
8. **model/predict.py** - Fallback model for missing files
9. **gui/main_window.py** - Cloud-aware initialization

## 🌐 Streamlit Cloud Setup Instructions

### Step 1: Repository Preparation
1. Commit all changes to your GitHub repository
2. Make sure the following files are in your repo root:
   - `requirements.txt`
   - `streamlit_app.py` (new entry point)
   - `packages.txt` (if needed)
   - `.streamlit/config.toml`

### Step 2: Streamlit Cloud Configuration
1. Go to https://share.streamlit.io
2. Connect your GitHub repository
3. **IMPORTANT**: Set the main file path to: `streamlit_app.py`
4. Deploy!

### Step 3: Troubleshooting Common Issues

#### Issue 1: NLTK Import Error ❌
**Fixed**: Added NLTK to requirements.txt and graceful import handling

#### Issue 2: Missing Model Files ❌  
**Fixed**: Created fallback model that works without trained model files

#### Issue 3: Path Issues ❌
**Fixed**: Cloud-aware path handling and initialization

#### Issue 4: Missing Data Directories ❌
**Fixed**: Automatic directory creation in setup_cloud.py

## 🔧 Local Testing Before Deployment

Test the cloud-optimized version locally:

```bash
# Install requirements
pip install -r requirements.txt

# Test cloud entry point
streamlit run streamlit_app.py

# Should work without errors even if model files are missing
```

## 📁 Required Directory Structure

The app will automatically create these directories in the cloud:

```
PhishSniffer/
├── streamlit_app.py          # ← Cloud entry point
├── requirements.txt          # ← Updated with NLTK
├── packages.txt             # ← System dependencies
├── setup_cloud.py           # ← Cloud initialization
├── .streamlit/
│   └── config.toml          # ← Streamlit config
├── gui/
│   └── main_window.py       # ← Updated for cloud
├── model/
│   ├── __init__.py          # ← Error-safe imports
│   ├── predict.py           # ← Fallback model support
│   └── features.py          # ← Optional NLTK
└── data/                    # ← Auto-created
    ├── settings.json        # ← Auto-created
    ├── analysis_history.json # ← Auto-created
    └── suspicious_urls.json  # ← Auto-created
```

## 🎯 Expected Behavior in Cloud

### ✅ What Works:
- Email text analysis (basic rule-based)
- URL analysis and detection
- Risk factor identification
- History tracking
- Settings management
- All GUI components

### ⚠️ Limitations in Cloud:
- Advanced ML model not available (uses fallback)
- No model training capability
- Limited feature extraction (no NLTK corpus)

### 🔄 Future Improvements:
- Upload pre-trained model to GitHub (if under 100MB)
- Use GitHub LFS for larger model files
- Implement model downloading from external source

## 🚀 Deployment Command Summary

```bash
# 1. Commit all changes
git add .
git commit -m "Cloud deployment optimizations"
git push origin main

# 2. Deploy on Streamlit Cloud with:
#    Repository: your-username/PhishSniffer
#    Branch: main
#    Main file path: streamlit_app.py
```

## 📞 Support

If deployment fails:
1. Check the Streamlit Cloud logs
2. Verify all required files are in the repository
3. Ensure the main file path is set to `streamlit_app.py`
4. Check that requirements.txt includes all dependencies

## 🔍 Monitoring Deployment

After deployment, the app should:
1. ✅ Load without import errors
2. ✅ Show the main interface
3. ✅ Accept email input for analysis
4. ✅ Display analysis results (even with fallback model)
5. ⚠️ Show warnings about limited functionality

The fallback model provides basic phishing detection based on:
- URL analysis (shortened URLs, IP addresses)
- Keyword detection (urgency, financial terms)
- Pattern matching (threats, offers)
- Text characteristics (length, complexity)
