import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component.
if not _RELEASE:
    _component_func = components.declare_component(
        "filter",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("filter", path=build_dir)


def filter(name, options=None, key=None):
    """Create a new filter component.

    Parameters
    ----------
    name: str
        The name of the filter.
    options: list
        List of options to choose from.
    key: str or None
        An optional key that uniquely identifies this component.

    Returns
    -------
    list
        The list of selected options.
    """
    if options is None:
        options = []
        
    return _component_func(
        filterName=name,
        options=options,
        default=[],
        key=key
    )