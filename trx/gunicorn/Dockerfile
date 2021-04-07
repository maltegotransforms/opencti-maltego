FROM python:3.8-slim

RUN mkdir /var/www/
RUN mkdir /var/www/TRX/
WORKDIR /var/www/TRX/

# System dependencies
RUN apt-get update
RUN apt-get install -y --no-install-recommends libmagic1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Install Gunicorn for running production server
RUN pip3 install gunicorn gevent

COPY . /var/www/TRX/

RUN chown -R www-data:www-data /var/www/TRX/

CMD ["python3", "project.py", "runserver"]
