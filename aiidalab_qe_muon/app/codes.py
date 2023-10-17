import ipywidgets as ipw
import traitlets as tl
from aiida import orm
from aiida.common import NotExistent
from aiida.engine import ProcessBuilderNamespace, submit
from aiidalab_widgets_base import ComputationalResourcesWidget, WizardAppWidgetStep
from IPython.display import display

from aiidalab_qe.app.parameters import DEFAULT_PARAMETERS
from aiidalab_qe.common.setup_codes import QESetupWidget
from aiidalab_qe.workflows import QeAppWorkChain

from aiidalab_qe.resource import ParallelizationSettings, ResourceSelectionWidget

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
