pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        SONAR_HOST_URL = 'http://172.31.14.190:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Python environment') {
            steps {
                sh '''
                    python3.12 -m venv .venv-ci
                    . .venv-ci/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov pysonar
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                    . .venv-ci/bin/activate
                    pytest -v --cov=app --cov-report=xml
                '''
            }
        }

        stage('Run SonarQube analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token-flask-todo', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        . .venv-ci/bin/activate
                        pysonar \
                          --sonar-host-url="${SONAR_HOST_URL}" \
                          --sonar-token="${SONAR_TOKEN}"
                    '''
                }
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                    docker build -t flask-todo:ci .
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
        }
    }
}