FROM python:3.10-slim

# OpenJDK installieren (Java 17+), plus libfaketime dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk tini git gcc make autoconf automake libtool pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# libfaketime installieren
RUN git clone https://github.com/wolfcw/libfaketime.git /tmp/libfaketime && \
    cd /tmp/libfaketime/src && \
    make && \
    make install && \
    rm -rf /tmp/libfaketime

# Symlink für LD_PRELOAD (falls nötig)
RUN ln -s /usr/local/lib/faketime/libfaketime.so.1 /usr/lib/x86_64-linux-gnu/libfaketime.so.1 || true

# Pfad für Keycloak ins PATH setzen
ENV PATH="/workspace/keycloak-26.1.0/bin:${PATH}"

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["sh", "-c", "LD_PRELOAD=/usr/local/lib/faketime/libfaketime.so.1 FAKETIME='2025-08-15 10:00:00' kc.sh start-dev"]
