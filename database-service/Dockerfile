FROM eclipse-temurin:21-jre
WORKDIR /opt/h2
ARG H2_VERSION=2.3.232
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL "https://repo.maven.apache.org/maven2/com/h2database/h2/${H2_VERSION}/h2-${H2_VERSION}.jar" -o h2.jar
COPY init/ /opt/h2/init/
RUN mkdir -p /data
VOLUME ["/data"]
EXPOSE 9092
CMD ["java", "-cp", "/opt/h2/h2.jar", "org.h2.tools.Server", "-tcp", "-tcpAllowOthers", "-ifNotExists", "-baseDir", "/data", "-tcpPort", "9092"]
