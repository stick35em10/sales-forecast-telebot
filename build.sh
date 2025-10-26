#!/bin/bash
set -e
pip install --upgrade pip
pip install --only-binary=:all: -r requirements.txt
