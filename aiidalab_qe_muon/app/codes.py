import traitlets
import ipywidgets as ipw
from aiidalab_qe.common.widgets import QEAppComputationalResourcesWidget

class TimeSettings(ipw.VBox):
    """Widget for setting the time settings, for now only used in pp.x here
       but it may be inserted in the QE app. 
    """

    prompt = ipw.HTML(
        """<div style="line-height:120%; padding-top:0px">
        <p style="padding-bottom:10px">
        Specify the max seconds for the pp.x calculations in the muons post processing.
        </p></div>"""
    )

    def __init__(self, **kwargs):
        extra = {
            "style": {"description_width": "150px"},
            "layout": {"min_width": "180px"},
        }
        self.time = ipw.BoundedIntText(
            value=3600, step=60, min=1, max=3600*72, description="Max seconds", width="20%"
        )
        super().__init__(
            children=[
                ipw.HBox(
                    children=[self.prompt, self.time],
                    layout=ipw.Layout(justify_content="space-between"),
                ),
            ]
        )

    def reset(self):
        """Reset the parallelization settings."""
        self.time.value = 3600

class PpComputationalResourcesWidget(QEAppComputationalResourcesWidget):
    """
    Computational resource widget for pp.x
    """
    max_wallclock_seconds = traitlets.Int(default_value=3600)
    
    def __init__(self, **kwargs):
        # we initialize also the max_wallclock_time widget
        # max is 72 hours.
        self.wallclock_widget = TimeSettings()
        super().__init__(**kwargs)
        self.children += (self.wallclock_widget,)
        
    
    def get_max_wallclock(self):
        """Return the max_wallclock_seconds settings."""
        return self.wallclock_widget.time.value

    def set_max_wallclock(self, max_wallclock_seconds):
        """Set the parallelization settings."""
        self.wallclock_widget.time.value = max_wallclock_seconds

    def get_parameters(self):
        """Return the parameters."""
        parameters = super().get_parameters()
        parameters.update({"max_wallclock_seconds": self.get_max_wallclock()})
        return parameters

    def set_parameters(self, parameters):
        """Set the parameters."""
        super().set_parameters(parameters)
        if "max_wallclock" in parameters:
            self.set_max_wallclock(parameters["set_max_wallclock"])