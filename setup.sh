#!/bin/bash

VENV_DIR=".venv"

python3 -m pip install virtualenv

if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

python3 -m pip install --upgrade pip setuptools wheel

python3 -m pip install --upgrade -r requirements.txt
