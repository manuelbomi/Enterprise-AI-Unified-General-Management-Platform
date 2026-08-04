"""Service scaffolding generator for enterprise AI platform experiments."""

import os
from pathlib import Path
from jinja2 import Template


class AIServiceGenerator:
    """Creates reusable service scaffolding for an enterprise AI platform."""

    def __init__(self, service_name: str, service_type: str):
        self.service_name = service_name
        self.service_type = service_type
        self.template_dir = Path(__file__).parent / "templates"

    def generate(self):
        """Generate the complete artifact set for a service."""
        self._create_terraform()
        self._create_dockerfile()
        self._create_cicd()
        self._create_monitoring()
        self._create_evaluation()
        self._create_api()

    def _create_terraform(self):
        """Generate Terraform module scaffolding for the service."""
        terraform_tpl = Template('''
        provider "aws" {
          region = var.region
        }

        resource "aws_ecr_repository" "ai_repo" {
          name = "{{ service_name }}-repo"
        }

        resource "aws_cloudwatch_log_group" "ai_logs" {
          name = "/ecs/{{ service_name }}"
        }
        ''')

        tf_main = terraform_tpl.render(service_name=self.service_name)
        os.makedirs(f"./terraform/{self.service_name}", exist_ok=True)
        with open(f"./terraform/{self.service_name}/main.tf", "w") as f:
            f.write(tf_main)

    def _create_dockerfile(self):
        """Generate a Dockerfile for the new service."""
        docker_tpl = Template('''
        FROM python:3.11-slim
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY src/ .
        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        ''')
        os.makedirs(f"./services/{self.service_name}", exist_ok=True)
        with open(f"./services/{self.service_name}/Dockerfile", "w") as f:
            f.write(docker_tpl.render(service_name=self.service_name))

    def _create_cicd(self):
        """Create a GitHub Actions workflow for the service."""
        cicd_tpl = Template('''
        name: Deploy {{ service_name }}

        on:
          push:
            branches: [main]
            paths:
              - 'services/{{ service_name }}/**'

        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v3
              - name: Install dependencies
                run: |
                  pip install -r services/{{ service_name }}/requirements-dev.txt
        ''')
        os.makedirs(f"./.github/workflows", exist_ok=True)
        with open(f"./.github/workflows/{self.service_name}.yml", "w") as f:
            f.write(cicd_tpl.render(service_name=self.service_name))

    def _create_monitoring(self):
        """Create simple monitoring metadata for the service."""
        monitor = {
            "service": self.service_name,
            "metrics": ["latency", "errors", "throughput", "cost"],
        }
        os.makedirs(f"./monitoring", exist_ok=True)
        with open(f"./monitoring/{self.service_name}-dashboard.json", "w") as f:
            f.write(str(monitor))

    def _create_evaluation(self):
        """Create evaluation test scaffolding for the service."""
        os.makedirs(f"./services/{self.service_name}/tests/evaluation", exist_ok=True)
        with open(f"./services/{self.service_name}/tests/evaluation/test_evaluation.py", "w") as f:
            f.write("# Evaluation tests for service\n")

    def _create_api(self):
        """Generate the API entrypoint scaffold for the service."""
        os.makedirs(f"./services/{self.service_name}/src", exist_ok=True)
        with open(f"./services/{self.service_name}/src/main.py", "w") as f:
            f.write("# FastAPI application entrypoint\n")
