FROM python:3.9

WORKDIR /report

COPY ./requirements.txt /report/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /report/requirements.txt

COPY ./app /report/app

CMD ["fastapi", "run", "app/app.py", "--port", "80"]