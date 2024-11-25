ARG ELASTIC_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch:${ELASTIC_VERSION}

USER root

COPY . /

RUN set -eux; \
    mkdir /state; \
    chown elasticsearch /state; \
    chmod +x /entrypoint.sh

USER elasticsearch:root

ENTRYPOINT ["/entrypoint.sh"]