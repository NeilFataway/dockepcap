FROM python:2.7.18-alpine3.11

EXPOSE 80

ARG PYPI_INDEX=http://mirrors.aliyun.com/pypi/simple
ARG PYPI_HOST=mirrors.aliyun.com

COPY dockerpcap /dockerpcap
WORKDIR /dockerpcap

RUN apk update && apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers && \
    mkdir ~/.pip && echo -e "[global]\nindex-url=${PYPI_INDEX}\ntrusted-host=${PYPI_HOST}\n" > ~/.pip/pip.conf && \
    echo -e "[easy_install]\nindex_url=${PYPY_INDEX}\n" > ~/.pydistutils.cfg && \
    python setup.py install && \
    runDeps="$(scanelf --needed --nobanner --recursive /usr/local | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' | \
    sort -u | xargs -r apk info --installed | sort -u)" && \
    apk add --virtual .rundeps $runDeps tzdata wireshark && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone && \
    apk del .build-deps

CMD ddump-server
