FROM python:3.9-slim
RUN apt-get update && apt-get install -y git iputils-ping
WORKDIR /app
COPY geometric_lib/ ./geometric_lib/ 
COPY script.py .
CMD ["python", "script.py"]