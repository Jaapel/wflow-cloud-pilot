FROM mambaorg/micromamba


WORKDIR /tmp

ADD environment.yaml environment.yaml

USER root

RUN apt-get update && apt-get install -y git && apt-get clean y

RUN micromamba env create -f environment.yaml

USER mambauser

ADD . /tmp 
