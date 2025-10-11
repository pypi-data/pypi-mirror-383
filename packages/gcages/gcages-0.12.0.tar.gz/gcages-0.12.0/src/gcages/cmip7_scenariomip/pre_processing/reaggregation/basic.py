"""
Basic reaggregation

This is called 'basic' because it's the first one we thought about.
It's also, in some ways, the simplest.
It assumes that domestic aviation is reported at the model region level.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Callable

import numpy as np
import pandas as pd
from attrs import define, field
from pandas_openscm.grouping import groupby_except
from pandas_openscm.index_manipulation import (
    set_levels,
    update_index_levels_func,
)
from pandas_openscm.indexing import multi_index_lookup

from gcages.aggregation import aggregate_df_level, get_region_sector_sum
from gcages.assertions import assert_only_working_on_variable_unit_region_variations
from gcages.cmip7_scenariomip.gridding_emissions import (
    COMPLETE_GRIDDING_SPECIES,
    SpatialResolutionOption,
)
from gcages.cmip7_scenariomip.pre_processing.reaggregation.common import (
    ToCompleteResult,
)
from gcages.completeness import assert_all_groups_are_complete, get_missing_levels
from gcages.index_manipulation import (
    combine_sectors,
    create_levels_based_on_existing,
    set_new_single_value_levels,
    split_sectors,
)
from gcages.internal_consistency import InternalConsistencyError
from gcages.testing import compare_close, get_variable_unit_default
from gcages.typing import NP_ARRAY_OF_FLOAT_OR_INT
from gcages.units_helpers import convert_unit_like

if TYPE_CHECKING:
    from gcages.typing import PINT_SCALAR


@define
class GriddingSectorComponents:
    """
    Definition of the components of a gridding sector for reporting

    This is meant for internal use only.

    OR logic is applied to the exclusions
    i.e. a variable will not be required
    if the sector is in `input_sectors_optional`
    or the species is in `input_species_optional`
    (i.e. we are maximally relaxed about optional reporting,
    instead of using AND logic and being restrictive).
    """

    gridding_sector: str
    """The gridding sector"""

    spatial_resolution: SpatialResolutionOption

    input_sectors: tuple[str, ...]
    """
    The input sectors
    """

    input_sectors_optional: tuple[str, ...]
    """
    The input sectors that are optional
    """

    all_species: tuple[str, ...]
    """The input species"""

    input_species_optional: tuple[str, ...]
    """The input species that are optional"""

    reporting_only: bool
    """Is this definition only used for reporting, not aggregating?"""

    def to_complete_variables(self) -> tuple[str, ...]:
        """
        Convert to the complete set of variables for this gridding sector
        """
        return tuple(
            f"Emissions|{species}|{sector}"
            for species in self.all_species
            for sector in self.input_sectors
        )

    def to_required_variables(self) -> tuple[str, ...]:
        """
        Convert to the required set of variables for this gridding sector
        """
        return tuple(
            f"Emissions|{species}|{sector}"
            for species in self.all_species
            for sector in self.input_sectors
            if not (
                sector in self.input_sectors_optional
                or species in self.input_species_optional
            )
        )


@define
class GriddingSectorComponentsCarbonRemovalReporting:
    """
    Definition of the components of a carbon removal gridding sector for reporting

    This is for carbon removal i.e. is for CO2 only.

    This is meant for internal use only.
    """

    gridding_sector: str
    """The gridding sector"""

    spatial_resolution: SpatialResolutionOption

    input_sectors: tuple[str, ...]
    """
    The input sectors
    """

    input_sectors_optional: tuple[str, ...]
    """
    The input sectors that are optional
    """

    reporting_only: bool
    """Is this definition only used for reporting, not aggregating?"""

    def to_complete_variables(self) -> tuple[str, ...]:
        """
        Convert to the complete set of variables for this gridding sector
        """
        return tuple(f"Carbon Removal|{sector}" for sector in self.input_sectors)

    def to_required_variables(self) -> tuple[str, ...]:
        """
        Convert to the required set of variables for this gridding sector
        """
        return tuple(
            f"Carbon Removal|{sector}"
            for sector in self.input_sectors
            if sector not in self.input_sectors_optional
        )


SECTOR_DOMESTIC_AVIATION = "Energy|Demand|Transportation|Domestic Aviation"
"""
Domestic aviation sector
"""

gridding_sectors_reporting = (
    GriddingSectorComponents(
        gridding_sector="Agricultural Waste Burning",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("AFOLU|Agricultural Waste Burning",),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=("CO2",),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Agriculture",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=(
            "AFOLU|Agriculture",
            "AFOLU|Land|Harvested Wood Products",
            "AFOLU|Land|Land Use and Land-Use Change",
            "AFOLU|Land|Other",
            "AFOLU|Land|Wetlands",
        ),
        input_sectors_optional=(
            "AFOLU|Land|Harvested Wood Products",
            "AFOLU|Land|Land Use and Land-Use Change",
            "AFOLU|Land|Other",
            "AFOLU|Land|Wetlands",
        ),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=(
            "BC",
            "CO",
            "OC",
            "CO2",
            "Sulfur",
        ),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Aircraft",
        spatial_resolution=SpatialResolutionOption.WORLD,
        input_sectors=(
            "Energy|Demand|Bunkers|International Aviation",
            # Domestic aviation is included too.
            # However, it has to be reported at the regional level
            # so we can subtract it from Transport
            # (hence it doesn't appear here, see below)
        ),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=("CH4",),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Domestic aviation headache",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=(SECTOR_DOMESTIC_AVIATION,),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=("CH4",),
        reporting_only=True,
    ),
    GriddingSectorComponents(
        gridding_sector="Transportation Sector",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Energy|Demand|Transportation",),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=(),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Energy Sector",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Energy|Supply",),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=(),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Forest Burning",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("AFOLU|Land|Fires|Forest Burning",),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=("CO2",),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Grassland Burning",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("AFOLU|Land|Fires|Grassland Burning",),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=("CO2",),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Industrial Sector",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=(
            "Energy|Demand|Industry",
            "Energy|Demand|Other Sector",
            "Industrial Processes",
            "Other",
        ),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_sectors_optional=(
            "Energy|Demand|Other Sector",
            "Other",
        ),
        input_species_optional=(),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="International Shipping",
        spatial_resolution=SpatialResolutionOption.WORLD,
        input_sectors=("Energy|Demand|Bunkers|International Shipping",),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=(),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Peat Burning",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("AFOLU|Land|Fires|Peat Burning",),
        input_sectors_optional=("AFOLU|Land|Fires|Peat Burning",),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=COMPLETE_GRIDDING_SPECIES,
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Residential Commercial Other",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Energy|Demand|Residential and Commercial and AFOFI",),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=(),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Solvents Production and Application",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Product Use",),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=("BC", "CH4", "CO", "NOx", "OC", "Sulfur"),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Waste",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Waste",),
        input_sectors_optional=(),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=(),
        reporting_only=False,
    ),
    GriddingSectorComponents(
        gridding_sector="Other CDR",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Other Capture and Removal",),
        input_sectors_optional=("Other Capture and Removal",),
        all_species=COMPLETE_GRIDDING_SPECIES,
        input_species_optional=(
            "CH4",
            "N2O",
            "BC",
            "CO",
            "NH3",
            "OC",
            "NOx",
            "Sulfur",
            "VOC",
        ),
        reporting_only=False,
    ),
    GriddingSectorComponentsCarbonRemovalReporting(
        gridding_sector="BECCS",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Geological Storage|Biomass",),
        input_sectors_optional=("Geological Storage|Biomass",),
        reporting_only=False,
    ),
    GriddingSectorComponentsCarbonRemovalReporting(
        gridding_sector="Enhanced Weathering",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Enhanced Weathering",),
        input_sectors_optional=("Enhanced Weathering",),
        reporting_only=False,
    ),
    GriddingSectorComponentsCarbonRemovalReporting(
        gridding_sector="Direct Air Capture",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Geological Storage|Direct Air Capture",),
        input_sectors_optional=("Geological Storage|Direct Air Capture",),
        reporting_only=False,
    ),
    GriddingSectorComponentsCarbonRemovalReporting(
        gridding_sector="Ocean",
        spatial_resolution=SpatialResolutionOption.MODEL_REGION,
        input_sectors=("Ocean",),
        input_sectors_optional=("Ocean",),
        reporting_only=False,
    ),
)
"""
The reporting sector component definitions

Note that this only defines the reporting sectors.
The sectors used for aggregation are defined in [to_gridding_sectors][(m).]
because the logic for how we do the re-aggregation is more complex
than a straight mapping.
"""

COMPLETE_WORLD_VARIABLES: tuple[str, ...] = tuple(
    v
    for gs in gridding_sectors_reporting
    if gs.spatial_resolution == SpatialResolutionOption.WORLD
    for v in gs.to_complete_variables()
)
"""
Complete set of variables at the world level
"""

REQUIRED_WORLD_VARIABLES: tuple[str, ...] = tuple(
    v
    for gs in gridding_sectors_reporting
    if gs.spatial_resolution == SpatialResolutionOption.WORLD
    for v in gs.to_required_variables()
)
"""
Required set of variables at the world level
"""

OPTIONAL_WORLD_VARIABLES: tuple[str, ...] = tuple(
    set(COMPLETE_WORLD_VARIABLES) - set(REQUIRED_WORLD_VARIABLES)
)
"""
Optional set of variables at the world level
"""

COMPLETE_MODEL_REGION_VARIABLES: tuple[str, ...] = tuple(
    v
    for gs in gridding_sectors_reporting
    if gs.spatial_resolution == SpatialResolutionOption.MODEL_REGION
    for v in gs.to_complete_variables()
)
"""
Complete set of variables at the model region level
"""

REQUIRED_MODEL_REGION_VARIABLES: tuple[str, ...] = tuple(
    v
    for gs in gridding_sectors_reporting
    if gs.spatial_resolution == SpatialResolutionOption.MODEL_REGION
    for v in gs.to_required_variables()
)
"""
Required set of variables at the model region level
"""

OPTIONAL_MODEL_REGION_VARIABLES: tuple[str, ...] = tuple(
    set(COMPLETE_MODEL_REGION_VARIABLES) - set(REQUIRED_MODEL_REGION_VARIABLES)
)
"""
Optional set of variables at the model region level
"""


def get_complete_timeseries_index(
    model_regions: tuple[str, ...],
    world_region: str = "World",
    region_level: str = "region",
    variable_level: str = "variable",
) -> pd.MultiIndex:
    """
    Get the index of complete data

    Parameters
    ----------
    model_regions
        Model regions to use while reaggregating

    world_region
        The value used when the data represents the sum over all regions

    region_level
        Region level in the data index

    variable_level
        Variable level in the data index

    Returns
    -------
    :
        Index of complete data
    """
    world_required = pd.MultiIndex.from_product(
        [COMPLETE_WORLD_VARIABLES, [world_region]], names=[variable_level, region_level]
    )

    model_region_required = pd.MultiIndex.from_product(
        [COMPLETE_MODEL_REGION_VARIABLES, model_regions],
        names=[variable_level, region_level],
    )

    res: pd.MultiIndex = world_required.append(model_region_required)  # type: ignore

    return res


def get_required_timeseries_index(
    model_regions: tuple[str, ...],
    world_region: str = "World",
    region_level: str = "region",
    variable_level: str = "variable",
) -> pd.MultiIndex:
    """
    Get the index of required data

    Parameters
    ----------
    model_regions
        Model regions to use while reaggregating

    world_region
        The value used when the data represents the sum over all regions

    region_level
        Region level in the data index

    variable_level
        Variable level in the data index

    Returns
    -------
    :
        Index for required data
    """
    world_required = pd.MultiIndex.from_product(
        [REQUIRED_WORLD_VARIABLES, [world_region]], names=[variable_level, region_level]
    )

    model_region_required = pd.MultiIndex.from_product(
        [REQUIRED_MODEL_REGION_VARIABLES, model_regions],
        names=[variable_level, region_level],
    )

    res: pd.MultiIndex = world_required.append(model_region_required)  # type: ignore

    return res


def get_internal_consistency_checking_index(
    model_regions: tuple[str, ...],
    world_region: str = "World",
    region_level: str = "region",
    variable_level: str = "variable",
) -> pd.MultiIndex:
    """
    Get the index which selects only data relevant for checking internal consistency

    Parameters
    ----------
    model_regions
        Model regions to use while reaggregating

    world_region
        The value used when the data represents the sum over all regions

    region_level
        Region level in the data index

    variable_level
        Variable level in the data index

    Returns
    -------
    :
        Internal consistency checking index
    """
    world_internal_consistency_checking = pd.MultiIndex.from_product(
        [COMPLETE_WORLD_VARIABLES, [world_region]], names=[variable_level, region_level]
    )
    model_region_consistency_checking_variables = [
        v
        for v in COMPLETE_MODEL_REGION_VARIABLES
        if not (
            # Avoid double counting with "Energy|Demand|Transportation"
            SECTOR_DOMESTIC_AVIATION in v
            or (v.startswith("Carbon Removal") and v.count("|") <= 1)
        )
    ]
    # Add components of the tree that are needed for consistency checking
    # but we don't otherwise use.
    # This is a nasty hack that we should clean up in future
    # so the logic of this is more obvious.
    model_region_consistency_checking_variables.append(
        "Carbon Removal|Geological Storage|Other Sources"
    )
    model_region_consistency_checking_variables.append(
        "Carbon Removal|Geological Storage|Synthetic Fuels"
    )
    model_region_consistency_checking = pd.MultiIndex.from_product(
        [model_region_consistency_checking_variables, model_regions],
        names=[variable_level, region_level],
    )

    res: pd.MultiIndex = world_internal_consistency_checking.append(  # type: ignore
        model_region_consistency_checking
    )

    return res


def get_example_input(  # noqa: PLR0913
    model_regions: tuple[str, ...],
    global_only_variables: tuple[tuple[str, str], ...] = (
        ("Emissions|HFC|HFC23", "kt HFC23/yr"),
        ("Emissions|HFC", "kt HFC134a-equiv/yr"),
        ("Emissions|HFC|HFC134a", "kt HFC134a/yr"),
        ("Emissions|HFC|HFC43-10", "kt HFC43-10/yr"),
        ("Emissions|PFC", "kt CF4-equiv/yr"),
        ("Emissions|F-Gases", "Mt CO2-equiv/yr"),
        ("Emissions|SF6", "kt SF6/yr"),
        ("Emissions|CF4", "kt CF4/yr"),
        ("Emissions|C2F6", "kt C2F6/yr"),
        ("Emissions|C6F14", "kt C6F14/yr"),
    ),
    timepoints: NP_ARRAY_OF_FLOAT_OR_INT = np.arange(2010, 2100 + 1, 10.0),
    get_variable_unit: Callable[[str], str] = get_variable_unit_default,
    rng: np.random.Generator = np.random.default_rng(),
    world_region: str = "World",
    model: str = "model",
    scenario: str = "scenario",
    region_level: str = "region",
    variable_level: str = "variable",
    model_level: str = "model",
    scenario_level: str = "scenario",
    unit_level: str = "unit",
    columns_name: str = "year",
) -> pd.DataFrame:
    """
    Get example input data

    Parameters
    ----------
    model_regions
        Model regions to use in the example data

    global_only_variables
        Variables to include only at the global total level

    timepoints
        Timepoints to use in the example

    get_variable_unit
        Function to use to get the unit for each variable

    rng
        Random number generator

    world_region
        The value used when the data represents the sum over all regions

    model
        Model metadata value

    scenario
        Scenario metadata value

    region_level
        Region level in the data index

    variable_level
        Variable level in the data index

    model_level
        Model level in the data index

    scenario_level
        Scenario level in the data index

    unit_level
        Unit level in the data index

    columns_name
        Name of the columns in the output

    Returns
    -------
    :
        Example input expected by the re-aggregator
    """
    # Hard-coded because the example input
    # is tightly coupled to the idea of completeness
    starting_variables = (*COMPLETE_MODEL_REGION_VARIABLES, *COMPLETE_WORLD_VARIABLES)

    # Get our starting point
    start_index = pd.MultiIndex.from_product(
        [starting_variables, model_regions, [model], [scenario]],
        names=[variable_level, region_level, model_level, scenario_level],
    )
    start = pd.DataFrame(
        rng.random((start_index.shape[0], timepoints.size)),
        columns=pd.Index(timepoints, name=columns_name),
        index=start_index,
    )

    # Aggregate up the sectors
    start_sector_full = aggregate_df_level(
        start, level="variable", on_clash="overwrite"
    )
    # Aggregate up the regions
    start_sector_full_region_sum = set_new_single_value_levels(
        groupby_except(start_sector_full, region_level).sum(),
        {region_level: world_region},
    )

    # Put it altogether
    all_info = pd.concat(
        [
            start_sector_full,
            start_sector_full_region_sum.reorder_levels(start_sector_full.index.names),
        ]
    )

    # Keep only the bits required for completeness
    complete_index = get_complete_timeseries_index(
        model_regions=model_regions,
        world_region=world_region,
        region_level=region_level,
        variable_level=variable_level,
    )
    res_gridding = multi_index_lookup(all_info, complete_index)

    # Add unit info
    res_gridding.index = create_levels_based_on_existing(
        res_gridding.index,  # type: ignore # fix when moving to pandas-openscm
        {unit_level: (variable_level, get_variable_unit)},
    )

    if global_only_variables:
        global_only = pd.DataFrame(
            rng.random((len(global_only_variables), timepoints.size)),
            columns=res_gridding.columns,
            index=pd.MultiIndex.from_tuples(
                [
                    (variable, unit, world_region, model, scenario)
                    for (variable, unit) in global_only_variables
                ],
                names=[
                    variable_level,
                    unit_level,
                    region_level,
                    model_level,
                    scenario_level,
                ],
            ),
        )

        res = pd.concat(
            [res_gridding, global_only.reorder_levels(res_gridding.index.names)]
        )

    else:
        res = res_gridding

    return res


def assert_has_all_required_timeseries(
    df: pd.DataFrame,
    model_regions: tuple[str, ...],
    world_region: str = "World",
    region_level: str = "region",
    variable_level: str = "variable",
) -> None:
    """
    Assert that the data has all the required timeseries

    Parameters
    ----------
    df
        Data to check

    model_regions
        Model regions to use while reaggregating

    world_region
        The value used when the data represents the sum over all regions

    region_level
        Region level in the data index

    variable_level
        Variable level in the data index

    Raises
    ------
    NotCompleteError
        `indf` is not complete
    """
    assert_all_groups_are_complete(
        df,
        complete_index=get_required_timeseries_index(
            model_regions=model_regions,
            world_region=world_region,
            region_level=region_level,
            variable_level=variable_level,
        ),
    )


def get_default_internal_conistency_checking_tolerances() -> (
    Mapping[str, Mapping[str, float]] | Mapping[str, Mapping[str, PINT_SCALAR]]
):
    """
    Get default tolerances used when checking the internal consistency of data

    If [openscm_units][] is available,
    we use [pint](https://pint.readthedocs.io)
    quantities for the tolerances to add unit awareness.
    If not, we return plain floats.

    Returns
    -------
    :
        Tolerances to use when checking the internal consistency of the data
    """
    try:
        import openscm_units

        Q = openscm_units.unit_registry.Quantity

        default_tolerances: (
            Mapping[str, Mapping[str, float]] | Mapping[str, Mapping[str, PINT_SCALAR]]
        ) = {  # type: ignore # some issue with openscm-units type hints
            "Emissions|BC": dict(rtol=1e-3, atol=Q(1e-3, "Mt BC/yr")),
            "Emissions|CH4": dict(rtol=1e-3, atol=Q(1e-2, "Mt CH4/yr")),
            "Emissions|CO": dict(rtol=1e-3, atol=Q(1e-1, "Mt CO/yr")),
            "Emissions|CO2": dict(rtol=1e-3, atol=Q(1e0, "Mt CO2/yr")),
            "Emissions|NH3": dict(rtol=1e-3, atol=Q(1e-2, "Mt NH3/yr")),
            "Emissions|NOx": dict(rtol=1e-3, atol=Q(1e-2, "Mt NO2/yr")),
            "Emissions|OC": dict(rtol=1e-3, atol=Q(1e-3, "Mt OC/yr")),
            "Emissions|Sulfur": dict(rtol=1e-3, atol=Q(1e-2, "Mt SO2/yr")),
            "Emissions|VOC": dict(rtol=1e-3, atol=Q(1e-2, "Mt VOC/yr")),
            "Emissions|N2O": dict(rtol=1e-3, atol=Q(1e-1, "kt N2O/yr")),
            "Carbon Removal|Enhanced Weathering": dict(
                rtol=1e-3, atol=Q(1e0, "Mt CO2/yr")
            ),
            "Carbon Removal|Geological Storage": dict(
                rtol=1e-3, atol=Q(1e0, "Mt CO2/yr")
            ),
            "Carbon Removal|Long-Lived Materials": dict(
                rtol=1e-3, atol=Q(1e0, "Mt CO2/yr")
            ),
            "Carbon Removal|Ocean": dict(rtol=1e-3, atol=Q(1e0, "Mt CO2/yr")),
            "Carbon Removal|Other": dict(rtol=1e-3, atol=Q(1e0, "Mt CO2/yr")),
        }

    except ImportError:
        default_tolerances = {
            "Emissions|BC": dict(rtol=1e-3, atol=1e-6),
            "Emissions|CH4": dict(rtol=1e-3, atol=1e-6),
            "Emissions|CO": dict(rtol=1e-3, atol=1e-6),
            "Emissions|CO2": dict(rtol=1e-3, atol=1e-6),
            "Emissions|NH3": dict(rtol=1e-3, atol=1e-6),
            "Emissions|NOx": dict(rtol=1e-3, atol=1e-6),
            "Emissions|OC": dict(rtol=1e-3, atol=1e-6),
            "Emissions|Sulfur": dict(rtol=1e-3, atol=1e-6),
            "Emissions|VOC": dict(rtol=1e-3, atol=1e-6),
            "Emissions|N2O": dict(rtol=1e-3, atol=1e-6),
            "Carbon Removal|Enhanced Weathering": dict(rtol=1e-3, atol=1e-6),
            "Carbon Removal|Geological Storage": dict(rtol=1e-3, atol=1e-6),
            "Carbon Removal|Long-Lived Materials": dict(rtol=1e-3, atol=1e-6),
            "Carbon Removal|Ocean": dict(rtol=1e-3, atol=1e-6),
            "Carbon Removal|Other": dict(rtol=1e-3, atol=1e-6),
        }

    return default_tolerances


def assert_is_internally_consistent(  # noqa: PLR0913
    df: pd.DataFrame,
    model_regions: tuple[str, ...],
    tolerances: Mapping[str, Mapping[str, float]]
    | Mapping[str, Mapping[str, PINT_SCALAR]],
    world_region: str = "World",
    region_level: str = "region",
    unit_level: str = "unit",
    variable_level: str = "variable",
) -> None:
    """
    Assert that the data is internally consistent

    Parameters
    ----------
    df
        Data to check

    model_regions
        Model regions to use while reaggregating

    tolerances
        Tolerances to apply while checking internal consistency

        Each key should be a variable up to species info
        e.g. "Emission|CH4"
        and each value should be the tolerance arguments to pass
        to [np.isclose][numpy.isclose].
        These tolerance arguments can be pint quantities,
        in which case they are converted to the data's units
        before passing to [np.isclose][numpy.isclose].

    world_region
        The value used when the data represents the sum over all regions

    region_level
        Region level in the data index

    unit_level
        Unit level in the data index

    variable_level
        Variable level in the data index

    Raises
    ------
    InternalConsistencyError
        The data is not internally consistent at the given tolerances
    """
    try:
        import pint
    except ModuleNotFoundError:
        pint = None  # type: ignore

    internal_consistency_checking_index = get_internal_consistency_checking_index(
        model_regions=model_regions,
        world_region=world_region,
        region_level=region_level,
        variable_level=variable_level,
    )

    # Hard-code the logic here
    # because that's what is needed for consistency with the rest of the module.
    # This is one of the issues with the data model used by ScmRun, pyam etc.:
    # the convention is that the first two levels are the species total
    # but this is only implied and not explicit at all
    # (and not even followed in all cases e.g. Emissions|HFC|HFC23).
    def get_species_total_variable(v: str) -> str:
        return "|".join(v.split("|")[:2])

    for species_total_variable, df_species in df.groupby(
        df.index.get_level_values(variable_level).map(get_species_total_variable)
    ):
        df_species_total_reported = df_species.loc[
            (
                df_species.index.get_level_values(variable_level)
                == species_total_variable
            )
            & (df_species.index.get_level_values(region_level) == world_region)
        ]
        if df_species_total_reported.empty:
            # Nothing reported so can move on
            continue

        df_species_internal_consistency_checking_relevant = multi_index_lookup(
            df_species, internal_consistency_checking_index
        )
        if df_species_internal_consistency_checking_relevant.empty:
            # Nothing relevant for checking internal consistency
            continue

        # Note: what we're checking here is that if you sum over the sectors
        # and regions using the index which provides internal consistency,
        # you should get the reported totals.
        # This is different to checking that the implied hierarchy
        # from the variable names
        # (i.e. that levels are separated by "|"
        # and each level should be the sum of its components)
        # is not what we're checking.

        # TODO: split out a function like
        # assert_reported_matches_sum_of_components
        # Would have to be very specific to this setup
        # because of how many different ways it can go wrong
        # e.g. you can have extra components that aren't used,
        # incorrect aggregation

        df_species_aggregate = get_region_sector_sum(
            df_species_internal_consistency_checking_relevant,
            region_level=region_level,
            world_region=world_region,
        ).reorder_levels(df_species.index.names)

        tolerances_species = {}
        for kwarg, value in tolerances[species_total_variable].items():
            if pint is not None and isinstance(value, pint.Quantity):
                if kwarg == "atol":
                    species_units = df_species.index.get_level_values(
                        unit_level
                    ).unique()
                    if len(species_units) > 1:
                        msg = (
                            "Cannot use pint conversion "
                            "if your data contains different units. "
                            f"For {species_total_variable=}, we have {species_units=}"
                        )
                        raise ValueError(msg)

                    tolerances_species[kwarg] = value.to(species_units[0]).m

                elif kwarg == "rtol":
                    tolerances_species[kwarg] = value.to("dimensionless").m

                else:
                    raise NotImplementedError(kwarg)

            else:
                tolerances_species[kwarg] = value

        comparison_species = compare_close(
            left=df_species_total_reported,
            right=df_species_aggregate,
            left_name="reported_total",
            right_name="derived_from_input",
            **tolerances_species,
        )

        if not comparison_species.empty:
            raise InternalConsistencyError(
                differences=comparison_species,
                data_that_was_summed=df_species,
                # Would need something like this to give full details
                # data_that_was_not_summed=data_that_was_not_summed,
                tolerances=tolerances_species,
            )


def to_complete(  # noqa: PLR0913
    indf: pd.DataFrame,
    model_regions: tuple[str, ...],
    unit_level: str = "unit",
    variable_level: str = "variable",
    region_level: str = "region",
    world_region: str = "World",
) -> ToCompleteResult:
    """
    Convert the raw data to complete data

    Parameters
    ----------
    indf
        Data to process

    model_regions
        Model regions to use while reaggregating

    unit_level
        Unit level in the data index

    variable_level
        Variable level in the data index

    region_level
        Region level in the data index

    world_region
        The value used when the data represents the sum over all regions

    Returns
    -------
    :
        To complete result
    """
    assert_only_working_on_variable_unit_region_variations(indf)

    complete_index = get_complete_timeseries_index(
        model_regions=model_regions,
        region_level=region_level,
        variable_level=variable_level,
        world_region=world_region,
    )

    keep = multi_index_lookup(indf, complete_index)
    missing_indexes = get_missing_levels(
        keep.index,  # type: ignore # pandas-stubs confused
        complete_index=complete_index,
        unit_col=unit_level,
    )

    if missing_indexes.empty:
        res = ToCompleteResult(complete=keep, assumed_zero=None)
    else:
        keep_split = split_sectors(keep, middle_level="species")

        species_unit_map = {
            species: unit
            for species, unit in keep_split.index.droplevel(
                keep_split.index.names.difference(["species", unit_level])  # type: ignore #pandas-stubs confused
            )
            .drop_duplicates()
            .reorder_levels(["species", unit_level])
        }

        emissions_mask = missing_indexes.get_level_values(
            variable_level
        ).str.startswith("Emissions")
        missing_indexes_emissions = missing_indexes[emissions_mask]
        missing_indexes_carbon_removal = missing_indexes[~emissions_mask]

        if not missing_indexes_emissions.empty:
            missing_indexes_emissions_split = split_sectors(missing_indexes_emissions)  # type: ignore # type hint is wrong upstream (fix when moving to pandas-openscm)
            zeros_index_split = create_levels_based_on_existing(
                missing_indexes_emissions_split,  # type: ignore # type hint is wrong upstream (fix when moving to pandas-openscm)
                {unit_level: ("species", species_unit_map)},  # type: ignore # type hint is wrong upstream (fix when moving to pandas-openscm)
            )
            zeros_index_emissions: pd.MultiIndex = combine_sectors(  # type: ignore # need to think through type hints for combine_sectors more carefully
                zeros_index_split,  # type: ignore # need to think through type hints for combine_sectors more carefully
                middle_level="species",
            )

        if not missing_indexes_carbon_removal.empty:
            existing_carbon_removal = keep_split[
                keep_split.index.get_level_values("table").str.startswith(
                    "Carbon Removal"
                )
            ]
            if existing_carbon_removal.empty:
                unit = species_unit_map["CO2"]
            else:
                # Use the first, as good as any
                unit = existing_carbon_removal.index.get_level_values("unit")[0]

            zeros_index_carbon_removal = set_levels(
                missing_indexes_carbon_removal, {unit_level: unit}
            )

        if (
            not missing_indexes_emissions.empty
            and not missing_indexes_carbon_removal.empty
        ):
            zeros_index = zeros_index_emissions.append(  # type: ignore # not supported by pandas-stubs
                zeros_index_carbon_removal.reorder_levels(zeros_index_emissions.names)  # type: ignore # not supported by pandas-stubs
            )

        elif not missing_indexes_emissions.empty:
            zeros_index = zeros_index_emissions

        elif not missing_indexes_carbon_removal.empty:
            zeros_index = zeros_index_carbon_removal

        else:
            raise AssertionError

        other_levels_deduped = indf.index.droplevel(
            [variable_level, unit_level, region_level]
        ).drop_duplicates()
        if other_levels_deduped.shape[0] != 1:
            msg = f"Multiple values in other levels:\n{other_levels_deduped=}"
            raise AssertionError(msg)

        extra_levels = {
            level: value
            for level, value in zip(other_levels_deduped.names, other_levels_deduped[0])
        }
        assumed_zero = set_new_single_value_levels(
            pd.DataFrame(
                np.zeros((zeros_index.shape[0], keep.shape[1])),
                columns=keep.columns,
                index=zeros_index,
            ),
            extra_levels,
            copy=False,
        )
        complete = pd.concat([keep, assumed_zero.reorder_levels(keep.index.names)])
        res = ToCompleteResult(complete=complete, assumed_zero=assumed_zero)

    return res


def aggregate_cols(
    df: pd.DataFrame, aggregations: dict[str, list[str]]
) -> pd.DataFrame:
    """
    Aggregate columns

    This is a helper function for [to_gridding_sectors][(m).].

    It does the aggregation in place so we can check that all the columns were used.

    Parameters
    ----------
    df
        Starting [pd.DataFrame][pandas.DataFrame]

    aggregations
        Aggregations to apply

        Each key is the output column,
        each value is the components that contribute to the output column.

    Returns
    -------
    :
        `df` with the aggregations applied
    """
    for aggregate, components in aggregations.items():
        df[aggregate] = df[components].sum(axis="columns")
        df = df.drop(
            # Subtract aggregate in case the aggregate and component have the same name
            list(set(components) - {aggregate}),
            axis="columns",
        )

    return df


def to_gridding_sectors(
    indf: pd.DataFrame, region_level: str = "region", world_region: str = "World"
) -> pd.DataFrame:
    """
    Re-aggregate data to the sectors used for gridding

    Parameters
    ----------
    indf
        Data to re-aggregate

    region_level
        Region level in the data index

    world_region
        The value used when the data represents the sum over all regions

    Returns
    -------
    :
        Data re-aggregated to the gridding sectors
    """
    # Split off the carbon removal tree first
    carbon_removal_mask = indf.index.get_level_values("variable").str.startswith(
        "Carbon Removal"
    )
    carbon_removal = indf[carbon_removal_mask]
    emissions = indf[~carbon_removal_mask]

    # Processing is way easier if we process the DataFrame's a bit first
    emissions_world_mask = (
        emissions.index.get_level_values(region_level) == world_region
    )

    # Data that is at the world level i.e. has no region information
    emissions_sector_df = (
        split_sectors(
            emissions.loc[emissions_world_mask].reset_index("region", drop=True),
            bottom_level="sectors",
        )
        .stack()
        .unstack("sectors")
    )

    # Data with region information
    emissions_region_sector_df = (
        split_sectors(emissions.loc[~emissions_world_mask], bottom_level="sectors")
        .stack()
        .unstack("sectors")
    )

    # CDR information
    emissions_cdr = -1 * update_index_levels_func(
        carbon_removal,
        {"variable": lambda x: x.replace("Carbon Removal", "Emissions|CO2|CDR")},
    )
    emissions_cdr_world_mask = (
        emissions_cdr.index.get_level_values(region_level) == world_region
    )
    if emissions_cdr_world_mask.any():
        raise NotImplementedError

    emissions_region_sector_df_co2_mask = (
        emissions_region_sector_df.index.get_level_values("species") == "CO2"
    )

    emissions_cdr_region_sector_df = convert_unit_like(
        split_sectors(  # type: ignore # pandas-stubs confused
            emissions_cdr.loc[~emissions_cdr_world_mask], bottom_level="sectors"
        )
        .stack()
        .unstack("sectors"),
        emissions_region_sector_df.loc[emissions_region_sector_df_co2_mask],  # type: ignore # pandas-stubs confused
    )

    # Move domestic aviation to the global level,
    # remove it from regional transport
    # and drop the levels we no longer use.
    domestic_aviation_sum = groupby_except(
        emissions_region_sector_df[SECTOR_DOMESTIC_AVIATION],  # type: ignore # issue in pandas-openscm
        region_level,
    ).sum()
    emissions_sector_df["Aircraft"] = (
        emissions_sector_df["Energy|Demand|Bunkers|International Aviation"]
        + domestic_aviation_sum
    )
    emissions_region_sector_df["Energy|Demand|Transportation"] = (
        emissions_region_sector_df["Energy|Demand|Transportation"]
        - emissions_region_sector_df[SECTOR_DOMESTIC_AVIATION]
    )
    emissions_sector_df = emissions_sector_df.drop(
        ["Energy|Demand|Bunkers|International Aviation"], axis="columns"
    )
    emissions_region_sector_df = emissions_region_sector_df.drop(
        [SECTOR_DOMESTIC_AVIATION], axis="columns"
    )

    # Handle the CDR sectors
    carbon_removal_map = {
        "CDR|Enhanced Weathering": "Other Capture and Removal",
        "CDR|Geological Storage|Biomass": "Energy|Supply",
        "CDR|Geological Storage|Direct Air Capture": "Other Capture and Removal",
        "CDR|Ocean": "Other Capture and Removal",
        # See note above
        # "CDR|Other": "Other Capture and Removal",
    }
    for cdr_sector, emissions_sector in carbon_removal_map.items():
        row_loc = emissions_region_sector_df_co2_mask
        col_loc = emissions_sector
        emissions_region_sector_df.loc[row_loc, col_loc] = (
            emissions_region_sector_df.loc[row_loc, col_loc]
            - emissions_cdr_region_sector_df[cdr_sector]
        )

    # Aggregate
    sector_df_gridding = aggregate_cols(
        emissions_sector_df,  # type: ignore # need to cast first or something
        {
            "International Shipping": ["Energy|Demand|Bunkers|International Shipping"],
            # Not the same as the reporting sector as we have done manipulations above
            "Aircraft": ["Aircraft"],
        },
    )
    region_sector_df_gridding = aggregate_cols(
        emissions_region_sector_df,  # type: ignore # need to cast first or something
        {
            "Agricultural Waste Burning": [
                "AFOLU|Agricultural Waste Burning",
            ],
            "Agriculture": [
                "AFOLU|Agriculture",
                "AFOLU|Land|Harvested Wood Products",
                "AFOLU|Land|Land Use and Land-Use Change",
                "AFOLU|Land|Other",
                "AFOLU|Land|Wetlands",
            ],
            "Energy Sector": ["Energy|Supply"],
            "Forest Burning": ["AFOLU|Land|Fires|Forest Burning"],
            "Grassland Burning": ["AFOLU|Land|Fires|Grassland Burning"],
            "Industrial Sector": [
                "Energy|Demand|Industry",
                "Energy|Demand|Other Sector",
                "Industrial Processes",
                "Other",
            ],
            "Other CDR": [
                "Other Capture and Removal",
            ],
            "Peat Burning": ["AFOLU|Land|Fires|Peat Burning"],
            "Residential Commercial Other": [
                "Energy|Demand|Residential and Commercial and AFOFI"
            ],
            "Solvents Production and Application": ["Product Use"],
            "Transportation Sector": ["Energy|Demand|Transportation"],
            "Waste": ["Waste"],
        },
    )

    emissions_cdr_region_sector_df_gridding = aggregate_cols(
        emissions_cdr_region_sector_df,
        {
            "BECCS": [
                "CDR|Geological Storage|Biomass",
            ],
            "Enhanced Weathering": [
                "CDR|Enhanced Weathering",
            ],
            "Direct Air Capture": [
                "CDR|Geological Storage|Direct Air Capture",
            ],
            "Ocean": [
                "CDR|Ocean",
            ],
        },
    )

    sector_df_gridding_like_input = combine_sectors(
        set_new_single_value_levels(
            sector_df_gridding.unstack().stack("sectors", future_stack=True),  # type: ignore # pandas-stubs confused
            {region_level: world_region},
        ),
        bottom_level="sectors",
    )
    region_sector_df_gridding_like_input = combine_sectors(
        region_sector_df_gridding.unstack().stack("sectors", future_stack=True),  # type: ignore # pandas-stubs confused
        bottom_level="sectors",
    )
    emissions_cdr_region_sector_df_gridding_like_input = combine_sectors(
        emissions_cdr_region_sector_df_gridding.unstack().stack(
            "sectors",  # type: ignore # pandas-stubs confused
            future_stack=True,
        ),
        bottom_level="sectors",
    )

    res = pd.concat(
        [
            df.reorder_levels(indf.index.names)
            for df in [
                sector_df_gridding_like_input,
                region_sector_df_gridding_like_input,
                emissions_cdr_region_sector_df_gridding_like_input,
            ]
        ]
    )

    return res


@define
class ReaggregatorBasic:
    """
    Reaggregator that follows this module's logic
    """

    model_regions: tuple[str, ...]
    """Model regions to use while reaggregating"""

    region_level: str = "region"
    """Region level in the data index"""

    unit_level: str = "unit"
    """Unit level in the data index"""

    variable_level: str = "variable"
    """Variable level in the data index"""

    world_region: str = "World"
    """
    The value used when the data represents the sum over all regions

    (Having a value for this is odd,
    there should really just be no region level when data is the sum,
    but this is the data format used so we have to follow this convention.)
    """

    internal_consistency_tolerances: (
        Mapping[str, Mapping[str, float]] | Mapping[str, Mapping[str, PINT_SCALAR]]
    ) = field()
    """
    Tolerances to apply when checking the internal consistency of the data
    """

    @internal_consistency_tolerances.default
    def default_tols_internal_consistency(
        self,
    ) -> Mapping[str, Mapping[str, float]] | Mapping[str, Mapping[str, PINT_SCALAR]]:
        """
        Get default tolerances for internal consistency checks
        """
        return get_default_internal_conistency_checking_tolerances()

    def assert_has_all_required_timeseries(self, indf: pd.DataFrame) -> None:
        """
        Assert that the data has all the required timeseries

        Parameters
        ----------
        indf
            Data to check

        Raises
        ------
        NotCompleteError
            `indf` is not complete
        """
        assert_has_all_required_timeseries(
            indf,
            model_regions=self.model_regions,
            world_region=self.world_region,
            region_level=self.region_level,
            variable_level=self.variable_level,
        )

    def assert_is_internally_consistent(self, indf: pd.DataFrame) -> None:
        """
        Assert that the data is internally consistent

        Parameters
        ----------
        indf
            Data to check

        Raises
        ------
        InternalConsistencyError
            The data is not internally consistent
        """
        assert_is_internally_consistent(
            indf,
            model_regions=self.model_regions,
            tolerances=self.internal_consistency_tolerances,
            world_region=self.world_region,
            region_level=self.region_level,
            unit_level=self.unit_level,
            variable_level=self.variable_level,
        )

    def get_internal_consistency_checking_index(self) -> pd.MultiIndex:
        """
        Get the index which selects only data relevant for checking internal consistency

        Returns
        -------
        :
            Internal consistency checking index
        """
        return get_internal_consistency_checking_index(
            model_regions=self.model_regions,
            world_region=self.world_region,
            region_level=self.region_level,
            variable_level=self.variable_level,
        )

    def to_complete(self, raw: pd.DataFrame) -> ToCompleteResult:
        """
        Convert the raw data to complete data

        Parameters
        ----------
        raw
            Raw data

        Returns
        -------
        :
            To complete result
        """
        return to_complete(
            indf=raw,
            model_regions=self.model_regions,
            unit_level=self.unit_level,
            variable_level=self.variable_level,
            region_level=self.region_level,
            world_region=self.world_region,
        )

    def to_gridding_sectors(self, indf: pd.DataFrame) -> pd.DataFrame:
        """
        Re-aggregate data to the sectors used for gridding

        Parameters
        ----------
        indf
            Data to re-aggregate

        Returns
        -------
        :
            Data re-aggregated to the gridding sectors
        """
        return to_gridding_sectors(
            indf=indf, region_level=self.region_level, world_region=self.world_region
        )
