FROM python:3.10-slim

# OpenJDK installieren (Java 17+)
RUN apt-get update && apt-get install -y openjdk-17-jdk tini && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Pfad für Keycloak ins PATH setzen
ENV PATH="/workspace/keycloak-26.1.0/bin:${PATH}"

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["sh", "-c", "kc.sh start-dev"]