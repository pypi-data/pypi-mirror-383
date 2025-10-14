from typing import Optional, Dict, Any


class Artifact:
    def __init__(self, name: str, path: str, optional: bool = False):
        self.name = name
        self.path = path
        self.optional = optional
    
    def to_dict(self) -> Dict[str, Any]:
        artifact_dict: Dict[str, Any] = {
            "name": self.name,
            "path": self.path
        }
        if self.optional:
            artifact_dict["optional"] = self.optional
        return artifact_dict


class InputArtifact(Artifact):
    def __init__(self, name: str, path: str, from_task, 
                 from_artifact: Optional[str] = None, optional: bool = False):
        super().__init__(name, path, optional)
        # Convert from_task to string if it's a task object
        if hasattr(from_task, 'name'):
            self.from_task = from_task.name
        else:
            self.from_task = from_task
        self.from_artifact = from_artifact or name
    
    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()


class OutputArtifact(Artifact):
    def __init__(self, name: str, path: str, optional: bool = False):
        super().__init__(name, path, optional)
