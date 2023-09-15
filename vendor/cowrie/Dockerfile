FROM ubuntu:latest
MAINTAINER fnndsc "dev@babymri.org"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/

ENV COWRIE_HOME=/cowrie

WORKDIR ${COWRIE_HOME}

COPY . ${COWRIE_HOME}/cowrie-git/

RUN pip3 install --no-cache-dir --upgrade pip wheel setuptools -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip3 install --no-cache-dir --upgrade cffi -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip3 install --no-cache-dir --upgrade -r ${COWRIE_HOME}/cowrie-git/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip3 install --no-cache-dir --upgrade -r ${COWRIE_HOME}/cowrie-git/requirements-output.txt -i https://mirrors.aliyun.com/pypi/simple/

RUN python3 -m compileall ${COWRIE_HOME} /usr/lib/python3.9

VOLUME [ "/cowrie/cowrie-git/var", "/cowrie/cowrie-git/etc" ]

WORKDIR ${COWRIE_HOME}/cowrie-git

ENV PATH=${COWRIE_HOME}/cowrie-env/bin:${PATH}
ENV PYTHONPATH=${COWRIE_HOME}/cowrie-git/src
ENV PYTHONUNBUFFERED=1


ENTRYPOINT [ "/usr/local/bin/twistd" ]
CMD [ "-n", "--umask=0022", "--pidfile=", "cowrie" ]

EXPOSE 2222 2223
