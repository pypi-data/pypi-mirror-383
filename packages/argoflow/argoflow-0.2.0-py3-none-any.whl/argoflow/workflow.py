from typing import List, Dict, Any, Optional
import requests
import json

from .enums import ArtifactGCStrategy, PodGCStrategy
from .task import WorkflowTask


class Workflow:
    def __init__(self,
                 name: str,
                 workflow_server_url: str,
                 namespace: str = "default",
                 labels: Optional[Dict[str, str]] = None,
                 pod_labels: Optional[Dict[str, str]] = None,
                 entrypoint: str = "main-entrypoint",
                 artifact_gc_strategy: ArtifactGCStrategy = ArtifactGCStrategy.ON_WORKFLOW_COMPLETION,
                 pod_gc_strategy: PodGCStrategy = PodGCStrategy.ON_POD_COMPLETION,
                 ttl_seconds_after_completion: int = 300,
                 server_dry_run: bool = False,
                 default_image: Optional[str] = None,
                 default_timeout: Optional[str] = None,
                 default_env_from: Optional[List[Dict[str, Any]]] = None):

        # Name must end with - for Argo to append unique suffixes
        if not name.endswith('-'):
            name += '-'
            
        self.name = name
        self.workflow_server_url = workflow_server_url
        self.namespace = namespace
        self.labels = labels or {}
        self.pod_labels = pod_labels or {}
        self.entrypoint = entrypoint
        self.artifact_gc_strategy = artifact_gc_strategy
        self.pod_gc_strategy = pod_gc_strategy
        self.ttl_seconds_after_completion = ttl_seconds_after_completion
        self.server_dry_run = server_dry_run
        self.default_image = default_image
        self.default_timeout = default_timeout
        self.default_env_from = default_env_from or []
        self.tasks: List[WorkflowTask] = []


    # Add a single task to workflow
    def add_task(self, task: WorkflowTask):
        # Apply default values if not set in the task
        if self.default_image and not hasattr(task, '_image_set'):
            task.image = self.default_image
        if self.default_timeout and not hasattr(task, '_timeout_set'):
            task.timeout = self.default_timeout
        if self.default_env_from and not task.env_from:
            task.env_from = self.default_env_from.copy()
        
        self.tasks.append(task)


    # Get a task by name
    def get_task(self, name: str) -> Optional[WorkflowTask]:
        for task in self.tasks:
            if task.name == name:
                return task
        return None


    # Add multiple tasks to workflow
    def add_tasks(self, *tasks: WorkflowTask):
        for task in tasks:
            self.add_task(task)


    # Get all tasks in the workflow
    def get_tasks(self) -> List[WorkflowTask]:
        return self.tasks
    

    # Build DAG tasks
    def _build_dag_tasks(self) -> List[Dict[str, Any]]:
        dag_tasks = []
        
        for task in self.tasks:
            dag_task: Dict[str, Any] = {
                "name": task.name,
                "template": task.template
            }
            
            # Add dependencies
            if task.depends_on:
                dag_task["depends"] = ".Succeeded && ".join(task.depends_on) + ".Succeeded"
            
            # Add input artifacts from previous tasks
            if task.inputs:
                arguments = {"artifacts": []}
                for input_artifact in task.inputs:
                    if input_artifact.from_task:
                        artifact_arg = {
                            "name": input_artifact.name,
                            "from": f"{{{{tasks.{input_artifact.from_task}.outputs.artifacts.{input_artifact.from_artifact}}}}}"
                        }
                        arguments["artifacts"].append(artifact_arg)
                
                if arguments["artifacts"]:
                    dag_task["arguments"] = arguments
            
            dag_tasks.append(dag_task)
        
        return dag_tasks
    

    # Convert workflow to dictionary representation
    def _to_dict(self) -> Dict[str, Any]:
        templates = []
        
        # Add individual task templates
        for task in self.tasks:
            templates.append(task.to_dict())
        
        # Add entrypoint template
        entrypoint_template = {
            "name": self.entrypoint,
            "dag": {
                "tasks": self._build_dag_tasks()
            }
        }
        templates.append(entrypoint_template)
        
        # Build workflow spec
        spec = {
            "entrypoint": self.entrypoint,
            "templates": templates,
            "podMetadata": {
                "labels": self.pod_labels
            },
            "artifactGC": {
                "strategy": self.artifact_gc_strategy.value
            },
            "ttlStrategy": {
                "secondsAfterCompletion": self.ttl_seconds_after_completion
            },
            "podGC": {
                "strategy": self.pod_gc_strategy.value
            }
        }
        
        # Build complete workflow
        workflow = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {
                "generateName": self.name,
                "namespace": self.namespace,
                "labels": self.labels
            },
            "spec": spec
        }
        
        return {
            "namespace": self.namespace,
            "serverDryRun": self.server_dry_run,
            "workflow": workflow
        }
    

    # Build and return the workflow as a dictionary
    def build(self) -> Dict[str, Any]:
        return self._to_dict()
    

    # Save workflow to a JSON file
    def save_to_file(self, filename: str, indent: int = 2):
        """Save workflow to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self._to_dict(), f, indent=indent)
        print(f"Workflow saved to {filename}")


    # Submit the workflow to the Argo server
    def run_workflow(self, serverUrl, executorToken, sslVerify=False) -> Dict[str, Any]:
        workflow_dict = self.build()

        response = requests.post(
            f"https://{serverUrl}/api/v1/workflows/{self.namespace}",
            json=workflow_dict,
            headers={"Authorization": f"Bearer {executorToken}"},
            verify=sslVerify
        )

        if response.status_code == 200 or response.status_code == 201:
            print("Workflow submitted successfully.")
            return response.json()
        else:
            print("Failed to submit workflow.")
            print("Response:", response.text)
            return {"error": response.text}
