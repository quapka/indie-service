# Run flask App
FROM python:3.14-trixie
# FROM debian:bookworm



# COPY requirements.txt requirements.txt
# COPY . .
# RUN pip3 install wheel
# RUN pip3 install swig
# RUN pip3 install pyscard
# RUN pip3 install --requirement requirements.txt
# ENV DEBIAN_FRONTEND=noninteractive

# RUN apt update --yes
# RUN apt install --yes \
#     python3-pip

# RUN apt add -u gcc musl-dev
RUN apt update --yes
RUN apt install --yes \
    libpcsclite-dev # pyscard dependency
RUN apt install --yes \
    openjdk-21-jdk
RUN apt install --yes \
    maven \
    help2man

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install --requirement requirements.txt
COPY . .

# # Gradle
# WORKDIR /opt/gradle
# RUN wget https://services.gradle.org/distributions/gradle-9.1.0-bin.zip
# RUN unzip -d /opt/gradle gradle-9.1.0-bin.zip
# ENV PATH=$PATH:/opt/gradle/gradle-9.1.0/bin

# # BouncyCastle

# WORKDIR /bc-java
# # NOTE Tests require also https://github.com/bcgit/bc-test-data and run for long
# RUN git clone --branch no-rsa-verif https://github.com/quapka/bc-java.git
# WORKDIR /bc-java/bc-java
# RUN ./gradlew clean build -x test
# # Install custom BouncyCastle as a local version
# RUN mvn install:install-file \
#     -Dfile=/bc-java/bc-java/prov/build/libs/bcprov-jdk18on-1.82.1.jar \
#     -DgroupId=org.bouncycastle \
#     -DartifactId=bcprov-fewer-rsa-checks \
#     -Dversion=1.82.1 \
#     -Dpackaging=jar

# # JCardEngine for JavaCard simulation
# WORKDIR /jcardengine
# RUN git clone \
#     --recurse-submodules \
#     --branch fewer-rsa-checks \
#     https://github.com/quapka/JCardEngine.git

# WORKDIR /vsmartcard
# RUN git clone --recurse-submodules https://github.com/frankmorgner/vsmartcard.git
# WORKDIR /vsmartcard/vsmartcard/virtualsmartcard
# RUN autoreconf --verbose --install
# RUN ./configure --sysconfdir=/etc
# RUN make
# RUN make install

# WORKDIR /jcardengine/JCardEngine
# RUN ./mvnw initialize
# RUN ./mvnw verify

# WORKDIR /indie-jc
# RUN git clone --recurse-submodules https://github.com/quapka/indie-jc.git
# WORKDIR /indie-jc/indie-jc
# # RUN ./gradlew buildJavaCard

# # RUN java -jar tool/target/jcard.jar  --vsmartcard /indie-jc/indie-jc/applet/build/javacard/indie.cap --params 00000000 --vsmartcard-port 35963 2>/dev/null


EXPOSE 8080
WORKDIR /python-docker
ENTRYPOINT ["flask"]
CMD ["--app", "indie_service", "run", "--port", "8080", "--host", "0.0.0.0"]
