FROM python:3.10-slim

WORKDIR /app

RUN apt-get update 
RUN pip install --upgrade pip
RUN pip install poetry

COPY pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root --no-ansi

COPY README.md /app/
COPY app.py /app/
RUN mkdir /app/files/
RUN mkdir /app/config/
COPY alembic.ini /app/
COPY trackme/ /app/trackme/ 
COPY run.sh /app/
RUN chmod +x run.sh
EXPOSE 5000

CMD ["./run.sh"]
