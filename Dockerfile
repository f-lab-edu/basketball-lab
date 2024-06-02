FROM python:3.12

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

EXPOSE 8000

CMD ["python", "-m", "uvicorn","--host", "0.0.0.0", "--port", "8000", "app.main:app"]

