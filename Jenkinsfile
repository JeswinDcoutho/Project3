pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
        AWS_ACCOUNT_ID     = '777000838263'
        ECR_REGISTRY       = '777000838263.dkr.ecr.ap-south-1.amazonaws.com'
        EKS_CLUSTER        = 'ecommerce-eks'
        NAMESPACE          = 'nodejs-devops'
        IMAGE_TAG          = "${BUILD_NUMBER}"
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

                        echo "===== Terraform Init: VPC ====="
                        cd terraform/vpc
                        terraform init

                        echo "===== Terraform Init: ECR ====="
                        cd ../ecr
                        terraform init

                        echo "===== Terraform Init: EKS ====="
                        cd ../eks
                        terraform init

                        echo "===== Terraform Init: RDS ====="
                        cd ../rds
                        terraform init

                        echo "===== Terraform Init: Redis ====="
                        cd ../redis
                        terraform init

                        echo "Terraform initialization completed."
                    '''
                }
            }
        }

        stage('Terraform Validate') {
            steps {
                sh '''
                    set -e

                    echo "===== Validating VPC ====="
                    cd terraform/vpc
                    terraform validate

                    echo "===== Validating ECR ====="
                    cd ../ecr
                    terraform validate

                    echo "===== Validating EKS ====="
                    cd ../eks
                    terraform validate

                    echo "===== Validating RDS ====="
                    cd ../rds
                    terraform validate

                    echo "===== Validating Redis ====="
                    cd ../redis
                    terraform validate

                    echo "Terraform validation completed successfully."
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

                        echo "===== Terraform Plan: VPC ====="
                        cd terraform/vpc
                        terraform plan

                        echo "===== Terraform Plan: ECR ====="
                        cd ../ecr
                        terraform plan

                        echo "===== Terraform Plan: EKS ====="
                        cd ../eks
                        terraform plan

                        echo "===== Terraform Plan: RDS ====="
                        cd ../rds
                        terraform plan

                        echo "===== Terraform Plan: Redis ====="
                        cd ../redis
                        terraform plan

                        echo "Terraform planning completed."
                    '''
                }
            }
        }

        stage('Terraform Apply') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user'],
                    string(credentialsId: 'rds-db-password',
                           variable: 'TF_VAR_db_password')
                ]) {
                    sh '''
                        set -e

                        echo "===== Creating VPC infrastructure ====="
                        cd terraform/vpc
                        terraform apply -auto-approve

                        echo "===== Creating ECR repositories ====="
                        cd ../ecr
                        terraform apply -auto-approve

                        echo "===== Creating EKS cluster ====="
                        cd ../eks
                        terraform apply -auto-approve

                        echo "===== Creating RDS database ====="
                        cd ../rds
                        terraform apply -auto-approve

                        echo "===== Creating Redis ====="
                        cd ../redis
                        terraform apply -auto-approve

                        echo "===== Terraform Apply completed successfully ====="
                    '''
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    set -e

                    echo "===== Building Docker Images ====="

                    docker build \
                        -t $ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG \
                        ./user-service

                    docker build \
                        -t $ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG \
                        ./product-service

                    docker build \
                        -t $ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG \
                        ./cart-service

                    docker build \
                        -t $ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG \
                        ./order-service

                    docker build \
                        -t $ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG \
                        ./payment-service

                    docker build \
                        -t $ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG \
                        ./inventory-service

                    echo "Docker images built successfully."
                    docker images | grep ecommerce
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

                        echo "===== Logging in to Amazon ECR ====="

                        aws sts get-caller-identity

                        aws ecr get-login-password \
                            --region $AWS_DEFAULT_REGION | \
                        docker login \
                            --username AWS \
                            --password-stdin $ECR_REGISTRY

                        echo "ECR login successful."
                    '''
                }
            }
        }

        stage('ECR Push') {
            steps {
                sh '''
                    set -e

                    echo "===== Pushing Images to ECR ====="

                    docker push \
                        $ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG

                    docker push \
                        $ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG

                    docker push \
                        $ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG

                    docker push \
                        $ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG

                    docker push \
                        $ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG

                    docker push \
                        $ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG

                    echo "All images pushed successfully."
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

                        echo "===== AWS Identity ====="
                        aws sts get-caller-identity

                        echo "===== Updating EKS kubeconfig ====="

                        aws eks update-kubeconfig \
                            --region $AWS_DEFAULT_REGION \
                            --name $EKS_CLUSTER

                        echo "===== EKS Nodes ====="
                        kubectl get nodes

                        echo "EKS configuration completed."
                    '''
                }
            }
        }

        stage('Prepare Namespace') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        kubectl create namespace $NAMESPACE \
                            --dry-run=client \
                            -o yaml | kubectl apply -f -

                        kubectl get namespace $NAMESPACE
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

                        echo "===== Applying ConfigMap ====="

                        kubectl apply \
                            -f k8s/configmap.yaml \
                            -n $NAMESPACE

                        kubectl get configmap \
                            ecommerce-config \
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

                        echo "===== Deploying User Service ====="
                        kubectl apply -f k8s/user-service-blue.yaml
                        kubectl apply -f k8s/user-service-green.yaml
                        kubectl apply -f k8s/user-service-bg-service.yaml

                        echo "===== Deploying Product Service ====="
                        kubectl apply -f k8s/product-service-blue.yaml
                        kubectl apply -f k8s/product-service-green.yaml
                        kubectl apply -f k8s/product-service-bg-service.yaml

                        echo "===== Deploying Cart Service ====="
                        kubectl apply -f k8s/cart-service-blue.yaml
                        kubectl apply -f k8s/cart-service-green.yaml
                        kubectl apply -f k8s/cart-service-bg-service.yaml

                        echo "===== Deploying Order Service ====="
                        kubectl apply -f k8s/order-service-blue.yaml
                        kubectl apply -f k8s/order-service-green.yaml
                        kubectl apply -f k8s/order-service-bg-service.yaml

                        echo "===== Deploying Payment Service ====="
                        kubectl apply -f k8s/payment-service-blue.yaml
                        kubectl apply -f k8s/payment-service-green.yaml
                        kubectl apply -f k8s/payment-service-bg-service.yaml

                        echo "===== Deploying Inventory Service ====="
                        kubectl apply -f k8s/inventory-service-blue.yaml
                        kubectl apply -f k8s/inventory-service-green.yaml
                        kubectl apply -f k8s/inventory-service-bg-service.yaml

                        echo "Blue/Green resources created."
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

                        kubectl -n $NAMESPACE set image \
                            deployment/user-service-green \
                            user-service=$ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image \
                            deployment/product-service-green \
                            product-service=$ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image \
                            deployment/cart-service-green \
                            cart-service=$ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image \
                            deployment/order-service-green \
                            order-service=$ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image \
                            deployment/payment-service-green \
                            payment-service=$ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG

                        kubectl -n $NAMESPACE set image \
                            deployment/inventory-service-green \
                            inventory-service=$ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG

                        echo "Green deployments updated with build $IMAGE_TAG."
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

                        kubectl rollout status \
                            deployment/user-service-green \
                            -n $NAMESPACE \
                            --timeout=300s

                        kubectl rollout status \
                            deployment/product-service-green \
                            -n $NAMESPACE \
                            --timeout=300s

                        kubectl rollout status \
                            deployment/cart-service-green \
                            -n $NAMESPACE \
                            --timeout=300s

                        kubectl rollout status \
                            deployment/order-service-green \
                            -n $NAMESPACE \
                            --timeout=300s

                        kubectl rollout status \
                            deployment/payment-service-green \
                            -n $NAMESPACE \
                            --timeout=300s

                        kubectl rollout status \
                            deployment/inventory-service-green \
                            -n $NAMESPACE \
                            --timeout=300s

                        echo "===== Deployments ====="
                        kubectl get deployments -n $NAMESPACE

                        echo "===== Pods ====="
                        kubectl get pods -n $NAMESPACE -o wide
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

                        echo "===== HPA Status ====="
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

                        echo "===== Adding Prometheus Helm Repository ====="

                        helm repo add prometheus-community \
                            https://prometheus-community.github.io/helm-charts \
                            || true

                        helm repo update

                        echo "===== Installing/Updating Monitoring Stack ====="

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

                        echo "===== Monitoring Pods ====="
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

                        echo "===== ServiceMonitors ====="
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

                        echo "======================================"
                        echo "       FINAL DEPLOYMENT STATUS"
                        echo "======================================"

                        echo "===== Nodes ====="
                        kubectl get nodes

                        echo "===== Deployments ====="
                        kubectl get deployments -n $NAMESPACE

                        echo "===== Pods ====="
                        kubectl get pods -n $NAMESPACE

                        echo "===== Services ====="
                        kubectl get services -n $NAMESPACE

                        echo "===== HPA ====="
                        kubectl get hpa -n $NAMESPACE

                        echo "===== Ingress ====="
                        kubectl get ingress -A || true

                        echo "===== ServiceMonitors ====="
                        kubectl get servicemonitor -n $NAMESPACE

                        echo "===== Monitoring ====="
                        kubectl get pods -n monitoring

                        echo "======================================"
                        echo "Deployment health checks completed."
                        echo "======================================"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '======================================'
            echo 'Project 3 Jenkins Pipeline SUCCESS'
            echo '======================================'
        }

        failure {
            echo '======================================'
            echo 'Project 3 Jenkins Pipeline FAILED'
            echo 'Check the failed stage in Console Output.'
            echo '======================================'
        }
    }
}
