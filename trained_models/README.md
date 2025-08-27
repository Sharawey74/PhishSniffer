# Trained Models Directory

This directory stores trained machine learning models and their associated files.

## Structure

```text
trained_models/
├── README.md                    # This file
├── model_name_YYYYMMDD_HHMMSS.joblib        # Trained model files
├── model_name_YYYYMMDD_HHMMSS_metadata.json # Model metadata
├── model_name_YYYYMMDD_HHMMSS_feature_extractor.joblib # Feature extractors
└── evaluation_plots/           # Model evaluation visualizations
    ├── confusion_matrix.png
    ├── roc_curve.png
    └── feature_importance.png
```

## File Formats

- **`.joblib`** - Serialized scikit-learn models (recommended format)
- **`.pkl`** - Pickle files (alternative format)
- **`.json`** - Model metadata and configuration
- **`.png/.pdf`** - Evaluation plots and visualizations

## Model Naming Convention

Models are named using the following pattern:

```text
{algorithm}_{timestamp}[_suffix].{extension}
```

Examples:

- `random_forest_20250817_035020.joblib`
- `xgboost_20250817_035020_metadata.json`
- `logistic_regression_20250817_035020_feature_extractor.joblib`

## Model Metadata

Each model should have an associated metadata file containing:

```json
{
    "model_type": "Random Forest Classifier",
    "version": "1.0.0",
    "training_date": "2025-08-17 03:50:20",
    "features_used": 50,
    "training_data_size": 43868,
    "accuracy": 0.9542,
    "precision": 0.9481,
    "recall": 0.9603,
    "f1_score": 0.9542,
    "dataset_files": ["CEAS_08.csv", "Nigerian_Fraud.csv", "Nazario.csv"],
    "hyperparameters": {...},
    "feature_names": [...],
    "created_by": "PhishSniffer Training Pipeline"
}
```

## Loading Models

Models are automatically loaded by the prediction system using:

```python
from model.predict import PhishingPredictor

predictor = PhishingPredictor()
predictor.load_model()  # Loads the most recent model
```

## Storage Guidelines

- Keep only the 5 most recent model versions
- Archive older models to external storage
- Include evaluation plots for each model
- Maintain metadata for reproducibility

## Git Tracking

- Model files (`.joblib`, `.pkl`) are ignored by git due to size
- Metadata files (`.json`) are tracked
- Evaluation plots are tracked for documentation
- This README and directory structure are tracked
