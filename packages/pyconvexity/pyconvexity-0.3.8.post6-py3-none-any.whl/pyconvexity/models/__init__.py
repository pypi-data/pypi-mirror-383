"""
Model management module for PyConvexity.

Contains high-level operations for networks, components, and attributes.
"""

from pyconvexity.models.components import (
    get_component_type, get_component, list_components_by_type,
    insert_component, create_component, update_component, delete_component,
    list_component_attributes, get_default_carrier_id, get_bus_name_to_id_map,
    get_component_by_name, get_component_id, component_exists, get_component_carrier_map
)

from pyconvexity.models.attributes import (
    set_static_attribute, set_timeseries_attribute, get_attribute, delete_attribute
)

from pyconvexity.models.network import (
    create_network, get_network_info, get_network_time_periods, list_networks,
    create_carrier, list_carriers, get_network_config, set_network_config,
    get_component_counts, get_master_scenario_id, resolve_scenario_id,
    get_first_network, get_network_by_name
)

# Import from new modules
from pyconvexity.models.scenarios import (
    list_scenarios as list_scenarios_new,
    get_scenario_by_name, get_scenario_by_id, get_master_scenario
)

from pyconvexity.models.results import (
    get_solve_results, get_yearly_results
)

from pyconvexity.models.carriers import (
    list_carriers as list_carriers_new,
    get_carrier_by_name, get_carrier_by_id, get_carrier_colors
)

# Try to import old scenarios functions if they exist
try:
    from pyconvexity.models.scenarios_old import (
        create_scenario, list_scenarios as list_scenarios_old, 
        get_scenario, delete_scenario
    )
    # Use old functions as primary for backward compatibility
    list_scenarios_primary = list_scenarios_old
except ImportError:
    # Old module doesn't exist, use new functions
    list_scenarios_primary = list_scenarios_new
    # Create dummy functions for backward compatibility
    def create_scenario(*args, **kwargs):
        raise NotImplementedError("create_scenario not yet implemented in new API")
    def get_scenario(*args, **kwargs):
        return get_scenario_by_id(*args, **kwargs)
    def delete_scenario(*args, **kwargs):
        raise NotImplementedError("delete_scenario not yet implemented in new API")

__all__ = [
    # Component operations
    "get_component_type", "get_component", "list_components_by_type",
    "insert_component", "create_component", "update_component", "delete_component",
    "list_component_attributes", "get_default_carrier_id", "get_bus_name_to_id_map",
    "get_component_by_name", "get_component_id", "component_exists", "get_component_carrier_map",
    
    # Attribute operations
    "set_static_attribute", "set_timeseries_attribute", "get_attribute", "delete_attribute",
    
    # Network operations
    "create_network", "get_network_info", "get_network_time_periods", "list_networks",
    "create_carrier", "list_carriers", "get_network_config", "set_network_config",
    "get_component_counts", "get_master_scenario_id", "resolve_scenario_id",
    "get_first_network", "get_network_by_name",
    
    # Scenario operations (backward compatible)
    "create_scenario", "list_scenarios_primary", "get_scenario", "delete_scenario",
    "list_scenarios_new", "get_scenario_by_name", "get_scenario_by_id", "get_master_scenario",
    
    # Results operations
    "get_solve_results", "get_yearly_results",
    
    # Carrier operations
    "list_carriers_new", "get_carrier_by_name", "get_carrier_by_id", "get_carrier_colors",
]

# Expose primary list_scenarios for convenience
list_scenarios = list_scenarios_primary
