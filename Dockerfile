FROM jenkins/jenkins:lts-jdk17

ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false -Dorg.apache.commons.jelly.tags.fmt.timeZone=Asia/Saigon
ENV CASC_JENKINS_CONFIG /var/jenkins_home/jcasc.yaml

COPY initialConfig.groovy /usr/share/jenkins/ref/init.groovy.d/initialConfigs.groovy
COPY jcasc.yaml /usr/share/jenkins/ref/jcasc.yaml
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

USER root

RUN apt-get update -qq \
    && apt-get install -qqy apt-transport-https ca-certificates time curl gnupg lsb-release software-properties-common \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update  -qq \
    && apt-get install -y docker-ce docker-ce-cli docker-compose-plugin \
    && usermod -aG docker jenkins \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

USER jenkins
