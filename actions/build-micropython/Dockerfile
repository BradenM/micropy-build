FROM docker:stable

# Action Info
LABEL "name"="build-micropython"
LABEL "maintainer"="Braden Mars <bradenmars@bradenmars.me>"
LABEL "version"="1.0.0"

LABEL "com.github.actions.name"="Build Micropython"
LABEL "com.github.actions.description"="Build and Publish Micropython Port"


# Setup Entrypoint
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]