from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    project_type = Column(String, nullable=False)  # fastapi, react, nodejs, etc.
    description = Column(Text, nullable=True)
    repository_url = Column(String, nullable=True)
    status = Column(String, default="active")  # active, archived, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configuration
    config = Column(JSON, nullable=True)  # Store project-specific configs
    
    # Relationships
    deployments = relationship("Deployment", back_populates="project", cascade="all, delete-orphan")
    sboms = relationship("SBOM", back_populates="project", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="project", cascade="all, delete-orphan")

class Deployment(Base):
    __tablename__ = "deployments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    version = Column(String, nullable=False)
    environment = Column(String, nullable=False)  # dev, staging, prod
    status = Column(String, default="pending")  # pending, success, failed, rollback
    commit_sha = Column(String, nullable=True)
    deployed_by = Column(String, nullable=True)
    deployed_at = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer, nullable=True)
    
    # Deployment metadata
    logs = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationship
    project = relationship("Project", back_populates="deployments")

class SBOM(Base):
    __tablename__ = "sboms"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    version = Column(String, nullable=False)
    sbom_data = Column(JSON, nullable=False)  # Full SBOM JSON
    
    # Security metrics
    vulnerabilities_count = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    security_score = Column(Float, default=100.0)  # 0-100 score
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    scan_tool = Column(String, default="trivy")  # trivy, syft, etc.
    
    # Relationship
    project = relationship("Project", back_populates="sboms")

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Resource metrics
    cpu_usage = Column(Float, nullable=True)  # percentage
    memory_usage = Column(Float, nullable=True)  # percentage
    disk_usage = Column(Float, nullable=True)  # percentage
    
    # Traffic metrics
    requests_per_minute = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)  # percentage
    avg_response_time = Column(Float, nullable=True)  # milliseconds
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="metrics")

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Model info
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    framework = Column(String, nullable=True)  # tensorflow, pytorch, sklearn
    model_type = Column(String, nullable=True)  # classification, regression, etc.
    
    # Tracking
    experiment_id = Column(String, nullable=True)
    run_id = Column(String, nullable=True)
    artifact_uri = Column(String, nullable=True)
    
    # Performance metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Drift detection
    drift_detected = Column(String, default="false")  # true, false
    drift_score = Column(Float, nullable=True)
    
    # Metadata
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_prediction_at = Column(DateTime, nullable=True)
    
    # Model metadata
    metadata = Column(JSON, nullable=True)

class Pipeline(Base):
    __tablename__ = "pipelines"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Pipeline info
    name = Column(String, nullable=False)
    pipeline_type = Column(String, nullable=False)  # ci, cd, security, ml
    status = Column(String, default="idle")  # idle, running, success, failed
    
    # Configuration
    config = Column(JSON, nullable=False)
    
    # Execution
    last_run_at = Column(DateTime, nullable=True)
    last_run_duration = Column(Integer, nullable=True)  # seconds
    success_rate = Column(Float, default=100.0)  # percentage
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
