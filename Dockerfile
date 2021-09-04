FROM python3.9

RUN mkdir /usr/skedule
WORKDIR /usr/skedule

COPY . /usr/skedule/
RUN pip install poetry=1.1.8

RUN poetry install --no-dev

CMD ["python3", "main.py"]