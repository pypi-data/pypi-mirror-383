"""Package containing models, the pythonic representation of feature classes.

They inherit from [`BaseFeature`][xplan_tools.model.base.BaseFeature], which extends the Pydantic `BaseModel` with some utility, and are usually instantiated with the [`model_factory`][xplan_tools.model.model_factory] method.
A feature collection is represented by the [`BaseCollection`][xplan_tools.model.base.BaseCollection] class.

Example:
    Load the BP_Plan model for XPlanung v6.0 and instantiate it with some data:
    ```
    plan = model_factory("BP_Plan", "6.0")
    instance = plan.model_validate(
        {
            "name": "Testplan",
            "gemeinde": [
                {
                    "ags": "1234"
                }
            ],
            "raeumlicherGeltungsbereich": {
                "srid": 25832,
                "wkt": <WKT-String>
            }
        }
    )
    ```
"""

from pydoc import locate
from typing import TYPE_CHECKING, Literal, Type

if TYPE_CHECKING:
    from .base import BaseFeature


def model_factory(
    model_name: str,
    model_version: str | None,
    data_type: Literal["xplan", "xtrasse", "plu", "def"] = "xplan",
) -> Type["BaseFeature"]:
    """Factory method for retrieving the corresponding pydantic model representation of a feature class.

    Args:
        model_name: name of the feature class
        model_version: version of the specification release
        data_type: Specification of either XPlanung, INSPIRE PLU, or general definitions used by both application schemas.

    Raises:
        ValueError: raises error for invalid model name and/or incompatible data version.

    Returns:
        BaseFeature: The concrete feature class inheriting from BaseFeature.
    """
    match data_type:
        case "xplan":
            version_map = {"6": "6.0", "5": "5.4", "4": "4.1"}
            model_version = version_map.get(model_version[0], model_version)
            model = locate(
                f"xplan_tools.model.appschema.xplan{model_version.replace('.', '')}.{model_name.replace('_', '')}"
            )
        case "plu":
            model = locate(
                f"xplan_tools.model.appschema.inspire_plu{model_version.replace('.', '')}.{model_name}"
            )
            model.model_config["extra"] = "ignore"
        case "def":
            model = locate(f"xplan_tools.model.appschema.definitions.{model_name}")
        case "xtrasse":
            model = locate(
                f"xplan_tools.model.appschema.xtrasse{model_version.replace('.', '')}.{model_name.replace('_', '')}"
            )

    if not model:
        raise ValueError(
            f"Invalid model name '{model_name}' or version '{model_version}' for data type '{data_type}'"
        )
    return model


__all__ = ["model_factory"]
