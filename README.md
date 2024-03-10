# Running a Jenkins in Docker with Configuration as Code

## Create an environment variables file by rename .env.sample to .env in root folder

```shell
cp .env.sample .env

```

## Create a folder for jenkins_home (as known jenkins data)

```shell
mkdir -p jenkins_home
```

## Run docker compose

```shell
docker compose up -d
```

## Browse to Jenkins console

> Go to: http://localhost:8089
