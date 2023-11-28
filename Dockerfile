FROM python:3.10-slim

WORKDIR /code

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

WORKDIR /code/src

CMD ["flask", "--app", "main", "run", "--host=0.0.0.0", "--port=80"]