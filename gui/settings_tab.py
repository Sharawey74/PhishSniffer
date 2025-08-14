import os
import tkinter as tk
from ttkbootstrap.dialogs import Messagebox 
import traceback
import pandas as pd
import ttkbootstrap as ttk
import webbrowser
from model.training import train_custom_model
from model.model_feedback import retrain_model_with_feedback


def setup_settings_tab(app):
    """Set up the settings tab with model info and app configuration"""
    container = ttk.Frame(app.settings_tab)
    container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Define the load_feedback_history function first, before using it
    def load_feedback_history(app):
        """Load and display feedback history"""
        # Clear existing items
        for item in app.feedback_tree.get_children():
            app.feedback_tree.delete(item)
            
        feedback_file = os.path.join(app.data_dir, "feedback", "feedback_log.csv")
        
        if not os.path.exists(feedback_file):
            # No feedback history yet
            return
            
        try:
            # Read the CSV file
            df = pd.read_csv(feedback_file)
            
            # Display feedback (most recent first)
            for idx, row in df.iloc[::-1].iterrows():
                values = (
                    row["timestamp"],
                    row["original_classification"],
                    row["user_feedback"],
                    row["source"]
                )
                app.feedback_tree.insert('', 'end', values=values)
        except Exception as e:
            print(f"Error loading feedback history: {e}")
            traceback.print_exc()
    
    # Define the retrain_with_feedback function before using it
    def retrain_with_feedback(app):
        """Retrain model with user feedback"""
        from model.model_feedback import retrain_model_with_feedback
        
        result = retrain_model_with_feedback(app)
        
        if result:
            # Update UI elements with new model metadata
            app.model_updated_label.config(text=app.model_metadata.get("last_updated", app.current_datetime))
            
            if "feedback_samples_used" in app.model_metadata:
                feedback_count = app.model_metadata["feedback_samples_used"]
                Messagebox.show_info(
                    f"Model updated successfully with {feedback_count} feedback samples.",
                    "Model Updated"
                )
        else:
              Messagebox.show_warning(
                "Unable to update model with feedback. Please check if you have provided any feedback samples.",
                "Update Failed"
            )

    # Two-column layout
    left_col = ttk.Frame(container)
    left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    right_col = ttk.Frame(container)
    right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    # Left column - Model Information
    model_frame = ttk.LabelFrame(
        left_col,
        text="Model Information",
        bootstyle="info"
    )
    model_frame.pack(fill=tk.BOTH, expand=True)

    # Model details
    model_details = ttk.Frame(model_frame)
    model_details.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Model type
    ttk.Label(
        model_details,
        text="Model Type:",
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, sticky="w", pady=5)

    app.model_type_label = ttk.Label(
        model_details,
        text=app.model_metadata.get("model_type", "Random Forest Classifier")
    )
    app.model_type_label.grid(row=0, column=1, sticky="w", pady=5)

    # Model version
    ttk.Label(
        model_details,
        text="Version:",
        font=("Segoe UI", 10, "bold")
    ).grid(row=1, column=0, sticky="w", pady=5)

    app.model_version_label = ttk.Label(
        model_details,
        text=app.model_metadata.get("version", "1.0.0")
    )
    app.model_version_label.grid(row=1, column=1, sticky="w", pady=5)

    # Last updated
    ttk.Label(
        model_details,
        text="Last Updated:",
        font=("Segoe UI", 10, "bold")
    ).grid(row=2, column=0, sticky="w", pady=5)

    app.model_updated_label = ttk.Label(
        model_details,
        text=app.model_metadata.get("last_updated", app.current_datetime)
    )
    app.model_updated_label.grid(row=2, column=1, sticky="w", pady=5)

    # Features
    ttk.Label(
        model_details,
        text="Features Used:",
        font=("Segoe UI", 10, "bold")
    ).grid(row=3, column=0, sticky="w", pady=5)

    app.model_features_label = ttk.Label(
        model_details,
        text=str(app.model_metadata.get("features_used", 10))  # Default is 10 features
    )
    app.model_features_label.grid(row=3, column=1, sticky="w", pady=5)

    # Training data
    ttk.Label(
        model_details,
        text="Training Data:",
        font=("Segoe UI", 10, "bold")
    ).grid(row=4, column=0, sticky="w", pady=5)

    training_data = app.model_metadata.get("training_data_size", "Custom datasets")
    app.model_training_label = ttk.Label(
        model_details,
        text=str(training_data)
    )
    app.model_training_label.grid(row=4, column=1, sticky="w", pady=5)

    # Dataset files
    ttk.Label(
        model_details,
        text="Datasets:",
        font=("Segoe UI", 10, "bold")
    ).grid(row=5, column=0, sticky="w", pady=5)

    datasets = app.model_metadata.get("dataset_files", ["CEAS_08.csv", "Nigerian_Fraud.csv", "Nazario.csv"])
    datasets_text = "\n".join(datasets) if isinstance(datasets, list) else str(datasets)

    app.model_datasets_label = ttk.Label(
        model_details,
        text=datasets_text,
        wraplength=200
    )
    app.model_datasets_label.grid(row=5, column=1, sticky="w", pady=5)

    # Train new model and retrain with feedback buttons

    buttons_frame = ttk.Frame(model_details)
    buttons_frame.grid(row=6, column=0, columnspan=2, pady=15)

    ttk.Button(
        buttons_frame,
        text="Train New Model",
        command=lambda: train_new_model(app),
        bootstyle="info"
    ).pack(side=tk.LEFT, padx=(0, 5))

    ttk.Button(
        buttons_frame,
        text="Incorporate Feedback",
        command=lambda: retrain_with_feedback(app),
        bootstyle="success-outline"
    ).pack(side=tk.RIGHT, padx=(5, 0))

        
    # Right column - About
    about_frame = ttk.LabelFrame(
        right_col,
        text="About",
        bootstyle="info"
    )
    about_frame.pack(fill=tk.BOTH, expand=True)

    about_content = ttk.Frame(about_frame)
    about_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # App logo and name
    ttk.Label(
        about_content,
        text="🛡️",
        font=("Segoe UI", 30)
    ).pack(pady=(0, 5))

    ttk.Label(
        about_content,
        text="Phishing Detector",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=(0, 5))

    ttk.Label(
        about_content,
        text="Version 1.0.0",
        bootstyle="secondary"
    ).pack(pady=(0, 10))

    # Add this to the right column in setup_settings_tab
    feedback_frame = ttk.LabelFrame(
        right_col,
        text="Feedback History",
        bootstyle="info"
    )
    feedback_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

    feedback_content = ttk.Frame(feedback_frame)
    feedback_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Feedback history list
    columns = ("Timestamp", "Original", "Feedback", "Source")
    app.feedback_tree = ttk.Treeview(
        feedback_content,
        columns=columns,
        show="headings",
        bootstyle="info",
        height=5
    )

    # Configure columns
    for col in columns:
        app.feedback_tree.heading(col, text=col)
        width = 100 if col != "Source" else 150
        app.feedback_tree.column(col, width=width)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(feedback_content, orient="vertical", command=app.feedback_tree.yview)
    app.feedback_tree.configure(yscrollcommand=scrollbar.set)

    # Pack elements
    app.feedback_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Load feedback history
    load_feedback_history(app)

    # Load feedback button
    ttk.Button(
        feedback_content,
        text="Refresh Feedback History",
        command=lambda: load_feedback_history(app),
        bootstyle="info-outline"
    ).pack(pady=(10, 0))


    # Description
    description = "Advanced email security tool that uses machine learning to detect phishing attempts. Analyze emails, track suspicious URLs, and protect yourself from cyber threats."

    desc_label = ttk.Label(
        about_content,
        text=description,
        wraplength=300,
        justify="center"
    )
    desc_label.pack(pady=(0, 10))

    # Links
    links_frame = ttk.Frame(about_content)
    links_frame.pack(pady=(0, 5))

    ttk.Button(
        links_frame,
        text="Documentation",
        command=lambda: webbrowser.open("https://github.com/Sharawey74/phishing-detector"),
        bootstyle="link"
    ).pack(side=tk.LEFT, padx=5)

    ttk.Button(
        links_frame,
        text="Report Issue",
        command=lambda: webbrowser.open("https://github.com/Sharawey74/phishing-detector/issues"),
        bootstyle="link"
    ).pack(side=tk.LEFT, padx=5)

    # Copyright
    ttk.Label(
        about_content,
        text=f"© 2025 {app.current_user}",
        bootstyle="secondary",
        font=("Segoe UI", 8)
    ).pack(pady=(10, 0))

def train_new_model(app):
    """Train a new model"""
    app.update_status("Training new model...", "info")
    train_custom_model(app)
    
    # Update UI after training
    app.model_type_label.config(text=app.model_metadata.get("model_type", "Random Forest Classifier"))
    app.model_version_label.config(text=app.model_metadata.get("version", "1.0.0"))
    app.model_updated_label.config(text=app.model_metadata.get("last_updated", app.current_datetime))
    app.model_features_label.config(text=str(app.model_metadata.get("features_used", 10)))
    
    training_data = app.model_metadata.get("training_data_size", "Custom datasets")
    app.model_training_label.config(text=str(training_data))
    
    datasets = app.model_metadata.get("dataset_files", ["CEAS_08.csv", "Nigerian_Fraud.csv", "Nazario.csv"])
    datasets_text = "\n".join(datasets) if isinstance(datasets, list) else str(datasets)
    app.model_datasets_label.config(text=datasets_text)
    
    app.update_status("Model training complete", "success")