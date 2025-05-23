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

# Sample data generator for demonstration purposes
# This would be replaced with connections to real data sources in production
def generate_sample_data():
    # Current date for reference
    today = datetime.datetime.now()
    
    # Generate projects data
    projects = []
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
        
        projects.append({
            "id": i+1,
            "name": project_name,
            "type": np.random.choice(project_types),
            "customer": f"Customer {np.random.randint(1, 15)}",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "status": np.random.choice(project_statuses),
            "progress": progress,
            "estimated_hours": estimated_hours,
            "actual_hours": actual_hours,
            "cost_variance": cost_variance,
            "schedule_variance": schedule_variance,
            "materials_cost": np.random.randint(50000, 200000),
            "labor_cost": np.random.randint(30000, 150000),
            "original_budget": np.random.randint(100000, 500000),
            "current_budget": np.random.randint(100000, 500000),
        })
    
    # Generate resource data
    resources = []
    resource_types = ["Engineer", "Technician", "Welder", "Electrician", "QA Specialist", "Programmer"]
    for i in range(30):
        utilization = np.random.randint(50, 100)
        resources.append({
            "id": i+1,
            "name": f"{np.random.choice(resource_types)} {i+1}",
            "type": np.random.choice(resource_types),
            "department": np.random.choice(["Engineering", "Production", "QA", "Assembly"]),
            "utilization": utilization,
            "available_hours": np.random.randint(20, 40),
            "scheduled_hours": np.random.randint(30, 45),
            "project_count": np.random.randint(1, 4)
        })
    
    # Generate inventory data
    inventory = []
    component_types = [
        "Motors", "Sensors", "Controllers", "Actuators", "Conveyors", 
        "Grippers", "Electrical Panels", "Vision Systems", "Safety Components",
        "Servo Drives", "Pneumatic Valves", "HMI Units", "Gearboxes"
    ]
    
    for component in component_types:
        inventory.append({
            "component": component,
            "on_hand": np.random.randint(5, 50),
            "allocated": np.random.randint(3, 30),
            "on_order": np.random.randint(0, 20),
            "lead_time_days": np.random.randint(7, 60),
            "reorder_point": np.random.randint(5, 15),
            "avg_monthly_usage": np.random.randint(3, 25),
            "cost_per_unit": np.random.randint(100, 5000)
        })
    
    # Generate KPI data
    current_month = today.replace(day=1)
    kpis = []
    
    # Create 12 months of KPI data
    for i in range(12):
        month = current_month - datetime.timedelta(days=30*i)
        kpis.append({
            "date": month.strftime("%Y-%m"),
            "on_time_delivery": np.random.randint(60, 95),
            "first_pass_yield": np.random.randint(70, 98),
            "labor_efficiency": np.random.randint(75, 95),
            "cycle_time_variance": np.random.uniform(-15, 15),
            "material_waste_percent": np.random.uniform(2, 10),
            "engineering_change_orders": np.random.randint(2, 12),
            "customer_satisfaction": np.random.randint(70, 95),
            "safety_incidents": np.random.randint(0, 3)
        })
    
    return {
        "projects": projects,
        "resources": resources,
        "inventory": inventory,
        "kpis": sorted(kpis, key=lambda x: x["date"])
    }

# Initialize data
data = generate_sample_data()

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