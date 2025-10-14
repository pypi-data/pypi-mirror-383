from typing import Optional, Dict, Any


class ResourceRequests:
    def __init__(self, cpu: Optional[str] = None, memory: Optional[str] = None, 
                 storage: Optional[str] = None):
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
    
    def to_dict(self) -> Dict[str, str]:
        requests = {}
        if self.cpu:
            requests["cpu"] = self.cpu
        if self.memory:
            requests["memory"] = self.memory
        if self.storage:
            requests["storage"] = self.storage
        return requests


class ResourceLimits:
    def __init__(self, cpu: Optional[str] = None, memory: Optional[str] = None,
                 storage: Optional[str] = None):
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
    
    def to_dict(self) -> Dict[str, str]:
        limits = {}
        if self.cpu:
            limits["cpu"] = self.cpu
        if self.memory:
            limits["memory"] = self.memory
        if self.storage:
            limits["storage"] = self.storage
        return limits


class Resources:
    def __init__(self, requests: Optional[ResourceRequests] = None,
                 limits: Optional[ResourceLimits] = None):
        self.requests = requests
        self.limits = limits
    
    def to_dict(self) -> Dict[str, Any]:
        resources = {}
        if self.requests:
            req_dict = self.requests.to_dict()
            if req_dict:
                resources["requests"] = req_dict
        if self.limits:
            limit_dict = self.limits.to_dict()
            if limit_dict:
                resources["limits"] = limit_dict
        return resources
