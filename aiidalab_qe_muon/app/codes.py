import traitlets
import ipywidgets as ipw
from aiidalab_qe.common.widgets import QEAppComputationalResourcesWidget,PWscfWidget

class TimeSettings(ipw.VBox):
    """Widget for setting the time settings, for now only used in pp.x here
       but it may be inserted in the QE app. 
    """


    def __init__(self, calc = "pp.x", **kwargs):
        extra = {
            "style": {"description_width": "150px"},
            "layout": {"min_width": "180px"},
        }
        
        # Here I am doing a bad implementation intentionally: should be only a temporary fixing.
        if calc == "pp.x":
            self.prompt = ipw.HTML(
            """<div style="line-height:120%; padding-top:0px">
            <p style="padding-bottom:10px">
            Specify the max seconds for the pp.x calculations in the muons post processing.
            </p></div>"""
            )
        else:
            self.prompt = ipw.HTML(
            """<div style="line-height:120%; padding-top:0px">
            <p style="padding-bottom:10px">
            Specify the max seconds for the muon pw.x calculations.
            </p></div>"""
            )
        
        
        self.time = ipw.BoundedIntText(
            value=3600, step=3600, min=1800, max=3600*24*10, description="Max seconds", width="20%"
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
        self.wallclock_widget = TimeSettings(calc="pp.x")
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
            
            
class MuonPWscfWidget(PWscfWidget):
    """ComputationalResources Widget for the pw.x calculation for muons. We add the walltime. TEMPORARY SOLUTION."""

    nodes = traitlets.Int(default_value=1)

    def __init__(self, **kwargs):
        # By definition, npool must be a divisor of the total number of k-points
        # thus we can not set a default value here, or from the computer.
        self.wallclock_widget = TimeSettings(calc="pw.x")
        super().__init__(**kwargs)
        # add nodes and cpus into the children of the widget
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
        parameters.update({"parallelization": self.get_parallelization()})
        parameters.update({"max_wallclock_seconds": self.get_max_wallclock()})

        return parameters

    def set_parameters(self, parameters):
        """Set the parameters."""
        super().set_parameters(parameters)
        if "parallelization" in parameters:
            self.set_parallelization(parameters["parallelization"])
        if "max_wallclock" in parameters:
            self.set_max_wallclock(parameters["set_max_wallclock"])