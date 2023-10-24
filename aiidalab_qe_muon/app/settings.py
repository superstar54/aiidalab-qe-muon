# -*- coding: utf-8 -*-
"""Panel for FindMuonWorkchain plugin.

Authors:

    * Miki Bonacci <miki.bonacci@psi.ch>
    Inspired by Xing Wang <xing.wang@psi.ch>
"""
import ipywidgets as ipw
from aiida import orm
import traitlets as tl
from aiida_quantumespresso.calculations.functions.create_kpoints_from_distance import (
    create_kpoints_from_distance,
)
from aiidalab_qe.common.panel import Panel

from aiida_muon.workflows.find_muon import gensup, niche_add_impurities


class Setting(Panel):
    title = "Muon Settings"
    
    input_structure = tl.Instance(orm.StructureData, allow_none=True)
    
    def __init__(self, **kwargs):
        self.settings_title = ipw.HTML(
            """<div style="padding-top: 0px; padding-bottom: 0px">
            <h4>Muon spectroscopy settings</h4></div>"""
        )
        self.settings_help = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 5px">
            Please select desired inputs to compute muon stopping sites and related properties. The muon is considered infinite-dilute
            in the crystal, so we should select a supercell in which the muon will stay and do not interact with its replica. 
            If you do not provide a size for the supercell size and select "Compute supercell", a pre-processing step will be submitted 
            to estimate it.
            </div>"""
        )
        
        #start charge 
        self.charge_help = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 5px; padding-bottom: 5px">
            <h5><b>Muon charge state</b></h5>
            If you select a neutral muon, this will resemble the "muonium" state. Usually, 
            this may happen in insulators. It represents the analogous of the hydrogen 
            atom (it can be thought as one of its lightest isotopes), which is the
            most simplest defects in a semiconductor. The electronic structure of H 
            and muonium are then expected to be identical;
            at variance, vibrational properties are not, as the involved masses are different.
            </div>"""
        )
        
        self.charged_muon_ = ipw.ToggleButtons(
            options=[("Muon (+1)", "on"), ("Muonium (neutral)", "off")],
            value="on",
            style={"description_width": "initial"},
        )
        #end charge
        
        self.workchain_protocol = ipw.ToggleButtons(
            options=["fast", "moderate", "precise"],
            value="moderate",
        )
        
        #start Supercell
        self.supercell=[1,1,1]
        def change_supercell(_=None):
            self.supercell = [
                self._sc_x.value,
                self._sc_y.value,
                self._sc_z.value,
            ]
            self._display_mesh()
            
        for elem in ["x","y","z"]:
            setattr(self,"_sc_"+elem,ipw.BoundedIntText(value=1, min=1, layout={"width": "40px"},disabled=True))
        
        for elem in [self._sc_x,self._sc_y,self._sc_z]:
            elem.observe(change_supercell, names="value")
            
        self.supercell_selector = ipw.HBox(
            children=[ipw.HTML(description="Supercell size:",style={"description_width": "initial"})] + [
                self._sc_x,self._sc_y,self._sc_z,], 
        )

        # SCell widget
        self.supercell_label = ipw.Label(
            "Compute supercell: ", 
            layout=ipw.Layout(justify_content="flex-start"),
            )
        self.compute_supercell_ = ipw.Checkbox(
            description="",
            indent=False,
            value=True,
        )
        #enable supercell setting
        self.compute_supercell_.observe(self._compute_supercell,"value")
            
        self.supercell_known_widget = ipw.HBox(
            [self.supercell_label, self.compute_supercell_,self.supercell_selector],
            layout=ipw.Layout(justify_content="flex-start"),
        )
        #end Supercell.
        
        #start enable Hubbard. Temporary
        self.hubbard__label = ipw.Label(
            "Enable Hubbard correction: ", 
            layout=ipw.Layout(justify_content="flex-start"),
            )
        self.hubbard_ = ipw.Checkbox(
            description="",
            indent=False,
            value=True,
        )
        self.hubbard__widget = ipw.HBox(
            [self.hubbard__label, self.hubbard_],
            layout=ipw.Layout(justify_content="flex-start"),
        )
        #end enable Hubbard.
        
        #start enable spin_polarised DFT calcs.
        self.spin_pol_label = ipw.Label(
            "Enable spin polarised DFT: ", 
            layout=ipw.Layout(justify_content="flex-start"),
            )
        self.spin_pol_ = ipw.Checkbox(
            description="",
            indent=False,
            value=True,
            layout=ipw.Layout(justify_content="flex-start"),
        )
        self.spin_pol_description = ipw.Label(
            """In case of magnetic system, it computes also the contact hyperfine field.""")
        self.spin_pol_widget = ipw.HBox(
            [self.spin_pol_label, self.spin_pol_,self.spin_pol_description],
            #layout=ipw.Layout(justify_content="flex-start"),
        )
        #end enable spin_polarised DFT calcs.
        
        #start kpoints distance: the code is the same as the advanced settings.
        self.kpoints_description = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 5px; padding-bottom: 5px">
            <h5><b>K-points mesh density</b></h5>
            The k-points mesh density for the relaxation of the muon supecells.
            The value below represents the maximum distance between the k-points in each direction of
            reciprocal space.</div>"""
        )
        
        self.kpoints_distance_ = ipw.BoundedFloatText(
            min=0.0,
            step=0.05,
            value=0.3,
            description="K-points distance (1/Å):",
            disabled=False,
            style={"description_width": "initial"},
        )
        self.kpoints_distance_.observe(self._display_mesh, "value")
        self.mesh_grid = ipw.HTML()
        #end kpoints distance.
        
        #start mu spacing. We should provide also some estimation on the # of the supercell generated.
        #in conjunction with the supercell size. 
        self.mu_spacing_description = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 5px; padding-bottom: 5px">
            <h5><b>Muons site distance</b></h5>
            Muons distance in Å for different candidate positions in the choosen supercell.</div>"""
        )
        
        self.mu_spacing_ = ipw.BoundedFloatText(
            min=0.05,
            step=0.05,
            value=1.0,
            description="mu_spacing (Å):",
            disabled=False,
            style={"description_width": "initial"},
        )
        self.mu_spacing_.observe(self._estimate_supercells, "value")
        self.number_of_supercells = ipw.HTML()
        #end mu spacing.
        
        #start TEMPORARY magnetic moments settings. this should be in the structure creation.
        #self.sites_widget = SitesWidgets(self)
        self.moments = ipw.HTML()
        #end
        
        self.children = [
            self.settings_title,
            self.settings_help,
            self.supercell_known_widget,
            self.hubbard__widget,
            self.spin_pol_widget,
            self.charge_help,
            ipw.HBox(
                children=[
                    ipw.Label(
                        "Charge state:",
                        layout=ipw.Layout(justify_content="flex-start"),
                    ),
                    self.charged_muon_,
                ]
            ),
            self.kpoints_description,
            ipw.HBox([self.kpoints_distance_, self.mesh_grid]),
            self.mu_spacing_description,
            ipw.HBox([self.mu_spacing_, self.number_of_supercells]),
            self.moments,
        ]
        super().__init__(**kwargs)
        
    @tl.observe("input_structure")
    def _update_input_structure(self, change):
        if self.input_structure is not None:
            self._display_mesh()
            self._estimate_supercells()
            self._display_moments()
            
    def _compute_supercell(self, change):
        for elem in [self._sc_x,self._sc_y,self._sc_z]:
            elem.disabled = change["new"]
            
    def _display_mesh(self, _=None):
        if self.input_structure is None:
            return
        if self.kpoints_distance_.value > 0:
            supercell_ = self.input_structure.get_pymatgen()
            supercell_ = supercell_.make_supercell(self.supercell)
            supercell = orm.StructureData(pymatgen=supercell_)
            mesh = create_kpoints_from_distance(
                supercell,
                orm.Float(self.kpoints_distance_.value),
                orm.Bool(True),
            )
            self.mesh_grid.value = "Mesh " + str(mesh.get_kpoints_mesh()[0])
        else:
            self.mesh_grid.value = "Please select a number higher than 0.0"
            
    def _estimate_supercells(self, _=None):
        """estimate the number of supercells, given sc_matrix and mu_spacing.
        this is copied from the FindMuonWorkChain, it is code duplication.
        should be not.
        """
        if self.input_structure is None:
            return
        else:
            mu_lst = niche_add_impurities(
                self.input_structure, orm.Str("H"), orm.Float(self.mu_spacing_.value), orm.Float(1.0)
            )
            
            sc_matrix = [[self.supercell[0],0,0],[0,self.supercell[1],0],[0,0,self.supercell[2]]]
            supercell_list = gensup(self.input_structure.get_pymatgen(), mu_lst, sc_matrix)  # ordinary function           
            self.number_of_supercells.value = "Number of supercells: "+str(len(supercell_list))
    
    def _display_moments(self, _=None):
        """
        Display the magnetic moments and set the magmoms inputs for the simulation.
        """
        if self.input_structure is None:
            self.moments=ipw.HTML()
            self.magmoms = None
        elif self.input_structure and "magmom" in self.input_structure.base.extras.keys():
            text = ""
            magmoms = self.input_structure.base.extras.get("magmom")
            text += "<h5><b>Magnetic moments in the unit cell</b></h5>"
            for site,magmom in zip(self.input_structure.sites,magmoms):
                text+=f'<p>{site.kind_name}, in {str(site.position)}: {str(magmom)}</p>'
            self.moments.value = text
            self.magmoms = magmoms
        else:
            self.magmoms = None
        
        if not self.magmoms:
            self.spin_pol_.value = False
            self.spin_pol_.disabled = True
        pass
         
    def SitesWidget(self,):
        """
        Widget to display sites and relative magnetic moment. 
        For now, magmoms can be modified by the user.
        """
        if self.input_structure is None:
            return
        else:
            for site in self.input_structure.sites:
                pass
            
        return
        
        
        
    def get_panel_value(self):
        """Return a dictionary with the input parameters for the plugin."""

        return {
                "supercell_selector": self.supercell,
                "charged_muon": self.charged_muon_.value,
                "kpoints_distance": self.kpoints_distance_.value,
                "mu_spacing": self.mu_spacing_.value,
                "compute_supercell":self.compute_supercell_.value,
                "magmoms":self.magmoms,
                "hubbard":self.hubbard_.value,
                "spin_pol":self.spin_pol_.value,
                }

    def load_panel_value(self, input_dict):
        """Load a dictionary with the input parameters for the plugin."""
        self.charged_muon_.value = input_dict.get("charged_muon", "on")
        self.compute_supercell_.value = input_dict.get("compute_supercell",False)
        self.supercell = input_dict.get("supercell_selector", [1,1,1])
        self.kpoints_distance_.value = input_dict.get("kpoints_distance", 0.3)
        self.mu_spacing_.value = input_dict.get("mu_spacing", 1)
        self.magmoms = input_dict.get("magmoms",None)
        self.hubbard_.value = input_dict.get("hubbard",False)
        self.spin_pol_.value = input_dict.get("spin_pol",True)
        
    def reset(self):
        """Reset the panel"""
        self.charged_muon_.value = "on"
        self.compute_supercell_.value = True
        self.supercell = [1,1,1]
        self.kpoints_distance_.value = 0.3
        self.mu_spacing_.value = 1
        self.magmoms = None
        self.hubbard_.value = True
        self.spin_pol_.value = True

