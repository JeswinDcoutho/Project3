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
                git url: 'https://github.com/JeswinDcoutho/Project3.git', branch: 'master'
            }
        }

        stage('Terraform Init') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-terraform-user']]) {
                    sh 'terraform -chdir=terraform/vpc init -input=false'
                    sh 'terraform -chdir=terraform/ecr init -input=false'
                    sh 'terraform -chdir=terraform/eks init -input=false'
                    sh 'terraform -chdir=terraform/rds init -input=false'
                    sh 'terraform -chdir=terraform/redis init -input=false'
                }
            }
        }

        stage('Terraform Validate') {
            steps {
                sh 'terraform -chdir=terraform/vpc validate'
                sh 'terraform -chdir=terraform/ecr validate'
                sh 'terraform -chdir=terraform/eks validate'
                sh 'terraform -chdir=terraform/rds validate'
                sh 'terraform -chdir=terraform/redis validate'
            }
        }

        stage('Terraform Plan') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-terraform-user'], string(credentialsId: 'rds-db-password', variable: 'TF_VAR_db_password')]) {
                    sh 'terraform -chdir=terraform/vpc plan -input=false'
                    sh 'terraform -chdir=terraform/ecr plan -input=false'
                    sh 'terraform -chdir=terraform/eks plan -input=false'
                    sh 'terraform -chdir=terraform/rds plan -input=false'
                    sh 'terraform -chdir=terraform/redis plan -input=false'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t $ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG ./user-service'
                sh 'docker build -t $ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG ./product-service'
                sh 'docker build -t $ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG ./cart-service'
                sh 'docker build -t $ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG ./order-service'
                sh 'docker build -t $ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG ./payment-service'
                sh 'docker build -t $ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG ./inventory-service'
            }
        }

        stage('ECR Login') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-terraform-user']]) {
                    sh 'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY'
                }
            }
        }

        stage('ECR Push') {
            steps {
                sh 'docker push $ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG'
                sh 'docker push $ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG'
                sh 'docker push $ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG'
                sh 'docker push $ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG'
                sh 'docker push $ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG'
                sh 'docker push $ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG'
            }
        }

        stage('Configure EKS') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-terraform-user']]) {
                    sh 'aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $EKS_CLUSTER'
                    sh 'kubectl get nodes'
                }
            }
        }

        stage('Deploy Config') {
            steps {
                sh 'kubectl apply -f k8s/configmap.yaml'
                sh 'kubectl apply -f k8s/secret.yaml'
            }
        }

        stage('Deploy Blue Green') {
            steps {
                sh 'kubectl apply -f k8s/user-service-bg-service.yaml'
                sh 'kubectl apply -f k8s/product-service-bg-service.yaml'
                sh 'kubectl apply -f k8s/cart-service-bg-service.yaml'
                sh 'kubectl apply -f k8s/order-service-bg-service.yaml'
                sh 'kubectl apply -f k8s/payment-service-bg-service.yaml'
                sh 'kubectl apply -f k8s/inventory-service-bg-service.yaml'
                sh 'kubectl apply -f k8s/user-service-green.yaml'
                sh 'kubectl apply -f k8s/product-service-green.yaml'
                sh 'kubectl apply -f k8s/cart-service-green.yaml'
                sh 'kubectl apply -f k8s/order-service-green.yaml'
                sh 'kubectl apply -f k8s/payment-service-green.yaml'
                sh 'kubectl apply -f k8s/inventory-service-green.yaml'
            }
        }

        stage('Update Green Images') {
            steps {
                sh 'kubectl set image deployment/user-service-green user-service=$ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG -n $NAMESPACE'
                sh 'kubectl set image deployment/product-service-green product-service=$ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG -n $NAMESPACE'
                sh 'kubectl set image deployment/cart-service-green cart-service=$ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG -n $NAMESPACE'
                sh 'kubectl set image deployment/order-service-green order-service=$ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG -n $NAMESPACE'
                sh 'kubectl set image deployment/payment-service-green payment-service=$ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG -n $NAMESPACE'
                sh 'kubectl set image deployment/inventory-service-green inventory-service=$ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG -n $NAMESPACE'
            }
        }

        stage('Verify Rollout') {
            steps {
                sh 'kubectl rollout status deployment/user-service-green -n $NAMESPACE --timeout=180s'
                sh 'kubectl rollout status deployment/product-service-green -n $NAMESPACE --timeout=180s'
                sh 'kubectl rollout status deployment/cart-service-green -n $NAMESPACE --timeout=180s'
                sh 'kubectl rollout status deployment/order-service-green -n $NAMESPACE --timeout=180s'
                sh 'kubectl rollout status deployment/payment-service-green -n $NAMESPACE --timeout=180s'
                sh 'kubectl rollout status deployment/inventory-service-green -n $NAMESPACE --timeout=180s'
            }
        }

        stage('Apply HPA') {
            steps {
                sh 'kubectl apply -f k8s/user-hpa.yaml'
                sh 'kubectl apply -f k8s/product-hpa.yaml'
                sh 'kubectl apply -f k8s/cart-hpa.yaml'
                sh 'kubectl apply -f k8s/order-hpa.yaml'
                sh 'kubectl apply -f k8s/payment-hpa.yaml'
                sh 'kubectl apply -f k8s/inventory-hpa.yaml'
                sh 'kubectl get hpa -n $NAMESPACE'
            }
        }

        stage('Monitoring') {
            steps {
                sh 'helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace --set grafana.resources.requests.cpu=50m --set grafana.resources.requests.memory=128Mi --set grafana.resources.limits.cpu=300m --set grafana.resources.limits.memory=512Mi --set prometheus.prometheusSpec.resources.requests.cpu=100m --set prometheus.prometheusSpec.resources.requests.memory=256Mi --set prometheus.prometheusSpec.resources.limits.cpu=300m --set prometheus.prometheusSpec.resources.limits.memory=512Mi'
            }
        }

        stage('Service Monitors') {
            steps {
                sh 'kubectl apply -f k8s/user-service-monitor.yaml'
                sh 'kubectl apply -f k8s/product-service-monitor.yaml'
                sh 'kubectl apply -f k8s/cart-service-monitor.yaml'
                sh 'kubectl apply -f k8s/order-service-monitor.yaml'
                sh 'kubectl apply -f k8s/payment-service-monitor.yaml'
                sh 'kubectl apply -f k8s/inventory-service-monitor.yaml'
            }
        }

        stage('Health Checks') {
            steps {
                sh 'kubectl get pods -n $NAMESPACE'
                sh 'kubectl get services -n $NAMESPACE'
                sh 'kubectl get deployments -n $NAMESPACE'
                sh 'kubectl get hpa -n $NAMESPACE'
                sh 'kubectl get servicemonitors -n $NAMESPACE'
            }
        }
    }

    post {
        success {
            echo 'E-Commerce Microservices CI/CD Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check the failed stage in the Jenkins console.'
        }
    }
}
