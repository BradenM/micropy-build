FROM python:3.7-slim as builder

LABEL maintainer="bradenmars@bradenmars.me"
LABEL description="MicroPython ESP32 Build Dockerfile"

# Allow Args to Override Env
ARG REPO
ARG BRANCH
ARG IDF
ARG IDF_REPO
# Compat (Pycom Sigfox)
ARG PORT_PATH
ARG BOARD

ENV REPO ${REPO:-https://github.com/micropython/micropython.git}
ENV BRANCH ${BRANCH:-master}
ENV IDF ${IDF:-5c88c5996dbde6208e3bec05abc21ff6cd822d26}
ENV IDF_REPO ${IDF_REPO:-https://github.com/espressif/esp-idf.git}
ENV PORT_PATH ${PORT_PATH:-ports/esp32}
ENV BOARD ${BOARD:-GENERIC}


# Requirements
RUN apt-get update \
    && apt-get install -y gcc git wget make libncurses-dev flex bison gperf python3 python3-pip python-setuptools python-serial python-cryptography python-future python-pyelftools

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd micropython

# Python Reqs
RUN pip3 install pyserial pyparsing==2.3.1

# Fetch and Setup Repos
RUN mkdir -p esp && git clone $IDF_REPO esp-idf \
    && git clone $REPO micropython \
    && cd esp-idf && git checkout $IDF && git submodule update --init --recursive\
    && cd .. && cd micropython && git checkout $BRANCH && git pull origin $BRANCH\
    && chown -R micropython:micropython ../esp-idf ../micropython ../esp


FROM builder as toolkit

# Environment
USER micropython

ENV ESPIDF=/esp-idf
# Pycom Sigfox
ENV IDF_PATH=/esp-idf

# Build Mpy Cross & ESP32 Toolkit
RUN cd micropython && make -C mpy-cross
RUN cd micropython && git submodule init lib/berkeley-db-1.xx && git submodule update

RUN cd esp && wget https://dl.espressif.com/dl/xtensa-esp32-elf-linux64-1.22.0-98-g4638c4f-5.2.0-20190827.tar.gz
RUN cd esp && mkdir xtensa-esp32-elf\
    && tar -xzf ./xtensa-esp32-elf-linux64-1.22.0-98-g4638c4f-5.2.0-20190827.tar.gz -C ./xtensa-esp32-elf
ENV PATH=/esp/xtensa-esp32-elf/xtensa-esp32-elf/bin:$PATH

ENTRYPOINT [ "/bin/bash" ]

FROM toolkit as mpbuild

USER root

# Build ESP32 (Support Pycom Params)
RUN cd /micropython/${PORT_PATH}\
    && if [ "$BOARD" != "GENERIC" ]; then make -j5 BOARD=${BOARD} TARGET=boot\
    && make -j5 BOARD=${BOARD} TARGET=app;\
    else make; fi


RUN mkdir /mnt/dev
ENV PATH=/micropython/mpy-cross:$PATH


# Post-build Helpers
RUN apt-get update \
    && apt-get install -y usbutils picocom

# Setup Entrypoint
# Must copy entrypoint or build from parent dir with -f option
COPY ./docker-entrypoint.py /docker-entrypoint.py

ENTRYPOINT ["/usr/bin/python3", "/docker-entrypoint.py"]
