from aiidalab_widgets_base import ComputationalResourcesWidget


class PpCode(ComputationalResourcesWidget):
    """class for the pp.x code of QE"""
    def __init__(self,**kwargs):
        description="pp.x:"
        default_calc_job_plugin="quantumespresso.pp"
        super().__init__(
            description=description,
            default_calc_job_plugin=default_calc_job_plugin,
            **kwargs,
            )
