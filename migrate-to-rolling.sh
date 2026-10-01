#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="nodejs-devops"

SERVICES=(
  user-service
  product-service
  cart-service
  order-service
  payment-service
  inventory-service
)

echo "=============================================="
echo " Creating rolling Deployment manifests"
echo "=============================================="

mkdir -p k8s

for SERVICE in "${SERVICES[@]}"; do

    SRC="k8s/${SERVICE}-blue.yaml"
    DST="k8s/${SERVICE}-deployment.yaml"

    if [ ! -f "$SRC" ]; then
        echo "ERROR: $SRC not found"
        exit 1
    fi

    cp "$SRC" "$DST"

    echo "Converting $SRC -> $DST"

    # --------------------------------------------------
    # Deployment name
    # --------------------------------------------------

    sed -i \
        "s/name: ${SERVICE}-blue/name: ${SERVICE}/g" \
        "$DST"

    # --------------------------------------------------
    # Remove blue/green version labels
    # --------------------------------------------------

    sed -i \
        '/^[[:space:]]*version: blue[[:space:]]*$/d' \
        "$DST"

    # --------------------------------------------------
    # HPA will own replica count.
    # New Deployment starts at Kubernetes default: 1.
    # --------------------------------------------------

    sed -i \
        '/^[[:space:]]*replicas: 2[[:space:]]*$/d' \
        "$DST"

    # --------------------------------------------------
    # Replace hard-coded :1.0 with a Jenkins placeholder
    # --------------------------------------------------

    sed -i -E \
        's#:[0-9]+\.[0-9]+([[:space:]]*)$#:IMAGE_TAG_PLACEHOLDER\1#' \
        "$DST"

    # --------------------------------------------------
    # Add labels:
    #
    #   app: service
    #   track: rolling
    #   monitoring: service
    #
    # The Service will select track=rolling.
    # ServiceMonitors will select monitoring=service.
    # --------------------------------------------------

    sed -i -E \
        "s/^([[:space:]]*)app: ${SERVICE}$/\1app: ${SERVICE}\n\1track: rolling\n\1monitoring: ${SERVICE}/" \
        "$DST"

    # --------------------------------------------------
    # RollingUpdate strategy
    #
    # maxSurge=0:
    #   Never intentionally create an extra Pod.
    #
    # maxUnavailable=1:
    #   One Pod may be unavailable during rollout.
    # --------------------------------------------------

    perl -0pi -e \
        's/^spec:\n/spec:\n  strategy:\n    type: RollingUpdate\n    rollingUpdate:\n      maxSurge: 0\n      maxUnavailable: 1\n/m' \
        "$DST"

    echo "Generated: $DST"
done


echo
echo "=============================================="
echo " Creating rolling Services"
echo "=============================================="

for SERVICE in "${SERVICES[@]}"; do

    SRC="k8s/${SERVICE}-bg-service.yaml"
    DST="k8s/${SERVICE}-service.yaml"

    if [ ! -f "$SRC" ]; then
        echo "ERROR: $SRC not found"
        exit 1
    fi

    cp "$SRC" "$DST"

    # Remove blue selector.
    sed -i \
        '/^[[:space:]]*version: blue[[:space:]]*$/d' \
        "$DST"

    # Service selects only the new rolling Deployment.
    #
    # Existing:
    #   app: service
    #
    # New:
    #   app: service
    #   track: rolling
    #
    sed -i -E \
        "s/^([[:space:]]*)app: ${SERVICE}$/\1app: ${SERVICE}\n\1track: rolling/" \
        "$DST"

    echo "Generated: $DST"
done


echo
echo "=============================================="
echo " Creating rolling HPAs"
echo "=============================================="

for SERVICE in "${SERVICES[@]}"; do

cat > "k8s/${SERVICE}-hpa.yaml" <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ${SERVICE}-hpa
  namespace: ${NAMESPACE}

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ${SERVICE}

  minReplicas: 1
  maxReplicas: 2

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60

    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60

  metrics:

    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70

    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
EOF

    echo "Generated: k8s/${SERVICE}-hpa.yaml"

done


echo
echo "=============================================="
echo " Migration manifests generated successfully"
echo "=============================================="

echo
echo "Review them with:"
echo
echo "  ls -1 k8s/*-deployment.yaml"
echo "  ls -1 k8s/*-service.yaml"
echo "  ls -1 k8s/*-hpa.yaml"
echo

echo "Original blue/green files have NOT been deleted."
