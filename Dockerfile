FROM python:3.11

RUN apt-get update && apt-get install -y redis-server

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

COPY start.sh /app/
RUN chmod +x /app/start.sh

EXPOSE 5000

ENV FLASK_APP=run.py

CMD ["/app/start.sh"]
