pipeline {
    agent none 
    stages {
        stage('Build') { 
            agent {
                docker {
                    image 'python:3' 
                }
            }
            steps {
                sh 'python -m compileall tradeframework' 
            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'python:3'
                }
            }
            steps {
                sh 'pip install feedparser nosexcover prometheus_client pycobertura pylint pytest pytest-cov setuptools'
                sh 'pip install -r requirements.txt'
                sh 'py.test --verbose --junit-xml test-reports/results.xml'
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
        }
    }
}