# PhishSniffer (AI_PhishingEmailDetector)

An advanced machine learning-based application for detecting and analyzing phishing emails with high accuracy.

![GitHub language count](https://img.shields.io/github/languages/top/LujainHesham/PhishingEmailDetector?color=brightgreen)
![License](https://img.shields.io/badge/license-All%20Rights%20Reserved-red)

## 🛡️ Key Features

- **Multi-factor Analysis**: Examines sender information, URLs, content patterns, and language indicators
- **ML-Powered Detection**: Uses custom-trained models with specialized phishing datasets
- **Real-time Scanning**: Instantly analyzes uploaded .eml files or pasted email content
- **URL Threat Detection**: Identifies shortened URLs, IP-based links, and suspicious domains
- **Detailed Reporting**: Provides comprehensive analysis with visual risk indicators
- **Modern UI**: Clean, intuitive interface built with ttkbootstrap

## 📋 Installation

```bash
# Clone the repository
git clone https://github.com/LujainHesham/PhishingEmailDetector.git

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 💻 Usage

1. Launch the application
2. Select "Analyze" tab
3. Upload an .eml file or paste email content
4. Click "Analyze Email" to receive detailed threat assessment
5. View comprehensive reports with identified threats and risk levels

## 🧠 Technical Details

- **Training Datasets**: CEAS_08, Nigerian_Fraud, and Enron.csv datasets
- **Feature Extraction**: Analyzes email headers, content, URLs, and linguistic patterns
- **Model Architecture**: Ensemble approach combining multiple specialized models
- **Local Processing**: All analysis performed on-device for enhanced privacy

## 📁 Project Structure

```
PhishingEmailDetector/
├── config/                # Configuration files
│   └── special_patterns.json  # Patterns for phishing detection
├── data/                  # Data storage directory
├── email_utils/           # Email parsing and analysis utilities
├── gui/                   # User interface components
│   ├── analyze_tab.py     # Email analysis interface
│   ├── main_window.py     # Main application window
│   ├── report_tab.py      # Results reporting interface
│   ├── settings_tab.py    # Settings configuration
│   ├── splash_screen.py   # Application splash screen
│   └── urls_tab.py        # URL analysis interface
├── model/                 # Machine learning models
│   ├── features.py        # Feature extraction
│   ├── model_feedback.py  # Model improvement utilities
│   ├── predict.py         # Prediction functionality
│   └── training.py        # Model training
├── modules/               # Additional functionality modules
├── resources/             # Training datasets
│   ├── CEAS_08.csv        # Collaborative Email Anti-Spam dataset
│   ├── Enron.csv          # Enron email corpus
│   └── Ling.csv           # Linguistic features dataset
├── storage/               # Data persistence
│   ├── extract.py         # Data extraction utilities
│   ├── history.py         # Analysis history management
│   └── urls.py            # URL database management
├── app.py                 # Application entry point
└── requirements.txt       # Python dependencies
```

## ⚠️ Copyright Notice

© 2025 Lujain Hesham. All Rights Reserved.

**Important**: This code is publicly viewable but not open-source. No permission is granted for use, modification, or distribution without explicit written permission from the owner.

## 👤 Author

Developed by Lujain Hesham, Abdelrahman Mohamed, Ahmed Tamer at AASTMT.

---

*This tool is designed for security research and legitimate email security purposes only.*
