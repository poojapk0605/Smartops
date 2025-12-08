pipeline {
    agent any

    parameters {
        choice(
            name: 'VERSION_BUMP',
            choices: ['none', 'patch', 'minor', 'major'],
            description: 'Semantic version bump type for this build'
        )
        string(
            name: 'ROLLBACK_VERSION',
            defaultValue: '',
            description: 'If set, skip build and rollback to this version (e.g. 1.0.0)'
        )
    }

    environment {
        PROJECT_ID   = "smartopsbackend"
        REGION       = "us-central1"
        REPO_NAME    = "smartopt-backend"
        SERVICE_NAME = "smartopt-backend"
        IMAGE_NAME   = "smartopt-backend"

        // NEW_VERSION will be set in the Compute Version stage
        NEW_VERSION  = ""
    }

    stages {

        /* -----------------------------
           ROLLBACK ONLY
        ----------------------------- */
        stage('Rollback') {
            when {
                expression { return params.ROLLBACK_VERSION?.trim() }
            }
            steps {
                echo "⚠️ Rolling back to image tag: ${params.ROLLBACK_VERSION}"

                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
                        gcloud config set project $PROJECT_ID

                        gcloud run deploy $SERVICE_NAME \
                          --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:${ROLLBACK_VERSION} \
                          --region=$REGION \
                          --platform=managed \
                          --allow-unauthenticated

                        echo "🔁 Rollback deployment completed."
                    '''
                }
            }
        }

        /* -----------------------------
           CHECKOUT
        ----------------------------- */
        stage('Checkout') {
            when { not { expression { params.ROLLBACK_VERSION?.trim() } } }
            steps {
                checkout scm
                echo "✅ Repository checkout complete."
            }
        }

        /* -----------------------------
           COMPUTE VERSION (Semantic)
        ----------------------------- */
        stage('Compute Version') {
            when { not { expression { params.ROLLBACK_VERSION?.trim() } } }
            steps {
                script {
                    if (params.VERSION_BUMP == 'none') {
                        env.NEW_VERSION = readFile('VERSION').trim()
                        echo "Using existing VERSION: ${env.NEW_VERSION}"
                    } else {
                        echo "Bumping VERSION with: ${params.VERSION_BUMP}"
                        env.NEW_VERSION = sh(
                            script: "python3 ci/bump_version.py ${params.VERSION_BUMP}",
                            returnStdout: true
                        ).trim()
                        echo "New semantic version: ${env.NEW_VERSION}"
                    }
                }
            }
        }

        /* -----------------------------
           STATIC ANALYSIS
        ----------------------------- */
        stage('Static Analysis') {
            when { not { expression { params.ROLLBACK_VERSION?.trim() } } }
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate

                    pip install --quiet ruff pyflakes

                    echo "▶ Running Ruff..."
                    ruff check . --fix || true

                    echo "▶ Running Pyflakes..."
                    pyflakes . || true

                    echo "✔ Static analysis completed."
                '''
            }
        }

        /* -----------------------------
           UNIT TESTS
        ----------------------------- */
        stage('Unit Tests') {
            when { not { expression { params.ROLLBACK_VERSION?.trim() } } }
            steps {
                sh '''
                    . venv/bin/activate
                    pip install pytest

                    # Allow src imports
                    export PYTHONPATH=$WORKSPACE

                    echo "▶ Running pytest..."
                    pytest tests --disable-warnings --maxfail=1
                '''
            }
        }

        /* -----------------------------
           DOCKER BUILD
        ----------------------------- */
        stage('Docker Build') {
            when { not { expression { params.ROLLBACK_VERSION?.trim() } } }
            steps {
                sh '''
                    echo "🐳 Building Docker image with tag: $NEW_VERSION"
                    docker build --platform=linux/amd64 -t $IMAGE_NAME:$NEW_VERSION .
                '''
            }
        }

        /* -----------------------------
           PUSH TO ARTIFACT REGISTRY
        ----------------------------- */
        stage('Push to Artifact Registry') {
            when { not { expression { params.ROLLBACK_VERSION?.trim() } } }
            steps {
                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        echo "🔐 Authenticating to GCP..."
                        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

                        echo "🔧 Configuring Docker for Artifact Registry..."
                        gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

                        echo "🏷 Tagging image for Artifact Registry..."
                        docker tag $IMAGE_NAME:$NEW_VERSION \
                          $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$NEW_VERSION

                        echo "⬆️ Pushing image..."
                        docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$NEW_VERSION
                    '''
                }
            }
        }

        /* -----------------------------
           TAG + GITHUB RELEASE (optional)
           Requires: GitHub CLI + GitHub token
        ----------------------------- */
        stage('Tag & GitHub Release') {
            when { not { expression { params.ROLLBACK_VERSION?.trim() } } }
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                    sh '''
                        echo "📝 Generating release notes..."
                        python3 ci/generate_changelog.py $NEW_VERSION

                        echo "🏷 Creating git tag v$NEW_VERSION"
                        git config user.name "Jenkins"
                        git config user.email "jenkins@smartopt"
                        git tag -a "v$NEW_VERSION" -m "SmartOpt v$NEW_VERSION"
                        git push origin "v$NEW_VERSION"

                        echo "🔐 Authenticating GitHub CLI..."
                        echo "$GITHUB_TOKEN" | gh auth login --with-token

                        echo "📦 Creating GitHub Release v$NEW_VERSION"
                        gh release create "v$NEW_VERSION" \
                          --title "SmartOpt v$NEW_VERSION" \
                          --notes-file CHANGELOG_RELEASE.md || true

                        echo "✔ GitHub Release step finished."
                    '''
                }
            }
        }

        /* -----------------------------
           DEPLOY TO CLOUD RUN
        ----------------------------- */
        stage('Deploy to Cloud Run') {
            when { not { expression { params.ROLLBACK_VERSION?.trim() } } }
            steps {
                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        echo "🚀 Deploying to Cloud Run with image tag: $NEW_VERSION"

                        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
                        gcloud config set project $PROJECT_ID

                        gcloud run deploy $SERVICE_NAME \
                          --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$NEW_VERSION \
                          --region=$REGION \
                          --platform=managed \
                          --allow-unauthenticated \
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
            echo "🎉 Build / Release / Deploy successful! Version: ${env.NEW_VERSION}"
        }
        failure {
            echo "❌ Build failed — check Jenkins logs."
        }
    }
}
