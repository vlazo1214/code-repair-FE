# Use an official Python image
FROM python:3.13

# Set the working directory
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements.txt .

RUN pip install --upgrade pip --root-user-action=ignore

# Install dependencies
RUN pip install --no-cache-dir -r  requirements.txt --root-user-action=ignore

# Copy the rest of the application code
COPY . .

# Expose the port Gradio runs on
EXPOSE 7860

# Command to run the Gradio app
CMD ["python", "main.py"]
