pipeline {
    agent any

    parameters {
        string  defaultValue: 'git@bitbucket.org:mobivi/mobile-gateway.git',
                description: 'Repo URL in SSH format',
                name: 'REPO_URL'

        string  defaultValue: 'production',
                description: 'Branch name',
                name: 'BRANCH'

        string  defaultValue: 'mobilegateway',
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
                logMessage('======== Checkout App Code ========', 'stage')
                script {
                    // Checkout app code
                    logMessage('Get code from git repository', 'step')
                    checkout scmGit(
                        branches: [[name: "*/${params.BRANCH}"]],
                        extensions: [cloneOption(depth: 1, noTags: false, reference: '', shallow: true)],
                        userRemoteConfigs: [[credentialsId: "${GIT_SSH_KEY_ID}",
                        url: "${params.REPO_URL}"]])

                    // Get commitID of git repository
                    logMessage('Get commitID of git repository', 'step')
                    imageTag = sh(script: 'git rev-parse --short=7 HEAD', returnStdout: true).trim()

                    logMessage('Checkout App Code completed', 'info')
                    logMessage("Image tag: ${imageTag}", 'info')
                }
            }
        }

        stage('SonarQube Scanner') {
            environment {
                scannerHome = tool 'sonarqube-scanner'
            }
            steps {
                logMessage('======== SonarQube Scanner ========', 'stage')
                script {
                    logMessage("Project Key: ${PROJECT_KEY}", 'info')
                    withSonarQubeEnv(installationName: 'sonarqube') {
                        sh "${scannerHome}/bin/sonar-scanner -D'sonar.projectKey=${PROJECT_KEY}' -D'sonar.exclusions=**/*.java'"
                    }
                }
            }
        }

        stage("Quality Gate") {
            steps {
                logMessage('======== Quality Gate ========', 'stage')
                script {
                    logMessage("Project Key: ${PROJECT_KEY}", 'info')
                    timeout(time: 2, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        stage('Dependency-Check') {
            steps {
                script {
                    logMessage ('======== Dependency-Check ========', 'stage')
                    dependencyCheck additionalArguments: '--format ALL --disableBundleAudit', odcInstallation: 'dependency-check'
                }
            }
            post {
                success {
                    dependencyCheckPublisher pattern: 'dependency-check-report.xml'
                }
            }
        }
    }
}

def imageTag

// Logs Message Functions
def logMessage(message, type) {
    def colorCode = ''
    def prefix = ''

    switch(type.toLowerCase()) {
        case 'stage':
            colorCode = '1;35'
            prefix = 'Stage'
            break
        case 'step':
            colorCode = '1;33'
            prefix = 'Step'
            break
        case 'info':
            colorCode = '34'
            prefix = 'Info'
            break
        case 'error':
            colorCode = '31'
            prefix = 'Error'
            break
        case 'success':
            colorCode = '32'
            prefix = 'Success'
            break
        default:
            colorCode = '0' // Default color for unrecognized types
            prefix = ''
    }

    echo "\033[${colorCode}m[${prefix}] ${message}\033[0m"
}