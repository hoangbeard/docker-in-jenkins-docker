def scan_type
def target

pipeline {
    agent any
    parameters {
        choice  choices: ["Baseline", "APIS", "Full"],
                description: 'Type of scan that is going to perform inside the container',
                name: 'SCAN_TYPE'

        string  defaultValue: "https://example.com",
                description: 'Target URL to scan',
                name: 'TARGET'

        booleanParam defaultValue: true,
                description: 'Parameter to know if wanna generate report.',
                name: 'GENERATE_REPORT'
    }
    stages {
        stage('Setting up OWASP ZAP docker container') {
            steps {
                script {
                    logMessage('======== Setting up OWASP ZAP docker container ========', 'stage')
                    sh """
                        docker run --rm \
                            --name zaproxy \
                            -dt ghcr.io/zaproxy/zaproxy:stable \
                            /bin/bash
                        docker exec zaproxy mkdir /zap/wrk
                    """
                }
            }
        }

        stage('Scanning target on zaproxy container') {
            steps {
                script {
                    logMessage('======== Scanning target on zap container ========', 'stage')
                    logMessage('OWASP ZAP Scanner', 'step')
                    logMessage("scan_type = ${params.SCAN_TYPE}", 'info')
                    if(scan_type == "Baseline"){
                        sh """
                            docker exec zaproxy \
                            zap-baseline.py \
                            -t ${params.TARGET} \
                            -x report.xml \
                            -I
                        """
                        sh "docker cp zaproxy:/zap/wrk/report.xml ${WORKSPACE}/zap-scan-report-$(date +%d-%b-%Y).xml"
                    }
                    else if(scan_type == "APIS"){
                        sh """
                            docker exec zaproxy \
                            zap-api-scan.py \
                            -t ${params.TARGET} \
                            -x report.xml \
                            -I
                        """
                        sh "docker cp zaproxy:/zap/wrk/report.xml ${WORKSPACE}/zap-scan-report-$(date +%d-%b-%Y).xml"
                    }
                    else if(scan_type == "Full"){
                        sh """
                            docker exec zaproxy \
                            zap-full-scan.py \
                            -t ${params.TARGET} \
                            -x report.xml \
                            -I
                        """
                        sh "docker cp zaproxy:/zap/wrk/report.xml ${WORKSPACE}/zap-scan-report-$(date +%d-%b-%Y).xml"
                        //-x report-$(date +%d-%b-%Y).xml
                    }
                    else{
                        echo "Something went wrong..."
                    }
                }
            }
        }
    }
    post {
        always {
            sh '''
                docker stop zaproxy
            '''
        }
    }
}