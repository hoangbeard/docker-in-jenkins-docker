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

    options {
        office365ConnectorWebhooks([[
            name: 'MS Teams - SysOps - System-Notifications Channel'
            url: 'https://outlook.office.com/webhook/123456...',
            startNotification(true)
            notifySuccess(true)
            notifyAborted(true)
            notifyNotBuilt(false)
            notifyUnstable(false)
            notifyFailure(true)
            notifyBackToNormal(false)
            notifyRepeatedFailure(false)
            timeout(30000)
        ]])
    }

    environment {
        GIT_SSH_KEY_ID = 'bitbucket'
        PROJECT_KEY = "${params.PROJECT_NAME}_${params.BRANCH}"
    }

    stages {
        stage('Checkout') {
            steps {
                logMessage('======== Checkout ========', 'stage')
                script {
                    // Checkout
                    logMessage('Get code from git repository', 'step')
                    checkout scmGit(
                        branches: [[name: "*/${params.BRANCH}"]],
                        extensions: [cloneOption(depth: 1, noTags: false, reference: '', shallow: true)],
                        userRemoteConfigs: [[credentialsId: "${GIT_SSH_KEY_ID}",
                        url: "${params.REPO_URL}"]])

                    // Get commitID of git repository
                    logMessage('Get commitID of git repository', 'step')
                    imageTag = sh(script: 'git rev-parse --short=7 HEAD', returnStdout: true).trim()

                    logMessage('Checkout completed', 'info')
                    logMessage("Image tag: ${imageTag}", 'info')
                }
            }
        }

        stage('SCA') {
            steps {
                script {
                    logMessage ('======== SCA ========', 'stage')
                    
                    logMessage('Trivy scanner', 'step')
                    sh "trivy fs ."
                    
                    logMessage('Grype scanner', 'step')
                    sh "grype . --scope all-layers --by-cve --name app-name"
                }
            }
            post {
                success {
                    echo "SCA success."
                }
            }
        }

        stage('SAST') {
            environment {
                scannerHome = tool 'sonarqube-scanner'
            }
            steps {
                logMessage('======== SAST ========', 'stage')
                script {
                    logMessage('SonarQube Scanner', 'step')
                    withSonarQubeEnv(installationName: 'sonarqube') {
                        sh "${scannerHome}/bin/sonar-scanner -D'sonar.projectKey=${PROJECT_KEY}' -D'sonar.exclusions=**/*.java'"
                    }

                    logMessage('SonarQube Quality Gate', 'step')
                    timeout(time: 2, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        // stage('Container Scanning') {
        //     steps {
        //         script {
        //             logMessage ('======== Container Scanning ========', 'stage')
                    
        //             logMessage('Trivy scanner', 'step')
        //             sh "trivy image ${ECR_URL}:${imageTag}"
                    
        //             logMessage('Grype scanner', 'step')
        //             sh "grype ${ECR_URL}:${imageTag} --scope all-layers --by-cve --name app-name"
        //         }
        //     }   
        // }
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