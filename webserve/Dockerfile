# slim for faster builds
FROM python:3.11.7-slim

# install the basic system deps we need
RUN apt-get update && apt-get install -y gnupg2 curl build-essential unixodbc-dev zip git
#set the shell
SHELL ["/bin/bash", "-c"]
# install pipx to make sure command line utils don't step on our project deps
RUN python3 -m pip install pipx
RUN source ~/.bashrc
RUN pipx ensurepath
RUN echo 'export PATH=$(python3 -m site --user-base)/bin:$PATH' >> ~/.bashrc
# use pipx to install poetry, ensures poetry deps don't conflict with deployed code
RUN PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install poetry
# expose the poetry command
RUN echo 'export PATH="$HOME/.poetry/bin:$PATH"' >> ~/.bashrc
RUN source ~/.bashrc
# not essential but matches a good patern for local dev
RUN poetry config virtualenvs.in-project true

WORKDIR /app
# add the two poetry env files we care about
COPY pyproject.toml poetry.lock .
# copy the project files
COPY . .
# install deps, only ones needed for a deployed run
RUN poetry install --without dev

RUN apt-get purge -y gnupg2 curl build-essential unixodbc-dev zip git

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "webserve.wsgi"]