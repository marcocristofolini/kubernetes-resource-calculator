# Kubernetes Resource Calculator

This repository contains a Kubernetes plugin written in Python that calculates the right requests and limits for CPU and memory based on the average usage observed in a specified period of time, with a buffer percentage to account for fluctuations in resource usage.

## Requirements

- Python 3.x
- Kubernetes Python client

## Installation

1. Clone the repository:

```bash
git clone https://github.com/marcocristofolini/kubernetes-resource-calculator.git
cd kubernetes-resource-calculator

2. Install the dependencies

pip install kubernetes
```

## Usage

```bash
python kube_resource_calculator.py [namespace]
```

Replace [`namespace`] with the desired Kubernetes namespace where your pods are running. If not provided, the script will use the "default" namespace.

## Configuration

You can configure the buffer percentage by modifying the `BUFFER_PERCENTAGE` constant in the `kube_resource_calculator.py` script. By default, it's set to 10% to provide a 10% extra margin for CPU and memory resources.

GitHub Action
This repository also includes a GitHub Action that sets up a Kubernetes cluster using Kind (Kubernetes in Docker) and runs the script on a specified branch when changes are pushed.

The action is defined in the `.github/workflows/main.yml` file. It sets up a Python environment, installs the necessary dependencies, creates a Kubernetes cluster using Kind, and runs the provided Python script using the Kubernetes cluster created for the workflow.

To enable the GitHub Action, commit and push the` .github/workflows/main.yml` file to your repository.

Triggering the GitHub Action
By default, the action is triggered on a push event to the main branch. You can replace main with the desired branch in the` .github/workflows/main.yml` file to trigger the action on a different branch.

## Output Sample

The script will update the requests and limits for each pod in the specified namespace based on the average usage observed in the past 24 hours, plus the configured buffer percentage. After running the script, you may see updates similar to the following example:

```bash
$ Updated pod 'example-pod-1' in namespace 'default' with CPU request and limit set to '1100m' and memory request and limit set to '512Mi'.

$ Updated pod 'example-pod-2' in namespace 'default' with CPU request and limit set to '600m' and memory request and limit set to '384Mi'.
```

**Attention**
> Please note that the output will vary depending on the actual resource usage in your Kubernetes cluster and the configured buffer percentage.


This output sample demonstrates how the script updates the requests and limits for each pod in the specified namespace. The exact values for CPU and memory requests and limits will depend on the actual resource usage in your Kubernetes cluster and the configured buffer percentage.

## License

MIT License
