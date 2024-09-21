###############################################################################
# GLOBAL ARGUMENTS                                                            #
###############################################################################
ARG IMAGE_REGISTRY="docker.arvancloud.ir"
ARG PYTHON_VERSION="3.12.6"


###############################################################################
# NONROOT BASE IMAGE                                                          #
###############################################################################
FROM ${IMAGE_REGISTRY}/python:${PYTHON_VERSION}-slim-bookworm AS nonroot


# TODOS: 
#    1. configure private debian repository
#    2. update image OS packages and install required drivers & etc.
#    3. configure private pip repository
#    4. ...


# configure the environment variables
ENV PROJECT_HOME="/project"
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONPATH=${PROJECT_HOME} \
    ENVIRONMENT="production" \
    SERVER_HOST="0.0.0.0" \
    SERVER_PORT=8000

# configure the nonroot group and user
RUN set -eux \
    && useradd --user-group --uid 1000 --home-dir ${PROJECT_HOME} \
        --create-home --no-log-init --shell /bin/bash --skel /dev/null nonroot

# change the user
USER nonroot


###############################################################################
# LEAN IMAGE                                                                  #
###############################################################################
FROM nonroot AS lean

# change the user
USER root

# set the working directory
WORKDIR ${PROJECT_HOME}

# install main python packages
COPY --chown=nonroot:nonroot ./requirements.txt .
RUN set -eux \
    && python -m pip install --no-cache-dir --no-deps --require-hashes \
    --requirement requirements.txt \
    && python -m pip cache purge

# copy the resources
COPY --chown=nonroot:nonroot . .

# configure the resources permission
RUN set -eux \
    && find ${PROJECT_HOME} -type d -exec chmod 755 {} \; \
    && find ${PROJECT_HOME} -type f -exec chmod 644 {} \; \
    && find ${PROJECT_HOME}/docker/*.sh -type f -exec chmod 755 {} \;

# expose the port
EXPOSE ${SERVER_PORT}

# change the user
USER nonroot

# Set the entrypoint
CMD ["./docker/bootstrap.sh", "app-uvicorn"]
