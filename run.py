#!/usr/bin/env python3
"""
Main entry point for Jadwal Dokter Converter Application
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from app.main import main

if __name__ == "__main__":
    main()
