# ESP32 Micropython Dockerfile

FROM python:3.7-slim as builder

LABEL maintainer="Braden Mars <bradenmars@bradenmars.me>"
LABEL description="MicroPython ESP32 Build Dockerfile"
LABEL org.opencontainers.image.source="https://github.com/bradenm/micropy-build"

# Allow Args to Override Env
ARG REPO
ARG BRANCH
ARG IDF
ARG IDF_REPO

# Environment
ENV REPO ${REPO:-https://github.com/micropython/micropython.git}
ENV BRANCH ${BRANCH:-master}
ENV IDF ${IDF:-5c88c5996dbde6208e3bec05abc21ff6cd822d26}
ENV IDF_REPO ${IDF_REPO:-https://github.com/espressif/esp-idf.git}

# Requirements
RUN apt-get update \
    && apt-get install -y \
    gcc \
    git \
    wget \
    make \
    cmake \
    libncurses-dev \
    flex \
    bison \
    gperf \
    python3 \
    python3-pip \
    python-setuptools \
    python-serial \
    python-cryptography \
    python-future \
    python-pyelftools

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd micropython

# Python Reqs
RUN pip3 install pyserial pyparsing==2.3.1

SHELL ["/bin/bash", "-c"]

# Fetch and Setup Repos
RUN mkdir -p esp && git clone $IDF_REPO esp-idf \
    && git clone $REPO micropython \
    && cd esp-idf \
    && git checkout $IDF \
    && git submodule update --init \
        components/bt/controller/lib \
        components/bt/host/nimble/nimble \
        components/esp_wifi \
        components/esptool_py/esptool \
        components/lwip/lwip \
        components/mbedtls/mbedtls \
    # @see https://github.com/pfalcon/pycopy/issues/48
    && if [[ $REPO == *"pycopy"* ]]; then (cd components/mbedtls/; rm -rf mbedtls; git clone -b mbedtls-2.16.5-idf-pycopy https://github.com/pfalcon/mbedtls/; cd mbedtls; git log -n1; cd ../../../); fi\
    && cd .. && cd micropython && git checkout $BRANCH && git pull origin $BRANCH\
    && chown -R micropython:micropython ../esp-idf ../micropython ../esp


ARG BOARD
FROM builder as toolkit

ARG NUM_PROC

ENV NUM_PROC ${NUM_PROC:-4}

# Post-build Helpers
RUN apt-get update \
    && apt-get install -y usbutils picocom \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER micropython

ENV ESPIDF=/esp-idf
# Pycom Sigfox
ENV IDF_PATH=/esp-idf

# Build Mpy Cross & ESP32 Toolkit
RUN cd micropython && make -j"$NUM_PROC" -C mpy-cross
RUN cd micropython && git submodule init lib/berkeley-db-1.xx && git submodule update

ENTRYPOINT [ "/bin/bash" ]


FROM toolkit as mpbuild

## Compat (Pycom Sigfox)
ARG PORT_PATH
ARG BOARD
ARG BRANCH
ARG NUM_PROC

# Environment
ENV PORT_PATH ${PORT_PATH:-ports/esp32}
ENV BOARD ${BOARD:-GENERIC}
ENV BRANCH ${BRANCH:-master}
ENV NUM_PROC ${NUM_PROC:-4}

USER root

# Copy Modules
COPY ./modules /pymodules

# Setup Entrypoint
# Must copy entrypoint or build from parent dir with -f option
COPY ./docker-entrypoint.py /docker-entrypoint.py


# Build ESP32 (Support Pycom Params)
RUN cd /micropython/${PORT_PATH}\
    && ls modules\
    && source /esp-idf/export.sh \
    && if [[ $REPO == *"pycopy"* ]]; then make -j"$NUM_PROC" submodules ; fi\
    && if [ "$BOARD" != "GENERIC" ]; then make -j"$NUM_PROC" BOARD=${BOARD} TARGET=boot\
    && make -j"$NUM_PROC" BOARD=${BOARD} TARGET=app;\
    else /usr/bin/python3 /docker-entrypoint.py build; fi

RUN mkdir /mnt/dev
ENV PATH=/micropython/mpy-cross:$PATH


ENTRYPOINT ["/usr/bin/python3", "/docker-entrypoint.py"]
