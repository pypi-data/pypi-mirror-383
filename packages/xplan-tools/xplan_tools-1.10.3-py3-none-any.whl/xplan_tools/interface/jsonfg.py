"""Module containing the class for extracting plans from and writing to JSON-FG datasources."""

import io
import logging
import re
from typing import IO, Literal
from uuid import uuid4

from pydantic_core import from_json, to_json

from xplan_tools.model import model_factory
from xplan_tools.model.base import BaseCollection
from xplan_tools.util import parse_srs, parse_uuid

from .base import BaseRepository

logger = logging.getLogger(__name__)


class JsonFGRepository(BaseRepository):
    """Repository class for loading from and writing to JSON-FG files or file-like objects."""

    def __init__(
        self,
        datasource: str | IO = "",
        version: str | None = None,
        data_type: Literal["xplan", "xtrasse", "plu"] = "xplan",
    ) -> None:
        """Initializes the JSON-FG Repository.

        Args:
            datasource: A file path as a String or a file-like object.
            version: If no explicit version is provided it is attempted to derive the version from the links object if its "rel" is "describedBy".
        """
        self.datasource = datasource
        self.data_type = data_type
        self.version = self._get_version() if version is None else version

    @property
    def content(self):
        """The JSON data as a dict."""
        if not hasattr(self, "_content") or self._content is None:
            try:
                match self.datasource:
                    case io.BytesIO() | io.StringIO():
                        self._content = from_json(self.datasource.getvalue())
                    case str():
                        with open(self.datasource, "r") as f:
                            self._content = from_json(f.read())
                    case _:
                        raise NotImplementedError("Unsupported datasource.")
            except Exception:
                logger.exception("Failed parsing datasource.")
                self._content = None
        return self._content

    def _write_to_datasource(self, collection: dict):
        match self.datasource:
            case io.StringIO():
                return self.datasource.write(
                    to_json(
                        collection,
                        indent=4,
                    ).decode()
                )
            case io.BytesIO():
                return self.datasource.write(
                    to_json(
                        collection,
                        indent=4,
                    )
                )
            case str():
                with open(self.datasource, "wb") as f:
                    f.write(
                        to_json(
                            collection,
                            indent=4,
                        )
                    )
            case _:
                raise NotImplementedError("Unsupported datasource.")

    def _get_version(self):
        try:
            uri = [
                link["href"]
                for link in self.content["links"]
                if link["rel"] == "describedby"
            ][0]
        except Exception:
            raise ValueError("JSON Schema not found in links")
        if self.data_type == "xtrasse":
            return "2.0"
        return re.search(r"(.*\/)(\d.\d)(\/.*)", uri).group(2)

    def _collection_template(self, srid: int, featuretype: str | None = None):
        template = {
            "type": "FeatureCollection",
            "featureType": featuretype,
            "coordRefSys": f"http://www.opengis.net/def/crs/EPSG/0/{srid}",
            "features": [],
            "links": [
                {
                    "href": "https://gitlab.opencode.de/xleitstelle/xtrasse/spezifikation/-/blob/main/json/featurecollection.json"
                    if self.data_type == "xtrasse"
                    else f"https://gitlab.opencode.de/xleitstelle/xplanung/schemas/json/-/raw/main/{self.version}/featurecollection.json",
                    "rel": "describedby",
                    "type": "application/schema+json",
                    "title": "JSON Schema of this document",
                }
            ],
        }
        if not featuretype:
            template.pop("featureType")
        return template

    def save_all(self, features: BaseCollection, **kwargs: dict) -> None:
        """Saves a Feature Collection to the datasource.

        Args:
            features: A BaseCollection instance.
            **kwargs: Keyword arguments to pass on to [`model_dump_jsonfg()`][xplan_tools.model.base.BaseFeature.model_dump_jsonfg].
        """
        if kwargs.get("single_collection", True):
            collection = self._collection_template(srid=features.srid)
            collection["features"].extend(
                feature.model_dump_jsonfg(**kwargs)
                for feature in features.get_features()
                if feature
            )
            self._write_to_datasource(collection)
        else:
            featuretypes = {}
            for feature in features.features.values():
                featuretypes.setdefault(feature.get_name(), []).append(feature)
            for featuretype, features in featuretypes.items():
                collection = self._collection_template(
                    srid=features.srid, featuretype=featuretype
                )
                collection["features"].extend(
                    feature.model_dump_jsonfg(**kwargs, write_featuretype=False)
                    for feature in features
                )
                self._write_to_datasource(collection)

    def get_all(self, **kwargs: dict) -> BaseCollection:
        """Retrieves a Feature Collection to the datasource.

        Args:
            **kwargs: Not used in this repository.
        """

        def update_related_features():
            for feature in self.content["features"]:
                model = model_factory(
                    feature["featureType"], self.version, self.data_type
                )
                assoc = model.get_associations()
                for k, v in feature["properties"].items():
                    if k in assoc:
                        if isinstance(v, list):
                            for i, item in enumerate(v):
                                if isinstance(item, str) and (
                                    new_id := id_mapping.get(item, None)
                                ):
                                    feature["properties"][k][i] = new_id
                        elif isinstance(v, str) and (new_id := id_mapping.get(v, None)):
                            feature["properties"][k] = new_id

        srid = parse_srs(self.content.get("coordRefSys", None))
        collection = {}
        id_mapping = {}

        for feature in self.content["features"]:
            feature_id = feature["id"]
            if not parse_uuid(feature_id, exact=True):
                new_id = str(uuid4())
                feature["id"] = new_id
                id_mapping[feature_id] = new_id
                logger.info(
                    f"Feature ID '{feature_id}' replaced with UUIDv4 '{new_id}'"
                )

        if id_mapping:
            update_related_features()

        for feature in self.content["features"]:
            if not srid:
                srid = parse_srs(feature.get("coordRefSys", "EPSG:4326"))
            model = model_factory(
                feature["featureType"], self.version, self.data_type
            ).model_validate(
                feature, context={"srid": srid, "data_type": self.data_type}
            )
            collection[model.id] = model
        return BaseCollection(features=collection, srid=srid)
