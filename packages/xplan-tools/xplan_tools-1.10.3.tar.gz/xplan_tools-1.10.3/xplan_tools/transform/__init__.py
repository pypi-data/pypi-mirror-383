"""Package containing a [`transformer_factory`][xplan_tools.transform.transformer_factory] for the transformation classes [`Transform_54_60`][xplan_tools.transform.transformer.Transform_54_60] and [`Transform_60_plu`][xplan_tools.transform.transformer.Transform_60_plu].

Example:
    Transformations for a collection ob XPlan objects can be chained like this
    ```
    collection = transformer_factory(collection, to_version="6.0").transform()
    collection = transformer_factory(collection, to_version="plu").transform()
    ```
    Thus, allowing a direct transformation for Xplan 5.* to INSPIRE PLU 4.0 in the
    final collection object
"""

from pydoc import locate
from typing import TYPE_CHECKING, Literal, Union

if TYPE_CHECKING:
    from xplan_tools.model.base import BaseCollection

    from .transformer import Transform_41_54, Transform_54_60, Transform_60_plu


def transformer_factory(
    collection: "BaseCollection", to_version: Literal["5.4", "6.0", "plu"]
) -> Union["Transform_41_54", "Transform_54_60", "Transform_60_plu"]:
    """Factory method for respective transformer from xplan 4.* to xplan 5.0, from xplan 5.* to xplan 6.0, as well as from xplan 6.0 to INSPIRE PLU 4.0.

    Args:
        collection (BaseCollection): collection of xplan objects
        to_version (Literal["5.4", "6.0", "plu"]): specifier for the respective transformation

    Returns:
        Union[Transform_41_54, Transform_54_60, Transform_60_plu]: instantiated transformer class
    """
    if to_version == "5.4":
        return locate("xplan_tools.transform.transformer.Transform_41_54")(collection)
    if to_version == "6.0":
        return locate("xplan_tools.transform.transformer.Transform_54_60")(collection)
    elif to_version == "plu":
        return locate("xplan_tools.transform.transformer.Transform_60_plu")(collection)


__all__ = ["transformer_factory"]
