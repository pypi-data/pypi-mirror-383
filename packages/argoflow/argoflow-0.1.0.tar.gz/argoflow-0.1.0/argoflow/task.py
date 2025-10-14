import os
from typing import List, Dict, Any, Optional, Union

from .resources import Resources
from .artifacts import InputArtifact, OutputArtifact


class WorkflowTask:
    def __init__(self, 
                 name: str,
                 template: str,
                 image: str = "python:3.9",
                 script: Optional[str] = None,
                 script_file: Optional[str] = None,
                 timeout: str = "5m",
                 inputs: Optional[List[InputArtifact]] = None,
                 outputs: Optional[List[OutputArtifact]] = None,
                 env_vars: Optional[Dict[str, str]] = None,
                 env_from: Optional[List[Dict[str, Any]]] = None,
                 resources: Optional[Resources] = None,
                 depends_on: Optional[List['WorkflowTask']] = None):
        self.name = name
        self.template = template
        self.image = image
        self.script = script
        self.script_file = script_file
        self.timeout = timeout
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.env_vars = env_vars or {}
        self.env_from = env_from or []
        self.resources = resources
        self.depends_on = [task.name for task in depends_on] if depends_on else []

        # Load script content from file if provided
        if self.script_file and not self.script:
            self._load_script_from_file()

    
    # Load script content from a file
    def _load_script_from_file(self):
        if not self.script_file:
            raise ValueError("Script file path is not provided")
        
        if not os.path.exists(self.script_file):
            raise FileNotFoundError(f"Script file not found: {self.script_file}")
        
        with open(self.script_file, 'r') as f:
            file_content = f.read()
        
        # If it's a Python file then run it with python3
        if self.script_file.endswith('.py'):
            script_name = os.path.basename(self.script_file).replace('.py', '')
            self.script = f"""echo "Running {script_name}..."
cat << 'PYTHON_SCRIPT_EOF' > /tmp/{script_name}.py
{file_content}
PYTHON_SCRIPT_EOF
python3 /tmp/{script_name}.py"""
        else:
            self.script = file_content


    # Add an input artifact to the task.
    def add_input(self, artifact: InputArtifact):
        self.inputs.append(artifact)
    

    # Add an output artifact to the task.
    def add_output(self, artifact: OutputArtifact):
        self.outputs.append(artifact)


    # Add a task dependency.
    def add_dependency(self, task: 'WorkflowTask'):
        if task.name not in self.depends_on:
            self.depends_on.append(task.name)


    # Convert task to dictionary representation.
    def to_dict(self) -> Dict[str, Any]:
        template = {
            "name": self.name,
            "script": self._get_script_spec(),
            "timeout": self.timeout
        }
        
        # Add inputs if present
        if self.inputs:
            template["inputs"] = {
                "artifacts": [artifact.to_dict() for artifact in self.inputs]
            }
        
        # Add outputs if present
        if self.outputs:
            template["outputs"] = {
                "artifacts": [artifact.to_dict() for artifact in self.outputs]
            }
        
        return template
    

    # Get script task specification.
    def _get_script_spec(self) -> Dict[str, Any]:
        spec = {
            "image": self.image,
            "source": self.script or "echo 'No script content provided'",
            "command": ["bash"]
        }
        
        # Add environment variables
        if self.env_vars:
            if isinstance(self.env_vars, dict):
                spec["env"] = [{"name": k, "value": v} for k, v in self.env_vars.items()]
            else:  # Assume it's already in the correct format
                spec["env"] = self.env_vars
        
        # Add envFrom
        if self.env_from:
            spec["envFrom"] = self.env_from
        
        # Add resources
        if self.resources:
            resource_dict = self.resources.to_dict()
            if resource_dict:
                spec["resources"] = resource_dict
        
        return spec