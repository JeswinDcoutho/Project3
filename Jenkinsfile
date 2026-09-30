pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
        AWS_ACCOUNT_ID     = '777000838263'
        ECR_REGISTRY       = '777000838263.dkr.ecr.ap-south-1.amazonaws.com'
        EKS_CLUSTER        = 'ecommerce-eks'
        NAMESPACE          = 'nodejs-devops'

        // Jenkins build number is used as the Docker image tag.
        IMAGE_TAG = "${BUILD_NUMBER}"

        // Dedicated S3 object for the Kubernetes database secret.
        DB_SECRET_S3_URI = 's3://ecommerce-terraform-state-777000838263/ecommerce/secrets/ecommerce-db-secret.json'
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


        stage('Terraform Infrastructure') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user'],
                    string(credentialsId: 'rds-db-password',
                           variable: 'TF_VAR_db_password')
                ]) {
                    sh '''
                        set -e

                        echo "======================================"
                        echo " Terraform Infrastructure Deployment"
                        echo "======================================"

                        # ==================================================
                        # VPC
                        # ==================================================

                        echo "===== Terraform Plan: VPC ====="

                        cd terraform/vpc
                        terraform plan

                        echo "===== Terraform Apply: VPC ====="

                        terraform apply -auto-approve

                        echo "===== Reading VPC ID ====="

                        VPC_ID=$(terraform output -raw vpc_id)

                        if [ -z "$VPC_ID" ]; then
                            echo "ERROR: VPC ID was not returned by Terraform."
                            exit 1
                        fi

                        echo "Created/Active VPC: $VPC_ID"

                        cd ../..

                        # ==================================================
                        # ECR
                        # ==================================================

                        echo "===== Terraform Plan: ECR ====="

                        cd terraform/ecr
                        terraform plan

                        echo "===== Terraform Apply: ECR ====="

                        terraform apply -auto-approve

                        cd ../..

                        # ==================================================
                        # EKS
                        # ==================================================

                        echo "===== Terraform Plan: EKS ====="
                        echo "Using VPC: $VPC_ID"

                        cd terraform/eks

                        terraform plan \
                            -var="vpc_id=$VPC_ID"

                        echo "===== Terraform Apply: EKS ====="

                        terraform apply \
                            -auto-approve \
                            -var="vpc_id=$VPC_ID"

                        echo "===== Reading EKS Security Group ID ====="

                        EKS_SG_ID=$(terraform output -raw cluster_security_group_id)

                        if [ -z "$EKS_SG_ID" ]; then
                            echo "ERROR: EKS security group ID was not returned by Terraform."
                            exit 1
                        fi

                        echo "Active EKS Security Group: $EKS_SG_ID"

                        cd ../..

                        # ==================================================
                        # RDS
                        # ==================================================

                        echo "===== Terraform Plan: RDS ====="
                        echo "Using VPC: $VPC_ID"
                        echo "Using EKS Security Group: $EKS_SG_ID"

                        cd terraform/rds

                        terraform plan \
                            -var="vpc_id=$VPC_ID" \
                            -var="eks_security_group_id=$EKS_SG_ID"

                        echo "===== Terraform Apply: RDS ====="

                        terraform apply \
                            -auto-approve \
                            -var="vpc_id=$VPC_ID" \
                            -var="eks_security_group_id=$EKS_SG_ID"

                        cd ../..

                        # ==================================================
                        # Redis
                        # ==================================================

                        echo "===== Terraform Plan: Redis ====="
                        echo "Using VPC: $VPC_ID"
                        echo "Using EKS Security Group: $EKS_SG_ID"

                        cd terraform/redis

                        terraform plan \
                            -var="vpc_id=$VPC_ID" \
                            -var="eks_security_group_id=$EKS_SG_ID"

                        echo "===== Terraform Apply: Redis ====="

                        terraform apply \
                            -auto-approve \
                            -var="vpc_id=$VPC_ID" \
                            -var="eks_security_group_id=$EKS_SG_ID"

                        cd ../..

                        echo "======================================"
                        echo " Terraform Infrastructure SUCCESS"
                        echo "======================================"
                        echo "VPC ID    : $VPC_ID"
                        echo "EKS SG ID : $EKS_SG_ID"
                        echo "EKS       : ecommerce-eks"
                        echo "======================================"
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
                sh '''
                    set -e

                    kubectl create namespace $NAMESPACE \
                        --dry-run=client \
                        -o yaml | kubectl apply -f -

                    kubectl get namespace $NAMESPACE
                '''
            }
        }


        // =========================================================
        // 5. CONFIGURATION
        // =========================================================

        stage('Deploy Config') {
            steps {
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


        // =========================================================
        // 6. DATABASE SECRET
        // =========================================================

        stage('Create Database Secret') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user'],
                    string(credentialsId: 'rds-db-password',
                           variable: 'RDS_DB_PASSWORD')
                ]) {
                    sh '''
                        set -e
                        set +x

                        echo "======================================"
                        echo " Creating Database Secret"
                        echo "======================================"

                        SECRET_NAME="ecommerce-db-secret"
                        SECRET_FILE="$(mktemp)"

                        cleanup() {
                            rm -f "$SECRET_FILE"
                        }

                        trap cleanup EXIT

                        # --------------------------------------------------
                        # Verify required tooling
                        # --------------------------------------------------

                        if ! command -v jq >/dev/null 2>&1; then
                            echo "ERROR: jq is required for secure JSON generation."
                            echo "Install jq on the Jenkins agent and retry."
                            exit 1
                        fi

                        # --------------------------------------------------
                        # Create Kubernetes Secret
                        # --------------------------------------------------

                        kubectl create secret generic "$SECRET_NAME" \
                            --namespace "$NAMESPACE" \
                            --from-literal=POSTGRES_USER=ecommerce \
                            --from-literal=POSTGRES_PASSWORD="$RDS_DB_PASSWORD" \
                            --dry-run=client \
                            -o yaml | \
                        kubectl apply -f -

                        # --------------------------------------------------
                        # Generate separate S3 secret object.
                        #
                        # IMPORTANT:
                        # The password is never echoed.
                        # --------------------------------------------------

                        jq -n \
                            --arg username "ecommerce" \
                            --arg password "$RDS_DB_PASSWORD" \
                            '{
                                POSTGRES_USER: $username,
                                POSTGRES_PASSWORD: $password
                            }' > "$SECRET_FILE"

                        # --------------------------------------------------
                        # Upload to dedicated S3 object.
                        # Existing Terraform state is NOT read.
                        # --------------------------------------------------

                        aws s3 cp \
                            "$SECRET_FILE" \
                            "$DB_SECRET_S3_URI" \
                            --region "$AWS_DEFAULT_REGION" \
                            --sse AES256

                        # --------------------------------------------------
                        # Verify Kubernetes Secret exists without exposing
                        # its contents.
                        # --------------------------------------------------

                        kubectl get secret "$SECRET_NAME" \
                            -n "$NAMESPACE"

                        echo "Kubernetes database Secret created/updated."

                        echo "Dedicated S3 database secret object uploaded:"
                        echo "$DB_SECRET_S3_URI"

                        echo "Database secret preparation completed."
                    '''
                }
            }
        }


        // =========================================================
        // 7. ROLLING DEPLOYMENTS
        // =========================================================

        stage('Deploy Rolling Deployments') {
            steps {
                script {

                    def services = [
                        'user-service',
                        'product-service',
                        'cart-service',
                        'order-service',
                        'payment-service',
                        'inventory-service'
                    ]

                    services.each { service ->

                        echo "======================================"
                        echo "Deploying ${service}"
                        echo "Image tag: ${env.IMAGE_TAG}"
                        echo "======================================"

                        sh """
                            set -e

                            echo "Applying ${service} Deployment"

                            sed 's|IMAGE_TAG_PLACEHOLDER|${IMAGE_TAG}|g' \
                                k8s/${service}-deployment.yaml | \
                            kubectl apply -f - \
                                -n ${NAMESPACE}

                            echo "Deployment ${service} applied."
                        """
                    }
                }
            }
        }


        // =========================================================
        // 8. SERVICES
        // =========================================================

        stage('Deploy Services') {
            steps {
                script {

                    def services = [
                        'user-service',
                        'product-service',
                        'cart-service',
                        'order-service',
                        'payment-service',
                        'inventory-service'
                    ]

                    services.each { service ->

                        sh """
                            set -e

                            echo "Applying ${service} Service"

                            kubectl apply \
                                -f k8s/${service}-service.yaml \
                                -n ${NAMESPACE}
                        """
                    }

                    sh '''
                        echo "===== Services ====="

                        kubectl get services \
                            -n $NAMESPACE
                    '''
                }
            }
        }


        // =========================================================
        // 9. HPA
        // =========================================================

        stage('Deploy HPAs') {
            steps {
                script {

                    def services = [
                        'user-service',
                        'product-service',
                        'cart-service',
                        'order-service',
                        'payment-service',
                        'inventory-service'
                    ]

                    services.each { service ->

                        sh """
                            set -e

                            echo "Applying ${service} HPA"

                            kubectl apply \
                                -f k8s/${service}-hpa.yaml \
                                -n ${NAMESPACE}
                        """
                    }

                    sh '''
                        echo "===== HPAs ====="

                        kubectl get hpa \
                            -n $NAMESPACE
                    '''
                }
            }
        }


        // =========================================================
        // 10. VERIFY ROLLING DEPLOYMENTS
        // =========================================================

        stage('Verify Rolling Deployments') {
            steps {
                script {

                    def services = [
                        'user-service',
                        'product-service',
                        'cart-service',
                        'order-service',
                        'payment-service',
                        'inventory-service'
                    ]

                    services.each { service ->

                        sh """
                            set -e

                            echo "======================================"
                            echo "Waiting for ${service} rollout"
                            echo "======================================"

                            kubectl rollout status \
                                deployment/${service} \
                                -n ${NAMESPACE} \
                                --timeout=300s

                            echo "===== ${service} Deployment ====="

                            kubectl get deployment \
                                ${service} \
                                -n ${NAMESPACE}
                        """
                    }
                }
            }
        }


        // =========================================================
        // 11. VERIFY PODS AND SERVICE ENDPOINTS
        // =========================================================

        stage('Verify Services and Endpoints') {
            steps {
                sh '''
                    set -e

                    echo "======================================"
                    echo "Verifying Services and Endpoints"
                    echo "======================================"

                    for service in \
                        user-service \
                        product-service \
                        cart-service \
                        order-service \
                        payment-service \
                        inventory-service
                    do

                        echo "--------------------------------------"
                        echo "Checking $service"
                        echo "--------------------------------------"

                        READY_REPLICAS=$(kubectl get deployment "$service" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.status.readyReplicas}')

                        if [ -z "$READY_REPLICAS" ]; then
                            READY_REPLICAS=0
                        fi

                        if [ "$READY_REPLICAS" -lt 1 ]; then
                            echo "ERROR: $service has no ready replicas."
                            kubectl describe deployment "$service" \
                                -n "$NAMESPACE" || true
                            exit 1
                        fi

                        echo "Ready replicas: $READY_REPLICAS"

                        ENDPOINT_COUNT=$(kubectl get endpoints "$service-bg" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{range .subsets[*].addresses[*]}1{end}' \
                            | wc -c)

                        if [ "$ENDPOINT_COUNT" -lt 1 ]; then
                            echo "ERROR: $service-bg has no endpoints."
                            kubectl describe service "$service-bg" \
                                -n "$NAMESPACE" || true
                            exit 1
                        fi

                        echo "$service-bg has active endpoints."

                    done

                    echo "======================================"
                    echo "All Services and Endpoints verified."
                    echo "======================================"
                '''
            }
        }


        // =========================================================
        // 12. VERIFY HPA
        // =========================================================

        stage('Verify HPA') {
            steps {
                sh '''
                    set -e

                    echo "======================================"
                    echo "Verifying HPA Targets"
                    echo "======================================"

                    for service in \
                        user-service \
                        product-service \
                        cart-service \
                        order-service \
                        payment-service \
                        inventory-service
                    do

                        HPA_NAME="${service}-hpa"

                        echo "--------------------------------------"
                        echo "Checking $HPA_NAME"
                        echo "--------------------------------------"

                        TARGET=$(kubectl get hpa "$HPA_NAME" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.spec.scaleTargetRef.name}')

                        EXPECTED="$service"

                        echo "HPA target   : $TARGET"
                        echo "Expected     : $EXPECTED"

                        if [ "$TARGET" != "$EXPECTED" ]; then
                            echo "ERROR: $HPA_NAME targets $TARGET"
                            echo "Expected $EXPECTED"
                            exit 1
                        fi

                        MIN_REPLICAS=$(kubectl get hpa "$HPA_NAME" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.spec.minReplicas}')

                        MAX_REPLICAS=$(kubectl get hpa "$HPA_NAME" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.spec.maxReplicas}')

                        echo "Min replicas : $MIN_REPLICAS"
                        echo "Max replicas : $MAX_REPLICAS"

                        echo "$HPA_NAME verification passed."

                    done

                    echo "======================================"
                    echo "All HPAs verified."
                    echo "======================================"

                    kubectl get hpa \
                        -n "$NAMESPACE"
                '''
            }
        }


        // =========================================================
        // 13. MONITORING
        // =========================================================

        stage('Apply Monitoring') {
            steps {
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


        // =========================================================
        // 14. SERVICE MONITORS
        // =========================================================

        stage('Apply ServiceMonitors') {
            steps {
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


        // =========================================================
        // 15. FINAL HEALTH CHECKS
        // =========================================================

        stage('Final Health Checks') {
            steps {
                sh '''
                    set -e

                    echo "======================================"
                    echo "       FINAL DEPLOYMENT STATUS"
                    echo "======================================"

                    echo "===== Nodes ====="

                    kubectl get nodes

                    echo "===== Rolling Deployments ====="

                    kubectl get deployments \
                        -n $NAMESPACE

                    echo "===== Pods ====="

                    kubectl get pods \
                        -n $NAMESPACE \
                        -o wide

                    echo "===== Services ====="

                    kubectl get services \
                        -n $NAMESPACE

                    echo "===== Endpoints ====="

                    kubectl get endpoints \
                        -n $NAMESPACE

                    echo "===== HPA ====="

                    kubectl get hpa \
                        -n $NAMESPACE

                    echo "===== HPA Details ====="

                    kubectl describe hpa user-service-hpa \
                        -n $NAMESPACE || true

                    kubectl describe hpa product-service-hpa \
                        -n $NAMESPACE || true

                    kubectl describe hpa cart-service-hpa \
                        -n $NAMESPACE || true

                    kubectl describe hpa order-service-hpa \
                        -n $NAMESPACE || true

                    kubectl describe hpa payment-service-hpa \
                        -n $NAMESPACE || true

                    kubectl describe hpa inventory-service-hpa \
                        -n $NAMESPACE || true

                    echo "===== Ingress ====="

                    kubectl get ingress \
                        -A || true

                    echo "===== ServiceMonitors ====="

                    kubectl get servicemonitor \
                        -n $NAMESPACE

                    echo "===== Monitoring ====="

                    kubectl get pods \
                        -n monitoring

                    echo "===== Rolling Deployment Verification ====="

                    for service in \
                        user-service \
                        product-service \
                        cart-service \
                        order-service \
                        payment-service \
                        inventory-service
                    do

                        echo "--------------------------------------"
                        echo "$service"
                        echo "--------------------------------------"

                        READY_REPLICAS=$(kubectl get deployment "$service" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.status.readyReplicas}')

                        DESIRED_REPLICAS=$(kubectl get deployment "$service" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.spec.replicas}')

                        IMAGE=$(kubectl get deployment "$service" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.spec.template.spec.containers[0].image}')

                        HPA_TARGET=$(kubectl get hpa "${service}-hpa" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.spec.scaleTargetRef.name}')

                        SERVICE_SELECTOR=$(kubectl get service "${service}-bg" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.spec.selector}')

                        echo "Image           : $IMAGE"
                        echo "Ready replicas  : $READY_REPLICAS"
                        echo "Desired replicas: $DESIRED_REPLICAS"
                        echo "HPA target      : $HPA_TARGET"
                        echo "Service selector: $SERVICE_SELECTOR"

                        if [ -z "$READY_REPLICAS" ]; then
                            echo "ERROR: $service has no ready replicas."
                            exit 1
                        fi

                        if [ "$READY_REPLICAS" -lt 1 ]; then
                            echo "ERROR: $service does not have a ready replica."
                            exit 1
                        fi

                        if [ "$HPA_TARGET" != "$service" ]; then
                            echo "ERROR: ${service}-hpa targets $HPA_TARGET"
                            exit 1
                        fi

                        echo "$service health check passed."

                    done

                    echo "======================================"
                    echo " ALL FINAL HEALTH CHECKS PASSED"
                    echo "======================================"

                    echo "Deployment model : RollingUpdate"
                    echo "Image tag        : $IMAGE_TAG"
                    echo "Namespace        : $NAMESPACE"
                    echo "======================================"
                '''
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================

    post {

        success {
            echo '======================================'
            echo 'Project 3 Jenkins Pipeline SUCCESS'
            echo 'Deployment strategy: RollingUpdate'
            echo "Image tag: ${env.IMAGE_TAG}"
            echo '======================================'
        }

        failure {
            echo '======================================'
            echo 'Project 3 Jenkins Pipeline FAILED'
            echo 'Check the failed stage in Console Output.'
            echo '======================================'
        }

        always {
            echo '======================================'
            echo 'Pipeline execution completed.'
            echo '======================================'
        }
    }
}
