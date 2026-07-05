# Frontend (Streamlit) image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app ./streamlit_app
WORKDIR /app/streamlit_app

EXPOSE 8501

CMD ["streamlit", "run", "home.py", "--server.address=0.0.0.0", "--server.port=8501"]
