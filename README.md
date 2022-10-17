# docker-in-jenkins-docker
## Build Custom Docker Image
'''
mkdir -p jenkins_home
docker image build -t custom-jenkins-docker .
'''

## Run jenkins docker by docker-compose with custom-jenkins-docker image
'''
docker compose up -d
docker compose logs
'''

Copy Jenkins password and go.

## Browse to jenkins console
Go to: http://localhost:8080 and follow setting wizard.
