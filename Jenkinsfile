pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        SONAR_HOST_URL = 'http://172.31.14.190:9000'
        AWS_REGION = 'ap-southeast-2'
        ECR_REPO = 'flask-todo'
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
                    rm -rf .venv-ci
                    python3.12 -m venv .venv-ci
                    . .venv-ci/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
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
        stage('Push Docker image to ECR') {
            steps {
                sh '''
                    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
                    ECR_REGISTRY=${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                    SHORT_SHA=$(git rev-parse --short HEAD)
                    IMAGE_TAG=${BUILD_NUMBER}-${SHORT_SHA}

                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${ECR_REGISTRY}

                    docker tag flask-todo:ci ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}
                    docker push ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}

                    echo "Pushed image: ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}"
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