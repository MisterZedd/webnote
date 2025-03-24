FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create volume mount points for data persistence
VOLUME ["/app/data"]

# Set environment variables
ENV FLASK_APP=app.py
ENV DATABASE_URI=sqlite:////app/data/webnote.db
ENV SECRET_KEY=change-this-in-production
ENV HELPEMAIL=youremail@example.com
ENV DEBUG=0
ENV NUM_DATES=10
ENV TIMEZONE=US/Eastern

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]