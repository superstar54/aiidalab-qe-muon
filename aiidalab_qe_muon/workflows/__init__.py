from aiidalab_qe_muon.workflows.settings import Setting
from aiidalab_qe_muon.workflows.workchain import workchain_and_builder
#from aiidalab_qe_vibroscopy.workflows.result import Result
from aiidalab_qe.common.panel import OutlinePanel


class Outline(OutlinePanel):
    title = "Muon spectroscopy"

property ={
"outline": Outline,
"setting": Setting,
"workchain": workchain_and_builder,
#"result": Result,
}