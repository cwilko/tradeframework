pipeline {
    agent { docker { image 'python:3.6.5' } }
    stages {
        stage('build') {
            steps {
                sh 'pip install -U pytest'
                sh 'pytest'
            }
        }
    }
}