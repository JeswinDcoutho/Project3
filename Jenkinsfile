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

        // Blue/Green state is persisted in .bg-state after detection.
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
                        echo "VPC ID        : $VPC_ID"
                        echo "EKS SG ID     : $EKS_SG_ID"
                        echo "EKS           : ecommerce-eks"
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
        // 5. PREPARE BLUE/GREEN RESOURCES
        // =========================================================

        stage('Prepare Blue Green Resources') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    sh '''
                        set -e

                        echo "===== Preparing Blue/Green Deployments ====="

                        kubectl get deployment user-service-blue \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/user-service-blue.yaml

                        kubectl get deployment user-service-green \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/user-service-green.yaml

                        kubectl get deployment product-service-blue \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/product-service-blue.yaml

                        kubectl get deployment product-service-green \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/product-service-green.yaml

                        kubectl get deployment cart-service-blue \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/cart-service-blue.yaml

                        kubectl get deployment cart-service-green \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/cart-service-green.yaml

                        kubectl get deployment order-service-blue \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/order-service-blue.yaml

                        kubectl get deployment order-service-green \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/order-service-green.yaml

                        kubectl get deployment payment-service-blue \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/payment-service-blue.yaml

                        kubectl get deployment payment-service-green \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/payment-service-green.yaml

                        kubectl get deployment inventory-service-blue \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/inventory-service-blue.yaml

                        kubectl get deployment inventory-service-green \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/inventory-service-green.yaml

                        echo "===== Preparing BG Services ====="

                        kubectl get service user-service-bg \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/user-service-bg-service.yaml

                        kubectl get service product-service-bg \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/product-service-bg-service.yaml

                        kubectl get service cart-service-bg \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/cart-service-bg-service.yaml

                        kubectl get service order-service-bg \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/order-service-bg-service.yaml

                        kubectl get service payment-service-bg \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/payment-service-bg-service.yaml

                        kubectl get service inventory-service-bg \
                            -n $NAMESPACE >/dev/null 2>&1 || \
                            kubectl apply -f k8s/inventory-service-bg-service.yaml

                        echo "Blue/Green resources prepared."
                    '''
                }
            }
        }


        // =========================================================
        // 6. DETERMINE ACTIVE / TARGET COLOR
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
                                set +e

                                kubectl get service user-service-bg \
                                    -n ${NAMESPACE} \
                                    -o jsonpath='{.spec.selector.version}' \
                                    2>/dev/null || true
                            """,
                            returnStdout: true
                        ).trim()

                        def activeColor
                        def targetColor

                        if (!currentColor) {

                            echo "No active color detected."
                            echo "Using BLUE as the initial production color."

                            activeColor = 'blue'
                            targetColor = 'green'

                        } else if (currentColor == 'blue') {

                            activeColor = 'blue'
                            targetColor = 'green'

                        } else if (currentColor == 'green') {

                            activeColor = 'green'
                            targetColor = 'blue'

                        } else {

                            error "Invalid service selector color detected: ${currentColor}"
                        }

                        writeFile(
                            file: '.bg-state',
                            text: "${activeColor}\n${targetColor}\n"
                        )

                        echo "======================================"
                        echo "Blue/Green Deployment Decision"
                        echo "======================================"
                        echo "Current color : ${activeColor}"
                        echo "Target color  : ${targetColor}"
                        echo "Image tag     : ${env.IMAGE_TAG}"
                        echo "======================================"
                    }
                }
            }
        }


        // =========================================================
        // 7. DEPLOY NEW VERSION TO TARGET COLOR
        // =========================================================

        stage('Deploy New Version') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    script {

                        def bgState = readFile('.bg-state').trim().split('\n')

                        if (bgState.size() < 2) {
                            error "Blue/Green state file is missing or invalid."
                        }

                        def currentColor = bgState[0].trim()
                        def targetColor  = bgState[1].trim()

                        if (!(currentColor in ['blue', 'green']) ||
                            !(targetColor in ['blue', 'green']) ||
                            currentColor == targetColor) {
                            error "Invalid Blue/Green state: current=${currentColor}, target=${targetColor}"
                        }

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

                                echo "Updating ${service}-${targetColor}"

                                kubectl set image \
                                    deployment/${service}-${targetColor} \
                                    ${service}=${ECR_REGISTRY}/ecommerce-${service}:${IMAGE_TAG} \
                                    -n ${NAMESPACE}
                            """
                        }
                    }
                }
            }
        }


        // =========================================================
        // 8. VERIFY TARGET ROLLOUT
        // =========================================================

        stage('Verify New Version') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    script {

                        def bgState = readFile('.bg-state').trim().split('\n')

                        if (bgState.size() < 2) {
                            error "Blue/Green state file is missing or invalid."
                        }

                        def currentColor = bgState[0].trim()
                        def targetColor  = bgState[1].trim()

                        if (!(currentColor in ['blue', 'green']) ||
                            !(targetColor in ['blue', 'green']) ||
                            currentColor == targetColor) {
                            error "Invalid Blue/Green state: current=${currentColor}, target=${targetColor}"
                        }

                        def services = [
                            'user-service',
                            'product-service',
                            'cart-service',
                            'order-service',
                            'payment-service',
                            'inventory-service'
                        ]

                        try {

                            services.each { service ->

                                sh """
                                    set -e

                                    echo "Waiting for ${service}-${targetColor}"

                                    kubectl rollout status \
                                        deployment/${service}-${targetColor} \
                                        -n ${NAMESPACE} \
                                        --timeout=300s
                                """
                            }

                            echo "======================================"
                            echo "TARGET DEPLOYMENTS ARE HEALTHY"
                            echo "Target color: ${targetColor}"
                            echo "======================================"

                        }
                        catch (Exception e) {

                            echo "======================================"
                            echo "TARGET DEPLOYMENT FAILED"
                            echo "Keeping production on ${currentColor}"
                            echo "======================================"

                            currentBuild.result = 'FAILURE'

                            throw e
                        }
                    }
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
                    script {

                        def bgState = readFile('.bg-state').trim().split('\n')

                        if (bgState.size() < 2) {
                            error "Blue/Green state file is missing or invalid."
                        }

                        def currentColor = bgState[0].trim()
                        def targetColor  = bgState[1].trim()

                        if (!(currentColor in ['blue', 'green']) ||
                            !(targetColor in ['blue', 'green']) ||
                            currentColor == targetColor) {
                            error "Invalid Blue/Green state: current=${currentColor}, target=${targetColor}"
                        }

                        def services = [
                            'user-service',
                            'product-service',
                            'cart-service',
                            'order-service',
                            'payment-service',
                            'inventory-service'
                        ]

                        try {

                            services.each { service ->

                                sh """
                                    set -e

                                    echo "Switching ${service}-bg to ${targetColor}"

                                    kubectl patch service ${service}-bg \
                                        -n ${NAMESPACE} \
                                        --type=merge \
                                        -p='{"spec":{"selector":{"app":"${service}","version":"${targetColor}"}}}'
                                """
                            }

                            echo "Traffic switched to ${targetColor}."

                        }
                        catch (Exception e) {

                            echo "Traffic switch failed."
                            echo "Rolling back to ${currentColor}."

                            services.each { service ->

                                sh """
                                    kubectl patch service ${service}-bg \
                                        -n ${NAMESPACE} \
                                        --type=merge \
                                        -p='{"spec":{"selector":{"app":"${service}","version":"${currentColor}"}}}' \
                                        || true
                                """
                            }

                            throw e
                        }
                    }
                }
            }
        }


        // =========================================================
        // 10. APPLY / UPDATE HPA TARGET
        // =========================================================

        stage('Update HPA Target') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    script {

                        def bgState = readFile('.bg-state').trim().split('\n')

                        if (bgState.size() < 2) {
                            error "Blue/Green state file is missing or invalid."
                        }

                        def currentColor = bgState[0].trim()
                        def targetColor  = bgState[1].trim()

                        if (!(currentColor in ['blue', 'green']) ||
                            !(targetColor in ['blue', 'green']) ||
                            currentColor == targetColor) {
                            error "Invalid Blue/Green state: current=${currentColor}, target=${targetColor}"
                        }

                        def services = [
                            'user-service',
                            'product-service',
                            'cart-service',
                            'order-service',
                            'payment-service',
                            'inventory-service'
                        ]

                        try {

                            services.each { service ->

                                sh """
                                    set -e

                                    echo "HPA target: ${service}-${targetColor}"

                                    kubectl patch hpa ${service}-hpa \
                                        -n ${NAMESPACE} \
                                        --type=merge \
                                        -p='{"spec":{"scaleTargetRef":{"apiVersion":"apps/v1","kind":"Deployment","name":"${service}-${targetColor}"}}}'
                                """
                            }

                            echo "All HPAs now target ${targetColor}."

                        }
                        catch (Exception e) {

                            echo "HPA update failed."
                            echo "Rolling traffic back to ${currentColor}."

                            services.each { service ->

                                sh """
                                    kubectl patch service ${service}-bg \
                                        -n ${NAMESPACE} \
                                        --type=merge \
                                        -p='{"spec":{"selector":{"app":"${service}","version":"${currentColor}"}}}' \
                                        || true

                                    kubectl patch hpa ${service}-hpa \
                                        -n ${NAMESPACE} \
                                        --type=merge \
                                        -p='{"spec":{"scaleTargetRef":{"apiVersion":"apps/v1","kind":"Deployment","name":"${service}-${currentColor}"}}}' \
                                        || true
                                """
                            }

                            throw e
                        }
                    }
                }
            }
        }


        // =========================================================
        // 11. VERIFY TRAFFIC AND HPA
        // =========================================================

        stage('Verify Traffic and HPA') {
            steps {
                withCredentials([
                    [$class: 'AmazonWebServicesCredentialsBinding',
                     credentialsId: 'aws-terraform-user']
                ]) {
                    script {

                        def bgState = readFile('.bg-state').trim().split('\n')

                        if (bgState.size() < 2) {
                            error "Blue/Green state file is missing or invalid."
                        }

                        def currentColor = bgState[0].trim()
                        def targetColor  = bgState[1].trim()

                        if (!(currentColor in ['blue', 'green']) ||
                            !(targetColor in ['blue', 'green']) ||
                            currentColor == targetColor) {
                            error "Invalid Blue/Green state: current=${currentColor}, target=${targetColor}"
                        }

                        def services = [
                            'user-service',
                            'product-service',
                            'cart-service',
                            'order-service',
                            'payment-service',
                            'inventory-service'
                        ]

                        try {

                            services.each { service ->

                                sh """
                                    set -e

                                    echo "======================================"
                                    echo "Verifying ${service}"
                                    echo "======================================"

                                    ACTIVE_COLOR=\\\$(kubectl get service ${service}-bg \
                                        -n ${NAMESPACE} \
                                        -o jsonpath='{.spec.selector.version}')

                                    echo "Service selector: \\\$ACTIVE_COLOR"
                                    echo "Expected color:   ${targetColor}"

                                    if [ "\\\$ACTIVE_COLOR" != "${targetColor}" ]; then
                                        echo "ERROR: ${service}-bg is pointing to \\\$ACTIVE_COLOR"
                                        echo "Expected ${targetColor}"
                                        exit 1
                                    fi

                                    HPA_TARGET=\\\$(kubectl get hpa ${service}-hpa \
                                        -n ${NAMESPACE} \
                                        -o jsonpath='{.spec.scaleTargetRef.name}')

                                    EXPECTED_HPA_TARGET="${service}-${targetColor}"

                                    echo "HPA target:       \\\$HPA_TARGET"
                                    echo "Expected target:  \\\$EXPECTED_HPA_TARGET"

                                    if [ "\\\$HPA_TARGET" != "\\\$EXPECTED_HPA_TARGET" ]; then
                                        echo "ERROR: ${service}-hpa is targeting \\\$HPA_TARGET"
                                        echo "Expected \\\\$EXPECTED_HPA_TARGET"
                                        exit 1
                                    fi

                                    kubectl get deployment \
                                        ${service}-${targetColor} \
                                        -n ${NAMESPACE}

                                    READY_REPLICAS=\\\$(kubectl get deployment \
                                        ${service}-${targetColor} \
                                        -n ${NAMESPACE} \
                                        -o jsonpath='{.status.readyReplicas}')

                                    DESIRED_REPLICAS=\\\$(kubectl get deployment \
                                        ${service}-${targetColor} \
                                        -n ${NAMESPACE} \
                                        -o jsonpath='{.spec.replicas}')

                                    echo "Ready replicas:   \\\$READY_REPLICAS"
                                    echo "Desired replicas: \\\$DESIRED_REPLICAS"

                                    if [ -z "\\\$READY_REPLICAS" ]; then
                                        echo "ERROR: ${service}-${targetColor} has no ready replicas"
                                        exit 1
                                    fi

                                    if [ "\\\$READY_REPLICAS" -lt "\\\$DESIRED_REPLICAS" ]; then
                                        echo "ERROR: ${service}-${targetColor} does not have all desired replicas ready"
                                        exit 1
                                    fi

                                    echo "✓ ${service} verification passed."
                                    echo
                                """
                            }

                            echo "======================================"
                            echo "ALL BLUE/GREEN VERIFICATIONS PASSED"
                            echo "======================================"
                            echo "Production color: ${targetColor}"
                            echo "All Services point to ${targetColor}"
                            echo "All HPAs target ${targetColor} deployments"
                            echo "All ${targetColor} deployments are ready"
                            echo "======================================"

                        }
                        catch (Exception e) {

                            echo "======================================"
                            echo "POST-DEPLOYMENT VERIFICATION FAILED"
                            echo "ROLLING BACK TO ${currentColor}"
                            echo "======================================"

                            services.each { service ->

                                sh """
                                    kubectl patch service ${service}-bg \
                                        -n ${NAMESPACE} \
                                        --type=merge \
                                        -p='{"spec":{"selector":{"app":"${service}","version":"${currentColor}"}}}' \
                                        || true

                                    kubectl patch hpa ${service}-hpa \
                                        -n ${NAMESPACE} \
                                        --type=merge \
                                        -p='{"spec":{"scaleTargetRef":{"apiVersion":"apps/v1","kind":"Deployment","name":"${service}-${currentColor}"}}}' \
                                        || true
                                """
                            }

                            echo "Rollback completed."

                            throw e
                        }
                    }
                }
            }
        }


        // =========================================================
        // 12. MONITORING
        // =========================================================

        stage('Apply Monitoring') {
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

                        kubectl get pods -n monitoring
                    '''
                }
            }
        }


        // =========================================================
        // 13. SERVICE MONITORS
        // =========================================================

        stage('Apply ServiceMonitors') {
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
        // 14. FINAL HEALTH CHECKS
        // =========================================================

        stage('Final Health Checks') {
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

                        echo "===== Actual Production Color ====="

                        ACTIVE_COLOR=$(kubectl get service user-service-bg \
                            -n $NAMESPACE \
                            -o jsonpath='{.spec.selector.version}')

                        echo "Actual production color: $ACTIVE_COLOR"
                        echo

                        echo "===== Nodes ====="
                        kubectl get nodes

                        echo "===== Deployments ====="
                        kubectl get deployments \
                            -n $NAMESPACE

                        echo "===== Pods ====="
                        kubectl get pods \
                            -n $NAMESPACE \
                            -o wide

                        echo "===== Services ====="
                        kubectl get services \
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

                        echo "===== Actual Blue/Green Status ====="

                        for service in \
                            user-service \
                            product-service \
                            cart-service \
                            order-service \
                            payment-service \
                            inventory-service
                        do
                            echo "---- $service ----"

                            echo -n "Service selector: "

                            kubectl get service ${service}-bg \
                                -n $NAMESPACE \
                                -o jsonpath='{.spec.selector.version}'

                            echo

                            echo -n "HPA target: "

                            kubectl get hpa ${service}-hpa \
                                -n $NAMESPACE \
                                -o jsonpath='{.spec.scaleTargetRef.name}'

                            echo

                            echo -n "Ready replicas: "

                            kubectl get deployment ${service}-${ACTIVE_COLOR} \
                                -n $NAMESPACE \
                                -o jsonpath='{.status.readyReplicas}'

                            echo
                            echo
                        done

                        echo "======================================"
                        echo "Deployment health checks completed."
                        echo "Actual production color: $ACTIVE_COLOR"
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
            script {
                def productionColor = sh(
                    script: """
                        kubectl get service user-service-bg \
                            -n ${NAMESPACE} \
                            -o jsonpath='{.spec.selector.version}'
                    """,
                    returnStdout: true
                ).trim()

                echo '======================================'
                echo 'Project 3 Jenkins Pipeline SUCCESS'
                echo "Production color: ${productionColor}"
                echo '======================================'
            }
        }

        failure {
            echo '======================================'
            echo 'Project 3 Jenkins Pipeline FAILED'
            echo 'Check the failed stage in Console Output.'
            echo '======================================'
        }
    }
}
