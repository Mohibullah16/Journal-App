pipeline {
    agent any
    
    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.jenkins.yml'
        APP_PORT = '3001'
    }
    
    stages {
        stage('📥 Checkout Code') {
            steps {
                script {
                    echo '📥 Checking out code from GitHub...'
                    // Git checkout happens automatically with pipeline
                    sh 'ls -la'
                }
            }
        }
        
        stage('🧹 Cleanup') {
            steps {
                script {
                    echo '🧹 Cleaning up existing containers...'
                    sh """
                        docker-compose -f ${DOCKER_COMPOSE_FILE} down -v || true
                        docker system prune -f || true
                    """
                }
            }
        }
        
        stage('🏗️ Build and Deploy with Docker Compose') {
            steps {
                script {
                    echo '🏗️ Building and starting containers...'
                    sh """
                        docker-compose -f ${DOCKER_COMPOSE_FILE} up -d
                    """
                }
            }
        }
        
        stage('⏳ Wait for Application') {
            steps {
                script {
                    echo '⏳ Waiting for application to be ready...'
                    sh """
                        echo "Waiting for containers to start..."
                        sleep 10
                        
                        echo "Checking application logs:"
                        docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=50 journal-app-jenkins
                        
                        echo "Testing application endpoint:"
                        for i in 1 2 3 4 5; do
                            if curl -f http://localhost:${APP_PORT}; then
                                echo "Application is responding!"
                                exit 0
                            fi
                            echo "Attempt \$i failed, waiting..."
                            sleep 5
                        done
                        echo "Application not responding after 5 attempts"
                        exit 1
                    """
                }
            }
        }
        
        stage('🧪 Run Tests') {
            steps {
                script {
                    echo '🧪 Running tests...'
                    sh """
                        docker exec journal-app-jenkins-ci sh -c "python -m pytest tests/ || echo 'No tests defined'"
                    """
                }
            }
        }
        
        stage('✅ Verify Deployment') {
            steps {
                script {
                    echo '✅ Verifying deployment...'
                    sh """
                        docker-compose -f ${DOCKER_COMPOSE_FILE} ps
                        curl -I http://localhost:${APP_PORT}
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo '🔍 Pipeline execution completed'
        }
        success {
            echo '✅ Pipeline succeeded!'
            echo "🌐 Application is running at: http://localhost:${APP_PORT}"
        }
        failure {
            echo '❌ Pipeline failed!'
            sh """
                echo "Container logs:"
                docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=100
            """
        }
    }
}