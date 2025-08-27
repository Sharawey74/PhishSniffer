# GUI Components

This folder contains all the Streamlit-based GUI components for PhishSniffer.

## Structure

- `main_window.py` - Main application entry point and navigation
- `analyze_tab.py` - Email analysis interface
- `report_tab.py` - Reports and analytics dashboard
- `urls_tab.py` - URL management interface
- `settings_tab.py` - Settings and configuration
- `main_window_tabbed.py` - Alternative tabbed interface
- `splash_screen.py` - Application splash screen
- `.streamlit/` - Streamlit configuration files

## Configuration

The `.streamlit/` folder contains configuration files for the Streamlit application:

- `config.toml` - Main Streamlit configuration
  - Theme settings (colors, fonts)
  - Server configuration
  - Browser settings
  - Logger configuration

## Usage

The GUI is launched through the main application entry points:

1. **Development**: `python streamlit_app.py` (from project root)
2. **Production**: `streamlit run streamlit_app.py` (from project root)
3. **Direct**: `python gui/main_window.py` (for testing)

## Theme Customization

The application uses a custom theme defined in `.streamlit/config.toml`:

- Primary Color: `#FF6B6B` (Coral Red)
- Background: `#FFFFFF` (White)
- Secondary Background: `#F0F2F6` (Light Gray)
- Text Color: `#262730` (Dark Gray)

## Development Notes

- All GUI components are modular and can be imported independently
- The main window handles navigation and app state
- Each tab is responsible for its own functionality
- Configuration is centralized in the `.streamlit/` folder
