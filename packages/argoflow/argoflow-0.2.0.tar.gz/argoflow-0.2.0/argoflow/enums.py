from enum import Enum


class ArtifactGCStrategy(Enum):
    ON_WORKFLOW_COMPLETION = "OnWorkflowCompletion"
    ON_WORKFLOW_SUCCESS = "OnWorkflowSuccess"
    ON_WORKFLOW_DELETION = "OnWorkflowDeletion"
    NEVER = "Never"


class PodGCStrategy(Enum):
    ON_POD_COMPLETION = "OnPodCompletion"
    ON_POD_SUCCESS = "OnPodSuccess"
    ON_WORKFLOW_COMPLETION = "OnWorkflowCompletion"
    ON_WORKFLOW_SUCCESS = "OnWorkflowSuccess"
