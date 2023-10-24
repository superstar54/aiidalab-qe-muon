from aiida.orm import load_code, Dict, Bool
from aiida.plugins import WorkflowFactory, DataFactory
from aiida_quantumespresso.common.types import ElectronicType, SpinType

from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData

ImplantMuonWorkChain = WorkflowFactory("muon_app.implant_muon")

"""try:
    DataFactory("atomistic.structure")
    old_structuredata=False
except:
    old_structuredata=True"""
    
old_structuredata=True

def get_builder(codes, structure, parameters):
    from copy import deepcopy
    
    protocol = parameters["workchain"].pop("protocol", "fast")
    pw_code = codes.get("pw")
    pp_code = codes.get("pp", None)
    
    magmom = parameters["muonic"].pop("magmoms",None)
    supercell = parameters["muonic"].pop("supercell_selector", None)
    sc_matrix = [[[supercell[0],0,0],[0,supercell[1],0],[0,0,supercell[2]]]]

    compute_supercell = parameters["muonic"].pop("compute_supercell", False)
    mu_spacing = parameters["muonic"].pop("mu_spacing",1.0)
    kpoints_distance = parameters["muonic"].pop("kpoints_distance",0.301)
    charge_supercell = parameters["muonic"].pop("charge_supercell",True)
    
    hubbard = parameters["muonic"].pop("hubbard",False)
    
    if hubbard and old_structuredata:
        structure = HubbardStructureData.from_structure(structure)
    
    if compute_supercell:
        sc_matrix = None
            
    trigger = "findmuon"
    

    scf_overrides = deepcopy(parameters["advanced"])
    overrides = {
        "relax":{
            "base": scf_overrides,
        },
        "pwscf": scf_overrides,
    }
    
    builder = ImplantMuonWorkChain.get_builder_from_protocol(
        pw_code=pw_code,
        pp_code=pp_code,
        pseudo_family="SSSP/1.2/PBEsol/efficiency", #hard coded...
        structure=structure,
        protocol=protocol,
        overrides=overrides,
        trigger=trigger,
        relax_unitcell=False, #but not true in the construction; in the end you relax in the first step of the QeAppWorkchain.
        magmom=magmom,
        sc_matrix=sc_matrix,
        mu_spacing=mu_spacing,
        kpoints_distance=kpoints_distance,
        charge_supercell=charge_supercell,
        hubbard=hubbard,
        electronic_type=ElectronicType(parameters["workchain"]["electronic_type"]),
        spin_type=SpinType(parameters["workchain"]["spin_type"]),
        initial_magnetic_moments=parameters["advanced"]["initial_magnetic_moments"],
        )
    
    pp_metadata = {
    "options": {
        "max_wallclock_seconds": 60*60, 
        "resources": {
            "num_machines": 1,
            "num_mpiprocs_per_machine":1,
            },
        },
    }
    if pp_code:
        builder.findmuon.pp_metadata = pp_metadata

    
    return builder


workchain_and_builder = {
    "workchain": ImplantMuonWorkChain,
    "exclude": ("clean_workdir",),
    "get_builder": get_builder,
}