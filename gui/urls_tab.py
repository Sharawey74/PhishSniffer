import tkinter as tk
from tkinter import filedialog, StringVar
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
import csv
import json
import traceback
from storage.urls import save_suspicious_urls


def setup_urls_tab(app):
    """Set up the suspicious URLs tab"""
    container = ttk.Frame(app.urls_tab)
    container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    print("Setting up URLs tab")  # Debug print
    
    # Top control panel
    control_panel = ttk.Frame(container)
    control_panel.pack(fill=tk.X, pady=(0, 15))
    
    # Title label
    ttk.Label(
        control_panel,
        text="Suspicious URLs Management",
        font=("Segoe UI", 16, "bold")
    ).pack(anchor=tk.W)
    
    # Control buttons
    buttons_frame = ttk.Frame(control_panel)
    buttons_frame.pack(fill=tk.X, pady=10)
    
     # Add URL button - NEW
    ttk.Button(
        buttons_frame,
        text="Add URL",
        command=lambda: add_url_dialog(app),
        bootstyle="success"
    ).pack(side=tk.LEFT, padx=(0, 5))
    
    # Remove button with direct function call to verify it's working
    ttk.Button(
        buttons_frame,
        text="Remove Selected",
        command=lambda: remove_selected_url(app),
        bootstyle="danger"
    ).pack(side=tk.LEFT, padx=(5, 5))
    
    # Export button
    ttk.Button(
        buttons_frame,
        text="Export List",
        command=lambda: export_urls(app),
        bootstyle="info"
    ).pack(side=tk.LEFT, padx=(5, 0))
    
    # URLs treeview
    columns = ("ID", "URL", "Source", "Date Added", "Risk Level")
    app.url_tree = ttk.Treeview(
        container,
        columns=columns,
        show="headings",
        bootstyle="danger"
    )
    
    # Configure columns
    app.url_tree.heading("ID", text="#")
    app.url_tree.column("ID", width=50)
    
    app.url_tree.heading("URL", text="URL")
    app.url_tree.column("URL", width=300)
    
    app.url_tree.heading("Source", text="Source")
    app.url_tree.column("Source", width=150)
    
    app.url_tree.heading("Date Added", text="Date Added")
    app.url_tree.column("Date Added", width=150)
    
    app.url_tree.heading("Risk Level", text="Risk Level")
    app.url_tree.column("Risk Level", width=100)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=app.url_tree.yview)
    app.url_tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack elements
    app.url_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Display any existing suspicious URLs
    display_suspicious_urls(app)

def remove_selected_url_direct(app):
    """Direct function to test URL removal"""
    print("Direct remove function called")
    # Get selected item
    selected = app.url_tree.selection()
    if not selected:
        print("No item selected")
        return
    
    # Get URL info
    item_id = selected[0]
    values = app.url_tree.item(item_id, "values")
    print(f"Selected values: {values}")
    
    # Delete directly from treeview to test basic functionality
    app.url_tree.delete(item_id)
    print("Item deleted from treeview")

def print_debug_info(app):
    """Print debug information about URLs"""
    print(f"Number of URLs in suspicious_urls: {len(app.suspicious_urls)}")
    print(f"URLs file path: {app.urls_file}")
    print(f"Selected items: {app.url_tree.selection()}")
    for i, url in enumerate(app.suspicious_urls):
        print(f"URL {i}: {url.get('url')}")

def display_suspicious_urls(app):
    """Display suspicious URLs in the treeview"""
    # Check if the treeview exists
    if not hasattr(app, 'url_tree'):
        return
        
    # Clear existing items
    for item in app.url_tree.get_children():
        app.url_tree.delete(item)

    # Add URLs to the treeview
    for i, url_entry in enumerate(app.suspicious_urls):
        values = (
            str(i + 1),
            url_entry.get('url', ''),
            url_entry.get('source', ''),
            url_entry.get('date_added', ''),
            url_entry.get('risk_level', '')
        )

        app.url_tree.insert('', 'end', text=str(i + 1), values=values)
        
    # Update the tree display immediately
    app.url_tree.update()
    
def add_url_dialog(app):
    """Show dialog to manually add a suspicious URL"""
    # Create dialog window
    dialog = ttk.Toplevel(app.root)
    dialog.title("Add Suspicious URL")
    dialog.geometry("500x300")

    # Center the dialog
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width - 500) // 2
    y = (screen_height - 300) // 2
    dialog.geometry(f"500x300+{x}+{y}")

    # Make it modal
    dialog.transient(app.root)
    dialog.grab_set()

    # Content
    content_frame = ttk.Frame(dialog)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    ttk.Label(
        content_frame,
        text="Add Suspicious URL",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=(0, 15))

    # URL input
    url_frame = ttk.Frame(content_frame)
    url_frame.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(
        url_frame,
        text="URL:",
        width=10
    ).pack(side=tk.LEFT)

    url_var = StringVar()
    url_entry = ttk.Entry(
        url_frame,
        textvariable=url_var,
        width=50
    )
    url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    url_entry.focus()

    # Source input
    source_frame = ttk.Frame(content_frame)
    source_frame.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(
        source_frame,
        text="Source:",
        width=10
    ).pack(side=tk.LEFT)

    source_var = StringVar(value="Manual entry")
    source_entry = ttk.Entry(
        source_frame,
        textvariable=source_var,
        width=50
    )
    source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Risk level
    risk_frame = ttk.Frame(content_frame)
    risk_frame.pack(fill=tk.X, pady=(0, 15))

    ttk.Label(
        risk_frame,
        text="Risk Level:",
        width=10
    ).pack(side=tk.LEFT)

    risk_var = StringVar(value="Medium")
    risk_combo = ttk.Combobox(
        risk_frame,
        textvariable=risk_var,
        values=["Low", "Medium", "High", "Critical"],
        width=15
    )
    risk_combo.pack(side=tk.LEFT)

    # Buttons
    button_frame = ttk.Frame(content_frame)
    button_frame.pack(fill=tk.X, pady=(15, 0))

    ttk.Button(
        button_frame,
        text="Cancel",
        bootstyle="secondary",
        command=dialog.destroy
    ).pack(side=tk.RIGHT, padx=(10, 0))

    ttk.Button(
        button_frame,
        text="Add URL",
        bootstyle="primary",
        command=lambda: add_url_from_dialog(app, url_var.get(), source_var.get(), risk_var.get(), dialog)
    ).pack(side=tk.RIGHT)

def add_url_from_dialog(app, url, source, risk_level, dialog):
    """Add URL from dialog input"""
    if not url:
        Messagebox.show_warning("Please enter a URL", "Missing URL")
        return

    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    try:
        # Create URL entry
        url_entry = {
            'url': url,
            'source': source,
            'date_added': app.current_datetime,
            'risk_level': risk_level
        }

        # Add to list and save
        app.suspicious_urls.append(url_entry)
        save_suspicious_urls(app.urls_file, app.suspicious_urls)

        # Update display
        display_suspicious_urls(app)

        # Close dialog
        dialog.destroy()

        app.update_status(f"Added suspicious URL: {url}", "info")

    except Exception as e:
        print(f"Error adding URL: {e}")
        traceback.print_exc()
        Messagebox.show_error(f"Error adding URL: {str(e)}", "Error")

def remove_selected_url(app):
    """Remove selected URL from the list"""
    print("Remove Selected URL button clicked!")
    
    # Get selected item
    selected = app.url_tree.selection()

    if not selected:
        Messagebox.show_info("Please select a URL to remove", "No Selection")
        return

    try:
        # Get URL from the selected item
        item_id = selected[0]
        values = app.url_tree.item(item_id, "values")
        
        # Debug information
        print(f"Selected item: {selected}")
        print(f"Values: {values}")
        
        if not values or len(values) < 2:
            Messagebox.show_error("Error retrieving URL information", "Error")
            return
            
        # Extract URL from values (index 1 is the URL column)
        url_to_remove = values[1]
        
        # Confirm deletion
        confirm = Messagebox.show_question(
            f"Are you sure you want to remove the URL:\n{url_to_remove}",
            "Confirm Removal"
        )
        
        if confirm != "yes":
            return
            
        # Find and remove from data structure
        found = False
        for i, url_entry in enumerate(app.suspicious_urls):
            if url_entry.get('url', '') == url_to_remove:
                app.suspicious_urls.pop(i)
                found = True
                break
        
        if not found:
            print(f"URL not found in data: {url_to_remove}")
            Messagebox.show_warning("URL not found in database", "Warning")
            return
            
        # Save the updated list
        # Direct implementation instead of importing
        import json
        import os
        
        os.makedirs(os.path.dirname(app.urls_file), exist_ok=True)
        with open(app.urls_file, 'w') as file:
            json.dump(app.suspicious_urls, file, indent=2, default=str)
        
        # Update the display
        app.url_tree.delete(item_id)
        
        # Update status
        app.update_status(f"Removed URL: {url_to_remove}", "success")
        
    except Exception as e:
        print(f"Error removing URL: {str(e)}")
        traceback.print_exc()
        Messagebox.show_error(f"Error removing URL: {str(e)}", "Error")

def export_urls(app):
    """Export suspicious URLs to a file"""
    if not app.suspicious_urls:
        Messagebox.show_info("No URLs to export", "Export URLs")
        return

    # Get a file path to save to
    file_path = filedialog.asksaveasfilename(
        title="Export URLs",
        filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")],
        defaultextension=".csv"
    )

    if not file_path:
        return

    try:
        # Export based on file extension
        if file_path.endswith('.csv'):
            export_urls_csv(app, file_path)
        elif file_path.endswith('.json'):
            export_urls_json(app, file_path)
        else:
            export_urls_csv(app, file_path)  # Default to CSV

        app.update_status(f"Exported URLs to {file_path.split('/')[-1]}", "success")

    except Exception as e:
        print(f"Error exporting URLs: {e}")
        traceback.print_exc()
        Messagebox.show_error(
            f"Error exporting URLs: {str(e)}",
            "Export Error"
        )

def export_urls_csv(app, file_path):
    """Export URLs to CSV file"""
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow(['URL', 'Source', 'Date Added', 'Risk Level'])

        # Write data
        for url_entry in app.suspicious_urls:
            writer.writerow([
                url_entry.get('url', ''),
                url_entry.get('source', ''),
                url_entry.get('date_added', ''),
                url_entry.get('risk_level', '')
            ])

def export_urls_json(app, file_path):
    """Export URLs to JSON file"""
    with open(file_path, 'w') as file:
        json.dump(app.suspicious_urls, file, indent=2)