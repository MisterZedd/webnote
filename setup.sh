#!/bin/bash

# Create project directories
mkdir -p static/images
mkdir -p templates
mkdir -p data
mkdir -p lib

# Copy static files
echo "Copying static files..."
cp objects.js static/
cp webnote.js static/
cp style.css static/
cp wp-layout.css static/
cp strings.js.en static/
cp strings.js.de static/
cp index.html static/
cp FAQ.html static/
cp hints.html static/

# Copy image files
echo "Copying image files..."
cp -r images/* static/images/

# Copy PyRSS2Gen library
echo "Setting up PyRSS2Gen library..."
mkdir -p lib/PyRSS2Gen-1.1-py2.7.egg-info
cp lib/PyRSS2Gen.py lib/
cp lib/__init__.py lib/

# Copy template files
echo "Copying template files..."
cp templates/workspace.html templates/

echo "Setup complete!"