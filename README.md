# Webnote - Self-Hosted Edition

A port of the Webnote application to be self-hosted on your own server. This version has been adapted from the original Google App Engine implementation to run on a standard web server using Flask.

## Features

- Create and manage digital sticky notes in a workspace
- Share workspaces with others
- Support for different note colors
- Basic formatting and HTML/link support in notes
- Version history for workspaces
- RSS feeds for workspaces

## Setup Instructions

### Option 1: Docker (Recommended)

1. Clone this repository
2. Run the setup script to organize files:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```
3. Modify docker-compose.yml with your settings if needed
4. Start the application:
   ```
   docker-compose up -d
   ```
5. Access the application at http://your-server-ip:5000/webnote/

### Option 2: Direct Installation

1. Clone this repository
2. Create a Python virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the setup script:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```
5. Set environment variables (create a .env file):
   ```
   FLASK_APP=app.py
   DATABASE_URI=sqlite:///data/webnote.db
   SECRET_KEY=your-secret-key
   HELPEMAIL=your-email@example.com
   DEBUG=0
   NUM_DATES=10
   TIMEZONE=US/Eastern
   ```
6. Run the application:
   ```
   flask run --host=0.0.0.0
   ```
7. Access the application at http://your-server-ip:5000/webnote/

### Option 3: Run on Proxmox

You can run this application on Proxmox using either:

1. An LXC container with Docker installed (using Docker Compose)
2. A full VM with Docker or direct installation
3. An LXC container with direct installation

## Data Storage

By default, the application stores data in an SQLite database located in the `data` directory. This directory is mounted as a volume in the Docker container to ensure data persistence.

For production use, consider:
- Using a more robust database like PostgreSQL
- Setting up regular backups of the data directory
- Putting the application behind a reverse proxy like Nginx with HTTPS

## Configuration

Configuration is handled through environment variables:

- `DATABASE_URI`: Database connection string
- `SECRET_KEY`: Flask secret key for sessions
- `HELPEMAIL`: Email address shown for support
- `DEBUG`: Enable debug mode (0 or 1)
- `NUM_DATES`: Number of history versions to show
- `TIMEZONE`: Timezone for displaying dates

## Customization

You can customize the application by modifying the static files in the `static` directory and the templates in the `templates` directory.