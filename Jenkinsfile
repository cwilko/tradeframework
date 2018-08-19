pipeline {
    agent none 
    stages {
        stage('Build') { 
            agent {
                docker {
                    image 'python:3.6' 
                }
            }
            steps {
                sh 'python -m compileall tradeframework' 
            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'python:3.6'
                }
            }
            steps {
                sh 'pip install pylint pytest pytest-cov'
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