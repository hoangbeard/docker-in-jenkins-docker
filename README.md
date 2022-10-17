# docker-in-jenkins-docker
## Build Custom Docker Image
```
mkdir -p jenkins_home
docker image build -t custom-jenkins-docker .
```

## Run Jenkins Docker
```
docker compose up -d
```
Get Jenkins Password
```
docker compose logs
```

Note: Copy Jenkins password and go.

## Browse to Jenkins console
Go to: http://localhost:8080 and follow setting wizard.
