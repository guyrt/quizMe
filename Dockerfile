# slim base image
FROM python:3.11-slim as builder

# install the basic system deps we need (for building)
RUN apt-get update && apt-get install -y gnupg2 unixodbc-dev zip git

# set the shell and add pipx to your image
SHELL ["/bin/bash", "-c"]
RUN python3 -m pip install pipx
RUN source ~/.bashrc
RUN pipx ensurepath
RUN echo 'export PATH=$(python3 -m site --user-base)/bin:$PATH' >> ~/.bashrc

# use a new stage for the final image
FROM python:3.11-slim as runtime

# remove unnecessary packages from your runtime image
RUN apt-get update && apt-get purge -y --yes gnupg2 curl build-essential unixodbc-dev zip git

# set the working directory and install dependencies (poetry) in the final image
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry config virtualenvs.in-project true && poetry install --without dev

# copy your application code
COPY webserve .

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "webserve.wsgi"]