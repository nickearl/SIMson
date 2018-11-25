# Use lightweight python image
FROM python:3-alpine

# Set working dir to current dir
WORKDIR /app

COPY . /app

RUN pip install --trusted-host pypi.python.org -r python/requirements.txt

CMD ["python", "bin/SIMson.py"]