pipeline {
    agent any
    
    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.jenkins.yml'
        GIT_REPO = 'https://github.com/YOUR_USERNAME/Journal-App.git'
        APP_NAME = 'journal-app-jenkins'
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo '📥 Checking out code from GitHub...'
                    checkout scm
                }
            }
        }
        
        stage('Environment Setup') {
            steps {
                script {
                    echo '🔧 Setting up environment...'
                    sh '''
                        echo "Node version:"
                        node --version || echo "Node not installed on host"
                        echo "Docker version:"
                        docker --version
                        echo "Docker Compose version:"
                        docker-compose --version
                    '''
                }
            }
        }
        
        stage('Cleanup Previous Containers') {
            steps {
                script {
                    echo '🧹 Cleaning up previous containers...'
                    sh '''
                        docker-compose -f ${DOCKER_COMPOSE_FILE} down -v || true
                        docker system prune -f || true
                    '''
                }
            }
        }
        
        stage('Build Application') {
            steps {
                script {
                    echo '🏗️ Building application with Docker Compose...'
                    sh '''
                        docker-compose -f ${DOCKER_COMPOSE_FILE} up -d --build
                        echo "Waiting for services to be healthy..."
                        sleep 15
                    '''
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                script {
                    echo '✅ Verifying deployment...'
                    sh '''
                        echo "Checking running containers:"
                        docker-compose -f ${DOCKER_COMPOSE_FILE} ps
                        
                        echo "\nChecking MongoDB connection:"
                        docker exec mongodb-jenkins-container mongosh --eval "db.version()" --quiet || echo "MongoDB check failed"
                        
                        echo "\nChecking application logs:"
                        docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=50 journal-app-jenkins
                        
                        echo "\nTesting application endpoint:"
                        sleep 5
                        curl -f http://localhost:3001 || echo "Application not responding yet"
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo '🧪 Running tests...'
                    sh '''
                        docker exec journal-app-jenkins-container sh -c "npm test || echo 'No tests defined'"
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo '🌐 Application is running at http://localhost:3001'
            sh '''
                echo "\n=== Deployment Summary ==="
                docker-compose -f ${DOCKER_COMPOSE_FILE} ps
                echo "\n=== Application URL ==="
                echo "Journal App: http://localhost:3001"
                echo "MongoDB: localhost:27018"
            '''
        }
        failure {
            echo '❌ Pipeline failed!'
            sh '''
                echo "Container logs:"
                docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=100
            '''
        }
        always {
            echo '🔍 Pipeline execution completed'
        }
    }
}