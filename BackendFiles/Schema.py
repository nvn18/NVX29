from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== PROJECT SCHEMAS ====================

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    project_type: str = Field(..., description="Project template type")
    description: Optional[str] = None
    repository_url: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    config: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# ==================== DEPLOYMENT SCHEMAS ====================

class DeploymentBase(BaseModel):
    project_id: int
    version: str
    environment: str = Field(..., description="dev, staging, or prod")
    commit_sha: Optional[str] = None
    deployed_by: Optional[str] = None

class DeploymentCreate(DeploymentBase):
    pass

class Deployment(DeploymentBase):
    id: int
    status: str
    deployed_at: datetime
    duration_seconds: Optional[int] = None
    logs: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

# ==================== SBOM SCHEMAS ====================

class SBOMBase(BaseModel):
    project_id: int
    version: str
    sbom_data: Dict[str, Any]
    vulnerabilities_count: int = 0
    security_score: float = 100.0

class SBOMCreate(SBOMBase):
    pass

class SBOM(SBOMBase):
    id: int
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    generated_at: datetime
    scan_tool: str
    
    class Config:
        from_attributes = True

# ==================== METRIC SCHEMAS ====================

class MetricBase(BaseModel):
    project_id: int
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    requests_per_minute: int = 0
    error_rate: float = 0.0
    avg_response_time: Optional[float] = None

class MetricCreate(MetricBase):
    pass

class Metric(MetricBase):
    id: int
    recorded_at: datetime
    
    class Config:
        from_attributes = True

# ==================== ML MODEL SCHEMAS ====================

class MLModelBase(BaseModel):
    project_id: int
    name: str
    version: str
    framework: Optional[str] = None
    model_type: Optional[str] = None
    experiment_id: Optional[str] = None
    run_id: Optional[str] = None
    artifact_uri: Optional[str] = None

class MLModelCreate(MLModelBase):
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class MLModel(MLModelBase):
    id: int
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    drift_detected: str
    drift_score: Optional[float] = None
    registered_at: datetime
    last_prediction_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# ==================== PIPELINE SCHEMAS ====================

class PipelineBase(BaseModel):
    project_id: int
    name: str
    pipeline_type: str = Field(..., description="ci, cd, security, or ml")
    config: Dict[str, Any]

class PipelineCreate(PipelineBase):
    pass

class Pipeline(PipelineBase):
    id: int
    status: str
    last_run_at: Optional[datetime] = None
    last_run_duration: Optional[int] = None
    success_rate: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== TEMPLATE SCHEMAS ====================

class TemplateGenerateRequest(BaseModel):
    project_name: str = Field(..., min_length=1)
    template_id: str = Field(..., description="Template identifier")
    features: List[str] = Field(
        default=[],
        description="Optional features to include"
    )
    repository_url: Optional[str] = None

class TemplateGenerateResponse(BaseModel):
    status: str
    project_name: str
    template: str
    repository_url: Optional[str] = None
    files_generated: List[str] = []
    message: str

# ==================== DASHBOARD SCHEMAS ====================

class DashboardStats(BaseModel):
    total_projects: int
    active_deployments: int
    avg_security_score: float
    healthy_projects: int
    total_vulnerabilities: int

class ProjectMetrics(BaseModel):
    project_id: int
    project_name: str
    total_deployments: int
    status: str
    security_score: Optional[float] = None
    last_deployment: Optional[datetime] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    requests_per_minute: int = 0
