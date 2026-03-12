from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class EvidencedStr(BaseModel):
    """An extracted string value paired with the supporting text snippet from the source article."""

    value: Optional[str] = Field(None, description="The extracted value.")
    evidence: Optional[str] = Field(
        None,
        description="Exact text snippet from the article that supports the extracted value."
    )

    model_config = {"extra": "forbid"}


class ElectrochemicalMethodology(BaseModel):
    """
    Top-level model for extracting electrochemical measurement methodology
    from scientific articles on hard carbon anodes in sodium-ion batteries.
    """

    counter_electrode: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Counter electrode material used in the cell, e.g. 'sodium metal', 'NVP (Na3V2(PO4)3)'."
    )
    additive: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Conductive additive used in the electrode slurry, e.g. 'Super P', 'carbon black', "
                    "'acetylene black', 'Ketjen black'."
    )
    binder: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Binder material used in the electrode slurry, e.g. 'PVDF', 'CMC', 'SBR', 'PAA'. "
                    "Include full name if given."
    )
    current_collector: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Material used as the current collector for the working electrode, e.g. 'Al foil', "
                    "'Cu foil', 'carbon-coated aluminium foil'."
    )
    active_mass_loading: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Areal mass loading of the electrode slurry on the current collector, typically in "
                    "mg cm⁻². Report as a range if given, e.g. '1.0–1.5 mg cm⁻²'."
    )
    electrode_composition: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Weight ratio of active material, conductive additive, and binder, e.g. '80:10:10', '90:5:5'."
    )
    slurry_solvent: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Solvent used for preparing the electrode slurry, e.g. 'NMP (N-methyl-2-pyrrolidone)', "
                    "'deionised water', 'DI water'."
    )
    electrolyte_salt: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Chemical formula or name of the electrolyte salt, e.g. 'NaClO4', 'NaPF6', 'NaTFSI'."
    )
    electrolyte_concentration: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Concentration of the electrolyte salt, e.g. '1 M', '0.8 mol L⁻¹'."
    )
    electrolyte_solvents: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Comma-separated list of solvents used in the electrolyte, e.g. "
                    "'ethylene carbonate (EC), propylene carbonate (PC)' or 'EC, DEC'."
    )
    electrolyte_solvent_ratio: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Volume or weight ratio of the electrolyte solvents, e.g. '1:1 v/v', '1:1:1 vol%'."
    )
    cell_type: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Type of electrochemical cell including format code if mentioned, e.g. 'coin cell CR2032', "
                    "'Swagelok cell', 'pouch cell'."
    )
    separator: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Separator material used in the cell, e.g. 'glass fiber', 'Celgard 2400', "
                    "'polypropylene membrane'."
    )
    cycling_instrument: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Battery cycler or instrument used for electrochemical testing, e.g. 'LAND CT2001A', "
                    "'Neware BTS4000', 'Arbin BT-2000'."
    )
    voltage_window: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Voltage range used for galvanostatic cycling, including reference if given, "
                    "e.g. '0.01–2.0 V vs Na/Na+'."
    )

    model_config = {"extra": "forbid"}
