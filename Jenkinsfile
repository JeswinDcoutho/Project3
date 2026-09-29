pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
        AWS_ACCOUNT_ID     = '777000838263'
        ECR_REGISTRY       = '777000838263.dkr.ecr.ap-south-1.amazonaws.com'
        EKS_CLUSTER        = 'ecommerce-eks'
        NAMESPACE          = 'nodejs-devops'

        // Jenkins build number is used as Docker image tag.
        IMAGE_TAG = "${BUILD_NUMBER}"

        // These are calculated during the pipeline.
        CURRENT_COLOR = ''
        TARGET_COLOR  = ''
    }

    stages {

        // =========================================================
        // 1. GIT CHECKOUT
        // =========================================================

        stage('Git Checkout') {
            steps {
                git branch: 'master',
                    credentialsId: 'github',
                    url: 'https://github.com/JeswinDcoutho/Project3.git'
            }
        }


        // =========================================================
        // 2. TERRAFORM
        // =========================================================

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


        // =========================================================
        // 3. DOCKER + ECR
        // =========================================================

        stage('Docker Build') {
            steps {
                sh '''
                    set -e

                    echo "===== Building Docker Images ====="
                    echo "Image tag: $IMAGE_TAG"

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


        // =========================================================
        // 4. EKS
        // =========================================================

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


        // =========================================================
        // 5. DETERMINE ACTIVE / TARGET COLOR
        // =========================================================

        stage('Determine Active Color') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    script {

                        def currentColor = sh(
                            script: """
                                kubectl get service user-service \
                                    -n ${NAMESPACE} \
                                    -o jsonpath='{.spec.selector.color}' \
                                    2>/dev/null || true
                            """,
                            returnStdout: true
                        ).trim()

                        /*
                         * First deployment:
                         *
                         * If the Service does not yet exist or does not
                         * have a color selector, we bootstrap with:
                         *
                         * CURRENT = blue
                         * TARGET  = green
                         *
                         * After that, Kubernetes Service state controls
                         * which color is active.
                         */

                        if (!currentColor) {

                            echo "No active Blue/Green color detected."
                            echo "This appears to be the first deployment."

                            env.CURRENT_COLOR = 'blue'
                            env.TARGET_COLOR  = 'green'

                        } else if (currentColor == 'blue') {

                            env.CURRENT_COLOR = 'blue'
                            env.TARGET_COLOR  = 'green'

                        } else if (currentColor == 'green') {

                            env.CURRENT_COLOR = 'green'
                            env.TARGET_COLOR  = 'blue'

                        } else {

                            error(
                                "Invalid color '${currentColor}' found in user-service. " +
                                "Expected blue or green."
                            )
                        }

                        echo "======================================"
                        echo "Blue/Green Deployment Decision"
                        echo "======================================"
                        echo "Current color : ${env.CURRENT_COLOR}"
                        echo "Target color  : ${env.TARGET_COLOR}"
                        echo "Image tag     : ${env.IMAGE_TAG}"
                        echo "======================================"
                    }
                }
            }
        }


        // =========================================================
        // 6. CREATE / UPDATE BOTH DEPLOYMENT SLOTS
        // =========================================================

        stage('Deploy Blue Green Resources') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        echo "===== Deploying User Service ====="

                        kubectl apply \
                            -f k8s/user-service-blue.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/user-service-green.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/user-service-bg-service.yaml \
                            -n $NAMESPACE


                        echo "===== Deploying Product Service ====="

                        kubectl apply \
                            -f k8s/product-service-blue.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/product-service-green.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/product-service-bg-service.yaml \
                            -n $NAMESPACE


                        echo "===== Deploying Cart Service ====="

                        kubectl apply \
                            -f k8s/cart-service-blue.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/cart-service-green.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/cart-service-bg-service.yaml \
                            -n $NAMESPACE


                        echo "===== Deploying Order Service ====="

                        kubectl apply \
                            -f k8s/order-service-blue.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/order-service-green.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/order-service-bg-service.yaml \
                            -n $NAMESPACE


                        echo "===== Deploying Payment Service ====="

                        kubectl apply \
                            -f k8s/payment-service-blue.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/payment-service-green.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/payment-service-bg-service.yaml \
                            -n $NAMESPACE


                        echo "===== Deploying Inventory Service ====="

                        kubectl apply \
                            -f k8s/inventory-service-blue.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/inventory-service-green.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/inventory-service-bg-service.yaml \
                            -n $NAMESPACE


                        echo "Blue/Green resources created/updated."
                    '''
                }
            }
        }


        // =========================================================
        // 7. UPDATE ONLY TARGET COLOR
        // =========================================================

        stage('Deploy New Version To Target') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        echo "======================================"
                        echo "Deploying New Version"
                        echo "======================================"
                        echo "Current color : $CURRENT_COLOR"
                        echo "Target color  : $TARGET_COLOR"
                        echo "Image tag     : $IMAGE_TAG"
                        echo "======================================"


                        echo "===== User Service ====="

                        kubectl -n $NAMESPACE set image \
                            deployment/user-service-$TARGET_COLOR \
                            user-service=$ECR_REGISTRY/ecommerce-user-service:$IMAGE_TAG


                        echo "===== Product Service ====="

                        kubectl -n $NAMESPACE set image \
                            deployment/product-service-$TARGET_COLOR \
                            product-service=$ECR_REGISTRY/ecommerce-product-service:$IMAGE_TAG


                        echo "===== Cart Service ====="

                        kubectl -n $NAMESPACE set image \
                            deployment/cart-service-$TARGET_COLOR \
                            cart-service=$ECR_REGISTRY/ecommerce-cart-service:$IMAGE_TAG


                        echo "===== Order Service ====="

                        kubectl -n $NAMESPACE set image \
                            deployment/order-service-$TARGET_COLOR \
                            order-service=$ECR_REGISTRY/ecommerce-order-service:$IMAGE_TAG


                        echo "===== Payment Service ====="

                        kubectl -n $NAMESPACE set image \
                            deployment/payment-service-$TARGET_COLOR \
                            payment-service=$ECR_REGISTRY/ecommerce-payment-service:$IMAGE_TAG


                        echo "===== Inventory Service ====="

                        kubectl -n $NAMESPACE set image \
                            deployment/inventory-service-$TARGET_COLOR \
                            inventory-service=$ECR_REGISTRY/ecommerce-inventory-service:$IMAGE_TAG


                        echo "New version deployed to $TARGET_COLOR."
                    '''
                }
            }
        }


        // =========================================================
        // 8. VERIFY TARGET ROLLOUT
        // =========================================================

        stage('Verify Target Rollout') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        echo "======================================"
                        echo "Waiting for $TARGET_COLOR rollouts"
                        echo "======================================"


                        kubectl rollout status \
                            deployment/user-service-$TARGET_COLOR \
                            -n $NAMESPACE \
                            --timeout=300s


                        kubectl rollout status \
                            deployment/product-service-$TARGET_COLOR \
                            -n $NAMESPACE \
                            --timeout=300s


                        kubectl rollout status \
                            deployment/cart-service-$TARGET_COLOR \
                            -n $NAMESPACE \
                            --timeout=300s


                        kubectl rollout status \
                            deployment/order-service-$TARGET_COLOR \
                            -n $NAMESPACE \
                            --timeout=300s


                        kubectl rollout status \
                            deployment/payment-service-$TARGET_COLOR \
                            -n $NAMESPACE \
                            --timeout=300s


                        kubectl rollout status \
                            deployment/inventory-service-$TARGET_COLOR \
                            -n $NAMESPACE \
                            --timeout=300s


                        echo "======================================"
                        echo "Target rollout successful."
                        echo "======================================"


                        echo "===== Target Pods ====="

                        kubectl get pods \
                            -n $NAMESPACE \
                            -l color=$TARGET_COLOR \
                            -o wide
                    '''
                }
            }
        }


        // =========================================================
        // 9. SWITCH TRAFFIC
        // =========================================================

        stage('Switch Traffic') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        echo "======================================"
                        echo "Switching Production Traffic"
                        echo "======================================"
                        echo "Old active color : $CURRENT_COLOR"
                        echo "New active color : $TARGET_COLOR"
                        echo "======================================"


                        echo "===== User Service ====="

                        kubectl patch service user-service \
                            -n $NAMESPACE \
                            --type=json \
                            -p="[{\\"op\\":\\"replace\\",\\"path\\":\\"/spec/selector/color\\",\\"value\\":\\"$TARGET_COLOR\\"]"


                        echo "===== Product Service ====="

                        kubectl patch service product-service \
                            -n $NAMESPACE \
                            --type=json \
                            -p="[{\\"op\\":\\"replace\\",\\"path\\":\\"/spec/selector/color\\",\\"value\\":\\"$TARGET_COLOR\\"]"


                        echo "===== Cart Service ====="

                        kubectl patch service cart-service \
                            -n $NAMESPACE \
                            --type=json \
                            -p="[{\\"op\\":\\"replace\\",\\"path\\":\\"/spec/selector/color\\",\\"value\\":\\"$TARGET_COLOR\\"]"


                        echo "===== Order Service ====="

                        kubectl patch service order-service \
                            -n $NAMESPACE \
                            --type=json \
                            -p="[{\\"op\\":\\"replace\\",\\"path\\":\\"/spec/selector/color\\",\\"value\\":\\"$TARGET_COLOR\\"]"


                        echo "===== Payment Service ====="

                        kubectl patch service payment-service \
                            -n $NAMESPACE \
                            --type=json \
                            -p="[{\\"op\\":\\"replace\\",\\"path\\":\\"/spec/selector/color\\",\\"value\\":\\"$TARGET_COLOR\\"]"


                        echo "===== Inventory Service ====="

                        kubectl patch service inventory-service \
                            -n $NAMESPACE \
                            --type=json \
                            -p="[{\\"op\\":\\"replace\\",\\"path\\":\\"/spec/selector/color\\",\\"value\\":\\"$TARGET_COLOR\\"]"


                        echo "======================================"
                        echo "Traffic successfully switched."
                        echo "Production color: $TARGET_COLOR"
                        echo "======================================"
                    '''
                }
            }
        }


        // =========================================================
        // 10. HPA
        // =========================================================

        stage('Apply HPA') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        echo "===== Applying HPA ====="

                        kubectl apply \
                            -f k8s/user-hpa.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/product-hpa.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/cart-hpa.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/order-hpa.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/payment-hpa.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/inventory-hpa.yaml \
                            -n $NAMESPACE


                        echo "===== HPA Status ====="

                        kubectl get hpa \
                            -n $NAMESPACE
                    '''
                }
            }
        }


        // =========================================================
        // 11. MONITORING
        // =========================================================

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

                        kubectl get pods \
                            -n monitoring
                    '''
                }
            }
        }


        // =========================================================
        // 12. SERVICE MONITORS
        // =========================================================

        stage('Service Monitors') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        kubectl apply \
                            -f k8s/user-service-monitor.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/product-service-monitor.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/cart-service-monitor.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/order-service-monitor.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/payment-service-monitor.yaml \
                            -n $NAMESPACE

                        kubectl apply \
                            -f k8s/inventory-service-monitor.yaml \
                            -n $NAMESPACE


                        echo "===== ServiceMonitors ====="

                        kubectl get servicemonitor \
                            -n $NAMESPACE
                    '''
                }
            }
        }


        // =========================================================
        // 13. FINAL HEALTH CHECK
        // =========================================================

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


                        echo "===== Active Color ====="

                        kubectl get service user-service \
                            -n $NAMESPACE \
                            -o jsonpath='{.spec.selector.color}'

                        echo ""


                        echo "===== Nodes ====="

                        kubectl get nodes


                        echo "===== Deployments ====="

                        kubectl get deployments \
                            -n $NAMESPACE


                        echo "===== Pods ====="

                        kubectl get pods \
                            -n $NAMESPACE


                        echo "===== Services ====="

                        kubectl get services \
                            -n $NAMESPACE


                        echo "===== HPA ====="

                        kubectl get hpa \
                            -n $NAMESPACE


                        echo "===== Ingress ====="

                        kubectl get ingress \
                            -A || true


                        echo "===== ServiceMonitors ====="

                        kubectl get servicemonitor \
                            -n $NAMESPACE


                        echo "===== Monitoring ====="

                        kubectl get pods \
                            -n monitoring


                        echo "======================================"
                        echo "Deployment health checks completed."
                        echo "======================================"
                    '''
                }
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================

    post {

        success {
            echo '''
======================================
Project 3 Jenkins Pipeline SUCCESS
======================================
'''
        }

        failure {
            echo '''
======================================
Project 3 Jenkins Pipeline FAILED
======================================

The production Service was only switched
after the target Blue/Green deployments
successfully completed their rollout.

Check the failed stage in Console Output.
'''
        }
    }
}
