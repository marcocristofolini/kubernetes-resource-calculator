import os
import sys
import time
from kubernetes import client, config
from typing import Tuple

BUFFER_PERCENTAGE = (
    10  # Buffer para garantir uma margem segura em caso de picos de utilização
)


def calculate_average_usage(pod: client.V1Pod) -> Tuple[float, float]:
    start_time = time.time() - (
        60 * 60 * 24
    )  # Calcula a utilização das últimas 24 horas
    end_time = time.time()
    cpu_usage, memory_usage = 0, 0
    cpu_count, memory_count = 0, 0

    config.load_kube_config()
    api = client.CoreV1Api()
    container_name = pod.spec.containers[0].name

    metrics_api = client.CustomObjectsApi()
    response = metrics_api.list_namespaced_custom_object(
        group="metrics.k8s.io",
        version="v1beta1",
        namespace=pod.metadata.namespace,
        plural="pods",
        label_selector=f"app={container_name}",
    )

    for item in response["items"]:
        pod_name = item["metadata"]["name"]
        pod_start_time = item["metadata"]["creationTimestamp"]

        if (
            time.mktime(time.strptime(pod_start_time, "%Y-%m-%dT%H:%M:%SZ"))
            < start_time
        ):
            continue

        containers = item["containers"]
        for container in containers:
            if container["name"] == container_name:
                cpu_usage += int(container["usage"]["cpu"].replace("n", ""))
                memory_usage += int(container["usage"]["memory"].replace("Ki", ""))
                cpu_count += 1
                memory_count += 1

    return (
        (cpu_usage / cpu_count) if cpu_count > 0 else 0,
        (memory_usage / memory_count) if memory_count > 0 else 0,
    )


def calculate_requests_limits(pod: client.V1Pod) -> Tuple[str, str]:
    average_cpu_usage, average_memory_usage = calculate_average_usage(pod)
    cpu_request = str(int(average_cpu_usage * (1 + BUFFER_PERCENTAGE / 100))) + "n"
    memory_request = (
        str(int(average_memory_usage * (1 + BUFFER_PERCENTAGE / 100))) + "Ki"
    )

    return cpu_request, memory_request


def update_pod_resources(pod: client.V1Pod):
    config.load_kube_config()
    api = client.CoreV1Api()
    container_name = pod.spec.containers[0].name

    cpu_request, memory_request = calculate_requests_limits(pod)
    resource_requirements = client.V1ResourceRequirements(
        requests={"cpu": cpu_request, "memory": memory_request},
        limits={"cpu": cpu_request, "memory": memory_request},
    )

    for container in pod.spec.containers:
        if container.name == container_name:
            container.resources = resource_requirements

    api.patch_namespaced_pod(pod.metadata.name, pod.metadata.namespace, pod)


if __name__ == "__main__":
    namespace = sys.argv[1] if len(sys.argv) > 1 else "default"
    config.load_kube_config()
    api = client.CoreV1Api()
    pods = api.list_namespaced_pod(namespace)

    for pod in pods.items:
        update_pod_resources(pod)
