import os
import json
import traceback

def load_analysis_history(history_file):
    """Load analysis history from file"""
    try:
        # Initialize empty history if file doesn't exist
        if not os.path.exists(history_file):
            with open(history_file, 'w') as file:
                json.dump([], file)
            history = []
        else:
            # Try to load existing history
            try:
                with open(history_file, 'r') as file:
                    # Create empty file if reading fails
                    file_content = file.read().strip()
                    if not file_content:
                        history = []
                    else:
                        history = json.loads(file_content)
            except json.JSONDecodeError as e:
                print(f"Error loading history: {e}")
                # Reset history file if corrupted
                with open(history_file, 'w') as file:
                    json.dump([], file)
                history = []

        return history

    except Exception as e:
        print(f"Error loading history: {e}")
        traceback.print_exc()
        # Reset history file if general error
        try:
            with open(history_file, 'w') as file:
                json.dump([], file)
        except:
            pass
        return []

def update_analysis_history(history_file, source, current_datetime, is_phishing, probability):
    """Update analysis history with new result"""
    try:
        # Load current history
        history = load_analysis_history(history_file)

        # Create entry using primitive types for JSON compatibility
        entry = {
            'source': source,
            'timestamp': current_datetime,
            'is_phishing': 1 if is_phishing else 0,  # Use integers instead of booleans
            'probability': float(probability)  # Ensure it's a float
        }

        # Add to history (keep most recent 10)
        history.insert(0, entry)
        if len(history) > 10:
            history = history[:10]

        # Save history
        with open(history_file, 'w') as file:
            json.dump(history, file)

        return history

    except Exception as e:
        print(f"Error saving history: {e}")
        traceback.print_exc()
        return []