# ETO Manufacturing Dashboard

A real-time dashboard for monitoring key performance indicators (KPIs) in an Engineer-to-Order (ETO) manufacturing environment specialized for food packaging robots.

## Features

- **Project Tracking**: Monitor project status, progress, schedule variance, and cost performance
- **Resource Management**: Track resource utilization, availability, and allocation across departments
- **Inventory Monitoring**: Visualize component inventory levels, lead times, and inventory value
- **Performance KPIs**: Analyze trends in key metrics including on-time delivery, first pass yield, and quality metrics

## Dashboard Screenshots

### Projects Overview
![Projects Overview](screenshots/projects.png)

### Resource Utilization
![Resource Utilization](screenshots/resources.png)

### Inventory Status
![Inventory Status](screenshots/inventory.png)

### Key Performance Indicators
![Key Performance Indicators](screenshots/kpis.png)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Required Python packages: dash, pandas, plotly, numpy, flask, dash-bootstrap-components

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/eto-manufacturing-dashboard.git
cd eto-manufacturing-dashboard
```

2. Install required packages:
```bash
pip install dash pandas plotly numpy flask dash-bootstrap-components
```

3. Run the dashboard:
```bash
python eto_dashboard.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Customization

The dashboard can be customized for your specific ETO manufacturing needs:

- Connect to your actual data sources by replacing the sample data generation functions
- Add additional metrics or visualizations specific to your food packaging robot operations
- Customize the color scheme and layout to match your company branding

## License

MIT License