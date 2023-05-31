#!/bin/sh

# pull latest code
git pull

# set pipenv path
if [[ -f "$HOME/.pyenv/shims/pipenv" ]]; then
  pipenv="$HOME/.pyenv/shims/pipenv"
elif [[ -f "$HOME/.local/bin/pipenv" ]]; then
  pipenv="$HOME/.local/bin/pipenv"
elif [[ -f "/opt/homebrew/bin/pipenv" ]]; then
  pipenv="/opt/homebrew/bin/pipenv"
elif [[ -f "/usr/local/bin/pipenv" ]]; then
  pipenv="/usr/local/bin/pipenv"
else
  echo "pipenv application not found"
fi

rm -rf .venv
rm Pipfile.lock
$pipenv install
$pipenv run pip install git+https://github.com/bxdoan/dongle-lte-api.git
