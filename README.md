# Running a Jenkins in Docker with Configuration as Code

## How to use it?

1. Clone this repository to internal

	By SSH

	```shell
	git clone git@github.com:hoangbeard/docker-in-jenkins-docker.git
	```

	Or by HTTPS

	```shell
	git clone https://github.com/hoangbeard/docker-in-jenkins-docker.git
	```

2. Create an environment variables file for docker-compose by renaming .env.sample to .env in the root folder. Modify the username and password that you want.

    ```shell
    cp .env.sample .env
    ```

3. Run container in background and print container ID

    ```shell
    docker compose up -d
    ```

4. Access to Jenkins console

    http://localhost:8080

        Default credential in .env
        Username: admin
        Password: password

## How to clean up?

1. Clean docker compose

    ```shell
    docker compose down --volumes
    ```

2. Remove jenkins data.
    **Notice: Skip this step if you want to keep the jenkins data**

    ```shell
    rm -rf jenkins_home
    ```