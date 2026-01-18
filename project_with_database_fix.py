import sqlite3
import pandas as pd
import os
import sys
import time
import wx
import shutil

# ============================================
# PyInstaller Database Handling
# ============================================

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_database_path():
    """Get writable path for database file"""
    # Check if running as PyInstaller exe
    if getattr(sys, 'frozen', False):
        # Running as compiled exe - use user's AppData folder
        app_data = os.path.join(os.environ['APPDATA'], 'GameCollection')
        if not os.path.exists(app_data):
            os.makedirs(app_data)
        db_path = os.path.join(app_data, 'collection.db')
        
        # Copy template database from bundled resources if it doesn't exist
        if not os.path.exists(db_path):
            template_db = resource_path('collection.db')
            if os.path.exists(template_db):
                shutil.copy2(template_db, db_path)
        
        return db_path
    else:
        # Running as Python script - use current directory
        return 'collection.db'

# Global database path - use this throughout the code
DB_PATH = get_database_path()

# ============================================
# Rest of your original code goes here
# Just replace 'collection.db' with DB_PATH
# ============================================

# For example, change this:
# conn = sqlite3.connect('collection.db')
# 
# To this:
# conn = sqlite3.connect(DB_PATH)

# And change this:
# if os.path.exists('collection.db'):
#
# To this:
# if os.path.exists(DB_PATH):
