pipeline {
    agent any

    environment {
        IMAGE_TAG = "${BUILD_NUMBER}"

        DOCKER_HOST = "tcp://192.168.49.2:2376"
        DOCKER_TLS_VERIFY = "1"
        DOCKER_CERT_PATH = "/var/lib/jenkins/minikube-certs"

        NAMESPACE = "ecommerce"

        BLUE_DEPLOYMENT = "user-service-blue"
        GREEN_DEPLOYMENT = "user-service-green"
        BG_SERVICE = "user-service-bg"
    }

    stages {

        stage('Build Docker Images') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "BUILDING DOCKER IMAGES"
                    echo "Build Number: ${IMAGE_TAG}"
                    echo "========================================="

                    docker build -t ecommerce-user-service:${IMAGE_TAG} ./user-service
                    docker build -t ecommerce-product-service:${IMAGE_TAG} ./product-service
                    docker build -t ecommerce-cart-service:${IMAGE_TAG} ./cart-service
                    docker build -t ecommerce-order-service:${IMAGE_TAG} ./order-service
                    docker build -t ecommerce-payment-service:${IMAGE_TAG} ./payment-service
                    docker build -t ecommerce-inventory-service:${IMAGE_TAG} ./inventory-service

                    echo ""
                    echo "All Docker images built successfully."
                '''
            }
        }

        stage('Verify Docker Images') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "VERIFYING DOCKER IMAGES"
                    echo "========================================="

                    docker image inspect ecommerce-user-service:${IMAGE_TAG}
                    docker image inspect ecommerce-product-service:${IMAGE_TAG}
                    docker image inspect ecommerce-cart-service:${IMAGE_TAG}
                    docker image inspect ecommerce-order-service:${IMAGE_TAG}
                    docker image inspect ecommerce-payment-service:${IMAGE_TAG}
                    docker image inspect ecommerce-inventory-service:${IMAGE_TAG}

                    echo ""
                    echo "All Docker images verified successfully."
                '''
            }
        }

        stage('Deploy Kubernetes Manifests') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "DEPLOYING KUBERNETES MANIFESTS"
                    echo "========================================="

                    kubectl apply -f k8s/namespace.yaml
                    kubectl apply -f k8s/configmap.yaml
                    kubectl apply -f k8s/secret.yaml

                    echo ""
                    echo "Deploying standard services..."

                    kubectl apply -f k8s/product-deployment.yaml
                    kubectl apply -f k8s/cart-deployment.yaml
                    kubectl apply -f k8s/order-deployment.yaml
                    kubectl apply -f k8s/payment-deployment.yaml
                    kubectl apply -f k8s/inventory-deployment.yaml

                    echo ""
                    echo "Deploying Blue-Green user-service..."

                    kubectl apply -f k8s/user-service-blue.yaml
                    kubectl apply -f k8s/user-service-green.yaml
                    kubectl apply -f k8s/user-service-bg-service.yaml

                    echo ""
                    echo "Kubernetes manifests deployed successfully."
                '''
            }
        }

        stage('Update Standard Services') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "UPDATING STANDARD SERVICES"
                    echo "========================================="

                    kubectl set image deployment/product-service \
                        product-service=ecommerce-product-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl set image deployment/cart-service \
                        cart-service=ecommerce-cart-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl set image deployment/order-service \
                        order-service=ecommerce-order-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl set image deployment/payment-service \
                        payment-service=ecommerce-payment-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl set image deployment/inventory-service \
                        inventory-service=ecommerce-inventory-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    echo ""
                    echo "Standard service images updated."
                '''
            }
        }

        stage('Deploy Green User Service') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "DEPLOYING GREEN USER SERVICE"
                    echo "Image: ecommerce-user-service:${IMAGE_TAG}"
                    echo "========================================="

                    kubectl set image deployment/${GREEN_DEPLOYMENT} \
                        user-service=ecommerce-user-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl rollout status deployment/${GREEN_DEPLOYMENT} \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    echo ""
                    echo "Green deployment completed successfully."
                '''
            }
        }

        stage('Verify Green Pods') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "VERIFYING GREEN PODS"
                    echo "========================================="

                    kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=user-service,version=green \
                        -o wide

                    GREEN_READY=$(kubectl get deployment ${GREEN_DEPLOYMENT} \
                        -n ${NAMESPACE} \
                        -o jsonpath='{.status.readyReplicas}')

                    GREEN_DESIRED=$(kubectl get deployment ${GREEN_DEPLOYMENT} \
                        -n ${NAMESPACE} \
                        -o jsonpath='{.spec.replicas}')

                    echo ""
                    echo "Green ready replicas: ${GREEN_READY}"
                    echo "Green desired replicas: ${GREEN_DESIRED}"

                    if [ "${GREEN_READY}" != "${GREEN_DESIRED}" ]; then
                        echo "ERROR: Green deployment is not fully ready."
                        exit 1
                    fi

                    echo ""
                    echo "Green deployment is healthy."
                '''
            }
        }

        stage('Verify Green Health') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "VERIFYING GREEN HEALTH ENDPOINT"
                    echo "========================================="

                    GREEN_POD=$(kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=user-service,version=green \
                        -o jsonpath='{.items[0].metadata.name}')

                    echo "Testing pod: ${GREEN_POD}"

                    kubectl exec ${GREEN_POD} \
                        -n ${NAMESPACE} \
                        -- python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8001/health').read().decode())"

                    echo ""
                    echo "Green health check passed."
                '''
            }
        }

        stage('Switch Traffic to Green') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "SWITCHING TRAFFIC TO GREEN"
                    echo "========================================="

                    kubectl patch service ${BG_SERVICE} \
                        -n ${NAMESPACE} \
                        -p '{"spec":{"selector":{"app":"user-service","version":"green"}}}'

                    echo ""
                    echo "Traffic switched to Green."

                    sleep 5

                    echo ""
                    echo "Current Green endpoints:"
                    kubectl get endpoints ${BG_SERVICE} -n ${NAMESPACE}
                '''
            }
        }

        stage('Verify Green Traffic') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "VERIFYING GREEN TRAFFIC"
                    echo "========================================="

                    GREEN_ENDPOINTS=$(kubectl get endpoints ${BG_SERVICE} \
                        -n ${NAMESPACE} \
                        -o jsonpath='{.subsets[*].addresses[*].ip}')

                    echo "Active service endpoints:"
                    echo "${GREEN_ENDPOINTS}"

                    if [ -z "${GREEN_ENDPOINTS}" ]; then
                        echo "ERROR: No active Green endpoints found."
                        exit 1
                    fi

                    GREEN_POD_IPS=$(kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=user-service,version=green \
                        -o jsonpath='{.items[*].status.podIP}')

                    echo ""
                    echo "Green pod IPs:"
                    echo "${GREEN_POD_IPS}"

                    for IP in ${GREEN_POD_IPS}; do
                        if echo "${GREEN_ENDPOINTS}" | grep -q "${IP}"; then
                            echo "Verified Green endpoint: ${IP}"
                        else
                            echo "ERROR: Green pod ${IP} is not an active service endpoint."
                            exit 1
                        fi
                    done

                    echo ""
                    echo "Green traffic verification successful."
                '''
            }
        }

        stage('Wait for Standard Services') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "WAITING FOR STANDARD SERVICE ROLLOUTS"
                    echo "========================================="

                    kubectl rollout status deployment/product-service \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl rollout status deployment/cart-service \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl rollout status deployment/order-service \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl rollout status deployment/payment-service \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl rollout status deployment/inventory-service \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    echo ""
                    echo "All standard services rolled out successfully."
                '''
            }
        }

        stage('Final Verification') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "FINAL KUBERNETES VERIFICATION"
                    echo "========================================="

                    echo ""
                    echo "Deployments:"
                    kubectl get deployments -n ${NAMESPACE}

                    echo ""
                    echo "Pods:"
                    kubectl get pods -n ${NAMESPACE}

                    echo ""
                    echo "Services:"
                    kubectl get services -n ${NAMESPACE}

                    echo ""
                    echo "Blue-Green Service:"
                    kubectl get service ${BG_SERVICE} -n ${NAMESPACE}

                    echo ""
                    echo "Blue-Green Endpoints:"
                    kubectl get endpoints ${BG_SERVICE} -n ${NAMESPACE}

                    echo ""
                    echo "Blue Pods:"
                    kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=user-service,version=blue

                    echo ""
                    echo "Green Pods:"
                    kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=user-service,version=green

                    echo ""
                    echo "========================================="
                    echo "BLUE-GREEN DEPLOYMENT SUCCESSFUL"
                    echo "========================================="
                '''
            }
        }
    }

    post {
        success {
            echo 'E-Commerce CI/CD with Blue-Green deployment completed successfully!'
        }

        failure {
            echo 'E-Commerce CI/CD pipeline failed.'
            echo 'Attempting automatic rollback to BLUE...'

            sh '''
                set +e

                echo "========================================="
                echo "ROLLING BACK TO BLUE"
                echo "========================================="

                kubectl patch service ${BG_SERVICE} \
                    -n ${NAMESPACE} \
                    -p '{"spec":{"selector":{"app":"user-service","version":"blue"}}}'

                sleep 3

                echo ""
                echo "Traffic restored to BLUE."

                echo ""
                echo "Current endpoints:"
                kubectl get endpoints ${BG_SERVICE} -n ${NAMESPACE}

                echo ""
                echo "Rollback completed."
            '''
        }
    }
}
