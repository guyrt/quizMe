FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY webserve .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "webserve.wsgi"]
