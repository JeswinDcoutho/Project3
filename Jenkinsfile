pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
        AWS_ACCOUNT_ID = '777000838263'
        ECR_REGISTRY = '777000838263.dkr.ecr.ap-south-1.amazonaws.com'
        EKS_CLUSTER = 'ecommerce-eks'
        NAMESPACE = 'nodejs-devops'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Git Checkout') {
            steps {
                git branch: 'master',
                    credentialsId: 'github',
                    url: 'https://github.com/JeswinDcoutho/Project3.git'
            }
        }

        stage('Terraform Init') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user'],
                    string(credentialsId: 'rds-db-password',
                           variable: 'TF_VAR_db_password')
                ]) {
                    sh '''
                        set -e

                        cd terraform/vpc
                        terraform init

                        cd ../ecr
                        terraform init

                        cd ../eks
                        terraform init

                        cd ../rds
                        terraform init

                        cd ../redis
                        terraform init
                    '''
                }
            }
        }

        stage('Terraform Validate') {
            steps {
                sh '''
                    set -e

                    cd terraform/vpc
                    terraform validate

                    cd ../ecr
                    terraform validate

                    cd ../eks
                    terraform validate

                    cd ../rds
                    terraform validate

                    cd ../redis
                    terraform validate
                '''
            }
        }

        stage('Terraform Plan') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user'],
                    string(credentialsId: 'rds-db-password',
                           variable: 'TF_VAR_db_password')
                ]) {
                    sh '''
                        set -e

                        cd terraform/vpc
                        terraform plan

                        cd ../ecr
                        terraform plan

                        cd ../eks
                        terraform plan

                        cd ../rds
                        terraform plan

                        cd ../redis
                        terraform plan
                    '''
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    set -e

                    docker build -t $ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG ./user-service
                    docker build -t $ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG ./product-service
                    docker build -t $ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG ./cart-service
                    docker build -t $ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG ./order-service
                    docker build -t $ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG ./payment-service
                    docker build -t $ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG ./inventory-service
                '''
            }
        }

        stage('ECR Login') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        aws ecr get-login-password \
                            --region $AWS_DEFAULT_REGION | \
                            docker login \
                            --username AWS \
                            --password-stdin $ECR_REGISTRY
                    '''
                }
            }
        }

        stage('ECR Push') {
            steps {
                sh '''
                    set -e

                    docker push $ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG
                    docker push $ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG
                    docker push $ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG
                    docker push $ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG
                    docker push $ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG
                    docker push $ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG
                '''
            }
        }

        stage('Configure EKS') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        aws sts get-caller-identity

                        aws eks update-kubeconfig \
                            --region $AWS_DEFAULT_REGION \
                            --name $EKS_CLUSTER

                        kubectl get nodes
                    '''
                }
            }
        }

        stage('Deploy Config') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        kubectl apply -f k8s/configmap.yaml \
                            -n $NAMESPACE

                        kubectl get configmap ecommerce-config \
                            -n $NAMESPACE
                    '''
                }
            }
        }

        stage('Deploy Blue Green') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        kubectl apply -f k8s/user-service-blue.yaml
                        kubectl apply -f k8s/user-service-green.yaml
                        kubectl apply -f k8s/user-service-bg-service.yaml

                        kubectl apply -f k8s/product-service-blue.yaml
                        kubectl apply -f k8s/product-service-green.yaml
                        kubectl apply -f k8s/product-service-bg-service.yaml

                        kubectl apply -f k8s/cart-service-blue.yaml
                        kubectl apply -f k8s/cart-service-green.yaml
                        kubectl apply -f k8s/cart-service-bg-service.yaml

                        kubectl apply -f k8s/order-service-blue.yaml
                        kubectl apply -f k8s/order-service-green.yaml
                        kubectl apply -f k8s/order-service-bg-service.yaml

                        kubectl apply -f k8s/payment-service-blue.yaml
                        kubectl apply -f k8s/payment-service-green.yaml
                        kubectl apply -f k8s/payment-service-bg-service.yaml

                        kubectl apply -f k8s/inventory-service-blue.yaml
                        kubectl apply -f k8s/inventory-service-green.yaml
                        kubectl apply -f k8s/inventory-service-bg-service.yaml
                    '''
                }
            }
        }

        stage('Update Green Images') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        kubectl -n $NAMESPACE set image deployment/user-service-green \
                            user-service=$ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image deployment/product-service-green \
                            product-service=$ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image deployment/cart-service-green \
                            cart-service=$ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image deployment/order-service-green \
                            order-service=$ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image deployment/payment-service-green \
                            payment-service=$ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image deployment/inventory-service-green \
                            inventory-service=$ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG
                    '''
                }
            }
        }

        stage('Verify Rollout') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        kubectl rollout status deployment/user-service-green \
                            -n $NAMESPACE --timeout=180s

                        kubectl rollout status deployment/product-service-green \
                            -n $NAMESPACE --timeout=180s

                        kubectl rollout status deployment/cart-service-green \
                            -n $NAMESPACE --timeout=180s

                        kubectl rollout status deployment/order-service-green \
                            -n $NAMESPACE --timeout=180s

                        kubectl rollout status deployment/payment-service-green \
                            -n $NAMESPACE --timeout=180s

                        kubectl rollout status deployment/inventory-service-green \
                            -n $NAMESPACE --timeout=180s

                        kubectl get pods -n $NAMESPACE
                    '''
                }
            }
        }

        stage('Apply HPA') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        kubectl apply -f k8s/user-hpa.yaml
                        kubectl apply -f k8s/product-hpa.yaml
                        kubectl apply -f k8s/cart-hpa.yaml
                        kubectl apply -f k8s/order-hpa.yaml
                        kubectl apply -f k8s/payment-hpa.yaml
                        kubectl apply -f k8s/inventory-hpa.yaml

                        kubectl get hpa -n $NAMESPACE
                    '''
                }
            }
        }

        stage('Monitoring') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        helm upgrade --install monitoring \
                            prometheus-community/kube-prometheus-stack \
                            --namespace monitoring \
                            --create-namespace \
                            --set grafana.resources.requests.cpu=50m \
                            --set grafana.resources.requests.memory=128Mi \
                            --set grafana.resources.limits.cpu=300m \
                            --set grafana.resources.limits.memory=512Mi \
                            --set prometheus.prometheusSpec.resources.requests.cpu=100m \
                            --set prometheus.prometheusSpec.resources.requests.memory=256Mi \
                            --set prometheus.prometheusSpec.resources.limits.cpu=300m \
                            --set prometheus.prometheusSpec.resources.limits.memory=512Mi

                        kubectl get pods -n monitoring
                    '''
                }
            }
        }

        stage('Service Monitors') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        kubectl apply -f k8s/user-service-monitor.yaml
                        kubectl apply -f k8s/product-service-monitor.yaml
                        kubectl apply -f k8s/cart-service-monitor.yaml
                        kubectl apply -f k8s/order-service-monitor.yaml
                        kubectl apply -f k8s/payment-service-monitor.yaml
                        kubectl apply -f k8s/inventory-service-monitor.yaml

                        kubectl get servicemonitor -n $NAMESPACE
                    '''
                }
            }
        }

        stage('Health Checks') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        echo "Checking Kubernetes resources..."
                        kubectl get deployments -n $NAMESPACE
                        kubectl get pods -n $NAMESPACE
                        kubectl get services -n $NAMESPACE
                        kubectl get hpa -n $NAMESPACE

                        echo "Checking ingress..."
                        kubectl get ingress -A || true

                        echo "Checking monitoring..."
                        kubectl get pods -n monitoring

                        echo "Deployment health checks completed successfully."
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check the failed stage in the Jenkins console.'
        }
    }
}
