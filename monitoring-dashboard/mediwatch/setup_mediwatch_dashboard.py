import os
from evidently.metrics import DatasetSummaryMetric, ColumnDriftMetric
from evidently.ui.dashboards import CounterAgg
from evidently.ui.dashboards import DashboardPanelCounter
from evidently.ui.dashboards import DashboardPanelPlot
from evidently.ui.dashboards import PanelValue
from evidently.ui.dashboards import PlotType
from evidently.ui.dashboards import ReportFilter
from evidently.ui.workspace import Workspace
from evidently.renderers.html_widgets import WidgetSize
import dagconfig as cfg
import shutil

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define a function to create a project within a workspace
def create_project(ws):
    print(f"create_project: Creating project {cfg.PROJECT_NAME}")
    project = ws.create_project(cfg.PROJECT_NAME)

    # Add a counter panel to the project's dashboard
    project.dashboard.add_panel(
        DashboardPanelCounter(
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            agg=CounterAgg.NONE,
            title="Diabetes Patient Redmission Data Dashboard",
            size=WidgetSize.FULL,
        )
    )

    # Add counter panels for various metrics to the dashboard
    # such as Model Calls, Unlabelled Inference Datapoints, Model Precision, Model Accuracy, and Drift Score
    project.dashboard.add_panel(
        DashboardPanelCounter(
            title="Model Calls",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            value=PanelValue(
                metric_id="DatasetSummaryMetric",
                field_path=DatasetSummaryMetric.fields.current.number_of_rows,
                legend="count",
            ),
            agg=CounterAgg.SUM,
            size=WidgetSize.FULL,
        )
    )

    # Add panels for Model Precision and Model Accuracy
    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Model Precision",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ClassificationQualityMetric",
                    field_path="current.precision",
                    legend="precision",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )

    project.dashboard.add_panel(
        DashboardPanelPlot(
            title="Model Accuracy",
            filter=ReportFilter(metadata_values={}, tag_values=[]),
            values=[
                PanelValue(
                    metric_id="ClassificationQualityMetric",
                    field_path="current.accuracy",
                    legend="accuracy",
                ),
            ],
            plot_type=PlotType.LINE,
            size=WidgetSize.HALF,
        )
    )

    # Save the project
    project.save()
    return project

# Define a function to set up the workspace
def setup_workspace():
    # Check if the workspace directory already exists, and if so, delete it
    if os.path.exists(cfg.WORKSACE_PATH):
        print("Workspace already exists... Deleting existing workspace")
        shutil.rmtree(cfg.WORKSACE_PATH)
    
    logger.info("Creating Workspace.... ")

    # Create a workspace and project
    ws = Workspace.create(cfg.WORKSACE_PATH)
    print("Creating Project............")
    project = create_project(ws)

if __name__ == '__main__':
    # Call the setup_workspace function to set up the workspace and project
    setup_workspace()