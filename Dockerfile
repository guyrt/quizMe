FROM python:3.11

WORKDIR /app
# add the two poetry env files we care about
COPY pyproject.toml poetry.lock ./
# install deps, only ones needed for a deployed run
RUN poetry install --without dev
# testing removing the tools this way
RUN apt-get purge -y gnupg2 curl build-essential unixodbc-dev git

COPY webserve .

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "webserve.wsgi"]
