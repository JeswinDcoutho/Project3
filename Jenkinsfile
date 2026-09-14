pipeline {
    agent any

    environment {
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_HOST = "tcp://192.168.49.2:2376"
        DOCKER_TLS_VERIFY = "1"
        DOCKER_CERT_PATH = "/var/lib/jenkins/minikube-certs"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    set -e

                    docker build -t ecommerce-user-service:${IMAGE_TAG} ./user-service
                    docker build -t ecommerce-product-service:${IMAGE_TAG} ./product-service
                    docker build -t ecommerce-cart-service:${IMAGE_TAG} ./cart-service
                    docker build -t ecommerce-order-service:${IMAGE_TAG} ./order-service
                    docker build -t ecommerce-payment-service:${IMAGE_TAG} ./payment-service
                    docker build -t ecommerce-inventory-service:${IMAGE_TAG} ./inventory-service
                '''
            }
        }

        stage('Verify Images') {
            steps {
                sh '''
                    set -e

                    docker image inspect ecommerce-user-service:${IMAGE_TAG}
                    docker image inspect ecommerce-product-service:${IMAGE_TAG}
                    docker image inspect ecommerce-cart-service:${IMAGE_TAG}
                    docker image inspect ecommerce-order-service:${IMAGE_TAG}
                    docker image inspect ecommerce-payment-service:${IMAGE_TAG}
                    docker image inspect ecommerce-inventory-service:${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    set -e

                    kubectl apply -f k8s/namespace.yaml
                    kubectl apply -f k8s/configmap.yaml
                    kubectl apply -f k8s/secret.yaml

                    kubectl apply -f k8s/
                '''
            }
        }

        stage('Update Images') {
            steps {
                sh '''
                    set -e

                    kubectl set image deployment/user-service \
                        user-service=ecommerce-user-service:${IMAGE_TAG} \
                        -n ecommerce

                    kubectl set image deployment/product-service \
                        product-service=ecommerce-product-service:${IMAGE_TAG} \
                        -n ecommerce

                    kubectl set image deployment/cart-service \
                        cart-service=ecommerce-cart-service:${IMAGE_TAG} \
                        -n ecommerce

                    kubectl set image deployment/order-service \
                        order-service=ecommerce-order-service:${IMAGE_TAG} \
                        -n ecommerce

                    kubectl set image deployment/payment-service \
                        payment-service=ecommerce-payment-service:${IMAGE_TAG} \
                        -n ecommerce

                    kubectl set image deployment/inventory-service \
                        inventory-service=ecommerce-inventory-service:${IMAGE_TAG} \
                        -n ecommerce
                '''
            }
        }

        stage('Wait for Rollout') {
            steps {
                sh '''
                    set -e

                    kubectl rollout status deployment/user-service \
                        -n ecommerce --timeout=180s

                    kubectl rollout status deployment/product-service \
                        -n ecommerce --timeout=180s

                    kubectl rollout status deployment/cart-service \
                        -n ecommerce --timeout=180s

                    kubectl rollout status deployment/order-service \
                        -n ecommerce --timeout=180s

                    kubectl rollout status deployment/payment-service \
                        -n ecommerce --timeout=180s

                    kubectl rollout status deployment/inventory-service \
                        -n ecommerce --timeout=180s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    kubectl get deployments -n ecommerce
                    kubectl get pods -n ecommerce
                    kubectl get services -n ecommerce
                '''
            }
        }
    }

    post {
        success {
            echo 'E-Commerce CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'E-Commerce CI/CD pipeline failed.'
        }
    }
}
