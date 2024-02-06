

```
sudo apt install software-properties-common
 
sudo add-apt-repository ppa:deadsnakes/ppa
 
sudo apt update

 
sudo apt install python3.11
sudo apt install python3.11-venv

python3.11 -m venv "secdata"
source secdata/bin/activate

```

With switch to poetry the above may nolonger be valid:
- install [pipx](https://pipx.pypa.io/latest/installation/) for isolation of CLI tools. 
- ensure pipx command is available
```shell
pipx ensurepath
```
- install [poetry](https://python-poetry.org/docs/) 
```shell
pipx install poetry
```
- set venv location to in-project
```shell
 poetry config virtualenvs.in-project true
```
- install poetry managed deps:
```shell
poetry install
```