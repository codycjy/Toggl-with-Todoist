FROM python:3.9-slim

WORKDIR /app


COPY requirements.txt .
RUN pip3 install -r requirements.txt \
    -i  https://mirrors.bfsu.edu.cn/pypi/web/simple

EXPOSE 8501

COPY . .

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
