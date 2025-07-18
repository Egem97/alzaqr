FROM python:3.12-slim

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y apt-transport-https\
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8501


ENTRYPOINT ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]