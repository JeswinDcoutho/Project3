pipeline {
    agent any

    environment {
        IMAGE_TAG = "${BUILD_NUMBER}"

        DOCKER_HOST = "tcp://192.168.49.2:2376"
        DOCKER_TLS_VERIFY = "1"
        DOCKER_CERT_PATH = "/var/lib/jenkins/minikube-certs"

        NAMESPACE = "ecommerce"

        USER_BLUE_DEPLOYMENT = "user-service-blue"
        USER_GREEN_DEPLOYMENT = "user-service-green"
        USER_BG_SERVICE = "user-service-bg"

        PRODUCT_BLUE_DEPLOYMENT = "product-service-blue"
        PRODUCT_GREEN_DEPLOYMENT = "product-service-green"
        PRODUCT_BG_SERVICE = "product-service-bg"

        CART_BLUE_DEPLOYMENT = "cart-service-blue"
        CART_GREEN_DEPLOYMENT = "cart-service-green"
        CART_BG_SERVICE = "cart-service-bg"

        ORDER_BLUE_DEPLOYMENT = "order-service-blue"
        ORDER_GREEN_DEPLOYMENT = "order-service-green"
        ORDER_BG_SERVICE = "order-service-bg"

        PAYMENT_BLUE_DEPLOYMENT = "payment-service-blue"
        PAYMENT_GREEN_DEPLOYMENT = "payment-service-green"
        PAYMENT_BG_SERVICE = "payment-service-bg"

        INVENTORY_BLUE_DEPLOYMENT = "inventory-service-blue"
        INVENTORY_GREEN_DEPLOYMENT = "inventory-service-green"
        INVENTORY_BG_SERVICE = "inventory-service-bg"
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

        stage('Deploy Blue-Green Manifests') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "DEPLOYING BLUE-GREEN MANIFESTS"
                    echo "========================================="

                    kubectl apply -f k8s/namespace.yaml
                    kubectl apply -f k8s/configmap.yaml
                    kubectl apply -f k8s/secret.yaml

                    echo ""
                    echo "Deploying User Service..."

                    kubectl apply -f k8s/user-service-blue.yaml
                    kubectl apply -f k8s/user-service-green.yaml
                    kubectl apply -f k8s/user-service-bg-service.yaml

                    echo ""
                    echo "Deploying Product Service..."

                    kubectl apply -f k8s/product-service-blue.yaml
                    kubectl apply -f k8s/product-service-green.yaml
                    kubectl apply -f k8s/product-service-bg-service.yaml

                    echo ""
                    echo "Deploying Cart Service..."

                    kubectl apply -f k8s/cart-service-blue.yaml
                    kubectl apply -f k8s/cart-service-green.yaml
                    kubectl apply -f k8s/cart-service-bg-service.yaml

                    echo ""
                    echo "Deploying Order Service..."

                    kubectl apply -f k8s/order-service-blue.yaml
                    kubectl apply -f k8s/order-service-green.yaml
                    kubectl apply -f k8s/order-service-bg-service.yaml

                    echo ""
                    echo "Deploying Payment Service..."

                    kubectl apply -f k8s/payment-service-blue.yaml
                    kubectl apply -f k8s/payment-service-green.yaml
                    kubectl apply -f k8s/payment-service-bg-service.yaml

                    echo ""
                    echo "Deploying Inventory Service..."

                    kubectl apply -f k8s/inventory-service-blue.yaml
                    kubectl apply -f k8s/inventory-service-green.yaml
                    kubectl apply -f k8s/inventory-service-bg-service.yaml

                    echo ""
                    echo "All Blue-Green manifests deployed successfully."
                '''
            }
        }

        stage('Update Green Deployments') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "UPDATING GREEN DEPLOYMENTS"
                    echo "Image Tag: ${IMAGE_TAG}"
                    echo "========================================="

                    kubectl set image deployment/${USER_GREEN_DEPLOYMENT} \
                        user-service=ecommerce-user-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl set image deployment/${PRODUCT_GREEN_DEPLOYMENT} \
                        product-service=ecommerce-product-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl set image deployment/${CART_GREEN_DEPLOYMENT} \
                        cart-service=ecommerce-cart-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl set image deployment/${ORDER_GREEN_DEPLOYMENT} \
                        order-service=ecommerce-order-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl set image deployment/${PAYMENT_GREEN_DEPLOYMENT} \
                        payment-service=ecommerce-payment-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    kubectl set image deployment/${INVENTORY_GREEN_DEPLOYMENT} \
                        inventory-service=ecommerce-inventory-service:${IMAGE_TAG} \
                        -n ${NAMESPACE}

                    echo ""
                    echo "All Green deployments updated."
                '''
            }
        }

        stage('Wait for Green Rollouts') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "WAITING FOR GREEN ROLLOUTS"
                    echo "========================================="

                    kubectl rollout status deployment/${USER_GREEN_DEPLOYMENT} \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl rollout status deployment/${PRODUCT_GREEN_DEPLOYMENT} \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl rollout status deployment/${CART_GREEN_DEPLOYMENT} \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl rollout status deployment/${ORDER_GREEN_DEPLOYMENT} \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl rollout status deployment/${PAYMENT_GREEN_DEPLOYMENT} \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl rollout status deployment/${INVENTORY_GREEN_DEPLOYMENT} \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    echo ""
                    echo "All Green deployments are ready."
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
                        -l version=green \
                        -o wide

                    echo ""
                    echo "Green pod verification completed."
                '''
            }
        }

        stage('Verify Green Health') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "VERIFYING GREEN HEALTH"
                    echo "========================================="

                    echo ""
                    echo "User Service:"
                    USER_POD=$(kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=user-service,version=green \
                        -o jsonpath='{.items[0].metadata.name}')

                    kubectl exec ${USER_POD} -n ${NAMESPACE} -- \
                        python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8001/health').read().decode())"

                    echo ""
                    echo "Product Service:"
                    PRODUCT_POD=$(kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=product-service,version=green \
                        -o jsonpath='{.items[0].metadata.name}')

                    kubectl exec ${PRODUCT_POD} -n ${NAMESPACE} -- \
                        python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8002/health').read().decode())"

                    echo ""
                    echo "Cart Service:"
                    CART_POD=$(kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=cart-service,version=green \
                        -o jsonpath='{.items[0].metadata.name}')

                    kubectl exec ${CART_POD} -n ${NAMESPACE} -- \
                        python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8003/health').read().decode())"

                    echo ""
                    echo "Order Service:"
                    ORDER_POD=$(kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=order-service,version=green \
                        -o jsonpath='{.items[0].metadata.name}')

                    kubectl exec ${ORDER_POD} -n ${NAMESPACE} -- \
                        python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8004/health').read().decode())"

                    echo ""
                    echo "Payment Service:"
                    PAYMENT_POD=$(kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=payment-service,version=green \
                        -o jsonpath='{.items[0].metadata.name}')

                    kubectl exec ${PAYMENT_POD} -n ${NAMESPACE} -- \
                        python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8005/health').read().decode())"

                    echo ""
                    echo "Inventory Service:"
                    INVENTORY_POD=$(kubectl get pods \
                        -n ${NAMESPACE} \
                        -l app=inventory-service,version=green \
                        -o jsonpath='{.items[0].metadata.name}')

                    kubectl exec ${INVENTORY_POD} -n ${NAMESPACE} -- \
                        python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8006/health').read().decode())"

                    echo ""
                    echo "All Green health checks passed."
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

                    kubectl patch svc ${USER_BG_SERVICE} \
                        -n ${NAMESPACE} \
                        -p '{"spec":{"selector":{"app":"user-service","version":"green"}}}'

                    kubectl patch svc ${PRODUCT_BG_SERVICE} \
                        -n ${NAMESPACE} \
                        -p '{"spec":{"selector":{"app":"product-service","version":"green"}}}'

                    kubectl patch svc ${CART_BG_SERVICE} \
                        -n ${NAMESPACE} \
                        -p '{"spec":{"selector":{"app":"cart-service","version":"green"}}}'

                    kubectl patch svc ${ORDER_BG_SERVICE} \
                        -n ${NAMESPACE} \
                        -p '{"spec":{"selector":{"app":"order-service","version":"green"}}}'

                    kubectl patch svc ${PAYMENT_BG_SERVICE} \
                        -n ${NAMESPACE} \
                        -p '{"spec":{"selector":{"app":"payment-service","version":"green"}}}'

                    kubectl patch svc ${INVENTORY_BG_SERVICE} \
                        -n ${NAMESPACE} \
                        -p '{"spec":{"selector":{"app":"inventory-service","version":"green"}}}'

                    echo ""
                    echo "Traffic successfully switched to Green."
                '''
            }
        }

        stage('Verify Traffic') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "VERIFYING GREEN TRAFFIC"
                    echo "========================================="

                    echo ""
                    echo "Service selectors:"

                    kubectl get svc -n ${NAMESPACE} \
                        -o custom-columns="SERVICE:.metadata.name,VERSION:.spec.selector.version"

                    echo ""
                    echo "Testing Ingress health endpoints..."

                    curl -f http://192.168.49.2/users/health
                    echo ""

                    curl -f http://192.168.49.2/products/health
                    echo ""

                    curl -f http://192.168.49.2/cart/health
                    echo ""

                    curl -f http://192.168.49.2/orders/health
                    echo ""

                    curl -f http://192.168.49.2/payments/health
                    echo ""

                    curl -f http://192.168.49.2/inventory/health
                    echo ""

                    echo ""
                    echo "All Green traffic health checks passed."
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
                    echo "Pods:"
                    kubectl get pods -n ${NAMESPACE}

                    echo ""
                    echo "Services:"
                    kubectl get svc -n ${NAMESPACE}

                    echo ""
                    echo "Deployments:"
                    kubectl get deployments -n ${NAMESPACE}

                    echo ""
                    echo "Blue-Green deployment completed successfully."
                '''
            }
        }
    }

    post {
        success {
            echo "========================================="
            echo "DEPLOYMENT SUCCESSFUL"
            echo "Build: ${BUILD_NUMBER}"
            echo "========================================="
        }

        failure {
            echo "========================================="
            echo "DEPLOYMENT FAILED"
            echo "Build: ${BUILD_NUMBER}"
            echo "========================================="
        }
    }
}
