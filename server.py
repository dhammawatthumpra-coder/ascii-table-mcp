#!/usr/bin/env python3
"""Thin wrapper — runs ascii_table_mcp package as `python server.py` or `python -m ascii_table_mcp`."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ascii_table_mcp import main
main()
