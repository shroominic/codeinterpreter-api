from python:3.9.17-slim
WORKDIR /app
copy requirements.txt .
RUN pip install --upgrade pip
RUN pip install codeinterpreterapi
# RUN pip install -r requirements.txt
CMD ["streamlit", "run", "frontend/app.py"]