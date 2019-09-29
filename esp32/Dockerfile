FROM ubuntu:18.04

LABEL maintainer="bradenmars@bradenmars.me"
LABEL description="MicroPython ESP32 Build Dockerfile"

ARG REPO=https://github.com/micropython/micropython.git
ARG BRANCH=master
ARG IDF=5c88c5996dbde6208e3bec05abc21ff6cd822d26
ARG IDF_REPO=https://github.com/espressif/esp-idf.git

# Requirements
RUN apt-get update \
    && apt-get install -y gcc git wget make libncurses-dev flex bison gperf python3 python3-pip python-setuptools python-serial python-cryptography python-future python-pyparsing python-pyelftools

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd micropython

# Python Reqs
RUN pip3 install pyserial pyparsing

# Fetch and Setup Repos
RUN mkdir -p esp && git clone $IDF_REPO esp-idf \
    && git clone $REPO micropython \
    && cd esp-idf && git checkout $IDF && git submodule update --init --recursive\
    && cd .. && cd micropython && git checkout $BRANCH && git pull origin $BRANCH\
    && chown -R micropython:micropython ../esp-idf ../micropython ../esp


# Environment
USER micropython

ENV ESPIDF=/esp-idf

# Build
RUN cd micropython && make -C mpy-cross
RUN cd micropython && git submodule init lib/berkeley-db-1.xx && git submodule update

RUN cd esp && wget https://dl.espressif.com/dl/xtensa-esp32-elf-linux64-1.22.0-80-g6c4433a-5.2.0.tar.gz
RUN cd esp && mkdir xtensa-esp32-elf\
    && tar -xzf ./xtensa-esp32-elf-linux64-1.22.0-80-g6c4433a-5.2.0.tar.gz -C ./xtensa-esp32-elf
ENV PATH=/esp/xtensa-esp32-elf/xtensa-esp32-elf/bin:$PATH


USER root

# Build ESP32
RUN cd /micropython/ports/esp32 && make


RUN mkdir /mnt/dev
ENV PATH=/micropython/mpy-cross:$PATH


# Post-build Helpers
RUN apt-get update \
    && apt-get install -y usbutils picocom
