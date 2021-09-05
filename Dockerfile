FROM python:3.9

RUN mkdir /usr/skedule
WORKDIR /usr/skedule

COPY . /usr/skedule/
RUN pip install SQLAlchemy==1.4.20 requests==2.25.1 python-telegram-bot==13.7 jproperties==2.1.0 mariadb==1.0.7 DateTimeRange==1.2.0 loguru=0.5.3

CMD ["python3", "main.py"]