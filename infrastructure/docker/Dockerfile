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
COPY metofficeamd/ app/metofficeamd/

# change to app folder
WORKDIR /app

# install library
#RUN pip uninstall cfgrib
#RUN pip install ecmwflibs
#RUN pip install eccodes==1.3.1
#RUN pip install cfgrib
RUN pip install -e .

# Example commnad that can be used, need to set API_KEY, API_SECRET and SAVE_DIR
CMD ["python", "-u","metofficeamd/app.py"]
