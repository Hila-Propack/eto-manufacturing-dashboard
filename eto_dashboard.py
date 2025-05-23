"""
ETO Manufacturing Dashboard for Food Packaging Robot Operations

A real-time dashboard for monitoring key performance indicators (KPIs) in an 
Engineer-to-Order (ETO) manufacturing environment specialized for food packaging robots.
"""
import os
import json
import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from models import Session, Project, Resource, InventoryItem, KpiRecord, create_tables, initialize_sample_data

# Create database tables and initialize with sample data if needed
create_tables()
initialize_sample_data()

# Function to get data from the database
def get_data_from_db():
    session = Session()
    
    # Get projects
    projects_db = session.query(Project).all()
    projects = []
    for project in projects_db:
        projects.append({
            "id": project.id,
            "name": project.name,
            "type": project.type,
            "customer": project.customer,
            "start_date": project.start_date.strftime("%Y-%m-%d") if project.start_date else "",
            "due_date": project.due_date.strftime("%Y-%m-%d") if project.due_date else "",
            "status": project.status,
            "progress": project.progress,
            "estimated_hours": project.estimated_hours,
            "actual_hours": project.actual_hours,
            "cost_variance": project.cost_variance,
            "schedule_variance": project.schedule_variance,
            "materials_cost": project.materials_cost,
            "labor_cost": project.labor_cost,
            "original_budget": project.original_budget,
            "current_budget": project.current_budget
        })
    
    # Get resources
    resources_db = session.query(Resource).all()
    resources = []
    for resource in resources_db:
        resources.append({
            "id": resource.id,
            "name": resource.name,
            "type": resource.type,
            "department": resource.department,
            "utilization": resource.utilization,
            "available_hours": resource.available_hours,
            "scheduled_hours": resource.scheduled_hours,
            "project_count": resource.project_count
        })
    
    # Get inventory
    inventory_db = session.query(InventoryItem).all()
    inventory = []
    for item in inventory_db:
        inventory.append({
            "component": item.component,
            "on_hand": item.on_hand,
            "allocated": item.allocated,
            "on_order": item.on_order,
            "lead_time_days": item.lead_time_days,
            "reorder_point": item.reorder_point,
            "avg_monthly_usage": item.avg_monthly_usage,
            "cost_per_unit": item.cost_per_unit
        })
    
    # Get KPIs
    kpis_db = session.query(KpiRecord).order_by(KpiRecord.date).all()
    kpis = []
    for kpi in kpis_db:
        kpis.append({
            "date": kpi.date.strftime("%Y-%m"),
            "on_time_delivery": kpi.on_time_delivery,
            "first_pass_yield": kpi.first_pass_yield,
            "labor_efficiency": kpi.labor_efficiency,
            "cycle_time_variance": kpi.cycle_time_variance,
            "material_waste_percent": kpi.material_waste_percent,
            "engineering_change_orders": kpi.engineering_change_orders,
            "customer_satisfaction": kpi.customer_satisfaction,
            "safety_incidents": kpi.safety_incidents
        })
    
    session.close()
    
    return {
        "projects": projects,
        "resources": resources,
        "inventory": inventory,
        "kpis": kpis
    }

# Initialize data from database
data = get_data_from_db()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Convert to DataFrames for easier manipulation
projects_df = pd.DataFrame(data["projects"])
resources_df = pd.DataFrame(data["resources"])
inventory_df = pd.DataFrame(data["inventory"])
kpis_df = pd.DataFrame(data["kpis"])

# Define colors
colors = {
    "primary": "#0466C8",
    "secondary": "#979DAC",
    "success": "#38B000",
    "warning": "#F48C06",
    "danger": "#D62828",
    "light": "#F5F3F4",
    "dark": "#1B263B",
    "background": "#F8F9FA",
    "text": "#212529"
}

# Dashboard layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1("ETO Manufacturing Dashboard", 
                            className="text-center my-4",
                            style={"color": colors["dark"]}),
                    width=12
                )
            ]
        ),
        
        # KPI Summary Cards
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("On-Time Delivery", className="card-title"),
                                    html.H2(f"{kpis_df['on_time_delivery'].iloc[-1]}%", 
                                           className="text-center display-4"),
                                    html.P(f"Target: 95%", className="card-text text-muted")
                                ]
                            )
                        ],
                        className="mb-4 text-center"
                    ),
                    width=3
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("First Pass Yield", className="card-title"),
                                    html.H2(f"{kpis_df['first_pass_yield'].iloc[-1]}%", 
                                           className="text-center display-4"),
                                    html.P(f"Target: 98%", className="card-text text-muted")
                                ]
                            )
                        ],
                        className="mb-4 text-center"
                    ),
                    width=3
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("Projects In Progress", className="card-title"),
                                    html.H2(f"{len(projects_df[projects_df['progress'] < 100])}", 
                                           className="text-center display-4"),
                                    html.P(f"Completed: {len(projects_df[projects_df['progress'] == 100])}", 
                                          className="card-text text-muted")
                                ]
                            )
                        ],
                        className="mb-4 text-center"
                    ),
                    width=3
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("Resource Utilization", className="card-title"),
                                    html.H2(f"{resources_df['utilization'].mean():.1f}%", 
                                           className="text-center display-4"),
                                    html.P(f"Target: 85%", className="card-text text-muted")
                                ]
                            )
                        ],
                        className="mb-4 text-center"
                    ),
                    width=3
                )
            ],
            className="mb-4"
        ),
        
        # Tabs for different views
        dbc.Tabs(
            [
                # Project Overview Tab
                dbc.Tab(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Project Status", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.bar(
                                                projects_df.groupby("status").size().reset_index(name="count"),
                                                x="status",
                                                y="count",
                                                color="status",
                                                title="Projects by Status",
                                                labels={"count": "Number of Projects", "status": "Status"},
                                                color_discrete_sequence=px.colors.qualitative.G10
                                            )
                                        )
                                    ],
                                    width=6
                                ),
                                dbc.Col(
                                    [
                                        html.H3("Project Types", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.pie(
                                                projects_df.groupby("type").size().reset_index(name="count"),
                                                names="type",
                                                values="count",
                                                title="Projects by Type",
                                                color_discrete_sequence=px.colors.qualitative.Plotly
                                            )
                                        )
                                    ],
                                    width=6
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Project Schedule Performance", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.scatter(
                                                projects_df,
                                                x="cost_variance",
                                                y="schedule_variance",
                                                size="original_budget",
                                                color="type",
                                                hover_name="name",
                                                title="Cost vs Schedule Variance",
                                                labels={
                                                    "cost_variance": "Cost Variance (%)",
                                                    "schedule_variance": "Schedule Variance (%)"
                                                }
                                            )
                                        )
                                    ],
                                    width=12
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Projects List", className="mt-4"),
                                        html.Div(
                                            dbc.Table.from_dataframe(
                                                projects_df[['name', 'customer', 'status', 'progress', 'due_date']],
                                                striped=True,
                                                bordered=True,
                                                hover=True,
                                                responsive=True
                                            ),
                                            style={"maxHeight": "400px", "overflow": "auto"}
                                        )
                                    ],
                                    width=12
                                )
                            ]
                        )
                    ],
                    label="Projects"
                ),
                
                # Resources Tab
                dbc.Tab(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Resource Utilization by Department", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.box(
                                                resources_df,
                                                x="department",
                                                y="utilization",
                                                color="department",
                                                title="Resource Utilization Distribution",
                                                labels={
                                                    "department": "Department",
                                                    "utilization": "Utilization (%)"
                                                }
                                            )
                                        )
                                    ],
                                    width=6
                                ),
                                dbc.Col(
                                    [
                                        html.H3("Resource Type Distribution", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.pie(
                                                resources_df.groupby("type").size().reset_index(name="count"),
                                                names="type",
                                                values="count",
                                                title="Resources by Type",
                                                color_discrete_sequence=px.colors.qualitative.Plotly
                                            )
                                        )
                                    ],
                                    width=6
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Resource Scheduled vs. Available Hours", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.scatter(
                                                resources_df,
                                                x="available_hours",
                                                y="scheduled_hours",
                                                color="department",
                                                size="utilization",
                                                hover_name="name",
                                                title="Available vs. Scheduled Hours",
                                                labels={
                                                    "available_hours": "Available Hours",
                                                    "scheduled_hours": "Scheduled Hours"
                                                }
                                            )
                                        )
                                    ],
                                    width=12
                                )
                            ]
                        )
                    ],
                    label="Resources"
                ),
                
                # Inventory Tab
                dbc.Tab(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Component Inventory Levels", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.bar(
                                                inventory_df,
                                                x="component",
                                                y=["on_hand", "allocated", "on_order"],
                                                title="Inventory Status by Component",
                                                labels={
                                                    "value": "Quantity",
                                                    "component": "Component",
                                                    "variable": "Status"
                                                },
                                                barmode="group"
                                            )
                                        )
                                    ],
                                    width=12
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Inventory Lead Times", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.bar(
                                                inventory_df.sort_values("lead_time_days", ascending=False),
                                                x="component",
                                                y="lead_time_days",
                                                color="lead_time_days",
                                                title="Component Lead Times",
                                                labels={
                                                    "lead_time_days": "Lead Time (Days)",
                                                    "component": "Component"
                                                },
                                                color_continuous_scale=px.colors.sequential.Viridis
                                            )
                                        )
                                    ],
                                    width=6
                                ),
                                dbc.Col(
                                    [
                                        html.H3("Inventory Value", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.pie(
                                                inventory_df,
                                                names="component",
                                                values=inventory_df["on_hand"] * inventory_df["cost_per_unit"],
                                                title="Inventory Value by Component",
                                                hole=0.4,
                                                labels={"value": "Value ($)"}
                                            )
                                        )
                                    ],
                                    width=6
                                )
                            ]
                        )
                    ],
                    label="Inventory"
                ),
                
                # Performance KPIs Tab
                dbc.Tab(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Key Performance Indicators Over Time", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.line(
                                                kpis_df,
                                                x="date",
                                                y=["on_time_delivery", "first_pass_yield", "labor_efficiency", "customer_satisfaction"],
                                                title="KPIs Trend",
                                                labels={
                                                    "value": "Percentage",
                                                    "date": "Month",
                                                    "variable": "KPI"
                                                }
                                            )
                                        )
                                    ],
                                    width=12
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Quality Metrics", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.line(
                                                kpis_df,
                                                x="date",
                                                y=["material_waste_percent", "cycle_time_variance", "engineering_change_orders"],
                                                title="Quality Metrics Trend",
                                                labels={
                                                    "value": "Value",
                                                    "date": "Month",
                                                    "variable": "Metric"
                                                }
                                            )
                                        )
                                    ],
                                    width=6
                                ),
                                dbc.Col(
                                    [
                                        html.H3("Safety Performance", className="mt-4"),
                                        dcc.Graph(
                                            figure=px.bar(
                                                kpis_df,
                                                x="date",
                                                y="safety_incidents",
                                                title="Safety Incidents by Month",
                                                labels={
                                                    "safety_incidents": "Number of Incidents",
                                                    "date": "Month"
                                                },
                                                color_discrete_sequence=["#D62828"]
                                            )
                                        )
                                    ],
                                    width=6
                                )
                            ]
                        )
                    ],
                    label="KPIs"
                )
            ]
        ),
        
        # Footer
        dbc.Row(
            [
                dbc.Col(
                    html.P(
                        "ETO Manufacturing Dashboard for Food Packaging Robot Operations", 
                        className="text-center text-muted my-4"
                    ),
                    width=12
                )
            ]
        )
    ],
    fluid=True,
    style={"backgroundColor": colors["background"]}
)

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)