# Dockerised flask nlp app

Docker-based flask app for ML-assisted content moderation using open-source nhs.uk css
## pip installation outside docker
`conda create --name reviews python=3.8`
`conda activate reviews`

## Dependencies
`pip install -r requirements.txt`

## Tests
`python -m pytest` (this will catch any potential path issues with pytest as opposed to just `pytest`)

## Startup
`python src/app.py` for local flask app. Access at `localhost:80`

## Docker startup
`docker build . -t flasknlp:latest` to build image
`docker run -p 80:80 flasknlp:latest` to run image. access through `localhost:80` for the web frontend.

The productionised container uses the `/automoderator` endpoint to moderate comments as part of a larger cloud infrastructure.

### Devs
Please run `black` and then `flake8` on code before committing to catch formatting issues.