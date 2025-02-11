# Use the Python3.7.2 image
FROM python:3

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt & install it
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy jellyfinSort.py to working dir
COPY jellyfinSort.py .

# run app
CMD ["python", "jellyfinSort.py"]