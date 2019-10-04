FROM ubuntu:18.04

LABEL maintainer="bradenmars@bradenmars.me"
LABEL description="MicroPython Unix Dockerfile"

ARG REPO=https://github.com/micropython/micropython.git
ARG BRANCH=master

# Requirements
RUN apt-get update \
    && apt-get install -y build-essential libffi-dev pkg-config git autoconf libtool python3 python3-pip python python-pip

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Fetch and Setup Repos
RUN git clone $REPO micropython \
    && cd micropython && git checkout $BRANCH && git pull origin $BRANCH\
    && git submodule update --init --recursive

# Build Deps & Tools
RUN cd micropython/ports/unix && make deplibs
RUN cd micropython/mpy-cross && make

# Build
RUN cd micropython/ports/unix && make

# Run Tests
RUN cd micropython/ports/unix && make test

# Setup Entrypoint
# Must copy entrypoint or build from parent dir with -f option
COPY ./docker-entrypoint.py /docker-entrypoint.py

ENTRYPOINT ["/usr/bin/python3", "/docker-entrypoint.py"]