FROM mambaorg/micromamba

USER root

RUN apt-get update && apt-get install -y git && apt-get clean y

USER mambauser

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yaml /tmp/env.yaml
RUN micromamba install -n base --yes --file /tmp/env.yaml \
 && micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1  # (otherwise python will not be found)

ADD . /tmp 
