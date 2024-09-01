# zapbot

## How to run

First we need to run wppconnect-server, with a custom password.

Create `.env` and `docker/wppconfig.js` from their respective samples, and change the token that says `PUT_YOUR_KEY_HERE` to some random string.

Then build and start wppconnect-server (see `scripts` folder)

The create a pyenv virtualenv for this project with pyenv

```
pyenv virtualenv zapzap
```

install the stuff in `requirements.txt` and run `app/main.py`