"""Contains base classes for Features and FeatureCollections.

The classes provide some utility, (de-)serialization and/or validation methods to simplify access and manipulation.
"""

import datetime
import logging
import re
from types import NoneType
from typing import Any, Iterator, Literal, Optional, Tuple, Type, get_args, get_origin
from uuid import UUID

from lxml.etree import _Element
from osgeo import ogr
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    SerializationInfo,
    SerializeAsAny,
    ValidationInfo,
    create_model,
    field_serializer,
    field_validator,
    model_validator,
)

from xplan_tools.model import model_factory
from xplan_tools.model.adapters import CoretableAdapter, GMLAdapter, JsonFGAdapter
from xplan_tools.model.orm import Feature
from xplan_tools.util import (
    cast_geom_to_multi,
    cast_geom_to_single,
    get_geometry_type_from_wkt,
    get_name,
)
from xplan_tools.util.style import add_style_properties_to_feature

ogr.UseExceptions()

logger = logging.getLogger(__name__)


class BaseCollection(BaseModel):
    """Container for features that provides validation of references.

    The features are stored in a dictionary with their ID as key and the feature instance as value.
    """

    features: SerializeAsAny[dict[str, "BaseFeature"]]
    srid: int

    @model_validator(mode="before")
    @classmethod
    def list_to_dict(cls, data: Any) -> Any:
        """Takes a list of BaseFeatures and returns a BaseCollection dict."""
        if isinstance(data, list):
            data_dict = {}
            for feature in data:
                if not isinstance(feature, BaseFeature):
                    raise TypeError(
                        f"Object is not an instance of BaseFeature: {feature}"
                    )
                data_dict[feature.id] = feature
            return data_dict
        return data

    @model_validator(mode="after")
    def check_references_and_srs(self) -> "BaseCollection":
        """Checks if all objects referenced via UUID are part of the collection and if all features have the same SRS."""
        logger.debug("checking feature references")
        keys = self.features.keys()
        srids = []
        for feature in self.features.values():
            if srid := feature.get_geom_srid():
                if srids and srid not in srids:
                    raise ValueError(
                        f"Multiple SRS within collection not supported: SRID {srid} != {srids[0]} for feature {feature.id}"
                    )
                else:
                    srids.append(srid)
            for name, value in feature:
                if isinstance(value, UUID):
                    if str(value) not in keys:
                        raise ValueError(
                            f"reference {name}: {value} in object {feature.id} not resolvable"
                        )
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, UUID) and str(item) not in keys:
                            raise ValueError(
                                f"reference {name}: {item} in object {feature.id} not resolvable"
                            )
        logger.debug("all feature references resolvable")
        return self

    def get_features(self) -> Iterator["BaseFeature"]:
        """Yields features stored in the collection."""
        return (feature for feature in self.features.values())

    def add_style_properties(
        self, to_text: bool = False, always_populate_schriftinhalt: bool = False
    ) -> None:
        """Add styling properties to presentational objects.

        This method parses object (dientZurDarstellungVon) and property (art) references from
        presentational objects and derives styling information (stylesheetId, schriftinhalt)
        based on a set of defined rules.

        Args:
            to_text: Whether to convert symbolic presentational objects to textual ones. Defaults to False.
            always_populate_schriftinhalt: Populate `schriftinhalt` even if a rule has no text template.
        """
        logger.info("adding style properties to collection")

        for obj in filter(lambda x: hasattr(x, "stylesheetId"), self.get_features()):
            if not obj.dientZurDarstellungVon:
                logger.info(
                    f"Feature {obj.id}: dientZurDarstellungVon not set, skipping"
                )
                continue
            elif len(obj.dientZurDarstellungVon) > 1:
                logger.warning(
                    f"Feature {obj.id}: references to multiple objects '{obj.dientZurDarstellungVon}' not supported, skipping"
                )
                continue
            elif not obj.art:
                logger.info(f"Feature {obj.id}: art not set, skipping")
                continue
            ref_obj = self.features.get(str(obj.dientZurDarstellungVon[0]))
            new_obj = add_style_properties_to_feature(
                obj, ref_obj, to_text, always_populate_schriftinhalt
            )
            self.features[obj.id] = new_obj

        logger.info("finished adding style properties to collection")

    def get_single_plans(
        self, with_name: bool = False
    ) -> Iterator["BaseCollection"] | Iterator[Tuple[str, "BaseCollection"]]:
        """Yields BaseCollection objects for every plan in the original collection."""
        for plan in filter(lambda x: "Plan" in x.get_name(), self.features.values()):
            collection = {plan.id: plan}
            for attr in ["texte", "begruendungsTexte"]:
                if refs := getattr(plan, attr):
                    collection.update(
                        {str(ref): self.features[str(ref)] for ref in refs}
                    )
            for bereich in filter(
                lambda x: str(getattr(x, "gehoertZuPlan", "")) == plan.id,
                self.features.values(),
            ):
                collection[bereich.id] = bereich
                for feature in filter(
                    lambda x: str(getattr(x, "gehoertZuBereich", "")) == bereich.id,
                    self.features.values(),
                ):
                    collection[feature.id] = feature
                    for attr in ["refBegruendungInhalt", "refTextInhalt"]:
                        if refs := getattr(feature, attr, None):
                            collection.update(
                                {str(ref): self.features[str(ref)] for ref in refs}
                            )
                if raster := getattr(bereich, "rasterBasis", None):
                    collection[str(raster)] = self.features[str(raster)]
                for attr in [
                    "nachrichtlich",
                    "inhaltBPlan",
                    "inhaltFPlan",
                    "inhaltLPlan",
                    "inhaltRPlan",
                    "inhaltSoPlan",
                    "rasterAenderung",
                ]:
                    if refs := getattr(bereich, attr, None):
                        collection.update(
                            {str(ref): self.features[str(ref)] for ref in refs}
                        )
            yield (
                plan.name,
                BaseCollection(features=collection, srid=self.srid)
                if with_name
                else BaseCollection(features=collection, srid=self.srid),
            )

    # def __iter__(self):
    #     return iter(self.root)

    # def __getitem__(self, item):
    #     return self.root[item]


class BaseFeature(BaseModel, GMLAdapter, CoretableAdapter, JsonFGAdapter):
    """Base class for application schema classes.

    It extends pydantic BaseModel with Feature-related helper methods as well as conversion capabilities from/to other formats via inheriting from respective adapter classes.
    """

    model_config = ConfigDict(defer_build=True, extra="forbid", from_attributes=True)

    # @computed_field
    # def featuretype(self) -> str:
    #     return self.__class__.get_name()

    @field_validator(
        "position",
        "geltungsbereich",
        "raeumlicherGeltungsbereich",
        "geltungsbereichAenderung",
        "extent",
        "geometry",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def _ensure_geometry(cls, v: Any) -> BaseModel | dict | None:
        """Attempts to convert invalid geometry types to a valid one by casting to its single or multi variant."""
        if isinstance(v, BaseFeature):
            v = v.model_dump()
        if not isinstance(v, dict):
            return v
        wkt = v["wkt"]
        if get_geometry_type_from_wkt(wkt) not in cls.get_geom_types():
            if not wkt.startswith("MULTI"):
                wkt = cast_geom_to_multi(wkt)
            else:
                wkt = cast_geom_to_single(wkt)
            v["wkt"] = wkt
        return v

    @field_validator("hatGenerAttribut", mode="before", check_fields=False)
    @classmethod
    def _validate_gener_att(cls, v: Any) -> list["BaseFeature"]:
        if isinstance(v, list):
            for i, item in enumerate(v):
                if not isinstance(item, dict):
                    continue
                if item.get("datatype", None):
                    v[i] = model_factory(item.pop("datatype"), cls.get_version())(
                        **item
                    )
                    continue
                match val := item.get("wert", None):
                    case int():
                        name = "Integer"
                    case float():
                        name = "Double"
                    case str():
                        if re.match("^[-+]?[0-9]+\\.[0-9]+$", val):
                            name = "Double"
                        elif re.match("^[-+]?[0-9]+$", val):
                            name = "Integer"
                        elif re.match(
                            "^https?:\\/\\/.*$",
                            val,
                        ):
                            name = "URL"
                        elif re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", val):
                            name = "Datum"
                        else:
                            name = "String"
                    case AnyUrl():
                        name = "URL"
                    case datetime.date():
                        name = "Datum"
                v[i] = model_factory(f"XP_{name}Attribut", cls.get_version())(**item)
        return v

    @field_validator("referenzURL", "georefURL", mode="before", check_fields=False)
    @classmethod
    def _validate_file_uri(cls, v: Any):
        if isinstance(v, str) and "://" not in v:
            return f"file:///{v}"
        return v

    @classmethod
    def get_name(cls) -> str:
        """Returns the canonical name of the FeatureClass."""
        return get_name(cls.__name__)

    @classmethod
    def get_geom_types(cls) -> list[Type["BaseFeature"]] | None:
        """Returns the types of the geometry attribute."""
        if geom_field := cls.get_geom_field():
            geom_annotation = cls.model_fields[geom_field].annotation
            args = get_args(geom_annotation)
            if not args:
                geom_model = [geom_annotation]
            else:
                geom_model = [arg for arg in args if arg is not NoneType]
            return geom_model

    @classmethod
    def get_version(cls) -> str:
        """Returns the application schema version of the object."""
        return f"{cls.__module__[-2:-1]}.{cls.__module__[-1:]}"

    @classmethod
    def get_data_type(cls) -> Literal["xplan", "xtrasse", "plu"]:
        """Return the data type."""
        # return re.match("xplan|plu|xtrasse", self.__module__)[0]
        # liefert bei input 'xplan_tools.model.appschema.xtrasse20'
        # den output 'xplan' statt 'xtrasse'
        return cls.__module__[:-2].split(".")[-1].split("_")[-1]

    @classmethod
    def get_property_info(cls, name: str) -> dict:
        """Property information.

        Returns a dict containing the following property information which might be useful e.g. for de-/serialization:

        - `stereotype`: the property's stereotype, e.g. DataType or Association
        - `typename`: the concrete type(s) of the property; may be an array, especially for associations
        - `list`: whether the property has a multiplicity > 1
        - `nullable`: whether the property is optional
        - `uom`: unit of measure for measure types
        - `enum_info`: names, aliases, description and, if available, tokens for codes from enumeration types
        - `assoc_info`: reverse properties and whether it's a source or a target end for associations

        Args:
            name: The property's name.

        Raises:
            AttributeError: The name was not found in the model fields.
        """
        try:
            field_info = cls.model_fields[name]
            extra_info = field_info.json_schema_extra or {}
        except KeyError:
            raise AttributeError(f"Unknown property: {name}")
        else:
            return {
                "stereotype": extra_info.get("stereotype", None),
                "typename": extra_info.get("typename", None),
                "list": get_origin(field_info.annotation) is list
                or list
                in [
                    arg.__origin__
                    for arg in get_args(field_info.annotation)
                    if getattr(arg, "__origin__", None)
                ],
                "nullable": NoneType in get_args(field_info.annotation),
                "uom": extra_info.get("uom", None),
                "enum_info": extra_info.get("enumDescription", None),
                "assoc_info": None
                if extra_info.get("stereotype", None) != "Association"
                else {
                    "reverse": extra_info.get("reverseProperty", None),
                    "source_or_target": extra_info.get("sourceOrTarget", None),
                },
            }

    @classmethod
    def get_associations(cls) -> list[str]:
        """Returns the classes association fields."""
        return [
            assoc
            for assoc in cls.model_fields.keys()
            if cls.get_property_info(assoc)["stereotype"] == "Association"
        ]

    @classmethod
    def get_geom_field(cls) -> Optional[str]:
        """Returns the classes geometry field name, if any."""
        if attr := {
            "position",
            "geltungsbereich",
            "raeumlicherGeltungsbereich",
            "geltungsbereichAenderung",
            "extent",
            "geometry",
        }.intersection(set(cls.model_fields.keys())):
            return attr.pop()

    @classmethod
    def get_properties(cls) -> BaseModel:
        """Returns a slimmed down model with just the properties, i.e. exluding id and geometry attributes as well as utility methods."""
        properties = {
            k: (v.annotation, v)
            for k, v in cls.model_fields.items()
            if k not in ["id", cls.get_geom_field()]
        }
        return create_model(cls.get_name(), **properties)

    # @model_validator(mode="after")
    # def validate_geom(self) -> "BaseFeature":
    #     """
    #     Performs basic geomety validation using GDAL/OGR regarding e.g. self-intersection or duplicate vertices.
    #     """

    #     if geom := self.get_geom_wkt():
    #         ogr_geom = ogr.CreateGeometryFromWkt(geom)
    #         if not ogr_geom:
    #             raise ValueError("Invalid WKT string")
    #         valid = ogr_geom.IsValid()
    #         ogr_geom = None
    #         if not valid:
    #             raise ValueError("Invalid geometry")
    #     return self

    @model_validator(mode="before")
    @classmethod
    def deserialization_hook(cls, data: Any, info: ValidationInfo) -> Any:
        """Provides deserialization for different formats/representations before validation."""
        if isinstance(data, _Element):
            data = cls._from_etree(data, info)
        elif isinstance(data, Feature):
            data = cls._from_coretable(data)
        elif isinstance(data, dict) and data.get("featureType", None):
            data = cls._from_jsonfg(data, info)
        return data

    @field_serializer("hatGenerAttribut", when_used="unless-none", check_fields=False)
    def _serialize_gener_att(
        self, v: list["BaseFeature"], info: SerializationInfo
    ) -> list[dict]:
        if (context := info.context) and context.get("datatype", False):
            return [
                {"name": item.name, "wert": item.wert, "datatype": item.get_name()}
                for item in v
            ]
        else:
            return [item.model_dump() for item in v]

    @field_serializer(
        "referenzURL", "georefURL", when_used="unless-none", check_fields=False
    )
    def _serialize_file_uri(self, v: AnyUrl, info: SerializationInfo) -> str:
        if (context := info.context) and context.get("file_uri", False):
            return str(v)
        else:
            return str(v).replace("file:///", "")

    def model_dump_gml(
        self,
        data_type: Literal["xplan", "xtrasse", "plu"] = "xplan",
        **kwargs,
    ) -> _Element:
        """Dumps the model data to a GML structure held in an etree.Element."""
        return self._to_etree(data_type, **kwargs)

    def model_dump_coretable(self) -> Feature:
        """Dumps the model data to a coretable Feature object to store in a database."""
        return self._to_coretable()

    def model_dump_jsonfg(
        self,
        **kwargs,
    ) -> dict:
        """Dumps the model data to a JSON-FG object."""
        return self._to_jsonfg(**kwargs)

    def get_geom_wkt(self) -> Optional[str]:
        """Returns the object's eWKT geometry's WKT representation withouth SRID, if any."""
        if geom_field := self.get_geom_field():
            if geom := getattr(self, geom_field, None):
                return geom.wkt

    def get_geom_srid(self) -> Optional[int]:
        """Returns the object's geometry's SRID, if any."""
        if geom_field := self.get_geom_field():
            if geom := getattr(self, geom_field, None):
                return geom.srid
