FROM python:3.10-slim

ARG TESTING=0

# update
RUN set -ex \
    && apt-get update

# Install build tools.
RUN set -ex \
    && apt-get install --yes --no-install-suggests --no-install-recommends \
      wget \
      git \
      cmake \
      gfortran \
      git \
      make
#
# Install build-time dependencies.
RUN set -ex \
    && apt-get install --yes --no-install-suggests --no-install-recommends \
      libproj-dev \
      libgeos-dev \
      libeccodes-dev

# Install ecbuild
ARG ECBUILD_VERSION=2021.08.0
RUN set -eux \
    && mkdir -p /src/ \
    && cd /src \
    && git clone https://github.com/ecmwf/ecbuild.git \
    && cd ecbuild \
    && git checkout ${ECBUILD_VERSION} \
    && mkdir -p /build/ecbuild \
    && cd /build/ecbuild \
    && cmake /src/ecbuild -DCMAKE_BUILD_TYPE=Release \
    && make -j4 \
    && make install

# Install eccodes
# requires ecbuild
ARG ECCODES_VERSION=2.25.0
RUN set -eux \
    && mkdir -p /src/ \
    && cd /src \
    && git clone https://github.com/ecmwf/eccodes.git \
    && cd eccodes \
    && git checkout ${ECCODES_VERSION} \
    && mkdir -p /build/eccodes \
    && cd /build/eccodes \
    && /usr/local/bin/ecbuild /src/eccodes -DECMWF_GIT=https -DCMAKE_BUILD_TYPE=Release \
    && make -j4 \
    && make install \
    && /sbin/ldconfig


RUN apt-get remove --yes wget \
      git \
      cmake \
      gfortran \
      git \
      make
RUN apt-get clean
RUN apt-get autoremove --yes

# copy files
COPY setup.py app/setup.py
COPY README.md app/README.md
COPY requirements.txt app/requirements.txt

# install requirements
RUN pip install -r app/requirements.txt

# copy library files
COPY metofficedatahub/ app/metofficedatahub/
COPY tests/ app/tests/

# change to app folder
WORKDIR /app

# install library
RUN pip install -e .

RUN if [ "$TESTING" = 1 ]; then pip install pytest; fi

# Example commnad that can be used, need to set API_KEY, API_SECRET and SAVE_DIR
CMD ["python", "-u","metofficedatahub/app.py"]
