"""
Model evaluation functions for phishing email detection.
Provides comprehensive evaluation metrics and visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

class ModelEvaluator:
    """Class for comprehensive model evaluation."""
    
    def __init__(self, model, X_test, y_test, X_train=None, y_train=None):
        self.model = model
        self.X_test = X_test
        self.y_test = y_test
        self.X_train = X_train
        self.y_train = y_train
        self.y_pred = None
        self.y_pred_proba = None
        
    def predict(self):
        """Generate predictions."""
        print("Generating predictions...")
        self.y_pred = self.model.predict(self.X_test)
        
        if hasattr(self.model, 'predict_proba'):
            self.y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]
        elif hasattr(self.model, 'decision_function'):
            self.y_pred_proba = self.model.decision_function(self.X_test)
        
        print("✓ Predictions generated")
    
    def calculate_metrics(self):
        """Calculate comprehensive evaluation metrics."""
        if self.y_pred is None:
            self.predict()
        
        print(f"\n{'='*50}")
        print("MODEL EVALUATION METRICS")
        print(f"{'='*50}")
        
        # Basic metrics
        accuracy = accuracy_score(self.y_test, self.y_pred)
        precision = precision_score(self.y_test, self.y_pred)
        recall = recall_score(self.y_test, self.y_pred)
        f1 = f1_score(self.y_test, self.y_pred)
        
        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        
        # AUC-ROC if probabilities available
        if self.y_pred_proba is not None:
            auc = roc_auc_score(self.y_test, self.y_pred_proba)
            print(f"AUC-ROC:   {auc:.4f}")
        
        # Detailed classification report
        print(f"\n{'='*50}")
        print("DETAILED CLASSIFICATION REPORT")
        print(f"{'='*50}")
        print(classification_report(self.y_test, self.y_pred, 
                                  target_names=['Legitimate', 'Phishing']))
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc_roc': auc if self.y_pred_proba is not None else None
        }
    
    def plot_confusion_matrix(self, save_path=None):
        """Plot confusion matrix."""
        if self.y_pred is None:
            self.predict()
        
        cm = confusion_matrix(self.y_test, self.y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Legitimate', 'Phishing'],
                   yticklabels=['Legitimate', 'Phishing'])
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        
        # Add percentage annotations
        total = cm.sum()
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(j + 0.5, i + 0.7, f'({cm[i,j]/total:.1%})', 
                        ha='center', va='center', fontsize=10, color='red')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Confusion matrix saved to: {save_path}")
        
        plt.tight_layout()
        plt.show()
        
        return cm
    
    def plot_roc_curve(self, save_path=None):
        """Plot ROC curve."""
        if self.y_pred_proba is None:
            print("No probability predictions available for ROC curve")
            return
        
        fpr, tpr, thresholds = roc_curve(self.y_test, self.y_pred_proba)
        auc = roc_auc_score(self.y_test, self.y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ ROC curve saved to: {save_path}")
        
        plt.tight_layout()
        plt.show()
        
        return fpr, tpr, thresholds
    
    def analyze_feature_importance(self, feature_names=None, top_n=20, save_path=None):
        """Analyze and plot feature importance."""
        if not hasattr(self.model, 'feature_importances_'):
            print("Model does not support feature importance analysis")
            return
        
        importance = self.model.feature_importances_
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(importance))]
        
        # Create feature importance dataframe
        feature_importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print(f"\n{'='*50}")
        print("TOP FEATURE IMPORTANCES")
        print(f"{'='*50}")
        print(feature_importance_df.head(top_n).to_string(index=False))
        
        # Plot feature importance
        plt.figure(figsize=(10, 8))
        top_features = feature_importance_df.head(top_n)
        sns.barplot(data=top_features, y='feature', x='importance', orient='h')
        plt.title(f'Top {top_n} Feature Importances')
        plt.xlabel('Importance')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Feature importance plot saved to: {save_path}")
        
        plt.show()
        
        return feature_importance_df
    
    def cross_validate(self, cv=5):
        """Perform cross-validation."""
        if self.X_train is None or self.y_train is None:
            print("Training data not available for cross-validation")
            return
        
        print(f"\n{'='*50}")
        print(f"CROSS-VALIDATION (k={cv})")
        print(f"{'='*50}")
        
        # Accuracy scores
        cv_scores = cross_val_score(self.model, self.X_train, self.y_train, 
                                   cv=cv, scoring='accuracy')
        print(f"Cross-validation accuracy scores: {cv_scores}")
        print(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Precision scores
        cv_precision = cross_val_score(self.model, self.X_train, self.y_train, 
                                      cv=cv, scoring='precision')
        print(f"Mean CV precision: {cv_precision.mean():.4f} (+/- {cv_precision.std() * 2:.4f})")
        
        # Recall scores
        cv_recall = cross_val_score(self.model, self.X_train, self.y_train, 
                                   cv=cv, scoring='recall')
        print(f"Mean CV recall: {cv_recall.mean():.4f} (+/- {cv_recall.std() * 2:.4f})")
        
        # F1 scores
        cv_f1 = cross_val_score(self.model, self.X_train, self.y_train, 
                               cv=cv, scoring='f1')
        print(f"Mean CV F1-score: {cv_f1.mean():.4f} (+/- {cv_f1.std() * 2:.4f})")
        
        return {
            'accuracy': cv_scores,
            'precision': cv_precision,
            'recall': cv_recall,
            'f1': cv_f1
        }
    
    def analyze_prediction_errors(self, sample_size=10):
        """Analyze prediction errors."""
        if self.y_pred is None:
            self.predict()
        
        # Find false positives and false negatives
        fp_mask = (self.y_test == 0) & (self.y_pred == 1)
        fn_mask = (self.y_test == 1) & (self.y_pred == 0)
        
        fp_indices = np.where(fp_mask)[0]
        fn_indices = np.where(fn_mask)[0]
        
        print(f"\n{'='*50}")
        print("PREDICTION ERROR ANALYSIS")
        print(f"{'='*50}")
        print(f"False Positives: {len(fp_indices)} ({len(fp_indices)/len(self.y_test)*100:.2f}%)")
        print(f"False Negatives: {len(fn_indices)} ({len(fn_indices)/len(self.y_test)*100:.2f}%)")
        
        # Sample some errors for manual inspection
        if len(fp_indices) > 0:
            print(f"\nSample False Positive indices: {fp_indices[:sample_size].tolist()}")
        
        if len(fn_indices) > 0:
            print(f"Sample False Negative indices: {fn_indices[:sample_size].tolist()}")
        
        return fp_indices, fn_indices
    
    def generate_evaluation_report(self, save_dir=None):
        """Generate comprehensive evaluation report."""
        print(f"\n{'='*80}")
        print("GENERATING COMPREHENSIVE EVALUATION REPORT")
        print(f"{'='*80}")
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        # Generate plots
        if save_dir:
            import os
            os.makedirs(save_dir, exist_ok=True)
            
            cm_path = os.path.join(save_dir, 'confusion_matrix.png')
            self.plot_confusion_matrix(save_path=cm_path)
            
            if self.y_pred_proba is not None:
                roc_path = os.path.join(save_dir, 'roc_curve.png')
                self.plot_roc_curve(save_path=roc_path)
            
            if hasattr(self.model, 'feature_importances_'):
                fi_path = os.path.join(save_dir, 'feature_importance.png')
                self.analyze_feature_importance(save_path=fi_path)
        else:
            self.plot_confusion_matrix()
            if self.y_pred_proba is not None:
                self.plot_roc_curve()
            if hasattr(self.model, 'feature_importances_'):
                self.analyze_feature_importance()
        
        # Cross-validation if training data available
        if self.X_train is not None:
            cv_results = self.cross_validate()
        
        # Error analysis
        fp_indices, fn_indices = self.analyze_prediction_errors()
        
        print(f"\n{'='*80}")
        print("EVALUATION REPORT COMPLETED")
        print(f"{'='*80}")
        
        return metrics

def evaluate_model(model, X_test, y_test, X_train=None, y_train=None, save_dir=None):
    """Convenience function to evaluate a model."""
    evaluator = ModelEvaluator(model, X_test, y_test, X_train, y_train)
    return evaluator.generate_evaluation_report(save_dir)
