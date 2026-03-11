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


class CurrentDensityItem(BaseModel):
    """A single current density value with its supporting evidence."""

    value: Optional[str] = Field(
        None,
        description="Current density value with units, e.g. '50 mA g⁻¹'."
    )
    evidence: Optional[str] = Field(
        None,
        description="Sentence from the article mentioning this current density."
    )

    model_config = {"extra": "forbid"}


class ElectrochemicalMethodology(BaseModel):
    """
    Top-level model for extracting electrochemical measurement methodology
    from scientific articles on hard carbon anodes in sodium-ion batteries.
    """

    cell_type: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="The type of electrochemical cell used, e.g. 'coin cell', 'Swagelok cell', "
                    "'pouch cell', 'cylindrical cell'. Include the format code if mentioned, e.g. 'CR2032'."
    )
    cell_configuration: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="The electrode configuration of the cell, e.g. 'half-cell', 'full cell', 'symmetric cell'."
    )
    cell_assembly_details: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Description of cell assembly conditions including counter electrode, separator, and atmosphere. "
                    "Example: 'CR2032 coin cells assembled in an argon-filled glovebox using sodium metal counter "
                    "electrode and glass fiber separator.'"
    )
    active_material: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="The active material used in the working electrode. Usually the hard carbon sample name "
                    "reported in the article."
    )
    electrode_composition: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Composition of the electrode slurry including active material, conductive additive, and "
                    "binder fractions. Example: '80 wt% hard carbon, 10 wt% Super P, 10 wt% PVDF'."
    )
    binder: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Binder material used in the electrode slurry, e.g. 'PVDF', 'CMC', 'SBR', 'PAA'. "
                    "Include full name if given."
    )
    current_collector: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Material used as the current collector for the working electrode, e.g. 'copper foil', "
                    "'Cu foil', 'carbon-coated aluminium foil'."
    )
    mass_loading: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Areal mass loading of active material on the electrode, typically in units such as "
                    "'mg cm⁻²'. If a range is given, include it as a string."
    )
    electrode_preparation: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Description of electrode slurry preparation, coating, and drying conditions. "
                    "Example: 'Slurry cast on Cu foil using NMP and dried at 80 °C under vacuum overnight.'"
    )
    electrolyte: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Full electrolyte composition including salt, concentration, solvent mixture, and additives. "
                    "Example: '1 M NaPF6 in EC:DEC (1:1) with 5 vol% FEC'."
    )
    separator: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Separator material used in the cell, e.g. 'glass fiber', 'Celgard 2400', "
                    "'polypropylene membrane'."
    )
    voltage_window: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Voltage range used for galvanostatic charge-discharge cycling, including reference "
                    "electrode if specified. Example: '0.01–2.5 V vs Na/Na+'."
    )
    current_densities: list[CurrentDensityItem] = Field(
        default_factory=list,
        description="List of current densities used during electrochemical testing, e.g. rate capability tests."
    )
    cycling_instrument: EvidencedStr = Field(
        default_factory=EvidencedStr,
        description="Battery cycler or instrument used for galvanostatic testing, e.g. 'LAND CT2001A', "
                    "'Neware BTS4000', 'Arbin'."
    )
    notes: Optional[str] = Field(
        None,
        description="Any additional details about electrochemical methodology not captured in the structured "
                    "fields above."
    )

    model_config = {"extra": "forbid"}