ARG JENKINS_VERSION=""
ARG JDK_VERSION="17"

FROM jenkins/jenkins:${JENKINS_VERSION:+${JENKINS_VERSION}-}lts-jdk${JDK_VERSION}

LABEL maintainer="HoangBeard <hoangbeard@gmail.com>"

ENV JAVA_OPTS='-Djenkins.install.runSetupWizard=false'
ENV CASC_JENKINS_CONFIG='/usr/share/jenkins/ref/jcasc.yaml'

USER root

# Install dependencies
RUN set -eux; \
    apt-get update; \
    apt-get install -y \
        apt-transport-https \
        apt-utils \
        ca-certificates \
        curl \
        debian-archive-keyring \
        dnsutils \
        inetutils-ping \
        inetutils-telnet \
        lsb-release \
        lsof \
        maven \
        net-tools \
        openssh-client \
        openssl \
        procps \
        time \
        unzip \
        wget \
    ; \
    apt-get -y clean; \
    rm -rf /var/lib/apt/lists/*

ADD --chmod=644 https://download.docker.com/linux/debian/gpg /etc/apt/keyrings/docker.asc

# Install Trivy and Docker CLI
RUN set -eux; \
    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin; \
    wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -; \
    echo \
        "deb https://aquasecurity.github.io/trivy-repo/deb "$(lsb_release -sc)" main" | \
        tee -a /etc/apt/sources.list.d/trivy.list; \
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
        $(. /etc/os-release && echo "${VERSION_CODENAME}") stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null \
    ; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        docker-ce \
        docker-ce-cli \
        docker-compose-plugin \
        trivy \
    ; \
    usermod -aG docker jenkins \
    ; \
    apt-get -y clean; \
    rm -rf /var/lib/apt/lists/*

COPY config/. /usr/share/jenkins/ref/

RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

WORKDIR /var/jenkins_home

USER jenkins