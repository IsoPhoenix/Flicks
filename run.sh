#!/bin/bash
cd venv/bin
. activate
cd ../..
export FLASK_APP=index.py
export FLASK_ENV=development
flask run