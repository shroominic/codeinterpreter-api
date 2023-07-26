from python:3.9.17-slim
WORKDIR /app
copy . .
RUN pip install --upgrade pip
RUN pip install redis
RUN pip install .
# RUN pip install -r requirements.txt
CMD ["streamlit", "run", "frontend/app.py"]