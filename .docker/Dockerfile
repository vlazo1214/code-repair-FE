# Use an official Python image
FROM python:3.13

# Set the working directory
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements.txt .

RUN pip install --upgrade pip 

# Install dependencies
RUN pip install --no-cache-dir -r --root-user-action requirements.txt 

# Copy the rest of the application code
COPY . .

# Expose the port Gradio runs on
EXPOSE 7860

# Command to run the Gradio app
CMD ["python", "interface.py"]
