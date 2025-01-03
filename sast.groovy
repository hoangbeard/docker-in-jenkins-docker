def stage_title(message) {
    echo "\033[1;35m[Stage: ${message}]\033[0m"
}

def step_title(message) {
    echo "\033[1;33m[Step: ${message}]\033[0m"
}

def info(message) {
    echo "\033[34m[Info] ${message}\033[0m"
}

def error(message) {
    echo "\033[31m[Error] ${message}\033[0m"
}

def success(message) {
    echo "\033[32m[Success] ${message}\033[0m"
}

pipeline {
    agent any

    parameters {
        string  defaultValue: '',
                description: 'Repo URL in SSH format',
                name: 'REPO_URL'

        string  defaultValue: 'master',
                description: 'Branch name',
                name: 'BRANCH'

        string  defaultValue: 'projectName',
                description: 'Project name as name will be shown on SonarQube Console',
                name: 'PROJECT_NAME'        
    }

    environment {
        GIT_SSH_KEY_ID = 'bitbucket'
        PROJECT_KEY = "${params.PROJECT_NAME}_${params.BRANCH}"
    }

    stages {
        stage('Checkout App Code') {
            steps {
                stage_title('======== Checkout App Code ========')
                script {
                    // Checkout app code
                    step_title('Get code from git repository')
                    checkout scmGit(
                        branches: [[name: "*/${params.BRANCH}"]],
                        extensions: [cloneOption(depth: 1, noTags: false, reference: '', shallow: true)],
                        userRemoteConfigs: [[credentialsId: "${GIT_SSH_KEY_ID}",
                        url: "${params.REPO_URL}"]])

                    // Get commitID of git repository
                    step_title('Get commitID of git repository')
                    imageTag = sh(script: 'git rev-parse --short=7 HEAD', returnStdout: true).trim()

                    info('Checkout App Code completed')
                    info("Image tag: ${imageTag}")
                }
            }
        }

        stage('SonarQube Scanner') {
            environment {
                scannerHome = tool 'sonarqube-scanner'
            }
            steps {
                stage_title('======== SonarQube Scanner ========')
                script {
                    info("Project Key: ${PROJECT_KEY}")
                    withSonarQubeEnv(installationName: 'sonarqube') {
                        sh "${scannerHome}/bin/sonar-scanner -D'sonar.projectKey=${PROJECT_KEY}' -D'sonar.exclusions=**/*.java'"
                    }
                }
            }
        }

        stage("Quality Gate") {
            steps {
                stage_title('======== Quality Gate ========')
                script {
                    info("Project Key: ${PROJECT_KEY}")
                    timeout(time: 2, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        // stage('Dependency-Check') {
        //     steps {
        //         script {
        //             echo "<---Dependency-Check is running--->"
        //             dependencyCheck additionalArguments: '--format ALL --disableBundleAudit', odcInstallation: 'dependency-check'
        //             echo "<---Remove repo directory--->"
        //             project_name = "${params.PROJECT_NAME}"
        //             echo "===> Project name: $project_name"
        //             sh "rm -rf $project_name"
        //         }
        //     }
        //     post {
        //         success {
        //             dependencyCheckPublisher pattern: 'dependency-check-report.xml'
        //         }
        //     }
        // }
    }
}