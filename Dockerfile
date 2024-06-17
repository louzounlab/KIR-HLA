FROM python:3.7

WORKDIR /app

COPY app/requirements.txt .

RUN pip install -r requirements.txt

COPY app .

RUN pip install gunicorn

CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "app:app"]
