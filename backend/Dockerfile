FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT ["/app/for_docker.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:9090", "foodgram.wsgi"]