# PhishSniffer - Advanced Email Security Platform

An advanced machine learning-based web application for detecting and analyzing phishing emails with high accuracy using modern Streamlit interface.

![GitHub language count](https://img.shields.io/github/languages/top/LujainHesham/PhishingEmailDetector?color=brightgreen)
![License](https://img.shields.io/badge/license-All%20Rights%20Reserved-red)

## 🚀 New Features (v2.0)

- **🌐 Modern Web Interface**: Complete Streamlit-based GUI replacing legacy tkinter
- **📊 Advanced Analytics**: Interactive charts and visualizations with Plotly
- **🔄 Enhanced ML Pipeline**: Improved model training and evaluation metrics
- **🔗 URL Analysis**: Comprehensive suspicious URL tracking and management
- **📈 Real-time Reporting**: Dynamic dashboards with export capabilities
- **⚙️ Configuration Management**: Advanced settings and model training controls

## 🛡️ Key Features

- **Multi-factor Analysis**: Examines sender information, URLs, content patterns, and language indicators
- **ML-Powered Detection**: Uses custom-trained models with specialized phishing datasets
- **Real-time Scanning**: Instantly analyzes uploaded .eml files or pasted email content
- **URL Threat Detection**: Identifies shortened URLs, IP-based links, and suspicious domains
- **Interactive Dashboards**: Visual analytics with filtering and export capabilities
- **Modern Web UI**: Responsive, mobile-friendly interface accessible via web browser

## 📋 Installation & Setup

### Requirements
- Python 3.8+
- pip package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/LujainHesham/PhishingEmailDetector.git
cd PhishingEmailDetector

# Install dependencies
pip install -r requirements.txt

# Launch the web application
streamlit run app_streamlit.py
```

### Alternative Launch Methods

#### Windows
```bash
# Double-click start_app.bat or run:
start_app.bat
```

#### Linux/Mac
```bash
# Make executable and run:
chmod +x start_app.sh
./start_app.sh
```

## 💻 Usage

1. **Launch Application**: Run the startup script or Streamlit command
2. **Open Browser**: Navigate to `http://localhost:8501`
3. **Analyze Emails**: 
   - Upload .eml files or paste email content
   - Get instant threat assessment with detailed analysis
4. **Review Reports**: View comprehensive security reports with risk indicators
5. **Manage URLs**: Track and analyze suspicious URLs with filtering
6. **Configure Settings**: Adjust model parameters and training options

## 🎯 Interface Overview

### 📧 Email Analysis
- **File Upload**: Drag-and-drop .eml file support
- **Text Input**: Direct email content analysis
- **Real-time Results**: Instant risk assessment with confidence scores
- **Detailed Reports**: Comprehensive analysis breakdown

### 📊 Reports & Analytics  
- **Analysis History**: Track all previous scans
- **Risk Trends**: Visualize threat patterns over time
- **Export Options**: CSV, JSON data export
- **Interactive Charts**: Plotly-powered visualizations

### 🔗 URL Management
- **Suspicious URL Tracking**: Monitor detected threats
- **Bulk Operations**: Mass URL management tools
- **Analytics Dashboard**: Domain analysis and statistics
- **Search & Filter**: Advanced URL filtering capabilities

### ⚙️ Settings & Configuration
- **Model Information**: View training details and performance
- **Training Controls**: Retrain models with new data
- **Feedback Integration**: Improve models with user feedback
- **App Settings**: Customize detection parameters

## 🧠 Technical Architecture

### Machine Learning Pipeline
- **Preprocessing**: Advanced email feature extraction with TF-IDF
- **Model Training**: Support for Random Forest, XGBoost, Logistic Regression
- **Feature Engineering**: 50+ security-focused features
- **Evaluation Metrics**: Comprehensive model assessment tools

### Training Datasets
- **CEAS_08**: Collaborative Email Anti-Spam dataset
- **Nigerian_Fraud**: Financial fraud email corpus  
- **Nazario**: Phishing email collection
- **Enron**: Legitimate email baseline
- **SpamAssasin**: Spam detection dataset

### Technology Stack
- **Frontend**: Streamlit with Plotly visualizations
- **Backend**: Python with scikit-learn, pandas, numpy
- **ML Models**: Ensemble approach with multiple algorithms
- **Data Storage**: JSON-based persistence with CSV exports

## 📁 Project Structure

```
PhishSniffer/
├── gui/                      # Streamlit web interface
│   ├── main_window.py        # Main application controller
│   ├── analyze_tab.py        # Email analysis interface
│   ├── report_tab.py         # Analytics dashboard
│   ├── urls_tab.py          # URL management interface
│   └── settings_tab.py       # Configuration panel
├── model/                    # Machine learning components
│   ├── features.py           # Feature extraction pipeline
│   ├── predict.py            # Prediction engine
│   ├── training.py           # Model training utilities
│   └── model_feedback.py     # Feedback learning system
├── preprocessing/            # Data preprocessing pipeline
│   ├── email_processor.py    # Email parsing and cleaning
│   ├── feature_extractor.py  # Advanced feature engineering
│   └── url_analyzer.py       # URL analysis utilities
├── storage/                  # Data persistence layer
│   ├── history.py            # Analysis history management
│   ├── urls.py               # URL database operations
│   └── extract.py            # Data extraction utilities
├── email_utils/              # Email parsing utilities
│   └── parser.py             # .eml file processing
├── config/                   # Configuration management
│   └── special_patterns.json # Detection patterns
├── resources/                # Training datasets
├── trained_models/           # Saved ML models
├── cleaned_data/             # Preprocessed datasets
├── tests/                    # Unit test suite
├── app_streamlit.py          # Streamlit application launcher
├── start_app.bat/.sh         # Platform startup scripts
└── requirements.txt          # Python dependencies
```

## 🔧 Configuration

### Model Training
- Adjust training parameters in Settings tab
- Retrain with custom datasets
- Incorporate user feedback for model improvement

### Detection Settings
- Configure risk thresholds
- Enable/disable URL checking
- Customize notification preferences

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Test specific components
python -m pytest tests/test_preprocessing.py
python -m pytest tests/test_model_training.py
```

## 📊 Performance Metrics

- **Accuracy**: >95% on test datasets
- **False Positive Rate**: <2%
- **Processing Speed**: <3 seconds per email
- **Model Training**: Optimized for various dataset sizes

## 🔄 Continuous Improvement

- **Feedback Learning**: User corrections improve model accuracy
- **Regular Updates**: Model retraining with new threat data
- **Performance Monitoring**: Automated evaluation metrics
- **Version Control**: Model versioning and rollback capabilities

## ⚠️ Security & Privacy

- **Local Processing**: All analysis performed on-device
- **No Data Transmission**: Email content never leaves your system
- **Secure Storage**: Encrypted local data persistence
- **Privacy First**: No telemetry or external data sharing

## 📄 License & Copyright

© 2025 Lujain Hesham. All Rights Reserved.

**Important**: This code is publicly viewable but not open-source. No permission is granted for use, modification, or distribution without explicit written permission from the owner.

## � Contributors

Developed by:
- Lujain Hesham
- Abdelrahman Mohamed  
- Ahmed Tamer

*Arab Academy for Science, Technology and Maritime Transport (AASTMT)*

## 🆘 Support

For issues, questions, or feature requests:
- 📧 Email: [support@phishsniffer.com]
- 🐛 Issues: [GitHub Issues](https://github.com/LujainHesham/PhishingEmailDetector/issues)
- 📖 Documentation: [Project Wiki](https://github.com/LujainHesham/PhishingEmailDetector/wiki)

---

*This tool is designed for security research and legitimate email security purposes only.*
