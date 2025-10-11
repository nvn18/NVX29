from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database
from datetime import datetime

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="NVX29 API",
    description="Internal Developer Platform API",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "name": "NVX29 API",
        "version": "0.1.0",
        "status": "running"
    }

# ==================== PROJECTS ====================

@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project with auto-generated configurations"""
    
    # Check if project already exists
    existing = db.query(models.Project).filter(
        models.Project.name == project.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Project already exists")
    
    # Create project
    db_project = models.Project(
        name=project.name,
        project_type=project.project_type,
        description=project.description,
        repository_url=project.repository_url,
        status="initializing",
        created_at=datetime.utcnow()
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # TODO: Trigger template generation in background
    # generate_project_template(db_project)
    
    return db_project

@app.get("/api/projects", response_model=List[schemas.Project])
def list_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all projects"""
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

@app.get("/api/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project by ID"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/api/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project_update: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):
    """Update project"""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project_update.dict(exclude_unset=True).items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete project"""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

# ==================== DEPLOYMENTS ====================

@app.post("/api/deployments", response_model=schemas.Deployment)
def create_deployment(deployment: schemas.DeploymentCreate, db: Session = Depends(get_db)):
    """Create a new deployment"""
    
    # Verify project exists
    project = db.query(models.Project).filter(
        models.Project.id == deployment.project_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_deployment = models.Deployment(
        project_id=deployment.project_id,
        version=deployment.version,
        environment=deployment.environment,
        status="pending",
        deployed_at=datetime.utcnow()
    )
    
    db.add(db_deployment)
    db.commit()
    db.refresh(db_deployment)
    
    return db_deployment

@app.get("/api/deployments", response_model=List[schemas.Deployment])
def list_deployments(
    project_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List deployments, optionally filtered by project"""
    query = db.query(models.Deployment)
    
    if project_id:
        query = query.filter(models.Deployment.project_id == project_id)
    
    deployments = query.offset(skip).limit(limit).all()
    return deployments

# ==================== SBOM ====================

@app.post("/api/sbom", response_model=schemas.SBOM)
def create_sbom(sbom: schemas.SBOMCreate, db: Session = Depends(get_db)):
    """Create SBOM record"""
    
    db_sbom = models.SBOM(
        project_id=sbom.project_id,
        version=sbom.version,
        sbom_data=sbom.sbom_data,
        vulnerabilities_count=sbom.vulnerabilities_count,
        security_score=sbom.security_score,
        generated_at=datetime.utcnow()
    )
    
    db.add(db_sbom)
    db.commit()
    db.refresh(db_sbom)
    
    return db_sbom

@app.get("/api/sbom/{project_id}", response_model=List[schemas.SBOM])
def get_project_sboms(project_id: int, db: Session = Depends(get_db)):
    """Get all SBOMs for a project"""
    sboms = db.query(models.SBOM).filter(
        models.SBOM.project_id == project_id
    ).order_by(models.SBOM.generated_at.desc()).all()
    
    return sboms

# ==================== METRICS ====================

@app.get("/api/metrics/{project_id}")
def get_project_metrics(project_id: int, db: Session = Depends(get_db)):
    """Get project metrics"""
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    deployments = db.query(models.Deployment).filter(
        models.Deployment.project_id == project_id
    ).count()
    
    latest_sbom = db.query(models.SBOM).filter(
        models.SBOM.project_id == project_id
    ).order_by(models.SBOM.generated_at.desc()).first()
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "total_deployments": deployments,
        "status": project.status,
        "security_score": latest_sbom.security_score if latest_sbom else None,
        "last_deployment": None  # TODO: Implement
    }

# ==================== TEMPLATES ====================

@app.get("/api/templates")
def list_templates():
    """List available project templates"""
    return {
        "templates": [
            {
                "id": "fastapi",
                "name": "FastAPI",
                "description": "Python FastAPI REST API with async support",
                "features": ["REST API", "Async", "Auto-docs", "Type hints"]
            },
            {
                "id": "react",
                "name": "React + Vite",
                "description": "Modern React app with Vite and TailwindCSS",
                "features": ["React 18", "Vite", "TailwindCSS", "Hot reload"]
            },
            {
                "id": "nodejs",
                "name": "Node.js Express",
                "description": "Express.js REST API with TypeScript",
                "features": ["Express", "TypeScript", "JWT Auth", "Middleware"]
            },
            {
                "id": "fastapi-ml",
                "name": "FastAPI + MLflow",
                "description": "ML inference API with model tracking",
                "features": ["FastAPI", "MLflow", "Model serving", "Tracking"]
            }
        ]
    }

@app.post("/api/templates/generate")
def generate_template(request: schemas.TemplateGenerateRequest):
    """Generate project from template"""
    # TODO: Implement template generation logic
    return {
        "status": "generating",
        "project_name": request.project_name,
        "template": request.template_id,
        "message": "Project generation started"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
