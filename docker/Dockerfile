FROM python:3.7

RUN mkdir /data

RUN pip install --upgrade pip
RUN pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system

WORKDIR /app/app

CMD uvicorn server:app --host 0.0.0.0 --port 8000 --reload
