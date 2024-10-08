FROM debian:sid
RUN echo 'deb http://mirror.psu.ac.th/debian/ sid main contrib non-free non-free-firmware' > /etc/apt/sources.list
RUN echo 'deb http://mirror.kku.ac.th/debian/ sid main contrib non-free non-free-firmware' >> /etc/apt/sources.list

RUN apt-get update && apt-get upgrade -y

RUN apt install -y python3 python3-dev python3-pip python3-venv npm git locales cmake
RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8 
# ENV LC_ALL en_US.UTF-8



RUN python3 -m venv /venv
ENV PYTHON=/venv/bin/python3
RUN $PYTHON -m pip install wheel poetry gunicorn

WORKDIR /app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="${PYTHONPATH}:/app/detectron2"

ENV VISAI_SETTINGS=/app/visai-production.cfg

COPY visai/cmd /app/visai/cmd
COPY poetry.lock pyproject.toml /app/

RUN . /venv/bin/activate \
	&& poetry config virtualenvs.create false \
	&& poetry install --no-interaction --only main

COPY visai/web/static/package.json visai/web/static/package-lock.json visai/web/static/
RUN npm install --prefix visai/web/static

COPY . /app
