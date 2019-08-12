FROM jenkins/jnlp-slave

ARG LMCTL_VERSION
ENV LMCTL_VERSION ${LMCTL_VERSION:-2.0.6}

USER root

RUN apt-get update && apt-get -y install python3 python3-pip
RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install lmctl==$LMCTL_VERSION

USER jenkins

RUN lmctl --version
