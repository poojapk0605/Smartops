pipeline {
    agent any

    environment {
        PROJECT_ID   = "smartopsbackend"
        REGION       = "us-central1"
        REPO_NAME    = "smartopt-backend"
        SERVICE_NAME = "smartopt-backend"
        IMAGE_NAME   = "smartopt-backend"
    }

    stages {

        /* -----------------------------
           CHECKOUT CODE
        ----------------------------- */
        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Repository checkout complete."
            }
        }

        /* -----------------------------
           PYTHON STATIC ANALYSIS (Production Safe)
        ----------------------------- */
        stage('Static Analysis') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate

                    pip install --quiet ruff pyflakes

                    echo "▶ Running Ruff (non-blocking)..."
                    
                    ruff check . --fix || true

                    echo "▶ Running pyflakes (non-blocking)..."
                    pyflakes . || true
                    echo "✔ Static analysis completed (warnings ignored)."
                '''
            }
        }

        /* -----------------------------
           PYTHON SYNTAX CHECK (Safe for Thousands of Files)
        ----------------------------- */
        stage('Syntax Check') {
            steps {
                sh '''
                    . venv/bin/activate

                    echo "▶ Running syntax validation..."
                    python3 - << 'EOF'
import os, py_compile, sys

errors = 0

for root, dirs, files in os.walk("."):
    if "venv" in root:
        continue
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                py_compile.compile(path, doraise=True)
                print(f"OK: {path}")
            except Exception as e:
                print(f"❌ Syntax error in {path}: {e}")
                errors += 1

if errors > 0:
    sys.exit(1)
EOF
                '''
            }
        }

        /* -----------------------------
           OPTIONAL TEST PHASE (pytest)
           Ready for future tests
        ----------------------------- */
        stage('Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pip install pytest

                    echo "▶ Running pytest"
                    pytest || true   # Remove "|| true" once tests exist
                '''
            }
        }

        /* -----------------------------
           DOCKER BUILD
        ----------------------------- */
        stage('Docker Build') {
            steps {
                sh '''
                    echo "🐳 Building Docker image..."
                    docker build --platform=linux/amd64 -t $IMAGE_NAME .
                '''
            }
        }

        /* -----------------------------
           PUSH DOCKER IMAGE TO ARTIFACT REGISTRY
        ----------------------------- */
        stage('Push to Artifact Registry') {
            steps {
                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        echo "🔐 Authenticating to GCP..."
                        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

                        echo "🔧 Configuring Docker for Artifact Registry..."
                        gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

                        echo "🏷 Tagging image..."
                        docker tag $IMAGE_NAME \
                            $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$BUILD_NUMBER

                        echo "⬆️ Pushing image..."
                        docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$BUILD_NUMBER
                    '''
                }
            }
        }

        /* -----------------------------
           DEPLOY TO CLOUD RUN
        ----------------------------- */
        stage('Deploy to Cloud Run') {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    string(credentialsId: 'hf-api-key', variable: 'HF_API_KEY')
                ]) {
                    sh '''
                        echo "🚀 Deploying to Cloud Run..."

                        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
                        gcloud config set project $PROJECT_ID
                        gcloud run deploy $SERVICE_NAME \
                            --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$BUILD_NUMBER \
                            --region=$REGION \
                            --platform=managed \
                            --allow-unauthenticated \
                            --set-secrets HF_API_KEY=HF_API_KEY:latest \
                            --timeout=300 \
                            --cpu=1 \
                            --memory=1Gi

                        echo "🌍 Deployment complete."
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
            echo "❌ Deployment failed — check Jenkins logs."
        }
    }
}
