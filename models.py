"""
Database models for the ETO Manufacturing Dashboard
"""
import os
import datetime
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Project(Base):
    """Project model represents manufacturing projects in the ETO company"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(100), nullable=False)
    customer = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    progress = Column(Integer, default=0)
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer, default=0)
    cost_variance = Column(Float, default=0.0)
    schedule_variance = Column(Float, default=0.0)
    materials_cost = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    original_budget = Column(Float, nullable=False)
    current_budget = Column(Float)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    resources = relationship("ResourceAllocation", back_populates="project")
    inventory_items = relationship("InventoryAllocation", back_populates="project")

class Resource(Base):
    """Resource model represents personnel resources in the manufacturing company"""
    __tablename__ = 'resources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    utilization = Column(Float, default=0.0)
    available_hours = Column(Integer, default=40)
    scheduled_hours = Column(Integer, default=0)
    project_count = Column(Integer, default=0)
    hourly_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    projects = relationship("ResourceAllocation", back_populates="resource")

class ResourceAllocation(Base):
    """ResourceAllocation tracks which resources are allocated to which projects"""
    __tablename__ = 'resource_allocations'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    resource_id = Column(Integer, ForeignKey('resources.id'))
    hours_allocated = Column(Float, default=0.0)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="resources")
    resource = relationship("Resource", back_populates="projects")

class InventoryItem(Base):
    """InventoryItem represents components and materials in the manufacturing inventory"""
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True)
    component = Column(String(100), nullable=False)
    on_hand = Column(Integer, default=0)
    allocated = Column(Integer, default=0)
    on_order = Column(Integer, default=0)
    lead_time_days = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    avg_monthly_usage = Column(Float, default=0.0)
    cost_per_unit = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    projects = relationship("InventoryAllocation", back_populates="inventory_item")

class InventoryAllocation(Base):
    """InventoryAllocation tracks which inventory items are allocated to which projects"""
    __tablename__ = 'inventory_allocations'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    inventory_id = Column(Integer, ForeignKey('inventory_items.id'))
    quantity_allocated = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="inventory_items")
    inventory_item = relationship("InventoryItem", back_populates="projects")

class KpiRecord(Base):
    """KpiRecord tracks key performance indicators over time"""
    __tablename__ = 'kpi_records'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    on_time_delivery = Column(Float)
    first_pass_yield = Column(Float)
    labor_efficiency = Column(Float)
    cycle_time_variance = Column(Float)
    material_waste_percent = Column(Float)
    engineering_change_orders = Column(Integer)
    customer_satisfaction = Column(Float)
    safety_incidents = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(engine)


def initialize_sample_data():
    """Initialize the database with sample data"""
    session = Session()
    
    # Check if we already have data
    if session.query(Project).count() > 0:
        session.close()
        return
    
    # Current date for reference
    today = datetime.datetime.now()
    
    # Create sample projects
    project_names = ["FR-1000", "PK-2500", "WR-750", "CP-3000", "BP-1200"]
    project_types = ["Food Robot", "Packaging Kit", "Wrapping Robot", "Case Packer", "Bottle Packer"]
    project_statuses = ["Engineering", "Procurement", "Production", "Testing", "Delivered"]
    
    for i in range(20):
        start_date = today - datetime.timedelta(days=np.random.randint(0, 180))
        duration = np.random.randint(30, 120)
        due_date = start_date + datetime.timedelta(days=duration)
        
        progress = 0
        if today > due_date:
            progress = 100
        else:
            days_passed = (today - start_date).days
            progress = min(100, int((days_passed / duration) * 100))
            # Add some randomness to progress
            progress = min(100, max(0, progress + np.random.randint(-10, 20)))
        
        estimated_hours = np.random.randint(300, 2000)
        actual_hours = int(estimated_hours * (progress/100) * np.random.uniform(0.8, 1.3))
        
        cost_variance = np.random.uniform(-15, 15)
        schedule_variance = np.random.uniform(-20, 10)
        
        # Use more realistic naming convention for projects
        project_name = f"{np.random.choice(project_names)}-{np.random.randint(1000, 9999)}"
        
        project = Project(
            name=project_name,
            type=np.random.choice(project_types),
            customer=f"Customer {np.random.randint(1, 15)}",
            start_date=start_date,
            due_date=due_date,
            status=np.random.choice(project_statuses),
            progress=progress,
            estimated_hours=estimated_hours,
            actual_hours=actual_hours,
            cost_variance=cost_variance,
            schedule_variance=schedule_variance,
            materials_cost=np.random.randint(50000, 200000),
            labor_cost=np.random.randint(30000, 150000),
            original_budget=np.random.randint(100000, 500000),
            current_budget=np.random.randint(100000, 500000),
        )
        session.add(project)
    
    session.commit()
    
    # Create sample resources
    resource_types = ["Engineer", "Technician", "Welder", "Electrician", "QA Specialist", "Programmer"]
    for i in range(30):
        utilization = np.random.randint(50, 100)
        resource = Resource(
            name=f"{np.random.choice(resource_types)} {i+1}",
            type=np.random.choice(resource_types),
            department=np.random.choice(["Engineering", "Production", "QA", "Assembly"]),
            utilization=utilization,
            available_hours=np.random.randint(20, 40),
            scheduled_hours=np.random.randint(30, 45),
            project_count=np.random.randint(1, 4),
            hourly_rate=np.random.randint(25, 95)
        )
        session.add(resource)
    
    session.commit()
    
    # Create sample inventory
    component_types = [
        "Motors", "Sensors", "Controllers", "Actuators", "Conveyors", 
        "Grippers", "Electrical Panels", "Vision Systems", "Safety Components",
        "Servo Drives", "Pneumatic Valves", "HMI Units", "Gearboxes"
    ]
    
    for component in component_types:
        inventory = InventoryItem(
            component=component,
            on_hand=np.random.randint(5, 50),
            allocated=np.random.randint(3, 30),
            on_order=np.random.randint(0, 20),
            lead_time_days=np.random.randint(7, 60),
            reorder_point=np.random.randint(5, 15),
            avg_monthly_usage=np.random.randint(3, 25),
            cost_per_unit=np.random.randint(100, 5000)
        )
        session.add(inventory)
    
    session.commit()
    
    # Create sample KPI records
    current_month = today.replace(day=1)
    
    # Create 12 months of KPI data
    for i in range(12):
        month = current_month - datetime.timedelta(days=30*i)
        kpi = KpiRecord(
            date=month,
            on_time_delivery=np.random.randint(60, 95),
            first_pass_yield=np.random.randint(70, 98),
            labor_efficiency=np.random.randint(75, 95),
            cycle_time_variance=np.random.uniform(-15, 15),
            material_waste_percent=np.random.uniform(2, 10),
            engineering_change_orders=np.random.randint(2, 12),
            customer_satisfaction=np.random.randint(70, 95),
            safety_incidents=np.random.randint(0, 3)
        )
        session.add(kpi)
    
    session.commit()
    session.close()

import numpy as np

if __name__ == "__main__":
    create_tables()
    initialize_sample_data()
    print("Database tables created and initialized with sample data.")