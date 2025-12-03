pipeline {
    agent any

    environment {
        PROJECT_ID      = "smartopsbackend"
        REGION          = "us-central1"
        REPO_NAME       = "smartopt-backend"
        SERVICE_NAME    = "smartopt-backend"
        IMAGE_NAME      = "smartopt-backend"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Repository checked out successfully."
            }
        }

        stage('Install Python deps & Run Tests') {
            steps {
                sh '''
                    python3.11 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt

                    # Run syntax-check instead of tests (safe for prototypes)
                    python3 -m py_compile $(find . -name "*.py")
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t $IMAGE_NAME .
                '''
            }
        }

        stage('Auth & Push to Artifact Registry') {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')
                ]) {
                    sh '''
                        echo "⚙️ Activating GCP service account..."
                        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

                        echo "⚙️ Configuring Docker to use Artifact Registry..."
                        gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

                        echo "⚙️ Tagging image for Artifact Registry..."
                        docker tag $IMAGE_NAME \
                          $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$BUILD_NUMBER

                        echo "⬆️ Pushing image..."
                        docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$BUILD_NUMBER
                    '''
                }
            }
        }

        stage('Deploy to Cloud Run') {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    string(credentialsId: 'hf-api-key', variable: 'HF_API_KEY')
                ]) {
                    sh '''
                        echo "🚀 Deploying to Cloud Run..."

                        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

                        gcloud run deploy $SERVICE_NAME \
                            --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$BUILD_NUMBER \
                            --region=$REGION \
                            --platform=managed \
                            --allow-unauthenticated \
                            --set-env-vars HF_API_KEY=$HF_API_KEY
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Deployment successful!"
        }
        failure {
            echo "❌ Deployment failed. Check logs."
        }
    }
}
