#!/bin/sh
export STREAMLIT_WATCHER_IGNORE_MODULES=torch
uv pip install streamlit
streamlit run src/app.py "$@"