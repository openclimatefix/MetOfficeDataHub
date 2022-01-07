FROM python:3.9-slim

RUN apt-get -qq update \
    && apt-get -qq install -y --no-install-recommends \
        libproj-dev \
        libgeos-dev \
        libeccodes-tools \
    && apt-get autoclean && apt-get autoremove \
    > /dev/null

# copy files
COPY setup.py app/setup.py
COPY README.md app/README.md
COPY requirements.txt app/requirements.txt

# install requirements
RUN pip install -r app/requirements.txt

# copy library files
COPY metofficedatahub/ app/metofficedatahub/

# change to app folder
WORKDIR /app

# install library
RUN pip install -e .

# Example commnad that can be used, need to set API_KEY, API_SECRET and SAVE_DIR
CMD ["python", "-u","metofficedatahub/app.py"]
