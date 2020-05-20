FROM jenkins/jnlp-slave

ARG LMCTL_VERSION
ENV LMCTL_VERSION ${LMCTL_VERSION:-2.5.0}

USER root

RUN apt update && apt upgrade -y \
  && apt install -y build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev libffi-dev
RUN wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tar.xz \
  && tar xf Python-3.7.7.tar.xz \
  && cd Python-3.7.7 \
  && sh configure --enable-optimizations \
  && make -j 8 \
  && make altinstall \
  && cd .. \
  && rm -rf Python-3.7.7 \
  && rm Python-3.7.7.tar.xz

RUN python3.7 -m pip install lmctl==$LMCTL_VERSION

USER jenkins

RUN lmctl --version
