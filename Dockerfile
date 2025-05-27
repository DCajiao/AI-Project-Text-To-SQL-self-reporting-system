FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y git libglib2.0-0 libsm6 libxrender1 libxext6 gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 8501

COPY ./src/ .
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
