"""Module containing the GMLAdapter for reading from and writing to gml."""

import logging
from datetime import date, timedelta
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from lxml import etree
from osgeo import ogr, osr
from pandas import Timedelta
from pydantic import AnyUrl, ValidationInfo

from xplan_tools.model import model_factory
from xplan_tools.util import parse_srs, parse_uuid

logger = logging.getLogger(__name__)


class GMLAdapter:
    """Class to add GML transformation methods to XPlan pydantic model via inheritance."""

    def _to_etree(
        self,
        data_type: Literal["xplan", "xtrasse", "plu"] = "xplan",
        **kwargs,
    ) -> etree._Element:
        """Converts XPlan and INSPIRE PLU object to lxml etree Element."""

        def parse_property(name, value):
            gml_name = f"{{{ns}}}{name}" if ns else name

            if value is None or name == "id":
                return
            # Patch for vertikaleDifferenzierung being optional with a default value of False instead of None
            if name == "vertikaleDifferenzierung" and value is False:
                return
            elif name in [
                "levelOfSpatialPlan",
                "planTypeName",
                "processStepGeneral",
                "hilucsLandUse",
                "specificLandUse",
                "regulationNature",
                "supplementaryRegulation",
                "specificSupplementaryRegulation",
                "level",
            ]:
                etree.SubElement(
                    feature,
                    gml_name,
                    attrib={"{http://www.w3.org/1999/xlink}href": str(value)},
                )
            elif name == self.get_geom_field():
                geometry = ogr.CreateGeometryFromWkt(self.get_geom_wkt())
                if geometry:
                    if kwargs.get("feature_srs", True):
                        srid = osr.SpatialReference()
                        srid.ImportFromEPSG(int(self.get_geom_srid()))
                        geometry.AssignSpatialReference(srid)
                    etree.SubElement(feature, name).append(
                        etree.fromstring(
                            geometry.ExportToGML(
                                options=[
                                    "FORMAT=GML32",
                                    f"GMLID=GML_{uuid4()}",
                                    "SRSNAME_FORMAT=OGC_URL"
                                    if data_type == "plu"
                                    else "GML3_LONGSRS=NO",
                                    "NAMESPACE_DECL=YES",
                                ]
                            )
                        )
                    )
                    geometry = None
                    srid = None
            elif isinstance(
                value,
                model_factory("Measure", None, "def"),
            ):
                etree.SubElement(
                    feature, gml_name, attrib={"uom": value.uom}
                ).text = str(value.value)
            elif isinstance(
                value,
                model_factory("Length", None, "def"),
            ):
                etree.SubElement(
                    feature, gml_name, attrib={"uom": value.uom}
                ).text = str(value.value)
            elif isinstance(
                value,
                model_factory("VoidReasonValue", None, "def"),
            ):
                etree.SubElement(
                    feature,
                    gml_name,
                    attrib={
                        "nilReason": str(value.nilReason),
                        "{http://www.w3.org/2001/XMLSchema-instance}nil": "true",
                    },
                )
            elif isinstance(value, bool):
                etree.SubElement(feature, gml_name).text = str(value).lower()
            elif isinstance(value, (str, int, float)):
                etree.SubElement(feature, gml_name).text = str(value)
            elif isinstance(value, AnyUrl):
                etree.SubElement(feature, gml_name).text = str(value).replace(
                    "file:///", ""
                )
            elif isinstance(value, date) and (data_type in ["xplan", "xtrasse"]):
                etree.SubElement(feature, gml_name).text = str(value)
            elif isinstance(value, timedelta) and (data_type in ["xplan", "xtrasse"]):
                etree.SubElement(feature, gml_name).text = Timedelta(value).isoformat()
            elif isinstance(value, date) and (data_type == "plu"):
                etree.SubElement(feature, gml_name).text = str(value.isoformat())
            elif isinstance(value, Enum):
                etree.SubElement(feature, gml_name).text = value.value
            elif isinstance(value, UUID):
                etree.SubElement(
                    feature,
                    gml_name,
                    attrib={"{http://www.w3.org/1999/xlink}href": f"#GML_{str(value)}"},
                )
            else:
                etree.SubElement(feature, gml_name).append(value._to_etree(data_type))

        application_schema_mapping = {
            "Identifier": "http://inspire.ec.europa.eu/schemas/base/3.3",
            "SpatialDataSet": "http://inspire.ec.europa.eu/schemas/base/3.3",
            "ConditionOfFacilityValue": "https://inspire.ec.europa.eu/schemas/tn/4.0",
            "VerticalPositionValue": "https://inspire.ec.europa.eu/schemas/tn/4.0",
            "Contact": "http://inspire.ec.europa.eu/schemas/base2/2.0",
            "OfficialJournalInformation": "http://inspire.ec.europa.eu/schemas/base2/2.0",
            "RelatedParty": "http://inspire.ec.europa.eu/schemas/base2/2.0",
            "ThematicIdentifier": "http://inspire.ec.europa.eu/schemas/base2/2.0",
            "HILUCSPercentage": "http://inspire.ec.europa.eu/schemas/lunom/4.0",
            "SpecificPercentage": "http://inspire.ec.europa.eu/schemas/lunom/4.0",
            "CIDate": "http://www.isotc211.org/2005/gmd",
            "DocumentCitation": "http://inspire.ec.europa.eu/schemas/base2/2.0",
            "LegislationCitation": "http://inspire.ec.europa.eu/schemas/base2/2.0",
        }
        ns = application_schema_mapping.get(self.get_name(), "")

        if self.get_name() == "CIDate":
            ci_date = etree.Element(f"{{{ns}}}CI_Date")
            etree.SubElement(
                etree.SubElement(ci_date, "{http://www.isotc211.org/2005/gmd}date"),
                "{http://www.isotc211.org/2005/gco}Date",
            ).text = str(self.date)
            etree.SubElement(
                etree.SubElement(ci_date, "{http://www.isotc211.org/2005/gmd}dateType"),
                "{http://www.isotc211.org/2005/gmd}CI_DateTypeCode",
                attrib={
                    "codeList": "https://standards.iso.org/iso/19139/resources/gmxCodelists.xml#CI_DateTypeCode",
                    "codeListValue": "creation",
                },
            )
            return ci_date

        feature = etree.Element(f"{{{ns}}}{self.get_name()}")

        if getattr(self, "id", None):
            feature.set("{http://www.opengis.net/gml/3.2}id", f"GML_{self.id}")
        for name, value in self:
            if isinstance(value, list):
                for item in value:
                    parse_property(name, item)
            else:
                parse_property(name, value)
        return feature

    @classmethod
    def _from_etree(cls, feature: etree._Element, info: ValidationInfo) -> dict:
        """Creates a XPlan object instance from a lxml etree Element."""
        data_type = info.context.get("data_type")
        data = {}
        id = feature.get("{http://www.opengis.net/gml/3.2}id")
        properties = None

        if id:
            data["id"] = parse_uuid(id, raise_exception=True)

            gml_geometry = feature.xpath(
                "./*[namespace-uri() != 'http://www.opengis.net/gml/3.2']/*[namespace-uri() = 'http://www.opengis.net/gml/3.2']"
            )

            if gml_geometry:
                ogr_geometry = (
                    ogr.CreateGeometryFromGML(
                        etree.tostring(gml_geometry[0], encoding="unicode")
                    )
                    if len(gml_geometry) > 0
                    else None
                )
                if ogr_geometry:
                    try:
                        if srs := gml_geometry[0].get("srsName", None):
                            srid = parse_srs(srs)
                        else:
                            srid = info.context.get("srid")
                        data[cls.get_geom_field()] = {
                            "srid": srid,
                            "wkt": ogr_geometry.ExportToWkt(),
                        }

                    except Exception:
                        raise ValueError("SRID could not be determined")

            properties = feature.xpath(
                "./*[namespace-uri() != 'http://www.opengis.net/gml/3.2' and not(namespace-uri(./*) = 'http://www.opengis.net/gml/3.2')]"
            )

        else:
            properties = list(feature)

        for property in properties:
            if (
                (not property.text or property.text.strip() == "")
                and not property.attrib
                and not len(property)
            ):
                continue

            name = etree.QName(property).localname
            prop_info = cls.get_property_info(name)
            value = None
            if list(property):  # Test for child elements -> data type
                value = model_factory(
                    etree.QName(property[0]).localname, cls.__module__[-2:], data_type
                )._from_etree(property[0], info)
            elif (
                id
                and (href := property.get("{http://www.w3.org/1999/xlink}href"))
                and href.startswith("#")
            ):
                value = parse_uuid(href, raise_exception=True)
            elif uom := property.get("uom"):
                value = {"value": property.text, "uom": uom}
            # elif (
            #     re.search(
            #         r"^.*\.[a-zA-Z]{3,4}$",
            #         property.text,
            #     )
            #     and "://" not in property.text
            # ):
            #     value = f"file://{property.text}"
            elif prop_info["stereotype"] == "Codelist":
                if codespace := property.get("codeSpace"):
                    value = (
                        codespace if codespace[-1] == "/" else codespace + "/"
                    ) + property.text
                    if not codespace.startswith("http"):
                        value = "http://" + value
                elif property.text.startswith("http"):
                    value = property.text
                else:
                    value = f"https://registry.gdi-de.org/codelist/de.xleitstelle.xplanung/{prop_info['typename']}/{property.text}"
            else:
                value = property.text

            if prop_info["list"]:
                data.setdefault(name, []).append(value)
            else:
                data[name] = value
        return data
