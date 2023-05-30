FROM python:3.8

WORKDIR /app

COPY project/techtrends .

RUN pip install -r requirements.txt

RUN python init_db.py

CMD ["python", "app.py"]

EXPOSE 3111
