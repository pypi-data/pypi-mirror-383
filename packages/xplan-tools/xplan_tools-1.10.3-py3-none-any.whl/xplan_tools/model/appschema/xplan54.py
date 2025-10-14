# generated from JSON Schema

from __future__ import annotations

from datetime import date as date_aliased
from datetime import timedelta
from typing import Annotated, Any, ClassVar, Literal
from uuid import UUID

from pydantic import AnyUrl, Field, RootModel

from ..base import BaseFeature
from . import definitions


class Model(RootModel[Any]):
    root: Any


class BPEmissionskontingentLaerm(BaseFeature):
    """
    Lärmemissionskontingent eines Teilgebietes nach DIN 45691, Abschnitt 4.6
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ekwertTag: Annotated[
        definitions.GenericMeasure,
        Field(
            description="Emissionskontingent Tag in db",
            json_schema_extra={
                "typename": "Measure",
                "stereotype": "Measure",
                "multiplicity": "1",
                "uom": "db",
            },
        ),
    ]
    ekwertNacht: Annotated[
        definitions.GenericMeasure,
        Field(
            description="Emissionskontingent Nacht in db",
            json_schema_extra={
                "typename": "Measure",
                "stereotype": "Measure",
                "multiplicity": "1",
                "uom": "db",
            },
        ),
    ]
    erlaeuterung: Annotated[
        str | None,
        Field(
            description="Erläuterung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPEmissionskontingentLaermGebiet(BPEmissionskontingentLaerm):
    """
    Lärmemissionskontingent eines Teilgebietes, das einem bestimmten Immissionsgebiet außerhalb des Geltungsbereiches des BPlans zugeordnet ist (Anhang A4 von DIN 45691).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    gebietsbezeichnung: Annotated[
        str,
        Field(
            description="Bezeichnung des Immissionsgebietes",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class BPRichtungssektor(BaseFeature):
    """
    Spezifikation von Zusatzkontingenten Tag/Nacht der Lärmemission für einen Richtungssektor
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    winkelAnfang: Annotated[
        definitions.Angle,
        Field(
            description="Startwinkel des Emissionssektors",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "1",
                "uom": "grad",
            },
        ),
    ]
    winkelEnde: Annotated[
        definitions.Angle,
        Field(
            description="Endwinkel des Emissionssektors",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "1",
                "uom": "grad",
            },
        ),
    ]
    zkWertTag: Annotated[
        definitions.GenericMeasure,
        Field(
            description="Zusatzkontingent Tag",
            json_schema_extra={
                "typename": "Measure",
                "stereotype": "Measure",
                "multiplicity": "1",
                "uom": "db",
            },
        ),
    ]
    zkWertNacht: Annotated[
        definitions.GenericMeasure,
        Field(
            description="Zusatzkontingent Nacht",
            json_schema_extra={
                "typename": "Measure",
                "stereotype": "Measure",
                "multiplicity": "1",
                "uom": "db",
            },
        ),
    ]


class XPDatumAttribut(BaseFeature):
    """
    Generische Attribute vom Datentyp "Datum"
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    name: Annotated[
        str,
        Field(
            description="Name des Generischen Attributs",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    wert: Annotated[
        date_aliased,
        Field(
            description="Attributwert",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "1",
            },
        ),
    ]


class XPDoubleAttribut(BaseFeature):
    """
    Generisches Attribut vom Datentyp "Double".
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    name: Annotated[
        str,
        Field(
            description="Name des Generischen Attributs",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    wert: Annotated[
        float,
        Field(
            description="Attributwert",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class XPGemeinde(BaseFeature):
    """
    Spezifikation einer für die Aufstellung des Plans zuständigen Gemeinde.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ags: Annotated[
        str | None,
        Field(
            description="Amtlicher Gemeindeschlüssel (früher Gemeinde-Kennziffer)",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rs: Annotated[
        str | None,
        Field(
            description="Regionalschlüssel",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gemeindeName: Annotated[
        str | None,
        Field(
            description="Name der Gemeinde.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ortsteilName: Annotated[
        str | None,
        Field(
            description="Name des Ortsteils",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPHoehenangabe(BaseFeature):
    """
    Spezifikation einer Angabe zur vertikalen Höhe oder zu einem Bereich vertikaler Höhen. Es ist möglich, spezifische Höhenangaben (z.B. die First- oder Traufhöhe eines Gebäudes) vorzugeben oder einzuschränken, oder den Gültigkeitsbereich eines Planinhalts auf eine bestimmte Höhe (hZwingend) bzw. einen Höhenbereich (hMin - hMax) zu beschränken, was vor allem bei der höhenabhängigen Festsetzung einer überbaubaren Grundstücksfläche (BP_UeberbaubareGrundstuecksflaeche), einer Baulinie (BP_Baulinie) oder einer Baugrenze (BP_Baugrenze) relevant ist. In diesem Fall bleiben die Attribute bezugspunkt und abweichenderBezugspunkt unbelegt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    abweichenderHoehenbezug: Annotated[
        str | None,
        Field(
            description='Textuelle Spezifikation des Höhenbezuges wenn das Attribut "hoehenbezug" nicht belegt ist.',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    hoehenbezug: Annotated[
        Literal["1000", "1100", "1200", "2000", "2500", "3000", "3500"] | None,
        Field(
            description="Art des Höhenbezuges.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "absolutNHN",
                        "description": "Absolute Höhenangabe im Bezugssystem NHN",
                    },
                    "1100": {
                        "name": "absolutNN",
                        "description": "Absolute Höhenangabe im Bezugssystem NN",
                    },
                    "1200": {
                        "name": "absolutDHHN",
                        "description": "Absolute Höhenangabe im Bezugssystem DHHN",
                    },
                    "2000": {
                        "name": "relativGelaendeoberkante",
                        "description": "Höhenangabe relativ zur Geländeoberkante an der Position des Planinhalts.",
                    },
                    "2500": {
                        "name": "relativGehwegOberkante",
                        "description": "Höhenangabe relativ zur Gehweg-Oberkante an der Position des Planinhalts.",
                    },
                    "3000": {
                        "name": "relativBezugshoehe",
                        "description": "Höhenangabe relativ zu der auf Planebene festgelegten absoluten Bezugshöhe (Attribut bezugshoehe von XP_Plan).",
                    },
                    "3500": {
                        "name": "relativStrasse",
                        "description": "Höhenangabe relativ zur Strassenoberkante an der Position des Planinhalts",
                    },
                },
                "typename": "XP_ArtHoehenbezug",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    abweichenderBezugspunkt: Annotated[
        str | None,
        Field(
            description='Textuelle Spezifikation eines Höhenbezugspunktes wenn das Attribut "bezugspunkt" nicht belegt ist.',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bezugspunkt: Annotated[
        Literal[
            "1000",
            "2000",
            "3000",
            "3500",
            "4000",
            "4500",
            "5000",
            "5500",
            "6000",
            "6500",
            "6600",
        ]
        | None,
        Field(
            description='Bestimmung des Bezugspunktes der Höhenangaben. Wenn weder dies Attribut noch das Attribut "abweichenderBezugspunkt" belegt sind, soll die Höhenangabe als vertikale Einschränkung des zugeordneten Planinhalts interpretiert werden.',
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "TH",
                        "description": "Traufhöhe als Höhenbezugspunkt",
                    },
                    "2000": {
                        "name": "FH",
                        "description": "Firsthöhe als Höhenbezugspunkt.",
                    },
                    "3000": {
                        "name": "OK",
                        "description": "Oberkante als Höhenbezugspunkt.",
                    },
                    "3500": {"name": "LH", "description": "Lichte Höhe"},
                    "4000": {"name": "SH", "description": "Sockelhöhe"},
                    "4500": {"name": "EFH", "description": "Erdgeschoss Fußbodenhöhe"},
                    "5000": {"name": "HBA", "description": "Höhe Baulicher Anlagen"},
                    "5500": {"name": "UK", "description": "Unterkante"},
                    "6000": {"name": "GBH", "description": "Gebäudehöhe"},
                    "6500": {"name": "WH", "description": "Wandhöhe"},
                    "6600": {"name": "GOK", "description": "Geländeoberkante"},
                },
                "typename": "XP_ArtHoehenbezugspunkt",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    hMin: Annotated[
        definitions.Length | None,
        Field(
            description='Minimal zulässige Höhe des Bezugspunktes (bezugspunkt) bei einer Bereichsangabe, bzw. untere Grenze des vertikalen Gültigkeitsbereiches eines Planinhalts, wenn "bezugspunkt" nicht belegt ist. In diesem Fall gilt: Ist  "hMax" nicht belegt, gilt die Festlegung ab der Höhe "hMin".',
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    hMax: Annotated[
        definitions.Length | None,
        Field(
            description='Maximal zulässige Höhe des Bezugspunktes (bezugspunkt) bei einer Bereichsangabe, bzw. obere Grenze des vertikalen Gültigkeitsbereiches eines Planinhalts, wenn "bezugspunkt" nicht belegt ist.  In diesem Fall gilt: Ist  "hMin" nicht belegt, gilt die Festlegung bis zur Höhe "hMax".',
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    hZwingend: Annotated[
        definitions.Length | None,
        Field(
            description="Zwingend einzuhaltende Höhe des Bezugspunktes (bezugspunkt) , bzw. Beschränkung der vertikalen Gültigkeitsbereiches eines Planinhalts auf eine bestimmte Höhe.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    h: Annotated[
        definitions.Length | None,
        Field(
            description="Maximal zulässige Höhe des Bezugspunktes (bezugspunkt) .",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None


class XPIntegerAttribut(BaseFeature):
    """
    Generische Attribute vom Datentyp "Integer".
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    name: Annotated[
        str,
        Field(
            description="Name des Generischen Attributs",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    wert: Annotated[
        int,
        Field(
            description="Attributwert",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class XPPlangeber(BaseFeature):
    """
    Spezifikation der Institution, die für den Plan verantwortlich ist.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    name: Annotated[
        str,
        Field(
            description="Name des Plangebers.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    kennziffer: Annotated[
        str | None,
        Field(
            description="Kennziffer des Plangebers.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPStringAttribut(BaseFeature):
    """
    Generisches Attribut vom Datentyp "CharacterString"
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    name: Annotated[
        str,
        Field(
            description="Name des Generischen Attributs",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    wert: Annotated[
        str,
        Field(
            description="Attributwert",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class XPURLAttribut(BaseFeature):
    """
    Generische Attribute vom Datentyp "URL"
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    name: Annotated[
        str,
        Field(
            description="Name des Generischen Attributs",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    wert: Annotated[
        AnyUrl,
        Field(
            description="Attributwert",
            json_schema_extra={
                "typename": "URI",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class XPVerbundenerPlan(BaseFeature):
    """
    Spezifikation eines anderen Plans, der mit dem Ausgangsplan verbunden ist und diesen ändert bzw. von ihm geändert wird.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    planName: Annotated[
        str | None,
        Field(
            description='Name (Attribut "name" von XP_Plan) des verbundenen Plans.',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rechtscharakter: Annotated[
        Literal["1000", "1100", "2000", "20000", "20001"],
        Field(
            description="Rechtscharakter der Planänderung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Aenderung",
                        "description": "Änderung eines Planes: Der Geltungsbereich des neueren Plans überdeckt nicht den gesamten Geltungsbereich des Ausgangsplans. Im Überlappungsbereich gilt das neuere Planrecht.",
                    },
                    "1100": {
                        "name": "Ergaenzung",
                        "description": "Ergänzung eines Plans: Die Inhalte des neuen Plans ergänzen die alten Inhalte, z.B. durch zusätzliche textliche Planinhalte oder Überlagerungsobjekte. Die Inhalte des älteren Plans bleiben aber gültig.",
                    },
                    "2000": {
                        "name": "Aufhebung",
                        "description": "Aufhebung des Plans: Der Geltungsbereich des neuen Plans überdeckt den alten Plan, und die Inhalte des neuen Plans ersetzen die alten Inhalte  vollständig.",
                    },
                    "20000": {
                        "name": "Aufhebungsverfahren",
                        "description": "Das altes Planrecht wurde durch ein förmliches Verfahren aufgehoben",
                    },
                    "20001": {
                        "name": "Ueberplanung",
                        "description": "Der alte Plan tritt ohne förmliches Verfahren außer Kraft",
                    },
                },
                "typename": "XP_RechtscharakterPlanaenderung",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    nummer: Annotated[
        str | None,
        Field(
            description='Nummer (Attribut "nummer" von XP_Plan) des verbundenen Plans',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    verbundenerPlan: Annotated[
        AnyUrl | UUID | None,
        Field(
            description="Referenz auf einen anderen Plan, der den aktuellen Plan ändert oder von ihm geändert wird.",
            json_schema_extra={
                "typename": ["BP_Plan", "FP_Plan", "LP_Plan", "RP_Plan", "SO_Plan"],
                "stereotype": "Association",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPVerfahrensMerkmal(BaseFeature):
    """
    Vermerk eines am Planungsverfahrens beteiligten Akteurs.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    vermerk: Annotated[
        str,
        Field(
            description="Inhalt des Vermerks.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    datum: Annotated[
        date_aliased,
        Field(
            description="Datum des Vermerks",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "1",
            },
        ),
    ]
    signatur: Annotated[
        str,
        Field(
            description="Unterschrift",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    signiert: Annotated[
        bool,
        Field(
            description="Angabe, ob die Unterschrift erfolgt ist.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class XPWirksamkeitBedingung(BaseFeature):
    """
    Spezifikation von Bedingungen für die Wirksamkeit oder Unwirksamkeit einer Festsetzung.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    bedingung: Annotated[
        str | None,
        Field(
            description="Textlich formulierte Bedingung für die Wirksamkeit oder Unwirksamkeit einer Festsetzung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    datumAbsolut: Annotated[
        date_aliased | None,
        Field(
            description="Datum an dem eine Festsetzung wirksam oder unwirksam wird.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    datumRelativ: Annotated[
        timedelta | None,
        Field(
            description="Zeitspanne, nach der eine Festsetzung wirksam oder unwirksam wird, wenn die im Attribut bedingung spezifizierte Bedingung erfüllt ist.",
            json_schema_extra={
                "typename": "TM_Duration",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPDachgestaltung(BaseFeature):
    """
    Zusammenfassung von Parametern zur Festlegung der zulässigen Dachformen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    DNmin: Annotated[
        definitions.Angle | None,
        Field(
            description="Minimale Dachneigung bei  einer Bereichsangabe. Das Attribut DNmax muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNmax: Annotated[
        definitions.Angle | None,
        Field(
            description="Maximale Dachneigung bei  einer Bereichsangabe. Das Attribut DNmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DN: Annotated[
        definitions.Angle | None,
        Field(
            description="Maximal zulässige Dachneigung",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNzwingend: Annotated[
        definitions.Angle | None,
        Field(
            description="Zwingend vorgeschriebene Dachneigung",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    dachform: Annotated[
        Literal[
            "1000",
            "2100",
            "2200",
            "3000",
            "3100",
            "3200",
            "3300",
            "3400",
            "3500",
            "3600",
            "3700",
            "3800",
            "3900",
            "4000",
            "4100",
            "5000",
            "9999",
        ]
        | None,
        Field(
            description="Erlaubte Dachform",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Flachdach",
                        "description": "Flachdach\r\nEmpfohlene Abkürzung: FD",
                    },
                    "2100": {
                        "name": "Pultdach",
                        "description": "Pultdach\r\nEmpfohlene Abkürzung: PD",
                    },
                    "2200": {
                        "name": "VersetztesPultdach",
                        "description": "Versetztes Pultdach\r\nEmpfohlene Abkürzung: VPD",
                    },
                    "3000": {
                        "name": "GeneigtesDach",
                        "description": "Kein Flachdach\r\nEmpfohlene Abkürzung: GD",
                    },
                    "3100": {
                        "name": "Satteldach",
                        "description": "Satteldach\r\nEmpfohlene Abkürzung: SD",
                    },
                    "3200": {
                        "name": "Walmdach",
                        "description": "Walmdach\r\nEmpfohlene Abkürzung: WD",
                    },
                    "3300": {
                        "name": "Krueppelwalmdach",
                        "description": "Krüppelwalmdach\r\nEmpfohlene Abkürzung: KWD",
                    },
                    "3400": {
                        "name": "Mansarddach",
                        "description": "Mansardendach\r\nEmpfohlene Abkürzung: MD",
                    },
                    "3500": {
                        "name": "Zeltdach",
                        "description": "Zeltdach\r\nEmpfohlene Abkürzung: ZD",
                    },
                    "3600": {
                        "name": "Kegeldach",
                        "description": "Kegeldach\r\nEmpfohlene Abkürzung: KeD",
                    },
                    "3700": {
                        "name": "Kuppeldach",
                        "description": "Kuppeldach\r\nEmpfohlene Abkürzung: KuD",
                    },
                    "3800": {
                        "name": "Sheddach",
                        "description": "Sheddach\r\nEmpfohlene Abkürzung: ShD",
                    },
                    "3900": {
                        "name": "Bogendach",
                        "description": "Bogendach\r\nEmpfohlene Abkürzung: BD",
                    },
                    "4000": {
                        "name": "Turmdach",
                        "description": "Turmdach\r\nEmpfohlene Abkürzung: TuD",
                    },
                    "4100": {
                        "name": "Tonnendach",
                        "description": "Tonnendach\r\nEmpfohlene Abkürzung: ToD",
                    },
                    "5000": {
                        "name": "Mischform",
                        "description": "Gemischte Dachform\r\nEmpfohlene Abkürzung: GDF",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Dachform\r\nEmpfohlene Abkürzung: SDF",
                    },
                },
                "typename": "BP_Dachform",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detaillierteDachform: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definiertere detailliertere Dachform.",
            json_schema_extra={
                "typename": "BP_DetailDachform",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPAbstraktesPraesentationsobjekt(BaseFeature):
    """
    Abstrakte Basisklasse für alle Präsentationsobjekte. Die Attribute entsprechen dem ALKIS-Objekt AP_GPO, wobei das Attribut "signaturnummer" in stylesheetId umbenannt wurde. Bei freien Präsentationsobjekten ist die Relation "dientZurDarstellungVon" unbelegt, bei gebundenen Präsentationsobjekten zeigt die Relation auf ein von XP_Objekt abgeleitetes Fachobjekt.
    Freie Präsentationsobjekte dürfen ausschließlich zur graphischen Annotation eines Plans verwendet werden
    Gebundene Präsentationsobjekte mit Raumbezug dienen ausschließlich dazu, Attributwerte des verbundenen Fachobjekts im Plan darzustellen. Die Namen der darzustellenden Fachobjekt-Attribute werden über das Attribut "art" spezifiziert. Bei mehrfach belegbaren Attributen in Fachobjekten gibt index die Position des Attributwertes an, auf den sich das Präsentationsobjekt bezieht.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    id: str | None = None
    stylesheetId: Annotated[
        AnyUrl | None,
        Field(
            description='Das Attribut "stylesheetId" zeigt auf ein extern definierte Stylesheet, das Parameter zur Visualisierung von Flächen, Linien, Punkten und Texten enthält. Jedem Stylesheet ist weiterhin eine Darstellungspriorität zugeordnet. Außerdem kann ein Stylesheet logische Elemente enthalten,  die die Visualisierung abhängig machen vom Wert des durch "art" definierten Attributes des Fachobjektes, das durch die Relation "dientZurDarstellungVon" referiert wird.',
            json_schema_extra={
                "typename": "XP_StylesheetListe",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    darstellungsprioritaet: Annotated[
        int | None,
        Field(
            description="Enthält die Darstellungspriorität für Elemente der Signatur. Eine vom Standardwert abweichende Priorität wird über dieses Attribut definiert und nicht über eine neue Signatur.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    art: Annotated[
        list[str] | None,
        Field(
            description='"art" gibt die Namen der Attribute an, die mit dem Präsentationsobjekt dargestellt werden sollen. Dabei ist beim Verweis auf komplexe Attribute des Fachobjekts die Xpath-Syntax zu verwenden. Wenn das zugehörige Attribut oder Sub-Attribut des Fachobjekts mehrfach belegt ist, sollte die []-Syntax zur Spezifikation des zugehörigen Instanz-Attributs benutzt werden. \r\n\r\nDas Attribut \'art\' darf nur bei "Freien Präsentationsobjekten" (dientZurDarstellungVon = NULL) nicht belegt sein.',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    index: Annotated[
        list[int] | None,
        Field(
            description='Wenn das Attribut, das vom Inhalt des Attributs "art“ bezeichnet wird, im Fachobjekt mehrfach belegt ist gibt "index" an, auf welche Instanz des Attributs sich das Präsentationsobjekt bezieht. Indexnummern beginnen dabei immer mit 0.\r\n\r\nDies Attribut ist als "veraltet" gekennzeichnet und wird in Version 6.0 voraussichtlich wegfallen. Alternativ sollte im Attribut "art" die XPath-Syntax benutzt werden.',
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    gehoertZuBereich: Annotated[
        AnyUrl | UUID | None,
        Field(
            description="Referenz auf den Bereich, zu dem das Präsentationsobjekt gehört.",
            json_schema_extra={
                "typename": [
                    "BP_Bereich",
                    "FP_Bereich",
                    "LP_Bereich",
                    "RP_Bereich",
                    "SO_Bereich",
                ],
                "stereotype": "Association",
                "reverseProperty": "praesentationsobjekt",
                "sourceOrTarget": "source",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    dientZurDarstellungVon: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Verweis auf das Fachobjekt, deren Plandarstellung durch das Präsentationsobjekt unterstützt werden soll.",
            json_schema_extra={
                "typename": [
                    "BP_AbgrabungsFlaeche",
                    "BP_AbstandsFlaeche",
                    "BP_AbstandsMass",
                    "BP_AbweichungVonBaugrenze",
                    "BP_AbweichungVonUeberbaubererGrundstuecksFlaeche",
                    "BP_AnpflanzungBindungErhaltung",
                    "BP_AufschuettungsFlaeche",
                    "BP_AusgleichsFlaeche",
                    "BP_AusgleichsMassnahme",
                    "BP_BauGrenze",
                    "BP_BauLinie",
                    "BP_BaugebietsTeilFlaeche",
                    "BP_BereichOhneEinAusfahrtLinie",
                    "BP_BesondererNutzungszweckFlaeche",
                    "BP_BodenschaetzeFlaeche",
                    "BP_EinfahrtPunkt",
                    "BP_EinfahrtsbereichLinie",
                    "BP_EingriffsBereich",
                    "BP_ErhaltungsBereichFlaeche",
                    "BP_FestsetzungNachLandesrecht",
                    "BP_FirstRichtungsLinie",
                    "BP_FlaecheOhneFestsetzung",
                    "BP_FoerderungsFlaeche",
                    "BP_FreiFlaeche",
                    "BP_GebaeudeFlaeche",
                    "BP_GemeinbedarfsFlaeche",
                    "BP_GemeinschaftsanlagenFlaeche",
                    "BP_GemeinschaftsanlagenZuordnung",
                    "BP_GenerischesObjekt",
                    "BP_GewaesserFlaeche",
                    "BP_GruenFlaeche",
                    "BP_HoehenMass",
                    "BP_Immissionsschutz",
                    "BP_KennzeichnungsFlaeche",
                    "BP_KleintierhaltungFlaeche",
                    "BP_Landwirtschaft",
                    "BP_LandwirtschaftsFlaeche",
                    "BP_NebenanlagenAusschlussFlaeche",
                    "BP_NebenanlagenFlaeche",
                    "BP_NichtUeberbaubareGrundstuecksflaeche",
                    "BP_NutzungsartenGrenze",
                    "BP_PersGruppenBestimmteFlaeche",
                    "BP_RegelungVergnuegungsstaetten",
                    "BP_RekultivierungsFlaeche",
                    "BP_RichtungssektorGrenze",
                    "BP_SchutzPflegeEntwicklungsFlaeche",
                    "BP_SchutzPflegeEntwicklungsMassnahme",
                    "BP_Sichtflaeche",
                    "BP_SpezielleBauweise",
                    "BP_SpielSportanlagenFlaeche",
                    "BP_StrassenVerkehrsFlaeche",
                    "BP_StrassenbegrenzungsLinie",
                    "BP_Strassenkoerper",
                    "BP_TechnischeMassnahmenFlaeche",
                    "BP_TextlicheFestsetzungsFlaeche",
                    "BP_UeberbaubareGrundstuecksFlaeche",
                    "BP_UnverbindlicheVormerkung",
                    "BP_VerEntsorgung",
                    "BP_Veraenderungssperre",
                    "BP_VerkehrsflaecheBesondererZweckbestimmung",
                    "BP_WaldFlaeche",
                    "BP_WasserwirtschaftsFlaeche",
                    "BP_Wegerecht",
                    "BP_WohngebaeudeFlaeche",
                    "BP_ZentralerVersorgungsbereich",
                    "BP_ZusatzkontingentLaerm",
                    "BP_ZusatzkontingentLaermFlaeche",
                    "FP_Abgrabung",
                    "FP_AnpassungKlimawandel",
                    "FP_Aufschuettung",
                    "FP_AusgleichsFlaeche",
                    "FP_BebauungsFlaeche",
                    "FP_Bodenschaetze",
                    "FP_DarstellungNachLandesrecht",
                    "FP_FlaecheOhneDarstellung",
                    "FP_Gemeinbedarf",
                    "FP_GenerischesObjekt",
                    "FP_Gewaesser",
                    "FP_Gruen",
                    "FP_KeineZentrAbwasserBeseitigungFlaeche",
                    "FP_Kennzeichnung",
                    "FP_Landwirtschaft",
                    "FP_LandwirtschaftsFlaeche",
                    "FP_NutzungsbeschraenkungsFlaeche",
                    "FP_PrivilegiertesVorhaben",
                    "FP_SchutzPflegeEntwicklung",
                    "FP_SpielSportanlage",
                    "FP_Strassenverkehr",
                    "FP_TextlicheDarstellungsFlaeche",
                    "FP_UnverbindlicheVormerkung",
                    "FP_VerEntsorgung",
                    "FP_VorbehalteFlaeche",
                    "FP_WaldFlaeche",
                    "FP_Wasserwirtschaft",
                    "FP_ZentralerVersorgungsbereich",
                    "LP_Abgrenzung",
                    "LP_AllgGruenflaeche",
                    "LP_AnpflanzungBindungErhaltung",
                    "LP_Ausgleich",
                    "LP_Biotopverbundflaeche",
                    "LP_Bodenschutzrecht",
                    "LP_ErholungFreizeit",
                    "LP_Forstrecht",
                    "LP_GenerischesObjekt",
                    "LP_Landschaftsbild",
                    "LP_NutzungsAusschluss",
                    "LP_NutzungserfordernisRegelung",
                    "LP_PlanerischeVertiefung",
                    "LP_SchutzPflegeEntwicklung",
                    "LP_SchutzobjektInternatRecht",
                    "LP_SonstigesRecht",
                    "LP_TextlicheFestsetzungsFlaeche",
                    "LP_WasserrechtGemeingebrEinschraenkungNaturschutz",
                    "LP_WasserrechtSchutzgebiet",
                    "LP_WasserrechtSonstige",
                    "LP_WasserrechtWirtschaftAbflussHochwSchutz",
                    "LP_ZuBegruenendeGrundstueckflaeche",
                    "LP_Zwischennutzung",
                    "RP_Achse",
                    "RP_Bodenschutz",
                    "RP_Einzelhandel",
                    "RP_Energieversorgung",
                    "RP_Entsorgung",
                    "RP_Erholung",
                    "RP_ErneuerbareEnergie",
                    "RP_Forstwirtschaft",
                    "RP_Freiraum",
                    "RP_Funktionszuweisung",
                    "RP_GenerischesObjekt",
                    "RP_Gewaesser",
                    "RP_Grenze",
                    "RP_GruenzugGruenzaesur",
                    "RP_Hochwasserschutz",
                    "RP_IndustrieGewerbe",
                    "RP_Klimaschutz",
                    "RP_Kommunikation",
                    "RP_Kulturlandschaft",
                    "RP_LaermschutzBauschutz",
                    "RP_Landwirtschaft",
                    "RP_Luftverkehr",
                    "RP_NaturLandschaft",
                    "RP_NaturschutzrechtlichesSchutzgebiet",
                    "RP_Planungsraum",
                    "RP_RadwegWanderweg",
                    "RP_Raumkategorie",
                    "RP_Rohstoff",
                    "RP_Schienenverkehr",
                    "RP_Siedlung",
                    "RP_SonstVerkehr",
                    "RP_SonstigeInfrastruktur",
                    "RP_SonstigerFreiraumschutz",
                    "RP_SonstigerSiedlungsbereich",
                    "RP_SozialeInfrastruktur",
                    "RP_Sperrgebiet",
                    "RP_Sportanlage",
                    "RP_Strassenverkehr",
                    "RP_Verkehr",
                    "RP_Wasserschutz",
                    "RP_Wasserverkehr",
                    "RP_Wasserwirtschaft",
                    "RP_WohnenSiedlung",
                    "RP_ZentralerOrt",
                    "SO_Bauverbotszone",
                    "SO_Bodenschutzrecht",
                    "SO_Denkmalschutzrecht",
                    "SO_Forstrecht",
                    "SO_Gebiet",
                    "SO_Gelaendemorphologie",
                    "SO_Gewaesser",
                    "SO_Grenze",
                    "SO_Linienobjekt",
                    "SO_Luftverkehrsrecht",
                    "SO_Objekt",
                    "SO_Schienenverkehrsrecht",
                    "SO_SchutzgebietNaturschutzrecht",
                    "SO_SchutzgebietSonstigesRecht",
                    "SO_SchutzgebietWasserrecht",
                    "SO_SonstigesRecht",
                    "SO_Strassenverkehrsrecht",
                    "SO_Wasserrecht",
                ],
                "stereotype": "Association",
                "reverseProperty": "wirdDargestelltDurch",
                "sourceOrTarget": "source",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class XPExterneReferenz(BaseFeature):
    """
    Verweis auf ein extern gespeichertes Dokument oder einen extern gespeicherten, georeferenzierten Plan. Einer der beiden Attribute "referenzName" bzw. "referenzURL" muss belegt sein.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    georefURL: Annotated[
        AnyUrl | None,
        Field(
            description="Referenz auf eine Georeferenzierungs-Datei. Das Attribut ist nur relevant bei Verweisen auf georeferenzierte Rasterbilder. Wenn der XPlanGML Datensatz und das referierte Dokument in einem hierarchischen Ordnersystem gespeichert sind, kann die URI auch einen relativen Pfad vom XPlanGML-Datensatz zum Dokument enthalten.",
            json_schema_extra={
                "typename": "URI",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    georefMimeType: Annotated[
        AnyUrl | None,
        Field(
            description='Mime-Type der Georeferenzierungs-Datei. Das Attribut ist nur relevant bei Verweisen auf georeferenzierte Rasterbilder.\r\n\r\nDas Attribut ist als "veraltet" gekennzeichnet und wird in Version 6.0 evtl. wegfallen.',
            json_schema_extra={
                "typename": "XP_MimeTypes",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    art: Annotated[
        Literal["Dokument", "PlanMitGeoreferenz"] | None,
        Field(
            description="Typisierung der referierten Dokumente: Beliebiges Dokument oder georeferenzierter Plan.",
            json_schema_extra={
                "enumDescription": {
                    "Dokument": {
                        "name": "Dokument",
                        "description": "Referenz auf ein Dokument.",
                    },
                    "PlanMitGeoreferenz": {
                        "name": "PlanMitGeoreferenz",
                        "description": "Referenz auf einen georeferenzierten Plan.",
                    },
                },
                "typename": "XP_ExterneReferenzArt",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    informationssystemURL: Annotated[
        AnyUrl | None,
        Field(
            description='URI des Informationssystems., in dem das Dokument gespeichert ist.\r\n\r\nDies Attribut ist als "veraltet" gekennzeichnet und wird in Version 6.0 evtl. wegfallen.',
            json_schema_extra={
                "typename": "URI",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    referenzName: Annotated[
        str | None,
        Field(
            description="Name bzw. Titel des referierten Dokuments",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    referenzURL: Annotated[
        AnyUrl | None,
        Field(
            description="URI des referierten Dokuments, über den auf das Dokument lesend zugegriffen werden kann. Wenn der XPlanGML Datensatz und das referierte Dokument in einem hierarchischen Ordnersystem gespeichert sind, kann die URI auch einen relativen Pfad vom XPlanGML-Datensatz zum Dokument enthalten.",
            json_schema_extra={
                "typename": "URI",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    referenzMimeType: Annotated[
        AnyUrl | None,
        Field(
            description="Mime-Type des referierten Dokumentes",
            json_schema_extra={
                "typename": "XP_MimeTypes",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    beschreibung: Annotated[
        str | None,
        Field(
            description="Beschreibung des referierten Dokuments",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    datum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des referierten Dokuments",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPFPO(XPAbstraktesPraesentationsobjekt):
    """
    Flächenförmiges Präsentationsobjekt. Entspricht der ALKIS Objektklasse AP_FPO.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Polygon | definitions.MultiPolygon,
        Field(
            description="Zur Plandarstellung benutzte Flächengeometrie.",
            json_schema_extra={
                "typename": "XP_Flaechengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]


class XPLPO(XPAbstraktesPraesentationsobjekt):
    """
    Linienförmiges Präsentationsobjekt Entspricht der ALKIS Objektklasse AP_LPO.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Line | definitions.MultiLine,
        Field(
            description="Zur Plandarstellung benutzte Liniengeometrie.",
            json_schema_extra={
                "typename": "XP_Liniengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]


class XPPPO(XPAbstraktesPraesentationsobjekt):
    """
    Punktförmiges Präsentationsobjekt. Entspricht der ALKIS-Objektklasse AP_PPO.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point | definitions.MultiPoint,
        Field(
            description="Position des zur Visualisierung benutzten  Textes oder Symbols,",
            json_schema_extra={
                "typename": "XP_Punktgeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    drehwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Winkel um den der Text oder die Signatur mit punktförmiger Bezugsgeometrie aus der Horizontalen gedreht ist, Angabe in Grad. Zählweise im mathematisch positiven Sinn (von Ost über Nord nach West und Süd).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    skalierung: Annotated[
        float | None,
        Field(
            description="Skalierungsfaktor für Symbole.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = 1.0
    hat: Annotated[
        AnyUrl | UUID | None,
        Field(
            description="Die Relation ermöglicht es, einem punktförmigen Präsentationsobjekt ein linienförmiges Präsentationsobjekt zuzuweisen. Einziger bekannter Anwendungsfall ist der Zuordnungspfeil eines Symbols oder einer Nutzungsschablone.",
            json_schema_extra={
                "typename": "XP_LPO",
                "stereotype": "Association",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPPraesentationsobjekt(XPAbstraktesPraesentationsobjekt):
    """
    Entspricht der ALKIS-Objektklasse AP_Darstellung mit dem Unterschied, dass auf das Attribut "positionierungssregel" verzichtet wurde.  Die Klasse darf nur als gebundenes Präsentationsobjekt verwendet werden. Die Standard-Darstellung des verbundenen Fachobjekts wird dann durch die über stylesheetId spezifizierte Darstellung ersetzt. Die Umsetzung dieses Konzeptes ist der Implementierung überlassen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class XPRasterdarstellung(BaseFeature):
    """
    Georeferenzierte Rasterdarstellung eines Plans. Das über refScan referierte Rasterbild zeigt den Basisplan, dessen Geltungsbereich durch den Geltungsbereich des Gesamtplans (Attribut geltungsbereich von XP_Plan) repräsentiert ist.

    Im Standard sind nur georeferenzierte Rasterpläne zugelassen. Die über refScan referierte externe Referenz muss deshalb entweder vom Typ "PlanMitGeoreferenz" sein oder einen WMS-Request enthalten.

    Die Klasse ist veraltet und wird in XPlanGML V. 6.0 eliminiert.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    id: str | None = None
    refScan: Annotated[
        list[XPExterneReferenz],
        Field(
            description="Referenz auf eine georeferenzierte Rasterversion des Basisplans",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "1..*",
            },
            min_length=1,
        ),
    ]
    refText: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf die textlich formulierten Inhalte des Plans.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refLegende: Annotated[
        list[XPExterneReferenz] | None,
        Field(
            description="Referenz auf die Legende des Plans.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class XPSPEMassnahmenDaten(BaseFeature):
    """
    Spezifikation der Attribute für einer Schutz-, Pflege- oder Entwicklungsmaßnahme.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    klassifizMassnahme: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "1300",
            "1400",
            "1500",
            "1600",
            "1700",
            "1800",
            "1900",
            "2000",
            "2100",
            "2200",
            "2300",
            "9999",
        ]
        | None,
        Field(
            description="Klassifikation der Maßnahme",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "ArtentreicherGehoelzbestand",
                        "description": "Artenreicher Gehölzbestand ist aus unterschiedlichen, standortgerechten Gehölzarten aufgebaut und weist einen Strauchanteil auf.",
                    },
                    "1100": {
                        "name": "NaturnaherWald",
                        "description": "Naturnahe Wälder zeichnen sich durch eine standortgemäße Gehölzzusammensetzung unterschiedlicher Altersstufen, durch eine Schichtung der Gehölze (z.B. Strauchschicht, sich überlagernder erster Baumschicht in 10-15 m Höhe und zweiter Baumschicht in 20-25 m Höhe) sowie durch eine in der Regeln artenreiche Krautschicht aus. Kennzeichnend sind zudem das gleichzeitige Nebeneinander von aufwachsenden Gehölzen, Altbäumen und Lichtungen in kleinräumigen Wechsel sowie ein gewisser Totholzanteil.",
                    },
                    "1200": {
                        "name": "ExtensivesGruenland",
                        "description": "Gegenüber einer intensiven Nutzung sind bei extensiver Grünlandnutzung sowohl Beweidungsintensitäten als auch der Düngereinsatz deutlich geringer. Als Folge finden eine Reihe von eher konkurrenzschwachen, oft auch trittempflindlichen Pflanzenarten Möglichkeiten, sich neben den in der Regel sehr robusten, wuchskräftigen, jedoch sehr nährstoffbedürftigen Pflanzen intensiver Wirtschaftsflächen zu behaupten.  Dadurch kommt es zur Ausprägung von standortbedingt unterschiedlichen Grünlandgesellschaften mit deutlichen höheren Artenzahlen (größere Vielfalt).",
                    },
                    "1300": {
                        "name": "Feuchtgruenland",
                        "description": "Artenreiches Feuchtgrünland entwickelt sich bei extensiver Bewirtschaftung auf feuchten bis wechselnassen Standorten. Die geringe Tragfähigkeit des vielfach anstehenden Niedermoorbodens erschwert den Einsatz von Maschinen, so dass die Flächen vorwiegend beweidet bzw. erst spät im Jahr gemäht werden.",
                    },
                    "1400": {
                        "name": "Obstwiese",
                        "description": "Obstwiesen umfassen mittel- oder hochstämmige, großkronige Obstbäume auf beweidetem (Obstweide) oder gemähtem (obstwiese) Grünland. Im Optimalfall setzt sich der aufgelockerte Baumbestand aus verschiedenen, möglichst alten, regional-typischen Kultursorten zusammen.",
                    },
                    "1500": {
                        "name": "NaturnaherUferbereich",
                        "description": "Naturahne Uferbereiche umfassen unterschiedlich zusammengesetzte Röhrichte und Hochstaudenrieder oder Seggen-Gesellschaften sowie Ufergehölze, die sich vorwiegend aus strauch- oder baumförmigen Weiden, Erlen oder Eschen zusammensetzen.",
                    },
                    "1600": {
                        "name": "Roehrichtzone",
                        "description": "Im flachen Wasser oder auf nassen Böden bilden sich hochwüchsige, oft artenarme Bestände aus überwiegend windblütigen Röhrichtarten aus. Naturliche Bestände finden sich im Uferbereich von Still- und Fließgewässern.",
                    },
                    "1700": {
                        "name": "Ackerrandstreifen",
                        "description": "Ackerrandstreifen sind breite Streifen im Randbereich eines konventionell oder ökologisch genutzten Ackerschlages.",
                    },
                    "1800": {
                        "name": "Ackerbrache",
                        "description": "Als Ackerbrachflächen werden solche Biotope angesprochen, die seit kurzer Zeit aus der Nutzung herausgenommen worden sind. Sie entstehen, indem Ackerflächen mindestens eine Vegetationsperiode nicht mehr bewirtschaftet werden.",
                    },
                    "1900": {
                        "name": "Gruenlandbrache",
                        "description": "Als Grünlandbrachen werden solche Biotope angesprochen, die seit kurzer Zeit aus der Nutzung herausgenommen worden sind. Sie entstehen, indem Grünland mindestens eine Vegetationsperiode nicht mehr bewirtschaftet wird.",
                    },
                    "2000": {
                        "name": "Sukzessionsflaeche",
                        "description": "Sukzessionsflächen umfassen dauerhaft ungenutzte, der natürlichen Entwicklung überlassene Vegetationsbestände auf trockenen bis feuchten Standorten.",
                    },
                    "2100": {
                        "name": "Hochstaudenflur",
                        "description": "Hochwüchsige, zumeist artenreiche Staudenfluren feuchter bis nasser Standorte entwickeln sich in der Regel auf Feuchtgrünland-Brachen, an gehölzfreien Uferstreifen oder an anderen zeitweilig gestörten Standorten mit hohen Grundwasserständen.",
                    },
                    "2200": {
                        "name": "Trockenrasen",
                        "description": "Trockenrasen sind durch zumindest zeitweilige extreme Trockenheit (Regelwasser versickert rasch) sowie durch Nährstoffarmut charakterisiert, die nur Arten mit speziell angepassten Lebensstrategien Entwicklungsmöglichkeiten bieten.",
                    },
                    "2300": {
                        "name": "Heide",
                        "description": "Heiden sind Zwergstrauchgesellschaften auf nährstoffarmen, sauren, trockenen (Calluna-Heide) oder feuchten (Erica-Heide) Standorten. Im Binnenland haben sie in der Regel nach Entwaldung (Abholzung) und langer Übernutzung (Beweidung) primär nährstoffarmer Standorte entwickelt.",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
                "typename": "XP_SPEMassnahmenTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahmeText: Annotated[
        str | None,
        Field(
            description="Durchzuführende Maßnahme als freier Text.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahmeKuerzel: Annotated[
        str | None,
        Field(
            description="Kürzel der durchzuführenden Maßnahme.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPSpezExterneReferenz(XPExterneReferenz):
    """
    Ergänzung des Datentyps XP_ExterneReferenz um ein Attribut zur semantischen Beschreibung des referierten Dokuments.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal[
            "1000",
            "1010",
            "1020",
            "1030",
            "1040",
            "1050",
            "1060",
            "1065",
            "1070",
            "1080",
            "1090",
            "2000",
            "2100",
            "2200",
            "2300",
            "2400",
            "2500",
            "2600",
            "2700",
            "2800",
            "2900",
            "3000",
            "3100",
            "4000",
            "5000",
            "9998",
            "9999",
        ],
        Field(
            description="Typ / Inhalt des referierten Dokuments oder Rasterplans.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Beschreibung",
                        "description": "Beschreibung eines Plans",
                    },
                    "1010": {
                        "name": "Begruendung",
                        "description": "Begründung eines Plans",
                    },
                    "1020": {"name": "Legende", "description": "Plan-Legende"},
                    "1030": {
                        "name": "Rechtsplan",
                        "description": "Elektronische Version des rechtsverbindlichen Plans",
                    },
                    "1040": {
                        "name": "Plangrundlage",
                        "description": "Elektronische Version der Plangrundlage, z.B. ein katasterplan",
                    },
                    "1050": {
                        "name": "Umweltbericht",
                        "description": "Umweltbericht - Ergebnis der Umweltprügung bzgl. der Umweltbelange",
                    },
                    "1060": {"name": "Satzung", "description": "Satzung"},
                    "1065": {
                        "name": "Verordnung",
                        "description": "Elektronische Version des Verordnungstextes",
                    },
                    "1070": {
                        "name": "Karte",
                        "description": "Referenz auf eine Karte, die in Bezug zum Plan steht",
                    },
                    "1080": {
                        "name": "Erlaeuterung",
                        "description": "Erläuterungsbericht",
                    },
                    "1090": {
                        "name": "ZusammenfassendeErklaerung",
                        "description": "Zusammenfassende Erklärung der in dem Verfahren berücksichtigten Umweltbelange gemäß §10 Absatz 4 BauGB.",
                    },
                    "2000": {
                        "name": "Koordinatenliste",
                        "description": "Koordinaten-Liste",
                    },
                    "2100": {
                        "name": "Grundstuecksverzeichnis",
                        "description": "Grundstücksverzeichnis",
                    },
                    "2200": {"name": "Pflanzliste", "description": "Pflanzliste"},
                    "2300": {
                        "name": "Gruenordnungsplan",
                        "description": "Grünordnungsplan",
                    },
                    "2400": {
                        "name": "Erschliessungsvertrag",
                        "description": "Erschließungsvertrag",
                    },
                    "2500": {
                        "name": "Durchfuehrungsvertrag",
                        "description": "Durchführungsvertrag",
                    },
                    "2600": {
                        "name": "StaedtebaulicherVertrag",
                        "description": "Elektronische Version eines städtebaulichen Vertrages",
                    },
                    "2700": {
                        "name": "UmweltbezogeneStellungnahmen",
                        "description": "Elentronisches Dokument mit umweltbezogenen Stellungnahmen.",
                    },
                    "2800": {
                        "name": "Beschluss",
                        "description": "Dokument mit den Beschluss des Gemeinderats zur öffentlichen Auslegung.",
                    },
                    "2900": {
                        "name": "VorhabenUndErschliessungsplan",
                        "description": "Referenz auf einen Vorhaben- und Erschließungsplan nach §7 BauBG-MaßnahmenG von 1993",
                    },
                    "3000": {
                        "name": "MetadatenPlan",
                        "description": "Referenz auf den Metadatensatz des Plans",
                    },
                    "3100": {
                        "name": "StaedtebaulEntwicklungskonzeptInnenentwicklung",
                        "description": "Städtebauliches Entwicklungskonzept zur Stärkung der Innenentwicklung",
                    },
                    "4000": {
                        "name": "Genehmigung",
                        "description": "Referenz auf ein Dokument mit dem Text der Genehmigung",
                    },
                    "5000": {
                        "name": "Bekanntmachung",
                        "description": "Referenz auf den Bekanntmachungs-Text",
                    },
                    "9998": {
                        "name": "Rechtsverbindlich",
                        "description": "Sonstiges rechtsverbindliches Dokument",
                    },
                    "9999": {
                        "name": "Informell",
                        "description": "Sonstiges nicht-rechtsverbindliches Dokument",
                    },
                },
                "typename": "XP_ExterneReferenzTyp",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]


class XPTPO(XPAbstraktesPraesentationsobjekt):
    """
    Abstrakte Oberklasse für textliche Präsentationsobjekte. Entspricht der ALKIS Objektklasse AP_TPO
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    schriftinhalt: Annotated[
        str | None,
        Field(
            description="Schriftinhalt; enthält den darzustellenden Text.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    fontSperrung: Annotated[
        float | None,
        Field(
            description="Die Zeichensperrung steuert den zusätzlichen Raum, der zwischen 2 aufeinanderfolgende Zeichenkörper geschoben wird. Er ist ein Faktor, der mit der angegebenen Zeichenhöhe multipliziert wird, um den einzufügenden Zusatzabstand zu erhalten. Mit der Abhängigkeit von der Zeichenhöhe wird erreicht, dass das Schriftbild unabhängig von der Zeichenhöhe gleich wirkt. Der Defaultwert ist 0.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = 0.0
    skalierung: Annotated[
        float | None,
        Field(
            description="Skalierungsfaktor der Schriftgröße, bezogen auf die von der interpretierenden Software festgelegte Standardschrift",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = 1.0
    horizontaleAusrichtung: Annotated[
        Literal["linksbündig", "rechtsbündig", "zentrisch"] | None,
        Field(
            description="Gibt die Ausrichtung des Textes bezüglich der Textgeometrie an.\r\nlinksbündig: Der Text beginnt an der Punktgeometrie bzw. am Anfangspunkt der Liniengeometrie.\r\nrechtsbündig: Der Text endet an der Punktgeometrie bzw. am Endpunkt der Liniengeometrie\r\nzentrisch: Der Text erstreckt sich von der Punktgeometrie gleich weit nach links und rechts bzw. steht auf der Mitte der Standlinie.",
            json_schema_extra={
                "enumDescription": {
                    "linksbündig": {
                        "name": "linksbündig",
                        "description": "Text linksbündig am Textpunkt bzw. am ersten Punkt der Linie.",
                    },
                    "rechtsbündig": {
                        "name": "rechtsbündig",
                        "description": "Text rechtsbündig am Textpunkt bzw. am letzten Punkt der Linie.",
                    },
                    "zentrisch": {
                        "name": "zentrisch",
                        "description": "Text zentriert am Textpunkt bzw. in der Mitte der Textstandlinie.",
                    },
                },
                "typename": "XP_HorizontaleAusrichtung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    vertikaleAusrichtung: Annotated[
        Literal["Basis", "Mitte", "Oben"] | None,
        Field(
            description="Die vertikale Ausrichtung eines Textes gibt an, ob die Bezugsgeometrie die Basis (Grundlinie) des Textes, die Mitte oder obere Buchstabenbegrenzung betrifft.",
            json_schema_extra={
                "enumDescription": {
                    "Basis": {
                        "name": "Basis",
                        "description": "Textgeometrie bezieht sich auf die Basis- bzw. Grundlinie der Buchstaben.",
                    },
                    "Mitte": {
                        "name": "Mitte",
                        "description": "Textgeometrie bezieht sich auf die Mittellinie der Buchstaben.",
                    },
                    "Oben": {
                        "name": "Oben",
                        "description": "Textgeometrie bezieht sich auf die Oberlinie der Großbuchstaben.",
                    },
                },
                "typename": "XP_VertikaleAusrichtung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    hat: Annotated[
        AnyUrl | UUID | None,
        Field(
            description="Die Relation ermöglicht es, einem textlichen Präsentationsobjekt ein linienförmiges Präsentationsobjekt zuzuweisen. Einziger bekannter Anwendungsfall ist der Zuordnungspfeil eines Symbols oder einer Nutzungsschablone.",
            json_schema_extra={
                "typename": "XP_LPO",
                "stereotype": "Association",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPTextAbschnitt(BaseFeature):
    """
    Ein Abschnitt der textlich formulierten Inhalte  des Plans.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    id: str | None = None
    schluessel: Annotated[
        str | None,
        Field(
            description="Schlüssel zur Referenzierung des Abschnitts.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gesetzlicheGrundlage: Annotated[
        str | None,
        Field(
            description="Gesetzliche Grundlage des Text-Abschnittes",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    text: Annotated[
        str | None,
        Field(
            description="Inhalt eines Abschnitts der textlichen Planinhalte",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refText: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf ein externes Dokument das den zug Textabschnitt enthält.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPTextAbschnitt(XPTextAbschnitt):
    """
    Texlich formulierter Inhalt eines Bebauungsplans, der einen anderen Rechtscharakter als das zugrunde liegende Fachobjekt hat (Attribut rechtscharakter des Fachobjektes), oder dem Plan als Ganzes zugeordnet ist.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "9998"],
        Field(
            description="Rechtscharakter des textlich formulierten Planinhalts.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Festsetzung",
                        "description": "Festsetzung in Bebauungsplan.",
                    },
                    "2000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahme aus anderen Planwerken.",
                    },
                    "3000": {"name": "Hinweis", "description": "Hinweis nach BauGB"},
                    "4000": {
                        "name": "Vermerk",
                        "description": "Vermerk nach § 5 BauGB",
                    },
                    "5000": {
                        "name": "Kennzeichnung",
                        "description": "Kennzeichnung von Flächen nach $9 Absatz 5 BauGB. Kennzeichnungen sind keine rechtsverbindlichen Festsetzungen, sondern Hinweise auf Besonderheiten (insbesondere der Baugrundverhältnisse), deren Kenntnis für das Verständnis des Bebauungsplans und seiner Festsetzungen wie auch für die Vorbereitung und Genehmigung von Vorhaben notwendig sind.",
                    },
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Der Rechtscharakter des BPlan-Inhaltes ist unbekannt.",
                    },
                },
                "typename": "BP_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]


class FPTextAbschnitt(XPTextAbschnitt):
    """
    Texlich formulierter Inhalt eines Flächennutzungsplans, der einen anderen Rechtscharakter als das zugrunde liegende Fachobjekt hat (Attribut rechtscharakter des Fachobjektes), oder dem Plan als Ganzes zugeordnet ist.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "9998"],
        Field(
            description="Rechtscharakter des textlich formulierten Planinhalts.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Darstellung",
                        "description": "Darstellung im Flächennutzungsplan",
                    },
                    "2000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahme aus anderen Planwerken.",
                    },
                    "3000": {"name": "Hinweis", "description": "Hinweis nach BauGB"},
                    "4000": {"name": "Vermerk", "description": "Vermerk nach §9 BauGB"},
                    "5000": {
                        "name": "Kennzeichnung",
                        "description": "Kennzeichnung nach §5 Abs. (3) BauGB.",
                    },
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Der Rechtscharakter des FPlan-Inhaltes ist unbekannt.",
                    },
                },
                "typename": "FP_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]


class LPTextAbschnitt(XPTextAbschnitt):
    """
    Texlich formulierter Inhalt eines Landschaftsplans, der einen anderen Rechtscharakter als das zugrunde liegende Fachobjekt hat (Attribut status des Fachobjektes), oder dem Plan als Ganzes zugeordnet ist.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "9998", "9999"],
        Field(
            description="Rechtscharakter des textlich formulierten Planinhalts.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Festsetzung",
                        "description": "Festsetzung im Landschaftsplan",
                    },
                    "2000": {
                        "name": "Geplant",
                        "description": "Geplante Festsetzung im Landschaftsplan",
                    },
                    "3000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahmen im Landschaftsplan",
                    },
                    "4000": {
                        "name": "DarstellungKennzeichnung",
                        "description": "Darstellungen und Kennzeichnungen im Landschaftsplan.",
                    },
                    "5000": {
                        "name": "FestsetzungInBPlan",
                        "description": "Planinhalt aus dem Bereich Naturschutzrecht, der in einem BPlan festgesetzt wird.",
                    },
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Der Rechtscharakter des LPlan-Inhalts ist unbekannt.",
                    },
                    "9999": {
                        "name": "SonstigerStatus",
                        "description": "Sonstiger Rechtscharakter",
                    },
                },
                "typename": "LP_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]


class RPLegendenobjekt(BaseFeature):
    """
    Die Klasse RP_Legendenobjekt enthält Daten zur Legende und Darstellung im Ursprungsplan.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    id: str | None = None
    legendenBezeichnung: Annotated[
        str,
        Field(
            description="Bezeichnung des XPlan-FeatureTypes in der Legende des dazugehörigen Plans.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    reflegendenBild: Annotated[
        XPExterneReferenz,
        Field(
            description="Referenz auf das Bild eines Planzeichens in der Legende eines Plans.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "1",
            },
        ),
    ]
    gehoertZuPraesentationsobjekt: Annotated[
        AnyUrl | UUID | None,
        Field(
            description="Verweis auf das zugehörige Präsentationsobjekt",
            json_schema_extra={
                "typename": [
                    "XP_FPO",
                    "XP_LPO",
                    "XP_LTO",
                    "XP_Nutzungsschablone",
                    "XP_PPO",
                    "XP_PTO",
                    "XP_Praesentationsobjekt",
                ],
                "stereotype": "Association",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPTextAbschnitt(XPTextAbschnitt):
    """
    Texlich formulierter Inhalt eines Raumordnungsplans, der einen anderen Rechtscharakter als das zugrunde liegende Fachobjekt hat (Attribut rechtscharakter des Fachobjektes), oder dem Plan als Ganzes zugeordnet ist.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal[
            "1000",
            "2000",
            "3000",
            "4000",
            "5000",
            "6000",
            "7000",
            "8000",
            "9000",
            "9998",
        ],
        Field(
            description="Rechtscharakter des textlich formulierten Planinhalts.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "ZielDerRaumordnung",
                        "description": "Ziel der Raumordnung. Verbindliche räumliche und sachliche Festlegung zur Entwicklung, Ordnung und Sicherung des Raumes.",
                    },
                    "2000": {
                        "name": "GrundsatzDerRaumordnung",
                        "description": "Grundsätze der Raumordnung sind nach §3 Abs. Aussagen zur Entwicklung, Ordnung und Sicherung des Raums als Vorgaben für nachfolgende Abwägungs- oder Ermessensentscheidungen. Grundsätze der Raumordnung können durch Gesetz oder Festlegungen in einem Raumordnungsplan (§7 Abs. 1 und 2, ROG) aufgestellt werden.",
                    },
                    "3000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahme.",
                    },
                    "4000": {
                        "name": "NachrichtlicheUebernahmeZiel",
                        "description": "Nachrichtliche Übernahme Ziel.",
                    },
                    "5000": {
                        "name": "NachrichtlicheUebernahmeGrundsatz",
                        "description": "Nachrichtliche Übernahme Grundsatz.",
                    },
                    "6000": {
                        "name": "NurInformationsgehalt",
                        "description": "Nur Informationsgehalt.",
                    },
                    "7000": {
                        "name": "TextlichesZiel",
                        "description": "Textliches Ziel.",
                    },
                    "8000": {
                        "name": "ZielundGrundsatz",
                        "description": "Ziel und Grundsatz.",
                    },
                    "9000": {"name": "Vorschlag", "description": "Vorschlag."},
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Unbekannter Rechtscharakter",
                    },
                },
                "typename": "RP_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]


class SOTextAbschnitt(XPTextAbschnitt):
    """
    Textlich formulierter Inhalt eines Sonstigen Plans, der einen anderen Rechtscharakter als das zugrunde liegende Fachobjekt hat (Attribut rechtscharakter des Fachobjektes), oder dem Plan als Ganzes zugeordnet ist.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal["1000", "1500", "1800", "2000", "3000", "4000", "5000", "9998", "9999"],
        Field(
            description="Rechtscharakter des textlich formulierten Planinhalts.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "FestsetzungBPlan",
                        "description": "Festsetzung im Bebauungsplan",
                    },
                    "1500": {
                        "name": "DarstellungFPlan",
                        "description": "Darstellung im Flächennutzungsplan",
                    },
                    "1800": {
                        "name": "InhaltLPlan",
                        "description": "Inhalt eines Landschaftsplans",
                    },
                    "2000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahme aus anderen Planwerken.",
                    },
                    "3000": {"name": "Hinweis", "description": "Hinweis nach BauGB"},
                    "4000": {"name": "Vermerk", "description": "Vermerk nach BauGB"},
                    "5000": {
                        "name": "Kennzeichnung",
                        "description": "Kennzeichnung nach BauGB",
                    },
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Der Rechtscharakter des Planinhalts ist unbekannt",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiger Rechtscharakter",
                    },
                },
                "typename": "SO_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]


class XPBegruendungAbschnitt(BaseFeature):
    """
    Ein Abschnitt der Begründung des Plans.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    id: str | None = None
    schluessel: Annotated[
        str | None,
        Field(
            description="Schlüssel zur Referenzierung des Abschnitts von einem Fachobjekt aus.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    text: Annotated[
        str | None,
        Field(
            description="Inhalt eines Abschnitts der Begründung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refText: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf ein externes Dokument das den Begründungs-Abschnitt enthält.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPBereich(BaseFeature):
    """
    Abstrakte Oberklasse für die Modellierung von Bereichen. Ein Bereich fasst die Inhalte eines Plans nach bestimmten Kriterien zusammen.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    id: str | None = None
    nummer: Annotated[
        int,
        Field(
            description="Nummer des Bereichs. Wenn der Bereich als Ebene eines BPlans interpretiert wird, kann aus dem Attribut die vertikale Reihenfolge der Ebenen rekonstruiert werden.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    name: Annotated[
        str | None,
        Field(
            description="Bezeichnung des Bereiches",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bedeutung: Annotated[
        Literal["1600", "1800", "9999"] | None,
        Field(
            description="Spezifikation der semantischen Bedeutung eines Bereiches.",
            json_schema_extra={
                "enumDescription": {
                    "1600": {
                        "name": "Teilbereich",
                        "description": "Räumliche oder sachliche Aufteilung der Planinhalte.",
                    },
                    "1800": {
                        "name": "Kompensationsbereich",
                        "description": "Aggregation von Objekten außerhalb des Geltungsbereiches gemäß Eingriffsregelung.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": 'Bereich, für den keine der aufgeführten Bedeutungen zutreffend ist. In dem Fall kann die Bedeutung über das Textattribut "detaillierteBedeutung" angegeben werden.',
                    },
                },
                "typename": "XP_BedeutungenBereich",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detaillierteBedeutung: Annotated[
        str | None,
        Field(
            description='Detaillierte Erklärung der semantischen Bedeutung eines Bereiches, in Ergänzung des Attributs "bedeutung".',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    erstellungsMassstab: Annotated[
        int | None,
        Field(
            description="Der bei der Erstellung der Inhalte des Bereichs benutzte Kartenmaßstab. Wenn dieses Attribut nicht spezifiziert ist, gilt für den Bereich der auf Planebene (XP_Plan) spezifizierte Maßstab.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    geltungsbereich: Annotated[
        definitions.Polygon | definitions.MultiPolygon | None,
        Field(
            description="Räumliche Abgrenzung des Bereiches. Wenn dieses Attribut nicht spezifiziert ist, gilt für den Bereich der auf Planebene (XP_Plan) spezifizierte Geltungsbereich.",
            json_schema_extra={
                "typename": "XP_Flaechengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refScan: Annotated[
        list[XPExterneReferenz] | None,
        Field(
            description='Referenz auf einen georeferenzierte Rasterplan, der die Inhalte des Bereichs wiedergibt. Das über refScan referierte Rasterbild zeigt einen Plan, dessen Geltungsbereich durch den Geltungsbereich des Bereiches (Attribut geltungsbereich von XP_Bereich) oder, wenn geltungsbereich nicht belegt ist, den Geltungsbereich des Gesamtplans (Attribut raeumlicherGeltungsbereich von XP_PLan) definiert ist. \r\n\r\nIm Standard sind nur georeferenzierte Rasterpläne zugelassen. Die über refScan referierte externe Referenz muss deshalb entweder vom Typ "PlanMitGeoreferenz" sein oder einen WMS-Request enthalten.',
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    rasterBasis: Annotated[
        AnyUrl | UUID | None,
        Field(
            description="Referenz auf einen georeferenzierte Rasterplan, der die Inhalte des Bereichs wiedergibt.\r\n\r\nDiese Relation ist veraltet und wird in XPlanGML 6.0 wegfallen. XP_Rasterdarstellung sollte folgendermaßen abgebildet werden:\r\n\r\nXP_Rasterdarstellung.refScan --> XP_Bereich.refScan\r\nXP_Rasterdarstellung.refText --> XP_Plan.texte\r\nXP_Rasterdarstellung.refLegende --> XP_Plan.externeReferenz",
            json_schema_extra={
                "typename": "XP_Rasterdarstellung",
                "stereotype": "Association",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    planinhalt: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Verweis auf einen Planinhalt des Bereichs",
            json_schema_extra={
                "typename": [
                    "BP_AbgrabungsFlaeche",
                    "BP_AbstandsFlaeche",
                    "BP_AbstandsMass",
                    "BP_AbweichungVonBaugrenze",
                    "BP_AbweichungVonUeberbaubererGrundstuecksFlaeche",
                    "BP_AnpflanzungBindungErhaltung",
                    "BP_AufschuettungsFlaeche",
                    "BP_AusgleichsFlaeche",
                    "BP_AusgleichsMassnahme",
                    "BP_BauGrenze",
                    "BP_BauLinie",
                    "BP_BaugebietsTeilFlaeche",
                    "BP_BereichOhneEinAusfahrtLinie",
                    "BP_BesondererNutzungszweckFlaeche",
                    "BP_BodenschaetzeFlaeche",
                    "BP_EinfahrtPunkt",
                    "BP_EinfahrtsbereichLinie",
                    "BP_EingriffsBereich",
                    "BP_ErhaltungsBereichFlaeche",
                    "BP_FestsetzungNachLandesrecht",
                    "BP_FirstRichtungsLinie",
                    "BP_FlaecheOhneFestsetzung",
                    "BP_FoerderungsFlaeche",
                    "BP_FreiFlaeche",
                    "BP_GebaeudeFlaeche",
                    "BP_GemeinbedarfsFlaeche",
                    "BP_GemeinschaftsanlagenFlaeche",
                    "BP_GemeinschaftsanlagenZuordnung",
                    "BP_GenerischesObjekt",
                    "BP_GewaesserFlaeche",
                    "BP_GruenFlaeche",
                    "BP_HoehenMass",
                    "BP_Immissionsschutz",
                    "BP_KennzeichnungsFlaeche",
                    "BP_KleintierhaltungFlaeche",
                    "BP_Landwirtschaft",
                    "BP_LandwirtschaftsFlaeche",
                    "BP_NebenanlagenAusschlussFlaeche",
                    "BP_NebenanlagenFlaeche",
                    "BP_NichtUeberbaubareGrundstuecksflaeche",
                    "BP_NutzungsartenGrenze",
                    "BP_PersGruppenBestimmteFlaeche",
                    "BP_RegelungVergnuegungsstaetten",
                    "BP_RekultivierungsFlaeche",
                    "BP_RichtungssektorGrenze",
                    "BP_SchutzPflegeEntwicklungsFlaeche",
                    "BP_SchutzPflegeEntwicklungsMassnahme",
                    "BP_Sichtflaeche",
                    "BP_SpezielleBauweise",
                    "BP_SpielSportanlagenFlaeche",
                    "BP_StrassenVerkehrsFlaeche",
                    "BP_StrassenbegrenzungsLinie",
                    "BP_Strassenkoerper",
                    "BP_TechnischeMassnahmenFlaeche",
                    "BP_TextlicheFestsetzungsFlaeche",
                    "BP_UeberbaubareGrundstuecksFlaeche",
                    "BP_UnverbindlicheVormerkung",
                    "BP_VerEntsorgung",
                    "BP_Veraenderungssperre",
                    "BP_VerkehrsflaecheBesondererZweckbestimmung",
                    "BP_WaldFlaeche",
                    "BP_WasserwirtschaftsFlaeche",
                    "BP_Wegerecht",
                    "BP_WohngebaeudeFlaeche",
                    "BP_ZentralerVersorgungsbereich",
                    "BP_ZusatzkontingentLaerm",
                    "BP_ZusatzkontingentLaermFlaeche",
                    "FP_Abgrabung",
                    "FP_AnpassungKlimawandel",
                    "FP_Aufschuettung",
                    "FP_AusgleichsFlaeche",
                    "FP_BebauungsFlaeche",
                    "FP_Bodenschaetze",
                    "FP_DarstellungNachLandesrecht",
                    "FP_FlaecheOhneDarstellung",
                    "FP_Gemeinbedarf",
                    "FP_GenerischesObjekt",
                    "FP_Gewaesser",
                    "FP_Gruen",
                    "FP_KeineZentrAbwasserBeseitigungFlaeche",
                    "FP_Kennzeichnung",
                    "FP_Landwirtschaft",
                    "FP_LandwirtschaftsFlaeche",
                    "FP_NutzungsbeschraenkungsFlaeche",
                    "FP_PrivilegiertesVorhaben",
                    "FP_SchutzPflegeEntwicklung",
                    "FP_SpielSportanlage",
                    "FP_Strassenverkehr",
                    "FP_TextlicheDarstellungsFlaeche",
                    "FP_UnverbindlicheVormerkung",
                    "FP_VerEntsorgung",
                    "FP_VorbehalteFlaeche",
                    "FP_WaldFlaeche",
                    "FP_Wasserwirtschaft",
                    "FP_ZentralerVersorgungsbereich",
                    "LP_Abgrenzung",
                    "LP_AllgGruenflaeche",
                    "LP_AnpflanzungBindungErhaltung",
                    "LP_Ausgleich",
                    "LP_Biotopverbundflaeche",
                    "LP_Bodenschutzrecht",
                    "LP_ErholungFreizeit",
                    "LP_Forstrecht",
                    "LP_GenerischesObjekt",
                    "LP_Landschaftsbild",
                    "LP_NutzungsAusschluss",
                    "LP_NutzungserfordernisRegelung",
                    "LP_PlanerischeVertiefung",
                    "LP_SchutzPflegeEntwicklung",
                    "LP_SchutzobjektInternatRecht",
                    "LP_SonstigesRecht",
                    "LP_TextlicheFestsetzungsFlaeche",
                    "LP_WasserrechtGemeingebrEinschraenkungNaturschutz",
                    "LP_WasserrechtSchutzgebiet",
                    "LP_WasserrechtSonstige",
                    "LP_WasserrechtWirtschaftAbflussHochwSchutz",
                    "LP_ZuBegruenendeGrundstueckflaeche",
                    "LP_Zwischennutzung",
                    "RP_Achse",
                    "RP_Bodenschutz",
                    "RP_Einzelhandel",
                    "RP_Energieversorgung",
                    "RP_Entsorgung",
                    "RP_Erholung",
                    "RP_ErneuerbareEnergie",
                    "RP_Forstwirtschaft",
                    "RP_Freiraum",
                    "RP_Funktionszuweisung",
                    "RP_GenerischesObjekt",
                    "RP_Gewaesser",
                    "RP_Grenze",
                    "RP_GruenzugGruenzaesur",
                    "RP_Hochwasserschutz",
                    "RP_IndustrieGewerbe",
                    "RP_Klimaschutz",
                    "RP_Kommunikation",
                    "RP_Kulturlandschaft",
                    "RP_LaermschutzBauschutz",
                    "RP_Landwirtschaft",
                    "RP_Luftverkehr",
                    "RP_NaturLandschaft",
                    "RP_NaturschutzrechtlichesSchutzgebiet",
                    "RP_Planungsraum",
                    "RP_RadwegWanderweg",
                    "RP_Raumkategorie",
                    "RP_Rohstoff",
                    "RP_Schienenverkehr",
                    "RP_Siedlung",
                    "RP_SonstVerkehr",
                    "RP_SonstigeInfrastruktur",
                    "RP_SonstigerFreiraumschutz",
                    "RP_SonstigerSiedlungsbereich",
                    "RP_SozialeInfrastruktur",
                    "RP_Sperrgebiet",
                    "RP_Sportanlage",
                    "RP_Strassenverkehr",
                    "RP_Verkehr",
                    "RP_Wasserschutz",
                    "RP_Wasserverkehr",
                    "RP_Wasserwirtschaft",
                    "RP_WohnenSiedlung",
                    "RP_ZentralerOrt",
                    "SO_Bauverbotszone",
                    "SO_Bodenschutzrecht",
                    "SO_Denkmalschutzrecht",
                    "SO_Forstrecht",
                    "SO_Gebiet",
                    "SO_Gelaendemorphologie",
                    "SO_Gewaesser",
                    "SO_Grenze",
                    "SO_Linienobjekt",
                    "SO_Luftverkehrsrecht",
                    "SO_Objekt",
                    "SO_Schienenverkehrsrecht",
                    "SO_SchutzgebietNaturschutzrecht",
                    "SO_SchutzgebietSonstigesRecht",
                    "SO_SchutzgebietWasserrecht",
                    "SO_SonstigesRecht",
                    "SO_Strassenverkehrsrecht",
                    "SO_Wasserrecht",
                ],
                "stereotype": "Association",
                "reverseProperty": "gehoertZuBereich",
                "sourceOrTarget": "target",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    praesentationsobjekt: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf ein Präsentationsbereich, das zum Bereich gehört.",
            json_schema_extra={
                "typename": [
                    "XP_FPO",
                    "XP_LPO",
                    "XP_LTO",
                    "XP_Nutzungsschablone",
                    "XP_PPO",
                    "XP_PTO",
                    "XP_Praesentationsobjekt",
                ],
                "stereotype": "Association",
                "reverseProperty": "gehoertZuBereich",
                "sourceOrTarget": "target",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class XPLTO(XPTPO):
    """
    Textförmiges Präsentationsobjekt mit linienförmiger Textgeometrie. Entspricht der ALKIS-Objektklasse AP_LTO.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Line | definitions.MultiLine,
        Field(
            description="Linienführung des Textes",
            json_schema_extra={
                "typename": "XP_Liniengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]


class XPObjekt(BaseFeature):
    """
    Abstrakte Oberklasse für alle XPlanung-Fachobjekte. Die Attribute dieser Klasse werden über den Vererbungs-Mechanismus an alle Fachobjekte weitergegeben.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    id: str | None = None
    uuid: Annotated[
        str | None,
        Field(
            description="Eindeutiger Identifier des Objektes.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    text: Annotated[
        str | None,
        Field(
            description="Beliebiger Text",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rechtsstand: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Angabe, ob der Planinhalt bereits besteht, geplant ist, oder zukünftig wegfallen soll.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Geplant",
                        "description": "Der Planinhalt bezieht sich auf eine Planung",
                    },
                    "2000": {
                        "name": "Bestehend",
                        "description": "Der Planinhalt stellt den aktuellen Zustand dar.",
                    },
                    "3000": {
                        "name": "Fortfallend",
                        "description": "Der Planinhalt beschreibt einen zukünftig fortfallenden Zustand.",
                    },
                },
                "typename": "XP_Rechtsstand",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gesetzlicheGrundlage: Annotated[
        AnyUrl | None,
        Field(
            description="Angabe der gesetzlichen Grundlage des Planinhalts.",
            json_schema_extra={
                "typename": "XP_GesetzlicheGrundlage",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gliederung1: Annotated[
        str | None,
        Field(
            description='Kennung im Plan für eine erste Gliederungsebene (z.B. GE-E für ein "Eingeschränktes Gewerbegebiet")',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gliederung2: Annotated[
        str | None,
        Field(
            description='Kennung im Plan für eine zweite Gliederungsebene (z.B. GE-E 3 für die "Variante 3 eines eingeschränkten Gewerbegebiets")',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ebene: Annotated[
        int | None,
        Field(
            description="Zuordnung des Objektes zu einer vertikalen Ebene. Der Standard-Ebene 0 sind Objekte auf der Erdoberfläche zugeordnet. Nur unter diesen Objekten wird der Flächenschluss hergestellt. Bei Plan-Objekten, die im wesentlichen unterhalb der Erdoberfläche liesen  (z.B. Tunnel), ist ebene < 0. Bei  Objekten, die im wesentlichen oberhalb der Erdoberfläche liegen (z.B. Festsetzungen auf Brücken), ist ebene > 0. Zwischen Objekten auf Ebene 0 und einer Ebene <> 0 muss nicht unbedingt eine (vollständige) physikalische Trennung bestehen.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = 0
    hatGenerAttribut: Annotated[
        list[
            XPDatumAttribut
            | XPDoubleAttribut
            | XPIntegerAttribut
            | XPStringAttribut
            | XPURLAttribut
        ]
        | None,
        Field(
            description="Erweiterung des definierten Attributsatzes eines Objektes durch generische Attribute.",
            json_schema_extra={
                "typename": [
                    "XP_DatumAttribut",
                    "XP_DoubleAttribut",
                    "XP_IntegerAttribut",
                    "XP_StringAttribut",
                    "XP_URLAttribut",
                ],
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    hoehenangabe: Annotated[
        list[XPHoehenangabe] | None,
        Field(
            description="Angaben zur vertikalen Lage und Höhe eines Planinhalts.",
            json_schema_extra={
                "typename": "XP_Hoehenangabe",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    externeReferenz: Annotated[
        list[XPSpezExterneReferenz] | None,
        Field(
            description="Referenz auf ein Dokument oder einen georeferenzierten Rasterplan.",
            json_schema_extra={
                "typename": "XP_SpezExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    gehoertZuBereich: Annotated[
        AnyUrl | UUID | None,
        Field(
            description="Verweis auf den Bereich, zu dem der Planinhalt gehört. Diese Relation sollte immer belegt werden. In Version 6.0 wird sie in eine Pflicht-Relation umgewandelt werden.",
            json_schema_extra={
                "typename": [
                    "BP_Bereich",
                    "FP_Bereich",
                    "LP_Bereich",
                    "RP_Bereich",
                    "SO_Bereich",
                ],
                "stereotype": "Association",
                "reverseProperty": "planinhalt",
                "sourceOrTarget": "source",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    wirdDargestelltDurch: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Verweis auf ein Präsentationsobjekt, das die Plandarstellung des Fachobjektes unterstützen soll.",
            json_schema_extra={
                "typename": [
                    "XP_FPO",
                    "XP_LPO",
                    "XP_LTO",
                    "XP_Nutzungsschablone",
                    "XP_PPO",
                    "XP_PTO",
                    "XP_Praesentationsobjekt",
                ],
                "stereotype": "Association",
                "reverseProperty": "dientZurDarstellungVon",
                "sourceOrTarget": "target",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    refBegruendungInhalt: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz eines raumbezogenen Fachobjektes auf Teile der Begründung.",
            json_schema_extra={
                "typename": "XP_BegruendungAbschnitt",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    startBedingung: Annotated[
        XPWirksamkeitBedingung | None,
        Field(
            description="Notwendige Bedingung für die Wirksamkeit eines Planinhalts.",
            json_schema_extra={
                "typename": "XP_WirksamkeitBedingung",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    endeBedingung: Annotated[
        XPWirksamkeitBedingung | None,
        Field(
            description="Notwendige Bedingung für das Ende der Wirksamkeit eines Planinhalts.",
            json_schema_extra={
                "typename": "XP_WirksamkeitBedingung",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    aufschrift: Annotated[
        str | None,
        Field(
            description="Spezifischer Text zur Beschriftung von Planinhalten",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class XPPTO(XPTPO):
    """
    Textförmiges Präsentationsobjekt mit punktförmiger Festlegung der Textposition. Entspricht der ALKIS-Objektklasse AP_PTO.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point | definitions.MultiPoint,
        Field(
            description="Position des Textes",
            json_schema_extra={
                "typename": "XP_Punktgeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    drehwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Winkel um den der Text oder die Signatur mit punktförmiger Bezugsgeometrie aus der Horizontalen gedreht ist, Angabe in Grad. Zählweise im mathematisch positiven Sinn (von Ost über Nord nach West und Süd).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class XPPlan(BaseFeature):
    """
    Abstrakte Oberklasse für alle Klassen raumbezogener Pläne.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    id: str | None = None
    name: Annotated[
        str,
        Field(
            description="Name des Plans.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    nummer: Annotated[
        str | None,
        Field(
            description="Nummer des Plans.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    internalId: Annotated[
        str | None,
        Field(
            description="Interner Identifikator des Plans.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    beschreibung: Annotated[
        str | None,
        Field(
            description="Kommentierende Beschreibung des Plans.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    kommentar: Annotated[
        str | None,
        Field(
            description="Beliebiger Kommentar zum Plan.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    technHerstellDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum, an dem der Plan technisch ausgefertigt wurde.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    genehmigungsDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum der Genehmigung des Plans",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    untergangsDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum, an dem der Plan (z.B. durch Ratsbeschluss oder Gerichtsurteil) aufgehoben oder für nichtig erklärt wurde.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    aendert: Annotated[
        list[XPVerbundenerPlan] | None,
        Field(
            description="Verweis auf einen anderen Plan, der durch den vorliegenden Plan geändert wird.",
            json_schema_extra={
                "typename": "XP_VerbundenerPlan",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    wurdeGeaendertVon: Annotated[
        list[XPVerbundenerPlan] | None,
        Field(
            description="Verweis auf einen anderen Plan, durch den der vorliegende Plan geändert wurde.",
            json_schema_extra={
                "typename": "XP_VerbundenerPlan",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    erstellungsMassstab: Annotated[
        int | None,
        Field(
            description="Der bei der Erstellung des Plans benutzte Kartenmaßstab.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bezugshoehe: Annotated[
        definitions.Length | None,
        Field(
            description="Standard Bezugshöhe (absolut NhN) für relative Höhenangaben von Planinhalten.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    technischerPlanersteller: Annotated[
        str | None,
        Field(
            description="Beizeichnung der Institution oder Firma, die den Plan technisch erstellt hat.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    raeumlicherGeltungsbereich: Annotated[
        definitions.Polygon | definitions.MultiPolygon,
        Field(
            description="Grenze des räumlichen Geltungsbereiches des Plans.",
            json_schema_extra={
                "typename": "XP_Flaechengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    verfahrensMerkmale: Annotated[
        list[XPVerfahrensMerkmal] | None,
        Field(
            description="Vermerke der am Planungsverfahren beteiligten Akteure.",
            json_schema_extra={
                "typename": "XP_VerfahrensMerkmal",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    hatGenerAttribut: Annotated[
        list[
            XPDatumAttribut
            | XPDoubleAttribut
            | XPIntegerAttribut
            | XPStringAttribut
            | XPURLAttribut
        ]
        | None,
        Field(
            description="Erweiterung der vorgegebenen Attribute durch generische Attribute.",
            json_schema_extra={
                "typename": [
                    "XP_DatumAttribut",
                    "XP_DoubleAttribut",
                    "XP_IntegerAttribut",
                    "XP_StringAttribut",
                    "XP_URLAttribut",
                ],
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    externeReferenz: Annotated[
        list[XPSpezExterneReferenz] | None,
        Field(
            description="Referenz auf ein Dokument, einen Datenbankeintrag oder einen georeferenzierten Rasterplan.",
            json_schema_extra={
                "typename": "XP_SpezExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    texte: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf einen textlich formulierten Planinhalt.",
            json_schema_extra={
                "typename": [
                    "BP_TextAbschnitt",
                    "FP_TextAbschnitt",
                    "LP_TextAbschnitt",
                    "RP_TextAbschnitt",
                    "SO_TextAbschnitt",
                ],
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    begruendungsTexte: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf einen Abschnitt der Begründung. Diese Relation darf nicht verwendet werden, wenn die Begründung als Gesamt-Dokument referiert werden soll. In diesem Fall sollte über das Attribut externeReferenz eine Objekt XP_SpezExterneReferent mit typ=1010 (Begruendung) verwendet werden.",
            json_schema_extra={
                "typename": "XP_BegruendungAbschnitt",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPBereich(XPBereich):
    """
    Diese Klasse modelliert einen Bereich eines Bebauungsplans, z.B. einen räumlichen oder sachlichen Teilbereich.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    versionBauNVODatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version der BauNVO.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauNVOText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation der zugrunde liegenden Version der BauNVO.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version des BauGB.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation der zugrunde liegenden Version des BauGB.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum einer zugrunde liegenden anderen Rechtsgrundlage als BauGB / BauNVO.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation einer zugrunde liegenden anderen Rechtsgrundlage als BauGB / BauNVO.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gehoertZuPlan: Annotated[
        AnyUrl | UUID,
        Field(
            description="Referenz eines Bereichs eines Bebauungsplans auf das zugehörige Plan-Objekt.",
            json_schema_extra={
                "typename": "BP_Plan",
                "stereotype": "Association",
                "reverseProperty": "bereich",
                "sourceOrTarget": "source",
                "multiplicity": "1",
            },
        ),
    ]


class BPObjekt(XPObjekt):
    """
    Basisklasse für alle raumbezogenen Festsetzungen,  Hinweise, Vermerke und Kennzeichnungen eines Bebauungsplans.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "9998"],
        Field(
            description="Rechtliche Charakterisierung des Planinhaltes.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Festsetzung",
                        "description": "Festsetzung in Bebauungsplan.",
                    },
                    "2000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahme aus anderen Planwerken.",
                    },
                    "3000": {"name": "Hinweis", "description": "Hinweis nach BauGB"},
                    "4000": {
                        "name": "Vermerk",
                        "description": "Vermerk nach § 5 BauGB",
                    },
                    "5000": {
                        "name": "Kennzeichnung",
                        "description": "Kennzeichnung von Flächen nach $9 Absatz 5 BauGB. Kennzeichnungen sind keine rechtsverbindlichen Festsetzungen, sondern Hinweise auf Besonderheiten (insbesondere der Baugrundverhältnisse), deren Kenntnis für das Verständnis des Bebauungsplans und seiner Festsetzungen wie auch für die Vorbereitung und Genehmigung von Vorhaben notwendig sind.",
                    },
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Der Rechtscharakter des BPlan-Inhaltes ist unbekannt.",
                    },
                },
                "typename": "BP_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    refTextInhalt: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz eines raumbezogenen Fachobjektes auf textuell formulierte Planinhalte, insbesondere textliche Festsetzungen.",
            json_schema_extra={
                "typename": [
                    "BP_TextAbschnitt",
                    "FP_TextAbschnitt",
                    "LP_TextAbschnitt",
                    "RP_TextAbschnitt",
                    "SO_TextAbschnitt",
                ],
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    wirdAusgeglichenDurchFlaeche: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf Ausgleichsfläche, die den Eingriff ausgleicht.",
            json_schema_extra={
                "typename": "BP_AusgleichsFlaeche",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    wirdAusgeglichenDurchABE: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf eine Anpflanzungs-, Bindungs- oder Erhaltungsmaßnahme, durch die ein Eingriff ausgeglichen wird.",
            json_schema_extra={
                "typename": "BP_AnpflanzungBindungErhaltung",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    wirdAusgeglichenDurchSPEMassnahme: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf eine Schutz-, Pflege- oder Entwicklungsmaßnahme, durch die ein Eingriff ausgeglichen wird.",
            json_schema_extra={
                "typename": "BP_SchutzPflegeEntwicklungsMassnahme",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    wirdAusgeglichenDurchSPEFlaeche: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf eine Schutz-, Pflege- oder Entwicklungs-Fläche, die den Eingriff ausgleicht.",
            json_schema_extra={
                "typename": "BP_SchutzPflegeEntwicklungsFlaeche",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    wirdAusgeglichenDurchMassnahme: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Verweis auf eine  Ausgleichsmaßnahme, die einen vorgenommenen Eingriff ausgleicht.",
            json_schema_extra={
                "typename": "BP_AusgleichsMassnahme",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    laermkontingent: Annotated[
        BPEmissionskontingentLaerm | None,
        Field(
            description="Festsetzung eines Lärmemissionskontingent nach DIN 45691",
            json_schema_extra={
                "typename": "BP_EmissionskontingentLaerm",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    laermkontingentGebiet: Annotated[
        list[BPEmissionskontingentLaermGebiet] | None,
        Field(
            description="Festsetzung von Lärmemissionskontingenten nach DIN 45691, die einzelnen Immissionsgebieten zugeordnet sind",
            json_schema_extra={
                "typename": "BP_EmissionskontingentLaermGebiet",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    zusatzkontingent: Annotated[
        AnyUrl | UUID | None,
        Field(
            description="Festsetzung von Zusatzkontingenten für die Lärmemission, die einzelnen Richtungssektoren zugeordnet sind. Die einzelnen Richtungssektoren werden parametrisch definiert.",
            json_schema_extra={
                "typename": "BP_ZusatzkontingentLaerm",
                "stereotype": "Association",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zusatzkontingentFlaeche: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Festsetzung von Zusatzkontingenten für die Lärmemission, die einzelnen Richtungssektoren zugeordnet sind. Die einzelnen Richtungssektoren werden durch explizite Flächen definiert.",
            json_schema_extra={
                "typename": "BP_ZusatzkontingentLaermFlaeche",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    richtungssektorGrenze: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Zuordnung einer Richtungssektor-Grenze für die Festlegung zusätzlicher Lärmkontingente",
            json_schema_extra={
                "typename": "BP_RichtungssektorGrenze",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPPlan(XPPlan):
    """
    Die Klasse modelliert einen Bebauungsplan
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    gemeinde: Annotated[
        list[XPGemeinde],
        Field(
            description="Die für den Plan zuständige Gemeinde.",
            json_schema_extra={
                "typename": "XP_Gemeinde",
                "stereotype": "DataType",
                "multiplicity": "1..*",
            },
            min_length=1,
        ),
    ]
    planaufstellendeGemeinde: Annotated[
        list[XPGemeinde] | None,
        Field(
            description="Die für die ursprüngliche Planaufstellung zuständige Gemeinde, falls diese nicht unter dem Attribut gemeinde aufgeführt ist. Dies kann z.B. nach Gemeindefusionen der Fall sein.",
            json_schema_extra={
                "typename": "XP_Gemeinde",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    plangeber: Annotated[
        XPPlangeber | None,
        Field(
            description="Für den Plan verantwortliche Stelle.",
            json_schema_extra={
                "typename": "XP_Plangeber",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    planArt: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "10001",
                "10002",
                "3000",
                "3100",
                "4000",
                "40000",
                "40001",
                "40002",
                "5000",
                "7000",
                "9999",
            ]
        ],
        Field(
            description="Typ des vorliegenden Bebauungsplans.",
            json_schema_extra={
                "typename": "BP_PlanArt",
                "stereotype": "Enumeration",
                "multiplicity": "1..*",
                "enumDescription": {
                    "1000": {
                        "name": "BPlan",
                        "description": "Planwerk der verbindlichen Bauleitplanung auf kommunaler Ebene",
                    },
                    "10000": {
                        "name": "EinfacherBPlan",
                        "description": "Einfacher BPlan, §30 Abs. 3 BauGB.",
                    },
                    "10001": {
                        "name": "QualifizierterBPlan",
                        "description": "Qualifizierter BPlan nach §30 Abs. 1 BauGB.",
                    },
                    "10002": {
                        "name": "BebauungsplanZurWohnraumversorgung",
                        "description": "Bebauungsplan zur Wohnraumversorgung für im Zusammenhang bebaute Ortsteile (§ 34) nach §9 Absatz 2d BauGB",
                    },
                    "3000": {
                        "name": "VorhabenbezogenerBPlan",
                        "description": "Vorhabensbezogener Bebauungsplan nach §12 BauGB",
                    },
                    "3100": {
                        "name": "VorhabenUndErschliessungsplan",
                        "description": "Satzung über Vorhaben- und Erschließungsplan gemäß §7 Maßnahmengesetz (BauGB-MaßnahmenG) von 1993",
                    },
                    "4000": {
                        "name": "InnenbereichsSatzung",
                        "description": "Kommunale Satzung gemäß §34 BauGB",
                    },
                    "40000": {
                        "name": "KlarstellungsSatzung",
                        "description": "Klarstellungssatzung nach  § 34 Abs.4 Nr.1 BauGB.",
                    },
                    "40001": {
                        "name": "EntwicklungsSatzung",
                        "description": "Entwicklungssatzung nach  § 34 Abs.4 Nr. 2 BauGB.",
                    },
                    "40002": {
                        "name": "ErgaenzungsSatzung",
                        "description": "Ergänzungssatzung nach  § 34 Abs.4 Nr. 3 BauGB.",
                    },
                    "5000": {
                        "name": "AussenbereichsSatzung",
                        "description": "Außenbereichssatzung nach § 35 Abs. 6 BauGB.",
                    },
                    "7000": {
                        "name": "OertlicheBauvorschrift",
                        "description": "Örtliche Bauvorschrift.",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstige Planart."},
                },
            },
            min_length=1,
        ),
    ]
    sonstPlanArt: Annotated[
        AnyUrl | None,
        Field(
            description='Über eine Codeliste spezifizierte  "Sonstige Planart", wenn das Attribut "planArt" den Wert 9999 (Sonstiges) hat.',
            json_schema_extra={
                "typename": "BP_SonstPlanArt",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    verfahren: Annotated[
        Literal["1000", "2000", "3000", "4000"] | None,
        Field(
            description="Verfahrensart der BPlan-Aufstellung oder -Änderung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Normal",
                        "description": "Normales BPlan Verfahren.",
                    },
                    "2000": {
                        "name": "Parag13",
                        "description": "BPlan Verfahren nach Paragraph 13 BauGB.",
                    },
                    "3000": {
                        "name": "Parag13a",
                        "description": "BPlan Verfahren nach Paragraph 13a BauGB.",
                    },
                    "4000": {
                        "name": "Parag13b",
                        "description": "BPlan Verfahren nach Paragraph 13b BauGB.",
                    },
                },
                "typename": "BP_Verfahren",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rechtsstand: Annotated[
        Literal[
            "1000",
            "2000",
            "2100",
            "2200",
            "2300",
            "2400",
            "3000",
            "4000",
            "4500",
            "5000",
            "50000",
            "50001",
        ]
        | None,
        Field(
            description="Aktueller Rechtsstand des Plans.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Aufstellungsbeschluss",
                        "description": "Ein Aufstellungsbeschluss der Gemeinde liegt vor.",
                    },
                    "2000": {
                        "name": "Entwurf",
                        "description": "Ein Planentwurf liegt vor.",
                    },
                    "2100": {
                        "name": "FruehzeitigeBehoerdenBeteiligung",
                        "description": "Die frühzeitige Beteiligung der Behörden (§ 4 Abs. 1 BauGB) hat stattgefunden.",
                    },
                    "2200": {
                        "name": "FruehzeitigeOeffentlichkeitsBeteiligung",
                        "description": "Die frühzeitige Beteiligung der Öffentlichkeit (§ 3 Abs. 1 BauGB), bzw. bei einem Verfahren nach § 13a BauGB die Unterrichtung der Öffentlichkeit (§ 13a Abs. 3 BauGB) hat stattgefunden.",
                    },
                    "2300": {
                        "name": "BehoerdenBeteiligung",
                        "description": "Die Beteiligung der Behörden hat stattgefunden (§ 4 Abs. 2 BauGB).",
                    },
                    "2400": {
                        "name": "OeffentlicheAuslegung",
                        "description": "Der Plan hat öffentlich ausgelegen. (§ 3 Abs. 2 BauGB).",
                    },
                    "3000": {
                        "name": "Satzung",
                        "description": "Die Satzung wurde durch Beschluss der Gemeinde verabschiedet.",
                    },
                    "4000": {
                        "name": "InkraftGetreten",
                        "description": "Der Plan ist in kraft getreten.",
                    },
                    "4500": {
                        "name": "TeilweiseUntergegangen",
                        "description": "Der Plan ist, z. B. durch einen Gerichtsbeschluss oder neuen Plan, teilweise untergegangen.",
                    },
                    "5000": {
                        "name": "Untergegangen",
                        "description": "Der Plan wurde außer Kraft gesetzt.",
                    },
                    "50000": {
                        "name": "Aufgehoben",
                        "description": "Der Plan wurde durch ein förmliches Verfahren aufgehoben",
                    },
                    "50001": {
                        "name": "AusserKraft",
                        "description": "Der Plan ist ohne förmliches Verfahren z.B. durch Überplanung außer Kraft getreten",
                    },
                },
                "typename": "BP_Rechtsstand",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    status: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter aktueller Status des Plans.",
            json_schema_extra={
                "typename": "BP_Status",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    hoehenbezug: Annotated[
        str | None,
        Field(
            description="Bei Höhenangaben im Plan standardmäßig verwendeter Höhenbezug (z.B. Höhe über NN).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    aenderungenBisDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum der berücksichtigten Plan-Änderungen.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    aufstellungsbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Aufstellungsbeschlusses.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    veraenderungssperreBeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Beschlussdatum der Veränderungssperre im gesamten Geltungsbereich",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    veraenderungssperreDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum, ab dem die Veränderungssperre im gesamten Geltungsbereich gilt",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    veraenderungssperreEndDatum: Annotated[
        date_aliased | None,
        Field(
            description="Enddatum der Veränderungssperre im gesamten Geltungsbereich",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    verlaengerungVeraenderungssperre: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Gibt an, ob die Veränderungssperre bereits ein- oder zweimal verlängert wurde",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Keine",
                        "description": "Veränderungssperre wurde noch nicht verlängert.",
                    },
                    "2000": {
                        "name": "ErsteVerlaengerung",
                        "description": "Veränderungssperre wurde einmal verlängert.",
                    },
                    "3000": {
                        "name": "ZweiteVerlaengerung",
                        "description": "Veränderungssperre wurde zweimal verlängert.",
                    },
                },
                "typename": "XP_VerlaengerungVeraenderungssperre",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    auslegungsStartDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="Start-Datum des Auslegungs-Zeitraums. Bei mehrfacher öffentlicher Auslegung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    auslegungsEndDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="End-Datum des Auslegungs-Zeitraums. Bei mehrfacher öffentlicher Auslegung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    traegerbeteiligungsStartDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="Start-Datum der Trägerbeteiligung. Bei mehrfacher Trägerbeteiligung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    traegerbeteiligungsEndDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="End-Datum der Trägerbeteiligung. Bei mehrfacher Trägerbeteiligung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    satzungsbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Satzungsbeschlusses.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rechtsverordnungsDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum der Rechtsverordnung.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    inkrafttretensDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Inkrafttretens.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ausfertigungsDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum der Ausfertigung.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    veraenderungssperre: Annotated[
        bool | None,
        Field(
            description='Gibt an, ob es im gesamten Geltungsbereich des Plans eine Veränderungssperre gibt.\r\nDies Attribut ist als "veraltet" gekennzeichnet und wird in der nächsten Hauptversion des Standards wegfallen. Es sollte der Gültigkeitszeitraum der Veränderungssperre spezifiziert werden.',
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    staedtebaulicherVertrag: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob es zum Plan einen städtebaulichen Vertrag gibt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    erschliessungsVertrag: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob es für den Plan einen Erschließungsvertrag gibt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    durchfuehrungsVertrag: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob für das Planungsgebiet einen Durchführungsvertrag (Kombination aus Städtebaulichen Vertrag und Erschließungsvertrag) gibt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    gruenordnungsplan: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob für den Plan ein zugehöriger Grünordnungsplan existiert.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    versionBauNVODatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version der BauNVO",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauNVOText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation der zugrunde liegenden Version der BauNVO",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version des BauGB.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation der zugrunde liegenden Version des BauGB.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum einer zugrunde liegenden anderen Rechtsgrundlage als BauGB / BauNVO.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation einer zugrunde liegenden anderen Rechtsgrundlage als BauGB / BauNVO.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bereich: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz eines Bebauungsplans auf einen Bereich",
            json_schema_extra={
                "typename": "BP_Bereich",
                "stereotype": "Association",
                "reverseProperty": "gehoertZuPlan",
                "sourceOrTarget": "target",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPPunktobjekt(BPObjekt):
    """
    Basisklasse für alle Objekte eines Bebauungsplans mit punktförmigem Raumbezug (Einzelpunkt oder Punktmenge).
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point | definitions.MultiPoint,
        Field(
            description="Punktförmiger Raumbezug (Einzelpunkt oder Punktmenge).",
            json_schema_extra={
                "typename": "XP_Punktgeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    nordwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Orientierung des Punktobjektes als Winkel gegen die Nordrichtung. Zählweise im geographischen Sinn (von Nord über Ost nach Süd und West).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class BPZusatzkontingentLaerm(BPPunktobjekt):
    """
    Parametrische Spezifikation von zusätzlichen Lärmemissionskontingenten für einzelne Richtungssektoren (DIN 45691, Anhang 2).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    bezeichnung: Annotated[
        str | None,
        Field(
            description="Bezeichnung des Kontingentes",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    richtungssektor: Annotated[
        list[BPRichtungssektor] | None,
        Field(
            description="Spezifikation der Richtungssektoren",
            json_schema_extra={
                "typename": "BP_Richtungssektor",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class FPBereich(XPBereich):
    """
    Diese Klasse modelliert einen Bereich eines Flächennutzungsplans.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    versionBauNVODatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version der BauNVO\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauNVOText: Annotated[
        str | None,
        Field(
            description="Zugrunde liegende Version der BauNVO. \r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version des BauGB.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBText: Annotated[
        str | None,
        Field(
            description="Zugrunde liegende Version des BauGB.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum einer zugrunde liegenden anderen Rechtsgrundlage als BauGB / BauNVO.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation einer zugrunde liegenden anderen Rechtsgrundlage als BauGB / BauNVO.\r\n\r\nDas Attribut ist veraltet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen das gleichnamige Attribut von BP_Plan verwendet werden.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gehoertZuPlan: Annotated[
        AnyUrl | UUID,
        Field(
            description="Referenz auf den Flächennutzungsplan, zu dem das Bereichsobjekt gehört.",
            json_schema_extra={
                "typename": "FP_Plan",
                "stereotype": "Association",
                "reverseProperty": "bereich",
                "sourceOrTarget": "target",
                "multiplicity": "1",
            },
        ),
    ]


class FPObjekt(XPObjekt):
    """
    Basisklasse für alle Fachobjekte des Flächennutzungsplans.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "9998"],
        Field(
            description="Rechtliche Charakterisierung des Planinhalts",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Darstellung",
                        "description": "Darstellung im Flächennutzungsplan",
                    },
                    "2000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahme aus anderen Planwerken.",
                    },
                    "3000": {"name": "Hinweis", "description": "Hinweis nach BauGB"},
                    "4000": {"name": "Vermerk", "description": "Vermerk nach §9 BauGB"},
                    "5000": {
                        "name": "Kennzeichnung",
                        "description": "Kennzeichnung nach §5 Abs. (3) BauGB.",
                    },
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Der Rechtscharakter des FPlan-Inhaltes ist unbekannt.",
                    },
                },
                "typename": "FP_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    spezifischePraegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte spezifische bauliche Prägung einer Darstellung.",
            json_schema_extra={
                "typename": "FP_SpezifischePraegungTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    vonGenehmigungAusgenommen: Annotated[
        bool | None,
        Field(
            description="Angabe, ob Teile des Flächennutzungsplans nach §6 Abs. 3 BauGB von der Genehmigung ausgenommen sind",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    refTextInhalt: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz eines raumbezogenen Fachobjektes auf textuell formulierte Planinhalte.",
            json_schema_extra={
                "typename": [
                    "BP_TextAbschnitt",
                    "FP_TextAbschnitt",
                    "LP_TextAbschnitt",
                    "RP_TextAbschnitt",
                    "SO_TextAbschnitt",
                ],
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    wirdAusgeglichenDurchFlaeche: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf eine Ausgleichsfläche, die den Eingriff ausgleicht.",
            json_schema_extra={
                "typename": "FP_AusgleichsFlaeche",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    wirdAusgeglichenDurchSPE: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf eine Schutz-,Pflege- oder Entwicklungsmaßnahme, die den Eingriff ausgleicht.",
            json_schema_extra={
                "typename": "FP_SchutzPflegeEntwicklung",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class FPPlan(XPPlan):
    """
    Klasse zur Modellierung eines gesamten Flächennutzungsplans.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    gemeinde: Annotated[
        list[XPGemeinde],
        Field(
            description="Zuständige Gemeinde",
            json_schema_extra={
                "typename": "XP_Gemeinde",
                "stereotype": "DataType",
                "multiplicity": "1..*",
            },
            min_length=1,
        ),
    ]
    planaufstellendeGemeinde: Annotated[
        list[XPGemeinde] | None,
        Field(
            description="Die für die ursprüngliche Planaufstellung zuständige Gemeinde, falls diese nicht unter dem Attribut gemeinde aufgeführt ist. Dies kann z.B. nach Gemeindefusionen der Fall sein.",
            json_schema_extra={
                "typename": "XP_Gemeinde",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    plangeber: Annotated[
        XPPlangeber | None,
        Field(
            description="Für die Planung zuständige Institution",
            json_schema_extra={
                "typename": "XP_Plangeber",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    planArt: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "9999"],
        Field(
            description="Typ des FPlans",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "FPlan",
                        "description": "Flächennutzungsplan nach § 5 BauGB.",
                    },
                    "2000": {
                        "name": "GemeinsamerFPlan",
                        "description": "Gemeinsamer Flächennutzungsplan nach § 204 BauGB",
                    },
                    "3000": {
                        "name": "RegFPlan",
                        "description": "Regionaler Flächennutzungsplan, der zugleich die Funktion eines Regionalplans als auch eines gemeinsamen Flächennutzungsplans nach § 204 BauGB erfüllt",
                    },
                    "4000": {
                        "name": "FPlanRegPlan",
                        "description": "Flächennutzungsplan mit regionalplanerischen Festlegungen (nur in HH, HB, B).",
                    },
                    "5000": {
                        "name": "SachlicherTeilplan",
                        "description": "Sachlicher Teilflächennutzungsplan nach §5 Abs. 2b BauGB.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiger Flächennutzungsplan",
                    },
                },
                "typename": "FP_PlanArt",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    sonstPlanArt: Annotated[
        AnyUrl | None,
        Field(
            description='Sonstiger Typ des FPlans bei "planArt" == 9999.',
            json_schema_extra={
                "typename": "FP_SonstPlanArt",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sachgebiet: Annotated[
        str | None,
        Field(
            description="Sachgebiet eines Teilflächennutzungsplans.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    verfahren: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Verfahren nach dem ein FPlan aufgestellt oder geändert wird.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Normal",
                        "description": "Normales FPlan Verfahren.",
                    },
                    "2000": {
                        "name": "Parag13",
                        "description": "FPlan Verfahren nach Parag 13 BauGB.",
                    },
                },
                "typename": "FP_Verfahren",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rechtsstand: Annotated[
        Literal[
            "1000",
            "2000",
            "2100",
            "2200",
            "2300",
            "2400",
            "3000",
            "4000",
            "5000",
            "50000",
            "50001",
        ]
        | None,
        Field(
            description="Aktueller Rechtsstand des Plans.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Aufstellungsbeschluss",
                        "description": "Der Aufstellungsbeschluss liegt vor.",
                    },
                    "2000": {
                        "name": "Entwurf",
                        "description": "Ein Planentwurf liegt vor.",
                    },
                    "2100": {
                        "name": "FruehzeitigeBehoerdenBeteiligung",
                        "description": "Die frühzeitige Bürgerbeteiligung ist abgeschlossen.",
                    },
                    "2200": {
                        "name": "FruehzeitigeOeffentlichkeitsBeteiligung",
                        "description": "Die frühzeitige Beteiligun der Öffentlichkeit ist abgeschlossen.",
                    },
                    "2300": {
                        "name": "BehoerdenBeteiligung",
                        "description": "Die Behördenbeteiligung ist abgeschlossen.",
                    },
                    "2400": {
                        "name": "OeffentlicheAuslegung",
                        "description": "Die öffentliche Auslegung ist beendet.",
                    },
                    "3000": {
                        "name": "Plan",
                        "description": "Der Plan ist technisch erstellt worden.",
                    },
                    "4000": {
                        "name": "Wirksamkeit",
                        "description": "Der Plan ist rechtswirksam.",
                    },
                    "5000": {
                        "name": "Untergegangen",
                        "description": "Der Plan wurde außer Kraft gesetzt",
                    },
                    "50000": {
                        "name": "Aufgehoben",
                        "description": "Der Plan wurde durch ein förmliches Verfahren aufgehoben",
                    },
                    "50001": {
                        "name": "AusserKraft",
                        "description": "Der Plan ist ohne förmliches Verfahren z.B. durch Überplanung außer Kraft getreten",
                    },
                },
                "typename": "FP_Rechtsstand",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    status: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter Status des Plans.",
            json_schema_extra={
                "typename": "FP_Status",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    aufstellungsbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Plan-Aufstellungsbeschlusses.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    auslegungsStartDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="Start-Datum der öffentlichen Auslegung. Bei mehrfacher öffentlicher Auslegung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    auslegungsEndDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="End-Datum der öffentlichen Auslegung. Bei mehrfacher öffentlicher Auslegung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    traegerbeteiligungsStartDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="Start-Datum der Trägerbeteiligung. Bei mehrfacher Trägerbeteiligung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    traegerbeteiligungsEndDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="End-Datum der Trägerbeteiligung. Bei mehrfacher Trägerbeteiligung  können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    aenderungenBisDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum, bis zu dem Änderungen des Plans berücksichtigt wurden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    entwurfsbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Entwurfsbeschlusses",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    planbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Planbeschlusses",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    wirksamkeitsDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum der Wirksamkeit",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauNVODatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version der BauNVO",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauNVOText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation der zugrunde liegenden Version der BauNVO",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version des BauGB.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation der zugrunde liegenden Version des BauGB.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum einer zugrunde liegenden anderen Rechtsgrundlage als BauGB / BauNVO.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation einer zugrunde liegenden anderen Rechtsgrundlage als BauGB / BauNVO.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bereich: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf einen Bereich des Flächennutzungsplans",
            json_schema_extra={
                "typename": "FP_Bereich",
                "stereotype": "Association",
                "reverseProperty": "gehoertZuPlan",
                "sourceOrTarget": "source",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class FPPunktobjekt(FPObjekt):
    """
    Basisklasse für alle Objekte eines Flächennutzungsplans mit punktförmigem Raumbezug (Einzelpunkt oder Punktmenge).
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point | definitions.MultiPoint,
        Field(
            description="Punktförmiger Raumbezug (Einzelpunkt oder Punktmenge).",
            json_schema_extra={
                "typename": "XP_Punktgeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    nordwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Orientierung des Punktobjektes als Winkel gegen die Nordrichtung. Zählweise im geographischen Sinn (von Nord über Ost nach Süd und West).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class LPBereich(XPBereich):
    """
    Ein Bereich eines Landschaftsplans.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    gehoertZuPlan: Annotated[
        AnyUrl | UUID,
        Field(
            description="Referenz auf den Landschaftsplan, zu dem der Bereich gehört.",
            json_schema_extra={
                "typename": "LP_Plan",
                "stereotype": "Association",
                "reverseProperty": "bereich",
                "sourceOrTarget": "source",
                "multiplicity": "1",
            },
        ),
    ]


class LPObjekt(XPObjekt):
    """
    Basisklasse für alle spezifischen Inhalte eines Landschaftsplans.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "9998", "9999"],
        Field(
            description="Rechtliche Charakterisierung des Planinhalts.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Festsetzung",
                        "description": "Festsetzung im Landschaftsplan",
                    },
                    "2000": {
                        "name": "Geplant",
                        "description": "Geplante Festsetzung im Landschaftsplan",
                    },
                    "3000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahmen im Landschaftsplan",
                    },
                    "4000": {
                        "name": "DarstellungKennzeichnung",
                        "description": "Darstellungen und Kennzeichnungen im Landschaftsplan.",
                    },
                    "5000": {
                        "name": "FestsetzungInBPlan",
                        "description": "Planinhalt aus dem Bereich Naturschutzrecht, der in einem BPlan festgesetzt wird.",
                    },
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Der Rechtscharakter des LPlan-Inhalts ist unbekannt.",
                    },
                    "9999": {
                        "name": "SonstigerStatus",
                        "description": "Sonstiger Rechtscharakter",
                    },
                },
                "typename": "LP_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    konkretisierung: Annotated[
        str | None,
        Field(
            description="Textliche Konkretisierung der rechtlichen Charakterisierung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refTextInhalt: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz eines raumbezogenen Fachobjektes auf textuell formulierte Planinhalte.",
            json_schema_extra={
                "typename": [
                    "BP_TextAbschnitt",
                    "FP_TextAbschnitt",
                    "LP_TextAbschnitt",
                    "RP_TextAbschnitt",
                    "SO_TextAbschnitt",
                ],
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class LPPlan(XPPlan):
    """
    Die Klasse modelliert ein Planwerk mit landschaftsplanerischen Festlegungen, Darstellungen bzw. Festsetzungen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    bundesland: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "1300",
            "1400",
            "1500",
            "1600",
            "1700",
            "1800",
            "1900",
            "2000",
            "2100",
            "2200",
            "2300",
            "2400",
            "2500",
            "3000",
        ],
        Field(
            description="Zuständiges Bundesland",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "BB", "description": "Brandenburg"},
                    "1100": {"name": "BE", "description": "Berlin"},
                    "1200": {"name": "BW", "description": "Baden-Württemberg"},
                    "1300": {"name": "BY", "description": "Bayern"},
                    "1400": {"name": "HB", "description": "Bremen"},
                    "1500": {"name": "HE", "description": "Hessen"},
                    "1600": {"name": "HH", "description": "Hamburg"},
                    "1700": {"name": "MV", "description": "Mecklenburg-Vorpommern"},
                    "1800": {"name": "NI", "description": "Niedersachsen"},
                    "1900": {"name": "NW", "description": "Nordrhein-Westfalen"},
                    "2000": {"name": "RP", "description": "Rheinland-Pfalz"},
                    "2100": {"name": "SH", "description": "Schleswig-Holstein"},
                    "2200": {"name": "SL", "description": "Saarland"},
                    "2300": {"name": "SN", "description": "Sachsen"},
                    "2400": {"name": "ST", "description": "Sachsen-Anhalt"},
                    "2500": {"name": "TH", "description": "Thüringen"},
                    "3000": {"name": "Bund", "description": "Der Bund."},
                },
                "typename": "XP_Bundeslaender",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    rechtlicheAussenwirkung: Annotated[
        bool,
        Field(
            description="Gibt an, ob der Plan eine rechtliche Außenwirkung hat.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    planArt: Annotated[
        list[Literal["1000", "2000", "3000", "4000", "9999"]],
        Field(
            description="Typ des vorliegenden Landschaftsplans.",
            json_schema_extra={
                "typename": "LP_PlanArt",
                "stereotype": "Enumeration",
                "multiplicity": "1..*",
                "enumDescription": {
                    "1000": {
                        "name": "Landschaftsprogramm",
                        "description": "ÜÜberörtliche konkretisierte Ziele, Erfordernisse und Maßnahmen des Naturschutzes und der Landschaftspflege auf räumlicher Ebene eines Bundeslandes",
                    },
                    "2000": {
                        "name": "Landschaftsrahmenplan",
                        "description": "Überörtliche konkretisierte Ziele, Erfordernisse und Maßnahmen des Naturschutzes und der Landschaftspflege für räumliche Teilbereiche eines Bundeslandes",
                    },
                    "3000": {
                        "name": "Landschaftsplan",
                        "description": "Planwerk mit konkretisierten Zielen, Erfordernissen und Maßnahmen des Naturschutzes und der Landschaftspflege auf gesamtstädtischer räumlicher Ebene",
                    },
                    "4000": {
                        "name": "Gruenordnungsplan",
                        "description": "Die für die örtliche Ebene konkretisierten Ziele, Erfordernisse und Maßnahmen des Naturschutzes und der Landschaftspflege werden für Teile eines Gemeindegebiets in Grünordnungsplänen dargestellt. (§ 11, Abs .1  BNatSchG)",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstige Planart"},
                },
            },
            min_length=1,
        ),
    ]
    sonstPlanArt: Annotated[
        AnyUrl | None,
        Field(
            description='Spezifikation einer "Sonstigen Planart", wenn kein Plantyp aus der Enumeration LP_PlanArt zutreffend ist. Das Attribut "planArt" muss in diesem Fall der Wert 9999 haben.',
            json_schema_extra={
                "typename": "LP_SonstPlanArt",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    planungstraegerGKZ: Annotated[
        str,
        Field(
            description="Gemeindekennziffer des Planungsträgers.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    planungstraeger: Annotated[
        str | None,
        Field(
            description="Bezeichnung des Planungsträgers.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rechtsstand: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000"] | None,
        Field(
            description="Rechtsstand des Plans",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Aufstellungsbeschluss",
                        "description": "Der Aufstellungsbeschluss wurde getroffen.",
                    },
                    "2000": {
                        "name": "Entwurf",
                        "description": "Ein Planentwurf liegt vor",
                    },
                    "3000": {
                        "name": "Plan",
                        "description": "Der Plan ist technisch erstellt, aber noch nicht rechtwirksam",
                    },
                    "4000": {
                        "name": "Wirksamkeit",
                        "description": "Der Plan ist rechtswirksam.",
                    },
                    "5000": {
                        "name": "Untergegangen",
                        "description": "Der Plan ist nicht mehr rechtswirksam.",
                    },
                },
                "typename": "LP_Rechtsstand",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    aufstellungsbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Aufstellungsbeschlusses",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    auslegungsDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="Datum der öffentlichen Auslegung.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    tOeBbeteiligungsDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="Datum der Beteiligung der Träger öffentlicher Belange.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    oeffentlichkeitsbeteiligungDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="Datum der Öffentlichkeits-Beteiligung.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    aenderungenBisDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum, bis zum Planänderungen berücksichtigt wurden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    entwurfsbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Entwurfsbeschlusses.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    planbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Planbeschlusses.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    inkrafttretenDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Inkrafttretens.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstVerfahrensDatum: Annotated[
        date_aliased | None,
        Field(
            description="Sonstiges Verfahrens-Datum.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bereich: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf einen Bereich des Landschaftsplans.",
            json_schema_extra={
                "typename": "LP_Bereich",
                "stereotype": "Association",
                "reverseProperty": "gehoertZuPlan",
                "sourceOrTarget": "target",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class LPPunktobjekt(LPObjekt):
    """
    Basisklasse für alle Objekte eines Landschaftsplans mit punktförmigem Raumbezug (Einzelpunkt oder Punktmenge).
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point | definitions.MultiPoint,
        Field(
            description="Punktförmiger Raumbezug (Einzelpunkt oder Punktmenge).",
            json_schema_extra={
                "typename": "XP_Punktgeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    nordwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Orientierung des Punktobjektes als Winkel gegen die Nordrichtung. Zählweise im geographischen Sinn (von Nord über Ost nach Süd und West).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class RPBereich(XPBereich):
    """
    Die Klasse RP_Bereich modelliert einen Bereich eines Raumordnungsplans. Bereiche strukturieren Pläne räumlich und inhaltlich.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    versionBROG: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version des ROG.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBROGText: Annotated[
        str | None,
        Field(
            description="Titel der zugrunde liegenden Version des Bundesraumordnungsgesetzes.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionLPLG: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum des zugrunde liegenden Landesplanungsgesetzes.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionLPLGText: Annotated[
        str | None,
        Field(
            description="Titel des zugrunde liegenden Landesplanungsgesetzes.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    geltungsmassstab: Annotated[
        int | None,
        Field(
            description="(Rechtlicher) Geltungsmaßstab des Bereichs.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gehoertZuPlan: Annotated[
        AnyUrl | UUID,
        Field(
            description="Relation auf den zugehörigen Plan",
            json_schema_extra={
                "typename": "RP_Plan",
                "stereotype": "Association",
                "reverseProperty": "bereich",
                "sourceOrTarget": "source",
                "multiplicity": "1",
            },
        ),
    ]


class RPObjekt(XPObjekt):
    """
    RP_Objekt ist die Basisklasse für alle spezifischen Festlegungen eines Raumordnungsplans. Sie selbst ist abstrakt, d.h. sie wird selbst nicht als eigenes Objekt verwendet, sondern vererbt nur ihre Attribute an spezielle Klassen.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal[
            "1000",
            "2000",
            "3000",
            "4000",
            "5000",
            "6000",
            "7000",
            "8000",
            "9000",
            "9998",
        ],
        Field(
            description="Rechtscharakter des Planinhalts.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "ZielDerRaumordnung",
                        "description": "Ziel der Raumordnung. Verbindliche räumliche und sachliche Festlegung zur Entwicklung, Ordnung und Sicherung des Raumes.",
                    },
                    "2000": {
                        "name": "GrundsatzDerRaumordnung",
                        "description": "Grundsätze der Raumordnung sind nach §3 Abs. Aussagen zur Entwicklung, Ordnung und Sicherung des Raums als Vorgaben für nachfolgende Abwägungs- oder Ermessensentscheidungen. Grundsätze der Raumordnung können durch Gesetz oder Festlegungen in einem Raumordnungsplan (§7 Abs. 1 und 2, ROG) aufgestellt werden.",
                    },
                    "3000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahme.",
                    },
                    "4000": {
                        "name": "NachrichtlicheUebernahmeZiel",
                        "description": "Nachrichtliche Übernahme Ziel.",
                    },
                    "5000": {
                        "name": "NachrichtlicheUebernahmeGrundsatz",
                        "description": "Nachrichtliche Übernahme Grundsatz.",
                    },
                    "6000": {
                        "name": "NurInformationsgehalt",
                        "description": "Nur Informationsgehalt.",
                    },
                    "7000": {
                        "name": "TextlichesZiel",
                        "description": "Textliches Ziel.",
                    },
                    "8000": {
                        "name": "ZielundGrundsatz",
                        "description": "Ziel und Grundsatz.",
                    },
                    "9000": {"name": "Vorschlag", "description": "Vorschlag."},
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Unbekannter Rechtscharakter",
                    },
                },
                "typename": "RP_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    konkretisierung: Annotated[
        str | None,
        Field(
            description="Konkretisierung des Rechtscharakters.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gebietsTyp: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1100",
                "1101",
                "1200",
                "1300",
                "1400",
                "1500",
                "1501",
                "1600",
                "1700",
                "1800",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Gebietstyp eines Objekts.",
            json_schema_extra={
                "typename": "RP_GebietsTyp",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Vorranggebiet",
                        "description": "Vorranggebiete sind für bestimmte raumbedeutsame Funktionen oder Nutzungen vorgesehen. In ihnen sind andere raumbedeutsame Nutzungen ausgeschlossen, soweit diese mit den vorrangigen Funktionen, Nutzungen oder Zielen der Raumordnung nicht vereinbar sind.",
                    },
                    "1001": {
                        "name": "Vorrangstandort",
                        "description": "Vorrangstandort.",
                    },
                    "1100": {
                        "name": "Vorbehaltsgebiet",
                        "description": "Vorbehaltsgebiete sind Gebiete, in denen bestimmten raumbedeutsamen Funktionen oder Nutzungen bei der Abwägung mit konkurrierenden raumbedeutsamen Nutzungen besonderes Gewicht begemessen werden soll. Vorbehaltsgebiete besitzen den Charakter von Grundsätzen der Raumordnung.",
                    },
                    "1101": {
                        "name": "Vorbehaltsstandort",
                        "description": "Vorbehaltsstandort.",
                    },
                    "1200": {
                        "name": "Eignungsgebiet",
                        "description": "Eignungsgebiete steuern raumbedeutsame Maßnahmen im bauplanungsrechtlichen Außenbereich. Diese Maßnahmen sind außerhalb dieser Gebiete regelmäßig ausgeschlossen, z.B. die Planung und Einrichtung von Windkraftanlagen. \r\nEignungsgebiete haben den Charakter von Zielen der Raumordnung.",
                    },
                    "1300": {
                        "name": "VorrangundEignungsgebiet",
                        "description": "Vorrang und Eignungsgebiet.",
                    },
                    "1400": {
                        "name": "Ausschlussgebiet",
                        "description": "Ausschlussgebiet.",
                    },
                    "1500": {
                        "name": "Vorsorgegebiet",
                        "description": "Vorsorgegebiet.",
                    },
                    "1501": {
                        "name": "Vorsorgestandort",
                        "description": "Vorsorgestandort.",
                    },
                    "1600": {"name": "Vorzugsraum", "description": "Vorzugsraum."},
                    "1700": {
                        "name": "Potenzialgebiet",
                        "description": "Potenzialgebiet.",
                    },
                    "1800": {
                        "name": "Schwerpunktraum",
                        "description": "Schwerpunktraum.",
                    },
                    "9999": {
                        "name": "SonstigesGebiet",
                        "description": "Sonstiges Gebiet.",
                    },
                },
            },
        ),
    ] = None
    kuestenmeer: Annotated[
        bool | None,
        Field(
            description="Zeigt an, ob das Objekt im Küstenmeer liegt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    bedeutsamkeit: Annotated[
        list[
            Literal[
                "1000", "2000", "3000", "4000", "5000", "6000", "7000", "8000", "9000"
            ]
        ]
        | None,
        Field(
            description="Bedeutsamkeit eines Objekts.",
            json_schema_extra={
                "typename": "RP_Bedeutsamkeit",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Regional", "description": "Regional Bedeutsam."},
                    "2000": {
                        "name": "Ueberregional",
                        "description": "Überregional Bedeutsam.",
                    },
                    "3000": {
                        "name": "Grossraeumig",
                        "description": "Großräumig Bedeutsam.",
                    },
                    "4000": {
                        "name": "Landesweit",
                        "description": "Landesweit Bedeutsam.",
                    },
                    "5000": {
                        "name": "Bundesweit",
                        "description": "Bundesweit Bedeutsam.",
                    },
                    "6000": {
                        "name": "Europaeisch",
                        "description": "Europäisch Bedeutsam.",
                    },
                    "7000": {
                        "name": "International",
                        "description": "International Bedeutsam.",
                    },
                    "8000": {
                        "name": "Flaechenerschliessend",
                        "description": "Flächenerschließend Bedeutsam.",
                    },
                    "9000": {
                        "name": "Herausragend",
                        "description": "Herausragend Bedeutsam.",
                    },
                },
            },
        ),
    ] = None
    istZweckbindung: Annotated[
        bool | None,
        Field(
            description="Zeigt an, ob es sich bei diesem Objekt um eine Zweckbindung handelt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    refTextInhalt: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz eines raumbezogenen Fachobjektes auf textuell formulierte Planinhalte.",
            json_schema_extra={
                "typename": [
                    "BP_TextAbschnitt",
                    "FP_TextAbschnitt",
                    "LP_TextAbschnitt",
                    "RP_TextAbschnitt",
                    "SO_TextAbschnitt",
                ],
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class RPPlan(XPPlan):
    """
    Die Klasse RP_Plan modelliert einen Raumordnungsplan.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    bundesland: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "1300",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "1900",
                "2000",
                "2100",
                "2200",
                "2300",
                "2400",
                "2500",
                "3000",
            ]
        ],
        Field(
            description="Zuständige Bundesländer für den Plan.",
            json_schema_extra={
                "typename": "XP_Bundeslaender",
                "stereotype": "Enumeration",
                "multiplicity": "1..*",
                "enumDescription": {
                    "1000": {"name": "BB", "description": "Brandenburg"},
                    "1100": {"name": "BE", "description": "Berlin"},
                    "1200": {"name": "BW", "description": "Baden-Württemberg"},
                    "1300": {"name": "BY", "description": "Bayern"},
                    "1400": {"name": "HB", "description": "Bremen"},
                    "1500": {"name": "HE", "description": "Hessen"},
                    "1600": {"name": "HH", "description": "Hamburg"},
                    "1700": {"name": "MV", "description": "Mecklenburg-Vorpommern"},
                    "1800": {"name": "NI", "description": "Niedersachsen"},
                    "1900": {"name": "NW", "description": "Nordrhein-Westfalen"},
                    "2000": {"name": "RP", "description": "Rheinland-Pfalz"},
                    "2100": {"name": "SH", "description": "Schleswig-Holstein"},
                    "2200": {"name": "SL", "description": "Saarland"},
                    "2300": {"name": "SN", "description": "Sachsen"},
                    "2400": {"name": "ST", "description": "Sachsen-Anhalt"},
                    "2500": {"name": "TH", "description": "Thüringen"},
                    "3000": {"name": "Bund", "description": "Der Bund."},
                },
            },
            min_length=1,
        ),
    ]
    planArt: Annotated[
        Literal["1000", "2000", "2001", "3000", "4000", "5000", "5001", "6000", "9999"],
        Field(
            description="Art des Raumordnungsplans.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Regionalplan", "description": "Regionalplan."},
                    "2000": {
                        "name": "SachlicherTeilplanRegionalebene",
                        "description": "Sachlicher Teilplan auf der räumlichen Ebene einer Region",
                    },
                    "2001": {
                        "name": "SachlicherTeilplanLandesebene",
                        "description": "Sachlicher Teilplan auf räumlicher Ebene eines Bundeslandes",
                    },
                    "3000": {
                        "name": "Braunkohlenplan",
                        "description": "Braunkohlenplan.",
                    },
                    "4000": {
                        "name": "LandesweiterRaumordnungsplan",
                        "description": "Landesweiter Raumordnungsplan auf räumlicher Ebene eines Bundeslandes",
                    },
                    "5000": {
                        "name": "StandortkonzeptBund",
                        "description": "Raumordnungsplan für das Bundesgebiet mit übergreifenden Standortkonzepten für Seehäfen, Binnenhäfen sowie Flughäfen gem. §17 Abs. 2 ROG.",
                    },
                    "5001": {
                        "name": "AWZPlan",
                        "description": "Plan des Bundes für den Gesamtraum und die ausschließliche Wirtschaftszone (AWZ).",
                    },
                    "6000": {
                        "name": "RaeumlicherTeilplan",
                        "description": "Räumlicher Teilplan auf regionaler Ebene",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges Planwerk der Raumordnung auf Bundesebene, Landesebene oder regionaler Ebene.",
                    },
                },
                "typename": "RP_Art",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    sonstPlanArt: Annotated[
        AnyUrl | None,
        Field(
            description="Spezifikation einer weiteren Planart (CodeList) bei planArt == 9999.",
            json_schema_extra={
                "typename": "RP_SonstPlanArt",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    planungsregion: Annotated[
        int | None,
        Field(
            description="Kennziffer der Planungsregion.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    teilabschnitt: Annotated[
        int | None,
        Field(
            description="Kennziffer des Teilabschnittes.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rechtsstand: Annotated[
        Literal[
            "1000",
            "2000",
            "2001",
            "2002",
            "2003",
            "2004",
            "3000",
            "4000",
            "5000",
            "6000",
            "7000",
        ]
        | None,
        Field(
            description="Rechtsstand des Plans.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Aufstellungsbeschluss",
                        "description": "Aufstellungsbeschluss.",
                    },
                    "2000": {"name": "Entwurf", "description": "Entwurf."},
                    "2001": {
                        "name": "EntwurfGenehmigt",
                        "description": "Entwurf genehmigt.",
                    },
                    "2002": {
                        "name": "EntwurfGeaendert",
                        "description": "Entwurf geändert.",
                    },
                    "2003": {
                        "name": "EntwurfAufgegeben",
                        "description": "Entwurf aufgegeben.",
                    },
                    "2004": {"name": "EntwurfRuht", "description": "Entwurf ruht."},
                    "3000": {"name": "Plan", "description": "Plan."},
                    "4000": {
                        "name": "Inkraftgetreten",
                        "description": "Inkraftgetreten.",
                    },
                    "5000": {
                        "name": "AllgemeinePlanungsabsicht",
                        "description": "Allgemeine Planungsabsicht.",
                    },
                    "6000": {"name": "AusserKraft", "description": "Außer Kraft."},
                    "7000": {"name": "PlanUngueltig", "description": "Plan ungültig."},
                },
                "typename": "RP_Rechtsstand",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    status: Annotated[
        AnyUrl | None,
        Field(
            description="Status des Plans, definiert über eine CodeList.",
            json_schema_extra={
                "typename": "RP_Status",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    aufstellungsbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Aufstellungsbeschlusses.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    auslegungStartDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="Start-Datum der öffentlichen Auslegung. Bei mehrfacher öffentlicher Auslegung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    auslegungEndDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="End-Datum der öffentlichen Auslegung. Bei mehrfacher öffentlicher Auslegung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    traegerbeteiligungsStartDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="Start-Datum der Trägerbeteiligung. Bei mehrfacher Trägerbeteiligung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    traegerbeteiligungsEndDatum: Annotated[
        list[date_aliased] | None,
        Field(
            description="End-Datum der Trägerbeteiligung. Bei mehrfacher Trägerbeteiligung können mehrere Datumsangaben spezifiziert werden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    aenderungenBisDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum, bis zu dem Planänderungen berücksichtigt wurden.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    entwurfsbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Entwurfsbeschlusses",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    planbeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Planbeschlusses.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    datumDesInkrafttretens: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Inkrafttretens des Plans.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    verfahren: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "6000"] | None,
        Field(
            description="Verfahrensstatus des Plans.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Aenderung", "description": "Änderung."},
                    "2000": {
                        "name": "Teilfortschreibung",
                        "description": "Teilfortschreibung.",
                    },
                    "3000": {
                        "name": "Neuaufstellung",
                        "description": "Neuaufstellung.",
                    },
                    "4000": {
                        "name": "Gesamtfortschreibung",
                        "description": "Gesamtfortschreibung.",
                    },
                    "5000": {
                        "name": "Aktualisierung",
                        "description": "Aktualisierung.",
                    },
                    "6000": {
                        "name": "Neubekanntmachung",
                        "description": "Mit der Neubekanntmachung wird eine authentische amtliche Gesamtfassung des geltenden Plans veröffentlicht, in der alle vorherigen, förmlich beschlossenen und verkündeten Änderungen inhaltlich unverändert einbezogen sind. Nur offensichtliche Unrichtigkeiten wie Schreibfehler dürfen berichtigt werden. Es handelt sich nicht um eine neue Planung oder neue Normsetzung.",
                    },
                },
                "typename": "RP_Verfahren",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    amtlicherSchluessel: Annotated[
        str | None,
        Field(
            description="Amtlicher Schlüssel eines Plans auf Basis des  AGS-Schlüssels (Amtlicher Gemeindeschlüssel).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    genehmigungsbehoerde: Annotated[
        str | None,
        Field(
            description="Zuständige Genehmigungsbehörde",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bereich: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Relation auf einen Bereich",
            json_schema_extra={
                "typename": "RP_Bereich",
                "stereotype": "Association",
                "reverseProperty": "gehoertZuPlan",
                "sourceOrTarget": "target",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class SOBereich(XPBereich):
    """
    Bereich eines sonstigen raumbezogenen Plans.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    gehoertZuPlan: Annotated[
        AnyUrl | UUID,
        Field(
            description="Referenz auf den Plan, zu dem der Bereich gehört",
            json_schema_extra={
                "typename": "SO_Plan",
                "stereotype": "Association",
                "reverseProperty": "bereich",
                "sourceOrTarget": "source",
                "multiplicity": "1",
            },
        ),
    ]


class SOObjekt(XPObjekt):
    """
    Basisklasse für die Inhalte sonstiger raumbezogener Planwerke sowie von Klassen zur Modellierung nachrichtlicher Übernahmen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rechtscharakter: Annotated[
        Literal["1000", "1500", "1800", "2000", "3000", "4000", "5000", "9998", "9999"],
        Field(
            description="Rechtscharakter des Planinhalts.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "FestsetzungBPlan",
                        "description": "Festsetzung im Bebauungsplan",
                    },
                    "1500": {
                        "name": "DarstellungFPlan",
                        "description": "Darstellung im Flächennutzungsplan",
                    },
                    "1800": {
                        "name": "InhaltLPlan",
                        "description": "Inhalt eines Landschaftsplans",
                    },
                    "2000": {
                        "name": "NachrichtlicheUebernahme",
                        "description": "Nachrichtliche Übernahme aus anderen Planwerken.",
                    },
                    "3000": {"name": "Hinweis", "description": "Hinweis nach BauGB"},
                    "4000": {"name": "Vermerk", "description": "Vermerk nach BauGB"},
                    "5000": {
                        "name": "Kennzeichnung",
                        "description": "Kennzeichnung nach BauGB",
                    },
                    "9998": {
                        "name": "Unbekannt",
                        "description": "Der Rechtscharakter des Planinhalts ist unbekannt",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiger Rechtscharakter",
                    },
                },
                "typename": "SO_Rechtscharakter",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    sonstRechtscharakter: Annotated[
        AnyUrl | None,
        Field(
            description='Klassifizierung des Rechtscharakters wenn das Attribut "rechtscharakter" den Wert "Sonstiges" (9999)  hat.',
            json_schema_extra={
                "typename": "SO_SonstRechtscharakter",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refTextInhalt: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz eines raumbezogenen Fachobjektes auf textuell formulierte Planinhalte.",
            json_schema_extra={
                "typename": [
                    "BP_TextAbschnitt",
                    "FP_TextAbschnitt",
                    "LP_TextAbschnitt",
                    "RP_TextAbschnitt",
                    "SO_TextAbschnitt",
                ],
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class SOPlan(XPPlan):
    """
    Klasse für sonstige, z. B. länderspezifische raumbezogene Planwerke.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    gemeinde: Annotated[
        list[XPGemeinde] | None,
        Field(
            description="Zuständige Gemeinde",
            json_schema_extra={
                "typename": "XP_Gemeinde",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    planaufstellendeGemeinde: Annotated[
        list[XPGemeinde] | None,
        Field(
            description="Die für die ursprüngliche Planaufstellung zuständige Gemeinde, falls diese nicht unter dem Attribut gemeinde aufgeführt ist. Dies kann z.B. nach Gemeindefusionen der Fall sein.",
            json_schema_extra={
                "typename": "XP_Gemeinde",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    planArt: Annotated[
        AnyUrl,
        Field(
            description="Über eine Codeliste definierter Typ des Plans.",
            json_schema_extra={
                "typename": "SO_PlanArt",
                "stereotype": "Codelist",
                "multiplicity": "1",
            },
        ),
    ]
    plangeber: Annotated[
        XPPlangeber | None,
        Field(
            description="Für den Plan zuständige Stelle.",
            json_schema_extra={
                "typename": "XP_Plangeber",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum der zugrunde liegenden Version des BauGB.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionBauGBText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation der zugrunde liegenden Version des BauGB.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageDatum: Annotated[
        date_aliased | None,
        Field(
            description="Bekanntmachungs-Datum einer zugrunde liegenden anderen Rechtsgrundlage als das BauGB.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    versionSonstRechtsgrundlageText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifikation einer zugrunde liegenden anderen Rechtsgrundlage als das  BauGB.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bereich: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf einen Bereich des sonstigen raumbezogenen Plans.",
            json_schema_extra={
                "typename": "SO_Bereich",
                "stereotype": "Association",
                "reverseProperty": "gehoertZuPlan",
                "sourceOrTarget": "target",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class SOPunktobjekt(SOObjekt):
    """
    Basisklasse für Objekte mit punktförmigem Raumbezug (Einzelpunkt oder Punktmenge).
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point | definitions.MultiPoint,
        Field(
            description="Punktförmiger Raumbezug (Einzelpunkt oder Punktmenge).",
            json_schema_extra={
                "typename": "XP_Punktgeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    nordwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Orientierung des Punktobjektes als Winkel gegen die Nordrichtung. Zählweise im geographischen Sinn (von Nord über Ost nach Süd und West).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class XPNutzungsschablone(XPPTO):
    """
    Modelliert eine Nutzungsschablone. Die darzustellenden Attributwerte werden zeilenweise in die Nutzungsschablone geschrieben.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    spaltenAnz: Annotated[
        int,
        Field(
            description="Anzahl der Spalten in der Nutzungsschablone",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]
    zeilenAnz: Annotated[
        int,
        Field(
            description="Anzahl der Zeilen in der Nutzungsschablone",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class BPEinfahrtPunkt(BPPunktobjekt):
    """
    Punktförmig abgebildete Einfahrt (§9 Abs. 1 Nr. 11 und Abs. 6 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Typ der Einfahrt",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Einfahrt", "description": "Nur Einfahrt möglich"},
                    "2000": {"name": "Ausfahrt", "description": "Nur Ausfahrt möglich"},
                    "3000": {
                        "name": "EinAusfahrt",
                        "description": "Ein- und Ausfahrt möglich",
                    },
                },
                "typename": "BP_EinfahrtTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPFlaechenobjekt(BPObjekt):
    """
    Basisklasse für alle Objekte eines Bebauungsplans mit flächenhaftem Raumbezug. Die von BP_Flaechenobjekt abgeleiteten Fachobjekte können sowohl als Flächenschlussobjekte als auch als Überlagerungsobjekte auftreten.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Polygon | definitions.MultiPolygon,
        Field(
            description="Flächenhafter Raumbezug des Objektes (Eine Einzelfläche oder eine Menge von Flächen, die sich nicht überlappen dürfen).",
            json_schema_extra={
                "typename": "XP_Flaechengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    flaechenschluss: Annotated[
        bool,
        Field(
            description="Zeigt an, ob das Objekt als Flächenschlussobjekt oder Überlagerungsobjekt gebildet werden soll. Flächenschlussobjekte dürfen sich nicht überlappen, sondern nur an den Flächenrändern berühren, wobei die jeweiligen Stützpunkte der Randkurven übereinander liegen müssen. Die Vereinigung der Flächenschlussobjekte überdeckt den Geltungsbereich des Bebauungsplans vollständig.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class BPFlaechenschlussobjekt(BPFlaechenobjekt):
    """
    Basisklasse für alle Objekte eines Bebauungsplans mit flächenhaftem Raumbezug, die auf Ebene 0 immer Flächenschlussobjekte sind.
    Flächenschlussobjekte dürfen sich nicht überlappen, sondern nur an den Flächenrändern berühren, wobei die jeweiligen Stützpunkte der Randkurven übereinander liegen müssen. Die Vereinigung der Flächenschlussobjekte überdeckt den Geltungsbereich des Bebauungsplans vollständig.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPGemeinbedarfsFlaeche(BPFlaechenschlussobjekt):
    """
    Einrichtungen und Anlagen zur Versorgung mit Gütern und Dienstleistungen des öffentlichen und privaten Bereichs, hier Flächen für den Gemeindebedarf (§9, Abs. 1, Nr.5 und Abs. 6 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    dachgestaltung: Annotated[
        list[BPDachgestaltung] | None,
        Field(
            description="Parameter zur Einschränkung der zulässigen Dachformen.",
            json_schema_extra={
                "typename": "BP_Dachgestaltung",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    DNmin: Annotated[
        definitions.Angle | None,
        Field(
            description="Minimal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNmax: Annotated[
        definitions.Angle | None,
        Field(
            description="Maxmal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DN: Annotated[
        definitions.Angle | None,
        Field(
            description="Maximal zulässige Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNZwingend: Annotated[
        definitions.Angle | None,
        Field(
            description="Zwingend vorgeschriebene Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    FR: Annotated[
        definitions.Angle | None,
        Field(
            description="Vorgeschriebene Firstrichtung",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    dachform: Annotated[
        list[
            Literal[
                "1000",
                "2100",
                "2200",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "3600",
                "3700",
                "3800",
                "3900",
                "4000",
                "4100",
                "5000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Erlaubte Dachformen.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "BP_Dachform",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Flachdach",
                        "description": "Flachdach\r\nEmpfohlene Abkürzung: FD",
                    },
                    "2100": {
                        "name": "Pultdach",
                        "description": "Pultdach\r\nEmpfohlene Abkürzung: PD",
                    },
                    "2200": {
                        "name": "VersetztesPultdach",
                        "description": "Versetztes Pultdach\r\nEmpfohlene Abkürzung: VPD",
                    },
                    "3000": {
                        "name": "GeneigtesDach",
                        "description": "Kein Flachdach\r\nEmpfohlene Abkürzung: GD",
                    },
                    "3100": {
                        "name": "Satteldach",
                        "description": "Satteldach\r\nEmpfohlene Abkürzung: SD",
                    },
                    "3200": {
                        "name": "Walmdach",
                        "description": "Walmdach\r\nEmpfohlene Abkürzung: WD",
                    },
                    "3300": {
                        "name": "Krueppelwalmdach",
                        "description": "Krüppelwalmdach\r\nEmpfohlene Abkürzung: KWD",
                    },
                    "3400": {
                        "name": "Mansarddach",
                        "description": "Mansardendach\r\nEmpfohlene Abkürzung: MD",
                    },
                    "3500": {
                        "name": "Zeltdach",
                        "description": "Zeltdach\r\nEmpfohlene Abkürzung: ZD",
                    },
                    "3600": {
                        "name": "Kegeldach",
                        "description": "Kegeldach\r\nEmpfohlene Abkürzung: KeD",
                    },
                    "3700": {
                        "name": "Kuppeldach",
                        "description": "Kuppeldach\r\nEmpfohlene Abkürzung: KuD",
                    },
                    "3800": {
                        "name": "Sheddach",
                        "description": "Sheddach\r\nEmpfohlene Abkürzung: ShD",
                    },
                    "3900": {
                        "name": "Bogendach",
                        "description": "Bogendach\r\nEmpfohlene Abkürzung: BD",
                    },
                    "4000": {
                        "name": "Turmdach",
                        "description": "Turmdach\r\nEmpfohlene Abkürzung: TuD",
                    },
                    "4100": {
                        "name": "Tonnendach",
                        "description": "Tonnendach\r\nEmpfohlene Abkürzung: ToD",
                    },
                    "5000": {
                        "name": "Mischform",
                        "description": "Gemischte Dachform\r\nEmpfohlene Abkürzung: GDF",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Dachform\r\nEmpfohlene Abkürzung: SDF",
                    },
                },
            },
        ),
    ] = None
    detaillierteDachform: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definiertere detailliertere Dachform.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteDachform" bezieht sich auf den an gleicher Position stehenden Attributwert von dachform.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.',
            json_schema_extra={
                "typename": "BP_DetailDachform",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "10001",
                "10002",
                "10003",
                "1200",
                "12000",
                "12001",
                "12002",
                "12003",
                "12004",
                "1400",
                "14000",
                "14001",
                "14002",
                "14003",
                "1600",
                "16000",
                "16001",
                "16002",
                "16003",
                "16004",
                "16005",
                "1800",
                "18000",
                "18001",
                "2000",
                "20000",
                "20001",
                "20002",
                "2200",
                "22000",
                "22001",
                "22002",
                "2400",
                "24000",
                "24001",
                "24002",
                "24003",
                "2600",
                "26000",
                "26001",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der festgesetzten Fläche",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungGemeinbedarf",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "OeffentlicheVerwaltung",
                        "description": "Einrichtungen und Anlagen für öffentliche Verwaltung",
                    },
                    "10000": {
                        "name": "KommunaleEinrichtung",
                        "description": "Kommunale Einrichtung wie z. B. Rathaus, Gesundheitsamt, Gesundheitsfürsorgestelle, Gartenbauamt, Gartenarbeitsstützpunkt, Fuhrpark.",
                    },
                    "10001": {
                        "name": "BetriebOeffentlZweckbestimmung",
                        "description": "Betrieb mit öffentlicher Zweckbestimmung wie z.B. ein Stadtreinigungsbetrieb, Autobusbetriebshof, Omnibusbahnhof.",
                    },
                    "10002": {
                        "name": "AnlageBundLand",
                        "description": "Eine Anlage des Bundes oder eines Bundeslandes wie z. B.  Arbeitsamt, Autobahnmeisterei, Brückenmeisterei, Patentamt, Wasserbauhof, Finanzamt.",
                    },
                    "10003": {
                        "name": "SonstigeOeffentlicheVerwaltung",
                        "description": "Sonstige Einrichtung oder Anlage der öffentlichen Verwaltung wie z. B. die Industrie und Handelskammer oder Handwerkskammer.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1000 verwendet werden.",
                    },
                    "1200": {
                        "name": "BildungForschung",
                        "description": "Einrichtungen und Anlagen für Bildung und Forschung",
                    },
                    "12000": {
                        "name": "Schule",
                        "description": "Schulische Einrichtung. Darunter fallen u. a. Allgemeinbildende Schule, Oberstufenzentrum, Sonderschule, Fachschule, Volkshochschule,\r\nKonservatorium.",
                    },
                    "12001": {
                        "name": "Hochschule",
                        "description": "Hochschule, Fachhochschule, Berufsakademie, o. Ä.",
                    },
                    "12002": {
                        "name": "BerufsbildendeSchule",
                        "description": "Berufsbildende Schule",
                    },
                    "12003": {
                        "name": "Forschungseinrichtung",
                        "description": "Forschungseinrichtung, Forschungsinstitut.",
                    },
                    "12004": {
                        "name": "SonstigesBildungForschung",
                        "description": "Sonstige Anlage oder Einrichtung aus Bildung und Forschung.\r\n\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1200 verwendet werden.",
                    },
                    "1400": {"name": "Kirche", "description": "Religiöse Einrichtung"},
                    "14000": {
                        "name": "Sakralgebaeude",
                        "description": "Religiösen Zwecken dienendes Gebäude wie z. B. Kirche, \r\n Kapelle, Moschee, Synagoge, Gebetssaal.",
                    },
                    "14001": {
                        "name": "KirchlicheVerwaltung",
                        "description": "Religiöses Verwaltungsgebäude, z. B. Pfarramt, Bischöfliches Ordinariat, Konsistorium.",
                    },
                    "14002": {
                        "name": "Kirchengemeinde",
                        "description": "Religiöse Gemeinde- oder Versammlungseinrichtung, z. B. Gemeindehaus, Gemeindezentrum.",
                    },
                    "14003": {
                        "name": "SonstigesKirche",
                        "description": "Sonstige religiösen Zwecken dienende Anlage oder Einrichtung.\r\n\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1400 verwendet werden.",
                    },
                    "1600": {
                        "name": "Sozial",
                        "description": "Einrichtungen und Anlagen für soziale Zwecke.",
                    },
                    "16000": {
                        "name": "EinrichtungKinder",
                        "description": "Soziale Einrichtung für Kinder, wie z. B. Kinderheim, Kindertagesstätte, Kindergarten.",
                    },
                    "16001": {
                        "name": "EinrichtungJugendliche",
                        "description": "Soziale Einrichtung für Jugendliche, wie z. B. Jugendfreizeitheim/-stätte, Jugendgästehaus, Jugendherberge, Jugendheim.",
                    },
                    "16002": {
                        "name": "EinrichtungFamilienErwachsene",
                        "description": "Soziale Einrichtung für Familien und Erwachsene, wie z. B. Bildungszentrum, Volkshochschule, Kleinkinderfürsorgestelle, Säuglingsfürsorgestelle, Nachbarschaftsheim.",
                    },
                    "16003": {
                        "name": "EinrichtungSenioren",
                        "description": "Soziale Einrichtung für Senioren, wie z. B. Alten-/Seniorentagesstätte, Alten-/Seniorenheim, Alten-/Seniorenwohnheim, Altersheim.",
                    },
                    "16004": {
                        "name": "SonstigeSozialeEinrichtung",
                        "description": "Sonstige soziale Einrichtung, z. B. Pflegeheim, Schwesternwohnheim, Studentendorf, Studentenwohnheim. Tierheim, Übergangsheim.\r\n\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1600 verwendet werden.",
                    },
                    "16005": {
                        "name": "EinrichtungBehinderte",
                        "description": "Soziale Einrichtung für Menschen mit Beeinträchtigung, wie z. B. Behindertentagesstätte, Behindertenwohnheim, Behindertenwerkstatt",
                    },
                    "1800": {
                        "name": "Gesundheit",
                        "description": "Einrichtungen und Anlagen für gesundheitliche Zwecke.",
                    },
                    "18000": {
                        "name": "Krankenhaus",
                        "description": "Krankenhaus oder vergleichbare Einrichtung (z. B. Klinik, Hospital, Krankenheim, Heil- und Pflegeanstalt),",
                    },
                    "18001": {
                        "name": "SonstigesGesundheit",
                        "description": "Sonstige Gesundheits-Einrichtung, z. B. Sanatorium, Kurklinik, Desinfektionsanstalt.\r\n\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1800 verwendet werden.",
                    },
                    "2000": {
                        "name": "Kultur",
                        "description": "Einrichtungen und Anlagen für kulturelle Zwecke.",
                    },
                    "20000": {
                        "name": "MusikTheater",
                        "description": "Kulturelle Einrichtung aus dem Bereich Musik oder Theater (z. B. Theater, Konzerthaus, Musikhalle, Oper).",
                    },
                    "20001": {
                        "name": "Bildung",
                        "description": "Kulturelle Einrichtung mit Bildungsfunktion ( z. B. Museum, Bibliothek, Bücherei, Stadtbücherei, Volksbücherei).",
                    },
                    "20002": {
                        "name": "SonstigeKultur",
                        "description": "Sonstige kulturelle Einrichtung, wie z. B. Archiv, Landesbildstelle, Rundfunk und Fernsehen, Kongress- und Veranstaltungshalle, Mehrzweckhalle..\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2000 verwendet werden.",
                    },
                    "2200": {
                        "name": "Sport",
                        "description": "Einrichtungen und Anlagen für sportliche Zwecke.",
                    },
                    "22000": {
                        "name": "Bad",
                        "description": "Schwimmbad, Freibad, Hallenbad, Schwimmhalle o. Ä..",
                    },
                    "22001": {
                        "name": "SportplatzSporthalle",
                        "description": "Sportplatz, Sporthalle, Tennishalle o. Ä.",
                    },
                    "22002": {
                        "name": "SonstigerSport",
                        "description": "Sonstige Sporteinrichtung.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2200 verwendet werden.",
                    },
                    "2400": {
                        "name": "SicherheitOrdnung",
                        "description": "Einrichtungen und Anlagen für Sicherheit und Ordnung.",
                    },
                    "24000": {
                        "name": "Feuerwehr",
                        "description": "Einrichtung oder Anlage der Feuerwehr.",
                    },
                    "24001": {"name": "Schutzbauwerk", "description": "Schutzbauwerk"},
                    "24002": {
                        "name": "Justiz",
                        "description": "Einrichtung der Justiz, wie z. B. Justizvollzug, Gericht, Haftanstalt.",
                    },
                    "24003": {
                        "name": "SonstigeSicherheitOrdnung",
                        "description": "Sonstige Anlage oder Einrichtung für Sicherheit und Ordnung, z. B. Polizei, Zoll, Feuerwehr, Zivilschutz, Bundeswehr, Landesverteidigung.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2400 verwendet werden.",
                    },
                    "2600": {
                        "name": "Infrastruktur",
                        "description": "Einrichtungen und Anlagen der Infrastruktur.",
                    },
                    "26000": {"name": "Post", "description": "Einrichtung der Post."},
                    "26001": {
                        "name": "SonstigeInfrastruktur",
                        "description": "Sonstige Anlage oder Einrichtung der Infrastruktur.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2600 verwendet werden.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Einrichtungen und Anlagen, die keiner anderen Kategorie zuzuordnen sind.",
                    },
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Festlegung der Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestGemeinbedarf",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    bauweise: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bauweise  (§9, Abs. 1, Nr. 2 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "OffeneBauweise",
                        "description": "Offene Bauweise",
                    },
                    "2000": {
                        "name": "GeschlosseneBauweise",
                        "description": "Geschlossene Bauweise",
                    },
                    "3000": {
                        "name": "AbweichendeBauweise",
                        "description": "Abweichende Bauweise",
                    },
                },
                "typename": "BP_Bauweise",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    abweichendeBauweise: Annotated[
        AnyUrl | None,
        Field(
            description='Nähere Bezeichnung einer "Abweichenden Bauweise" ("bauweise" == 3000).',
            json_schema_extra={
                "typename": "BP_AbweichendeBauweise",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungsArt: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "6000", "7000", "8000"] | None,
        Field(
            description="Detaillierte Festsetzung der Bauweise (§9, Abs. 1, Nr. 2 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Einzelhaeuser",
                        "description": "Nur Einzelhäuser zulässig.",
                    },
                    "2000": {
                        "name": "Doppelhaeuser",
                        "description": "Nur Doppelhäuser zulässig.",
                    },
                    "3000": {
                        "name": "Hausgruppen",
                        "description": "Nur Hausgruppen zulässig.",
                    },
                    "4000": {
                        "name": "EinzelDoppelhaeuser",
                        "description": "Nur Einzel- oder Doppelhäuser zulässig.",
                    },
                    "5000": {
                        "name": "EinzelhaeuserHausgruppen",
                        "description": "Nur Einzelhäuser oder Hausgruppen zulässig.",
                    },
                    "6000": {
                        "name": "DoppelhaeuserHausgruppen",
                        "description": "Nur Doppelhäuser oder Hausgruppen zulässig.",
                    },
                    "7000": {
                        "name": "Reihenhaeuser",
                        "description": "Nur Reihenhäuser zulässig.",
                    },
                    "8000": {
                        "name": "EinzelhaeuserDoppelhaeuserHausgruppen",
                        "description": "Es sind Einzelhäuser, Doppelhäuser und Hausgruppen zulässig.",
                    },
                },
                "typename": "BP_BebauungsArt",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zugunstenVon: Annotated[
        str | None,
        Field(
            description="Angabe des Begünstigten einer Ausweisung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPGeometrieobjekt(BPObjekt):
    """
    Basisklasse für alle Objekte eines Bebauungsplans mit variablem Raumbezug. Das bedeutet, die abgeleiteten Objekte können kontextabhängig mit Punkt-, Linien- oder Flächengeometrie gebildet. Die Aggregation von Punkten, Linien oder Flächen ist zulässig, nicht aber die Mischung von Punkt-, Linien- und Flächengeometrie.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point
        | definitions.MultiPoint
        | definitions.Line
        | definitions.MultiLine
        | definitions.Polygon
        | definitions.MultiPolygon,
        Field(
            description="Raumbezug - Entweder punktförmig, linienförmig oder flächenhaft, gemischte Geometrie ist nicht zugelassen.",
            json_schema_extra={
                "typename": "XP_VariableGeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    flaechenschluss: Annotated[
        bool | None,
        Field(
            description="Zeigt bei flächenhaftem Raumbezug an, ob das Objekt als Flächenschlussobjekt oder Überlagerungsobjekt gebildet werden soll.\r\nFlächenschlussobjekte dürfen sich nicht überlappen, sondern nur an den Flächenrändern berühren, wobei die jeweiligen Stützpunkte der Randkurven übereinander liegen müssen. Die Vereinigung der Flächenschlussobjekte überdeckt den Geltungsbereich des Bebauungsplans vollständig.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    flussrichtung: Annotated[
        bool | None,
        Field(
            description='Das Attribut ist nur relevant, wenn ein Geometrieobjekt einen linienhaften Raumbezug hat. Ist es mit dem Wert true belegt, wird damit ausgedrückt, dass der Linie eine Flussrichtung  in Digitalisierungsrichtung, bei Attributwert "false" gegen die Digitalisierungsrichtung zugeordnet ist. In diesem Fall darf bei Im- und Export die Digitalisierungsreihenfolge der Stützpunkte nicht geändert werden.Wie eine definierte Flussrichtung  zu interpretieren oder bei einer Plandarstellung zu visualisieren ist, bleibt der Implementierung überlassen.\r\nIst der Attributwert false oder das Attribut nicht belegt, ist die Digitalisierungsreihenfolge der Stützpunkte irrelevant.',
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nordwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Orientierung des Objektes bei punktförmigem Raumbezug als Winkel gegen die Nordrichtung. Zählweise im geographischen Sinn (von Nord über Ost nach Süd und West).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class BPGewaesserFlaeche(BPFlaechenschlussobjekt):
    """
    Festsetzung neuer Wasserflächen nach §9 Abs. 1 Nr. 16a BauGB.
    Diese Klasse wird in der nächsten Hauptversion des Standards eventuell wegfallen und durch SO_Gewaesser ersetzt werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        Literal["1000", "10000", "1100", "1200", "9999"] | None,
        Field(
            description="Zweckbestimmung der Wasserfläche.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Hafen", "description": "Hafen"},
                    "10000": {
                        "name": "Sportboothafen",
                        "description": "Sportboothafen",
                    },
                    "1100": {
                        "name": "Wasserflaeche",
                        "description": "Stehende Wasserfläche, auch See, Teich.",
                    },
                    "1200": {
                        "name": "Fliessgewaesser",
                        "description": "Fließgewässer, auch Fluss, Bach",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges Gewässer, sofern keiner der anderen Codes zutreffend ist.",
                    },
                },
                "typename": "XP_ZweckbestimmungGewaesser",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Zweckbestimmung der Fläche.",
            json_schema_extra={
                "typename": "BP_DetailZweckbestGewaesser",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPGruenFlaeche(BPFlaechenschlussobjekt):
    """
    Festsetzungen von öffentlichen und privaten Grünflächen (§ 9, Abs. 1, Nr. 15 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "10001",
                "10002",
                "10003",
                "1200",
                "12000",
                "1400",
                "14000",
                "14001",
                "14002",
                "14003",
                "14004",
                "14005",
                "14006",
                "14007",
                "1600",
                "16000",
                "16001",
                "1800",
                "18000",
                "2000",
                "2200",
                "22000",
                "22001",
                "2400",
                "24000",
                "24001",
                "24002",
                "24003",
                "24004",
                "24005",
                "24006",
                "2600",
                "2700",
                "9999",
                "99990",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Grünfläche",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungGruen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Parkanlage",
                        "description": "Parkanlage; auch: Erholungsgrün, Grünanlage, Naherholung.",
                    },
                    "10000": {
                        "name": "ParkanlageHistorisch",
                        "description": "Historische Parkanlage",
                    },
                    "10001": {
                        "name": "ParkanlageNaturnah",
                        "description": "Naturnahe Parkanlage",
                    },
                    "10002": {
                        "name": "ParkanlageWaldcharakter",
                        "description": "Parkanlage mit Waldcharakter",
                    },
                    "10003": {
                        "name": "NaturnaheUferParkanlage",
                        "description": "Ufernahe Parkanlage",
                    },
                    "1200": {
                        "name": "Dauerkleingarten",
                        "description": "Dauerkleingarten; auch: Gartenfläche, Hofgärten, Gartenland.",
                    },
                    "12000": {
                        "name": "ErholungsGaerten",
                        "description": "Erholungsgarten",
                    },
                    "1400": {"name": "Sportplatz", "description": "Sportplatz"},
                    "14000": {
                        "name": "Reitsportanlage",
                        "description": "Reitsportanlage",
                    },
                    "14001": {
                        "name": "Hundesportanlage",
                        "description": "Hundesportanlage",
                    },
                    "14002": {
                        "name": "Wassersportanlage",
                        "description": "Wassersportanlage",
                    },
                    "14003": {"name": "Schiessstand", "description": "Schießstand"},
                    "14004": {"name": "Golfplatz", "description": "Golfplatz"},
                    "14005": {"name": "Skisport", "description": "Anlage für Skisport"},
                    "14006": {"name": "Tennisanlage", "description": "Tennisanlage"},
                    "14007": {
                        "name": "SonstigerSportplatz",
                        "description": "Sonstiger Sportplatz\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1400 verwendet werden.",
                    },
                    "1600": {"name": "Spielplatz", "description": "Spielplatz"},
                    "16000": {"name": "Bolzplatz", "description": "Bolzplatz"},
                    "16001": {
                        "name": "Abenteuerspielplatz",
                        "description": "Abenteuerspielplatz",
                    },
                    "1800": {"name": "Zeltplatz", "description": "Zeltplatz"},
                    "18000": {"name": "Campingplatz", "description": "Campingplatz"},
                    "2000": {
                        "name": "Badeplatz",
                        "description": "Badeplatz, auch Schwimmbad, Liegewiese.",
                    },
                    "2200": {
                        "name": "FreizeitErholung",
                        "description": "Anlage für Freizeit und Erholung.",
                    },
                    "22000": {
                        "name": "Kleintierhaltung",
                        "description": "Anlage für Kleintierhaltung",
                    },
                    "22001": {"name": "Festplatz", "description": "Festplatz"},
                    "2400": {
                        "name": "SpezGruenflaeche",
                        "description": "Spezielle Grünfläche",
                    },
                    "24000": {
                        "name": "StrassenbegleitGruen",
                        "description": "Straßenbegleitgrün",
                    },
                    "24001": {
                        "name": "BoeschungsFlaeche",
                        "description": "Böschungsfläche",
                    },
                    "24002": {
                        "name": "FeldWaldWiese",
                        "description": "Feld, Wald, Wiese allgemein\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2400 verwendet werden.",
                    },
                    "24003": {
                        "name": "Uferschutzstreifen",
                        "description": "Uferstreifen",
                    },
                    "24004": {"name": "Abschirmgruen", "description": "Abschirmgrün"},
                    "24005": {
                        "name": "UmweltbildungsparkSchaugatter",
                        "description": "Umweltbildungspark, Schaugatter",
                    },
                    "24006": {
                        "name": "RuhenderVerkehr",
                        "description": "Fläche für den ruhenden Verkehr.",
                    },
                    "2600": {"name": "Friedhof", "description": "Friedhof"},
                    "2700": {
                        "name": "Naturerfahrungsraum",
                        "description": "Naturerfahrungsräume sollen insbesondere Kindern und Jugendlichen die Möglichkeit geben, in ihrem direkten Umfeld Natur vorzufinden, um eigenständig Erfahrung mit Pflanzen und Tieren sammeln zu können.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Zweckbestimmung, falls keine der aufgeführten Klassifikationen anwendbar ist.",
                    },
                    "99990": {"name": "Gaertnerei", "description": "Gärtnerei"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Festlegung der Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestGruenFlaeche",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    nutzungsform: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Nutzungsform der festgesetzten Fläche.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Privat", "description": "Private Nutzung"},
                    "2000": {
                        "name": "Oeffentlich",
                        "description": "Öffentliche Nutzung",
                    },
                },
                "typename": "XP_Nutzungsform",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zugunstenVon: Annotated[
        str | None,
        Field(
            description="Angabe des Begünstigten einer Ausweisung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPHoehenMass(BPGeometrieobjekt):
    """
    Festsetzungen nach §9 Abs. 1 Nr. 1 BauGB für übereinanderliegende Geschosse und Ebenen und sonstige Teile baulicher Anlagen (§9 Abs.3 BauGB), sowie Hinweise auf Geländehöhen. Die Höhenwerte werden über das Attribut hoehenangabe der Basisklasse XP_Objekt spezifiziert.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPImmissionsschutz(BPGeometrieobjekt):
    """
    Festsetzung einer von der Bebauung freizuhaltenden Schutzfläche und ihre Nutzung, sowie einer Fläche für besondere Anlagen und Vorkehrungen zum Schutz vor schädlichen Umwelteinwirkungen und sonstigen Gefahren im Sinne des Bundes-Immissionsschutzgesetzes sowie die zum Schutz vor solchen Einwirkungen oder zur  Vermeidung oder Minderung solcher Einwirkungen zu treffenden baulichen und sonstigen technischen Vorkehrungen (§9, Abs. 1, Nr. 24 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    nutzung: Annotated[
        str | None,
        Field(
            description="Festgesetzte Nutzung einer Schutzfläche",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    laermpegelbereich: Annotated[
        Literal["1000", "1100", "1200", "1300", "1400", "1500", "1600"] | None,
        Field(
            description="Festlegung der erforderlichen Luftschalldämmung von Außenbauteilen nach DIN 4109.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "I",
                        "description": "Lärmpegelbereich I nach  DIN 4109.",
                    },
                    "1100": {
                        "name": "II",
                        "description": "Lärmpegelbereich II nach  DIN 4109.",
                    },
                    "1200": {
                        "name": "III",
                        "description": "Lärmpegelbereich III nach  DIN 4109.",
                    },
                    "1300": {
                        "name": "IV",
                        "description": "Lärmpegelbereich IV nach  DIN 4109.",
                    },
                    "1400": {
                        "name": "V",
                        "description": "Lärmpegelbereich V nach  DIN 4109.",
                    },
                    "1500": {
                        "name": "VI",
                        "description": "Lärmpegelbereich VI nach  DIN 4109.",
                    },
                    "1600": {
                        "name": "VII",
                        "description": "Lärmpegelbereich VII nach  DIN 4109.",
                    },
                },
                "typename": "BP_Laermpegelbereich",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    typ: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Differenzierung der Immissionsschutz-Fläche",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Schutzflaeche",
                        "description": '"Von der Bebauung freizuhaltende Schutzfläche" nach §9 Abs. 1 Nr. 24 BauGB',
                    },
                    "2000": {
                        "name": "BesondereAnlagenVorkehrungen",
                        "description": '"Fläche für besondere Anlagen und Vorkehrungen zum Schutz vor schädlichen Umwelteinwirkungen" nach §9 Abs. 1 Nr. 24 BauGB',
                    },
                },
                "typename": "BP_ImmissionsschutzTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    technVorkehrung: Annotated[
        Literal["1000", "10000", "10001", "10002", "9999"] | None,
        Field(
            description="Klassifizierung der auf der Fläche zu treffenden baulichen oder sonstigen technischen Vorkehrungen",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Laermschutzvorkehrung",
                        "description": "Allgemeine Lärmschutzvorkehrung",
                    },
                    "10000": {
                        "name": "FassadenMitSchallschutzmassnahmen",
                        "description": "Fassaden mit Schallschutzmaßnahmen",
                    },
                    "10001": {
                        "name": "Laermschutzwand",
                        "description": "Lärmschutzwand",
                    },
                    "10002": {
                        "name": "Laermschutzwall",
                        "description": "Lärmschutzwall",
                    },
                    "9999": {
                        "name": "SonstigeVorkehrung",
                        "description": "Sonstige Vorkehrung zum Immissionsschutz",
                    },
                },
                "typename": "BP_TechnVorkehrungenImmissionsschutz",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detaillierteTechnVorkehrung: Annotated[
        AnyUrl | None,
        Field(
            description="Detaillierte Klassifizierung der auf der Fläche zu treffenden baulichen oder sonstigen technischen Vorkehrungen",
            json_schema_extra={
                "typename": "BP_DetailTechnVorkehrungImmissionsschutz",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPKennzeichnungsFlaeche(BPFlaechenobjekt):
    """
    Flächen für Kennzeichnungen gemäß §9 Abs. 5 BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000", "2000", "3000", "4000", "5000", "6000", "7000", "8000", "9999"
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Kennzeichnungs-Fläche.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungKennzeichnung",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Naturgewalten",
                        "description": "Flächen, bei deren Bebauung besondere bauliche Sicherungsmaßnahmen gegen Naturgewalten erforderlich sind (§5, Abs. 3, Nr. 1 BauGB).",
                    },
                    "2000": {
                        "name": "Abbauflaeche",
                        "description": "Flächen, die für den Abbau von Mineralien bestimmt sind (§5, Abs. 3, Nr. 2 und §9, Abs. 5, Nr. 2. BauGB).",
                    },
                    "3000": {
                        "name": "AeussereEinwirkungen",
                        "description": "Flächen, bei deren Bebauung besondere bauliche Sicherungsmaßnahmen gegen äußere Einwirkungen erforderlich sind (§5, Abs. 3, Nr. 1 BauGB).",
                    },
                    "4000": {
                        "name": "SchadstoffBelastBoden",
                        "description": "Für bauliche Nutzung vorgesehene Flächen, deren Böden erheblich mit umweltgefährdenden Stoffen belastet sind (§5, Abs. 3, Nr. 3 BauGB).",
                    },
                    "5000": {
                        "name": "LaermBelastung",
                        "description": "Für bauliche Nutzung vorgesehene Flächen, die erheblicher Lärmbelastung ausgesetzt sind.",
                    },
                    "6000": {
                        "name": "Bergbau",
                        "description": "Flächen, unter denen der Bergbau umgeht  (§5, Abs. 3, Nr. 2 und §9, Abs. 5, Nr. 2. BauGB).",
                    },
                    "7000": {
                        "name": "Bodenordnung",
                        "description": "Für Bodenordnungsmaßnahmen vorgesehene Gebiete, \r\nz.B. Gebiete für Umlegungen oder Flurbereinigung",
                    },
                    "8000": {
                        "name": "Vorhabensgebiet",
                        "description": "Räumlich besonders gekennzeichnetes Vorhabengebiets, das kleiner als der Geltungsbereich ist, innerhalb eines vorhabenbezogenen BPlans.",
                    },
                    "9999": {
                        "name": "AndereGesetzlVorschriften",
                        "description": "Kennzeichnung nach anderen gesetzlichen Vorschriften.",
                    },
                },
            },
        ),
    ] = None
    istVerdachtsflaeche: Annotated[
        bool | None,
        Field(
            description="Legt fest, ob eine Altlast-Verdachtsfläche vorliegt",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    nummer: Annotated[
        str | None,
        Field(
            description="Nummer im Altlastkataster",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPKleintierhaltungFlaeche(BPFlaechenschlussobjekt):
    """
    Fläche für die Errichtung von Anlagen für die Kleintierhaltung wie Ausstellungs- und Zuchtanlagen, Zwinger, Koppeln und dergleichen (§ 9 Abs. 1 Nr. 19 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPLandwirtschaft(BPGeometrieobjekt):
    """
    Festsetzungen für die Landwirtschaft  (§ 9, Abs. 1, Nr. 18a BauGB)

    Die Klasse wird als veraltet gekennzeichnet und wird in Version 6.0 wegfallen. Es sollte stattdessen die Klasse BP_LandwirtschaftsFlaeche verwendet werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "9999"
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmungen der Ausweisung.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungLandwirtschaft",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "LandwirtschaftAllgemein",
                        "description": "Allgemeine Landwirtschaft",
                    },
                    "1100": {"name": "Ackerbau", "description": "Ackerbau"},
                    "1200": {
                        "name": "WiesenWeidewirtschaft",
                        "description": "Wiesen- und Weidewirtschaft",
                    },
                    "1300": {
                        "name": "GartenbaulicheErzeugung",
                        "description": "Gartenbauliche Erzeugung",
                    },
                    "1400": {"name": "Obstbau", "description": "Obstbau"},
                    "1500": {"name": "Weinbau", "description": "Weinbau"},
                    "1600": {"name": "Imkerei", "description": "Imkerei"},
                    "1700": {
                        "name": "Binnenfischerei",
                        "description": "Binnenfischerei",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestLandwirtschaft",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPLandwirtschaftsFlaeche(BPFlaechenschlussobjekt):
    """
    Festsetzungen für die Landwirtschaft  (§ 9, Abs. 1, Nr. 18a BauGB)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "9999"
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmungen der Ausweisung.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungLandwirtschaft",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "LandwirtschaftAllgemein",
                        "description": "Allgemeine Landwirtschaft",
                    },
                    "1100": {"name": "Ackerbau", "description": "Ackerbau"},
                    "1200": {
                        "name": "WiesenWeidewirtschaft",
                        "description": "Wiesen- und Weidewirtschaft",
                    },
                    "1300": {
                        "name": "GartenbaulicheErzeugung",
                        "description": "Gartenbauliche Erzeugung",
                    },
                    "1400": {"name": "Obstbau", "description": "Obstbau"},
                    "1500": {"name": "Weinbau", "description": "Weinbau"},
                    "1600": {"name": "Imkerei", "description": "Imkerei"},
                    "1700": {
                        "name": "Binnenfischerei",
                        "description": "Binnenfischerei",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestLandwirtschaft",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPLinienobjekt(BPObjekt):
    """
    Basisklasse für alle Objekte eines Bebauungsplans mit linienförmigem Raumbezug (Eine einzelne zusammenhängende Kurve, die aus Linienstücken und Kreisbögen zusammengesetzt sein kann, oder eine Menge derartiger Kurven).
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Line | definitions.MultiLine,
        Field(
            description="Linienförmiger Raumbezug (Einzelne zusammenhängende Kurve, die aus Linienstücken und Kreisbögen aufgebaut sit, oder eine Menge derartiger Kurven),",
            json_schema_extra={
                "typename": "XP_Liniengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]


class BPNutzungsartenGrenze(BPLinienobjekt):
    """
    Abgrenzung unterschiedlicher Nutzung, z.B. von Baugebieten wenn diese nach PlanzVO in der gleichen Farbe dargestellt werden, oder Abgrenzung unterschiedlicher Nutzungsmaße innerhalb eines Baugebiets ("Knödellinie", § 1 Abs. 4, § 16 Abs. 5 BauNVO).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "9999"] | None,
        Field(
            description="Typ der Abgrenzung. Wenn das Attribut nicht belegt ist, ist die Abgrenzung eine Nutzungsarten-Grenze (Schlüsselnummer 1000).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Nutzungsartengrenze",
                        "description": "Nutzungsarten-Grenze zur Abgrenzung von Baugebieten mit unterschiedlicher Art oder unterschiedlichem Maß der baulichen Nutzung.",
                    },
                    "2000": {
                        "name": "UnterschiedlicheHoehen",
                        "description": "Abgrenzung von Bereichen mit unterschiedlichen Festsetzungen zur Gebäudehöhe und/oder Zahl der Vollgeschosse.",
                    },
                    "9999": {
                        "name": "SonstigeAbgrenzung",
                        "description": "Sonstige Abgrenzung",
                    },
                },
                "typename": "BP_AbgrenzungenTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Detaillierter Typ der Abgrenzung, wenn das Attribut typ den Wert 9999 (Sonstige Abgrenzung) hat.",
            json_schema_extra={
                "typename": "BP_DetailAbgrenzungenTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPRekultivierungsFlaeche(BPFlaechenobjekt):
    """
    Rekultivierungs-Fläche

    Die Klasse wird als veraltet gekennzeichnet und wird in XPlanGML 6.0 wegfallen. Es sollte stattdessen die Klasse SO_SonstigesRecht verwendet werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPRichtungssektorGrenze(BPLinienobjekt):
    """
    Linienhafte Repräsentation einer Richtungssektor-Grenze
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    winkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Richtungswinkel der Sektorengrenze",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class BPSchutzPflegeEntwicklungsFlaeche(BPFlaechenobjekt):
    """
    Umgrenzung von Flächen für Maßnahmen zum Schutz, zur Pflege und zur Entwicklung von Natur und Landschaft (§9 Abs. 1 Nr. 20 und Abs. 4 BauGB)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der auf der Fläche durchzuführenden Maßnahmen.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstZiel: Annotated[
        str | None,
        Field(
            description="Textlich formuliertes Ziel, wenn das Attribut ziel den Wert 9999 (Sonstiges) hat.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahme: Annotated[
        list[XPSPEMassnahmenDaten] | None,
        Field(
            description="Durchzuführende Maßnahme.",
            json_schema_extra={
                "typename": "XP_SPEMassnahmenDaten",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    istAusgleich: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob die Fläche zum Ausgleich von Eingriffen genutzt wird.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    refMassnahmenText: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf ein Dokument zur Beschreibung der durchzuführenden Maßnahmen.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refLandschaftsplan: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf den Landschaftsplan",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPSchutzPflegeEntwicklungsMassnahme(BPGeometrieobjekt):
    """
    Maßnahmen zum Schutz, zur Pflege und zur Entwicklung von Natur und Landschaft (§9 Abs. 1 Nr. 20 und Abs. 4 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der Maßnahme",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstZiel: Annotated[
        str | None,
        Field(
            description="Textlich formuliertes Ziel, wenn das Aztribut ziel den Wert 9999 (Sonstiges) hat.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahme: Annotated[
        list[XPSPEMassnahmenDaten] | None,
        Field(
            description="Durchzuführende Maßnahme.",
            json_schema_extra={
                "typename": "XP_SPEMassnahmenDaten",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    istAusgleich: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob die Maßnahme zum Ausgleich von Eingriffen genutzt wird.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    refMassnahmenText: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf ein Dokument, das die durchzuführenden Maßnahmen beschreibt.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refLandschaftsplan: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf den Landschaftsplan.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPSpielSportanlagenFlaeche(BPFlaechenschlussobjekt):
    """
    Einrichtungen und Anlagen zur Versorgung mit Gütern und Dienstleistungen des öffentlichen und privaten Bereichs, hier Flächen für Sport- und Spielanlagen (§9, Abs. 1, Nr. 5 und Abs. 6 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zweckbestimmung: Annotated[
        list[Literal["1000", "2000", "3000", "9999"]] | None,
        Field(
            description="Zweckbestimmung der festgesetzten Fläche.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungSpielSportanlage",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Sportanlage", "description": "Sportanlage"},
                    "2000": {"name": "Spielanlage", "description": "Spielanlage"},
                    "3000": {
                        "name": "SpielSportanlage",
                        "description": "Spiel- und/oder Sportanlage.",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Festlegung der Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestSpielSportanlage",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    zugunstenVon: Annotated[
        str | None,
        Field(
            description="Angabe des Begünstigten einer Ausweisung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPStrassenVerkehrsFlaeche(BPFlaechenschlussobjekt):
    """
    Strassenverkehrsfläche (§ 9 Abs. 1 Nr. 11 und Abs. 6 BauGB) .
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nutzungsform: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Nutzungsform der Fläche",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Privat", "description": "Private Nutzung"},
                    "2000": {
                        "name": "Oeffentlich",
                        "description": "Öffentliche Nutzung",
                    },
                },
                "typename": "XP_Nutzungsform",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    begrenzungslinie: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf eine Linie, die die Verkehrsfläche begrenzt.",
            json_schema_extra={
                "typename": "BP_StrassenbegrenzungsLinie",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPStrassenbegrenzungsLinie(BPLinienobjekt):
    """
    Straßenbegrenzungslinie (§ 9 Abs. 1 Nr. 11 und Abs. 6 BauGB) .
    Durch die Digitalisierungsreihenfolge der Linienstützpunkte muss sichergestellt sein, dass die abzugrenzende Straßenfläche relativ zur Laufrichtung auf der linken Seite liegt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    bautiefe: Annotated[
        definitions.Length | None,
        Field(
            description="Minimaler Abstand der Bebauung von der Straßenbegrenzungslinie.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None


class BPStrassenkoerper(BPGeometrieobjekt):
    """
    Flächen für Aufschüttungen, Abgrabungen und Stützmauern, soweit sie zur Herstellung des Straßenkörpers erforderlich sind (§9, Abs. 1, Nr. 26 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000"],
        Field(
            description="Notwendige Maßnahme zur Herstellung des Straßenkörpers.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Aufschuettung", "description": "Aufschüttung"},
                    "2000": {"name": "Abgrabung", "description": "Abgrabung"},
                    "3000": {"name": "Stuetzmauer", "description": "Stützmauer"},
                },
                "typename": "BP_StrassenkoerperHerstellung",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]


class BPUeberlagerungsobjekt(BPFlaechenobjekt):
    """
    Basisklasse für alle Objekte eines Bebauungsplans mit flächenhaftem Raumbezug, die immer Überlagerungsobjekte sind.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPUnverbindlicheVormerkung(BPGeometrieobjekt):
    """
    Unverbindliche Vormerkung späterer Planungsabsichten.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    vormerkung: Annotated[
        str | None,
        Field(
            description="Text der Vormerkung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPVerEntsorgung(BPGeometrieobjekt):
    """
    Flächen und Leitungen für Versorgungsanlagen, für die Abfallentsorgung und Abwasserbeseitigung sowie für Ablagerungen (§9 Abs. 1, Nr. 12, 14 und Abs. 6 BauGB)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "10001",
                "10002",
                "10003",
                "10004",
                "10005",
                "10006",
                "10007",
                "10008",
                "10009",
                "100010",
                "100011",
                "100012",
                "100013",
                "1200",
                "12000",
                "12001",
                "12002",
                "12003",
                "12004",
                "12005",
                "1300",
                "13000",
                "13001",
                "13002",
                "13003",
                "1400",
                "14000",
                "14001",
                "14002",
                "1600",
                "16000",
                "16001",
                "16002",
                "16003",
                "16004",
                "16005",
                "1800",
                "18000",
                "18001",
                "18002",
                "18003",
                "18004",
                "18005",
                "18006",
                "2000",
                "20000",
                "20001",
                "2200",
                "22000",
                "22001",
                "22002",
                "22003",
                "2400",
                "24000",
                "24001",
                "24002",
                "24003",
                "24004",
                "24005",
                "2600",
                "26000",
                "26001",
                "26002",
                "2800",
                "3000",
                "9999",
                "99990",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Festsetzung..",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungVerEntsorgung",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Elektrizitaet",
                        "description": "Elektrizität allgemein",
                    },
                    "10000": {
                        "name": "Hochspannungsleitung",
                        "description": "Hochspannungsleitung",
                    },
                    "10001": {
                        "name": "TrafostationUmspannwerk",
                        "description": "Trafostation, auch Umspannwerk",
                    },
                    "10002": {
                        "name": "Solarkraftwerk",
                        "description": "Solarkraftwerk",
                    },
                    "10003": {
                        "name": "Windkraftwerk",
                        "description": "Windkraftwerk, Windenergieanlage, Windrad.",
                    },
                    "10004": {
                        "name": "Geothermiekraftwerk",
                        "description": "Geothermie Kraftwerk",
                    },
                    "10005": {
                        "name": "Elektrizitaetswerk",
                        "description": "Elektrizitätswerk allgemein",
                    },
                    "10006": {
                        "name": "Wasserkraftwerk",
                        "description": "Wasserkraftwerk",
                    },
                    "10007": {
                        "name": "BiomasseKraftwerk",
                        "description": "Biomasse-Kraftwerk",
                    },
                    "10008": {"name": "Kabelleitung", "description": "Kabelleitung"},
                    "10009": {
                        "name": "Niederspannungsleitung",
                        "description": "Niederspannungsleitung",
                    },
                    "100010": {"name": "Leitungsmast", "description": "Leitungsmast"},
                    "100011": {"name": "Kernkraftwerk", "description": "Kernkraftwerk"},
                    "100012": {
                        "name": "Kohlekraftwerk",
                        "description": "Kohlekraftwerk",
                    },
                    "100013": {"name": "Gaskraftwerk", "description": "Kohlekraftwerk"},
                    "1200": {"name": "Gas", "description": "Gas allgemein"},
                    "12000": {
                        "name": "Ferngasleitung",
                        "description": "Ferngasleitung",
                    },
                    "12001": {"name": "Gaswerk", "description": "Gaswerk"},
                    "12002": {"name": "Gasbehaelter", "description": "Gasbehälter"},
                    "12003": {
                        "name": "Gasdruckregler",
                        "description": "Gasdruckregler",
                    },
                    "12004": {"name": "Gasstation", "description": "Gasstation"},
                    "12005": {"name": "Gasleitung", "description": "Gasleitung"},
                    "1300": {"name": "Erdoel", "description": "Erdöl allgemein"},
                    "13000": {"name": "Erdoelleitung", "description": "Erdölleitung"},
                    "13001": {"name": "Bohrstelle", "description": "Bohrstelle"},
                    "13002": {
                        "name": "Erdoelpumpstation",
                        "description": "Erdölpumpstation",
                    },
                    "13003": {"name": "Oeltank", "description": "Öltank"},
                    "1400": {
                        "name": "Waermeversorgung",
                        "description": "Wärmeversorgung allgemein",
                    },
                    "14000": {
                        "name": "Blockheizkraftwerk",
                        "description": "Blockheizkraftwerk",
                    },
                    "14001": {
                        "name": "Fernwaermeleitung",
                        "description": "Fernwärmeleitung",
                    },
                    "14002": {"name": "Fernheizwerk", "description": "Fernheizwerk"},
                    "1600": {
                        "name": "Wasser",
                        "description": "Trink- und Brauchwasser allgemein",
                    },
                    "16000": {"name": "Wasserwerk", "description": "Wasserwerk"},
                    "16001": {
                        "name": "Wasserleitung",
                        "description": "Trinkwasserleitung",
                    },
                    "16002": {
                        "name": "Wasserspeicher",
                        "description": "Wasserspeicher",
                    },
                    "16003": {"name": "Brunnen", "description": "Brunnen"},
                    "16004": {"name": "Pumpwerk", "description": "Pumpwerk"},
                    "16005": {"name": "Quelle", "description": "Quelle"},
                    "1800": {"name": "Abwasser", "description": "Abwasser allgemein"},
                    "18000": {
                        "name": "Abwasserleitung",
                        "description": "Abwasserleitung",
                    },
                    "18001": {
                        "name": "Abwasserrueckhaltebecken",
                        "description": "Abwasserrückhaltebecken",
                    },
                    "18002": {
                        "name": "Abwasserpumpwerk",
                        "description": "Abwasserpumpwerk, auch Abwasserhebeanlage",
                    },
                    "18003": {"name": "Klaeranlage", "description": "Kläranlage"},
                    "18004": {
                        "name": "AnlageKlaerschlamm",
                        "description": "Anlage zur Speicherung oder Behandlung von Klärschlamm.",
                    },
                    "18005": {
                        "name": "SonstigeAbwasserBehandlungsanlage",
                        "description": "Sonstige Abwasser-Behandlungsanlage.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1800 verwendet werden.",
                    },
                    "18006": {
                        "name": "SalzOderSoleleitungen",
                        "description": "Salz- oder Sole-Leitungen",
                    },
                    "2000": {
                        "name": "Regenwasser",
                        "description": "Regenwasser allgemein",
                    },
                    "20000": {
                        "name": "RegenwasserRueckhaltebecken",
                        "description": "Regenwasser Rückhaltebecken",
                    },
                    "20001": {
                        "name": "Niederschlagswasserleitung",
                        "description": "Niederschlagswasser-Leitung",
                    },
                    "2200": {
                        "name": "Abfallentsorgung",
                        "description": "Abfallentsorgung allgemein",
                    },
                    "22000": {
                        "name": "Muellumladestation",
                        "description": "Müll-Umladestation",
                    },
                    "22001": {
                        "name": "Muellbeseitigungsanlage",
                        "description": "Müllbeseitigungsanlage",
                    },
                    "22002": {
                        "name": "Muellsortieranlage",
                        "description": "Müllsortieranlage",
                    },
                    "22003": {"name": "Recyclinghof", "description": "Recyclinghof"},
                    "2400": {
                        "name": "Ablagerung",
                        "description": "Ablagerung allgemein",
                    },
                    "24000": {
                        "name": "Erdaushubdeponie",
                        "description": "Erdaushub-Deponie",
                    },
                    "24001": {
                        "name": "Bauschuttdeponie",
                        "description": "Bauschutt-Deponie",
                    },
                    "24002": {
                        "name": "Hausmuelldeponie",
                        "description": "Hausmüll-Deponie",
                    },
                    "24003": {
                        "name": "Sondermuelldeponie",
                        "description": "Sondermüll-Deponie",
                    },
                    "24004": {
                        "name": "StillgelegteDeponie",
                        "description": "Stillgelegte Deponie",
                    },
                    "24005": {
                        "name": "RekultivierteDeponie",
                        "description": "Rekultivierte Deponie",
                    },
                    "2600": {
                        "name": "Telekommunikation",
                        "description": "Telekommunikation allgemein",
                    },
                    "26000": {
                        "name": "Fernmeldeanlage",
                        "description": "Fernmeldeanlage",
                    },
                    "26001": {
                        "name": "Mobilfunkanlage",
                        "description": "Mobilfunkanlage",
                    },
                    "26002": {
                        "name": "Fernmeldekabel",
                        "description": "Fernmeldekabel",
                    },
                    "2800": {
                        "name": "ErneuerbareEnergien",
                        "description": "Erneuerbare Energien allgemein",
                    },
                    "3000": {
                        "name": "KraftWaermeKopplung",
                        "description": "Fläche oder Anlage für Kraft-Wärme Kopplung",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige, durch keinen anderen Code abbildbare Ver- oder Entsorgungsfläche bzw. -Anlage.",
                    },
                    "99990": {
                        "name": "Produktenleitung",
                        "description": "Produktenleitung",
                    },
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung der Festsetzung\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestVerEntsorgung",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    textlicheErgaenzung: Annotated[
        str | None,
        Field(
            description="Zusätzliche textliche Beschreibung der Ver- bzw. Entsorgungseinrichtung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zugunstenVon: Annotated[
        str | None,
        Field(
            description="Angabe des Begünstigten der Ausweisung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPVeraenderungssperre(BPUeberlagerungsobjekt):
    """
    Ausweisung einer Veränderungssperre, die nicht den gesamten Geltungsbereich des Plans umfasst. Bei Verwendung dieser Klasse muss das Attribut "veraenderungssperre" des zugehörigen Plans (Klasse BP_Plan) auf "false" gesetzt werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    veraenderungssperreBeschlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Beschlussdatum der Veränderungssperre im Teilbereich",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    veraenderungssperreStartDatum: Annotated[
        date_aliased | None,
        Field(
            description="Startdatum der Veränderungssperre im Teilbereich.\r\nIn der nächsten Hauptversion wird dies Attribut verpflichtend zu belegen sein.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gueltigkeitsDatum: Annotated[
        date_aliased,
        Field(
            description="Datum, bis zu dem die Veränderungssperre bestehen bleibt.",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "1",
            },
        ),
    ]
    verlaengerung: Annotated[
        Literal["1000", "2000", "3000"],
        Field(
            description="Gibt an, ob die Veränderungssperre bereits ein- oder zweimal verlängert wurde.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Keine",
                        "description": "Veränderungssperre wurde noch nicht verlängert.",
                    },
                    "2000": {
                        "name": "ErsteVerlaengerung",
                        "description": "Veränderungssperre wurde einmal verlängert.",
                    },
                    "3000": {
                        "name": "ZweiteVerlaengerung",
                        "description": "Veränderungssperre wurde zweimal verlängert.",
                    },
                },
                "typename": "XP_VerlaengerungVeraenderungssperre",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    refBeschluss: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf das Dokument mit dem zug. Beschluss.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPVerkehrsflaecheBesondererZweckbestimmung(BPGeometrieobjekt):
    """
    Verkehrsfläche besonderer Zweckbestimmung (§ 9 Abs. 1 Nr. 11 und Abs. 6 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "1300",
                "1400",
                "1500",
                "1550",
                "1560",
                "1580",
                "1600",
                "1700",
                "1800",
                "2000",
                "2100",
                "2200",
                "2300",
                "2400",
                "2500",
                "2600",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Fläche",
            json_schema_extra={
                "typename": "BP_ZweckbestimmungStrassenverkehr",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Parkierungsflaeche",
                        "description": "Fläche für das Parken von Fahrzeugen",
                    },
                    "1100": {
                        "name": "Fussgaengerbereich",
                        "description": "Fußgängerbereich",
                    },
                    "1200": {
                        "name": "VerkehrsberuhigterBereich",
                        "description": "Verkehrsberuhigte Zone",
                    },
                    "1300": {"name": "RadGehweg", "description": "Rad- und Fußweg"},
                    "1400": {"name": "Radweg", "description": "Reiner Radweg"},
                    "1500": {"name": "Gehweg", "description": "Reiner Fußweg"},
                    "1550": {"name": "Wanderweg", "description": "Wanderweg"},
                    "1560": {
                        "name": "ReitKutschweg",
                        "description": "Reit- oder Kutschweg",
                    },
                    "1580": {"name": "Wirtschaftsweg", "description": "Wirtschaftsweg"},
                    "1600": {
                        "name": "FahrradAbstellplatz",
                        "description": "Abstellplatz für Fahrräder",
                    },
                    "1700": {
                        "name": "UeberfuehrenderVerkehrsweg",
                        "description": "Brückenbereich, hier der überführende Verkehrsweg.",
                    },
                    "1800": {
                        "name": "UnterfuehrenderVerkehrsweg",
                        "description": "Brückenbereich, hier der unterführende Verkehrsweg.",
                    },
                    "2000": {
                        "name": "P_RAnlage",
                        "description": "Park-and-Ride Anlage",
                    },
                    "2100": {"name": "Platz", "description": "Platz"},
                    "2200": {
                        "name": "Anschlussflaeche",
                        "description": "Anschlussfläche",
                    },
                    "2300": {
                        "name": "LandwirtschaftlicherVerkehr",
                        "description": "Landwirtschaftlicher Verkehr",
                    },
                    "2400": {"name": "Verkehrsgruen", "description": "Verkehrsgrün"},
                    "2500": {"name": "Rastanlage", "description": "Rastanlage"},
                    "2600": {"name": "Busbahnhof", "description": "Busbahnhof"},
                    "3000": {
                        "name": "CarSharing",
                        "description": "Fläche zum Car-Sharing",
                    },
                    "3100": {
                        "name": "BikeSharing",
                        "description": "Fläche zum Abstellen gemeinschaftlich genutzter Fahrräder",
                    },
                    "3200": {
                        "name": "B_RAnlage",
                        "description": "Bike and Ride Anlage",
                    },
                    "3300": {"name": "Parkhaus", "description": "Parkhaus"},
                    "3400": {
                        "name": "Mischverkehrsflaeche",
                        "description": "Mischverkehrsfläche",
                    },
                    "3500": {
                        "name": "Ladestation",
                        "description": "Flächen für Ladeinfrastruktur elektrisch betriebener Fahrzeuge.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Zweckbestimmung Straßenverkehr.",
                    },
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung der Fläche.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestStrassenverkehr",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    nutzungsform: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Nutzungsform der Fläche.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Privat", "description": "Private Nutzung"},
                    "2000": {
                        "name": "Oeffentlich",
                        "description": "Öffentliche Nutzung",
                    },
                },
                "typename": "XP_Nutzungsform",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    begrenzungslinie: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf eine Linie, die die Verkehrsfläche begrenzt.",
            json_schema_extra={
                "typename": "BP_StrassenbegrenzungsLinie",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    zugunstenVon: Annotated[
        str | None,
        Field(
            description="Begünstigter der Festsetzung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPWaldFlaeche(BPFlaechenschlussobjekt):
    """
    Festsetzung von Waldflächen  (§ 9, Abs. 1, Nr. 18b BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "1200",
                "1400",
                "1600",
                "16000",
                "16001",
                "16002",
                "16003",
                "16004",
                "1700",
                "1800",
                "1900",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Funktion der Waldfläche",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungWald",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Naturwald", "description": "Naturwald"},
                    "10000": {
                        "name": "Waldschutzgebiet",
                        "description": "Waldschutzgebiet",
                    },
                    "1200": {"name": "Nutzwald", "description": "Nutzwald"},
                    "1400": {"name": "Erholungswald", "description": "Erholungswald"},
                    "1600": {"name": "Schutzwald", "description": "Schutzwald"},
                    "16000": {
                        "name": "Bodenschutzwald",
                        "description": "Bodenschutzwald",
                    },
                    "16001": {
                        "name": "Biotopschutzwald",
                        "description": "Biotopschutzwald",
                    },
                    "16002": {
                        "name": "NaturnaherWald",
                        "description": "Naturnaher Wald",
                    },
                    "16003": {
                        "name": "SchutzwaldSchaedlicheUmwelteinwirkungen",
                        "description": "Wald zum Schutz vor schädlichen Umwelteinwirkungen",
                    },
                    "16004": {"name": "Schonwald", "description": "Schonwald"},
                    "1700": {"name": "Bannwald", "description": "Bannwald"},
                    "1800": {
                        "name": "FlaecheForstwirtschaft",
                        "description": "Fläche für die Forstwirtschaft.",
                    },
                    "1900": {
                        "name": "ImmissionsgeschaedigterWald",
                        "description": "Immissionsgeschädigter Wald",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstigr Wald"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Festlegung der Funktion des Waldes.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestWaldFlaeche",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    eigentumsart: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "12000",
            "12001",
            "2000",
            "20000",
            "20001",
            "3000",
            "9999",
        ]
        | None,
        Field(
            description="Festlegung der Eigentumsart des Waldes",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "OeffentlicherWald",
                        "description": "Öffentlicher Wald allgemein",
                    },
                    "1100": {"name": "Staatswald", "description": "Staatswald"},
                    "1200": {
                        "name": "Koerperschaftswald",
                        "description": "Körperschaftswald",
                    },
                    "12000": {"name": "Kommunalwald", "description": "Kommunalwald"},
                    "12001": {"name": "Stiftungswald", "description": "Stiftungswald"},
                    "2000": {
                        "name": "Privatwald",
                        "description": "Privatwald allgemein",
                    },
                    "20000": {
                        "name": "Gemeinschaftswald",
                        "description": "Gemeinschaftswald",
                    },
                    "20001": {
                        "name": "Genossenschaftswald",
                        "description": "Genossenschaftswald",
                    },
                    "3000": {"name": "Kirchenwald", "description": "Kirchenwald"},
                    "9999": {"name": "Sonstiges", "description": "Sonstiger Wald"},
                },
                "typename": "XP_EigentumsartWald",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    betreten: Annotated[
        list[Literal["1000", "2000", "3000", "4000"]] | None,
        Field(
            description="Festlegung zusätzlicher, normalerweise nicht-gestatteter Aktivitäten, die in dem Wald ausgeführt werden dürfen, nach §14 Abs. 2 Bundeswaldgesetz.",
            json_schema_extra={
                "typename": "XP_WaldbetretungTyp",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Radfahren", "description": "Radfahren"},
                    "2000": {"name": "Reiten", "description": "Reiten"},
                    "3000": {"name": "Fahren", "description": "Fahren"},
                    "4000": {"name": "Hundesport", "description": "Hundesport"},
                },
            },
        ),
    ] = None


class BPWasserwirtschaftsFlaeche(BPFlaechenobjekt):
    """
    Flächen für die Wasserwirtschaft (§9 Abs. 1 Nr. 16a BauGB), sowie Flächen für Hochwasserschutz-anlagen und für die Regelung des Wasserabflusses (§9 Abs. 1 Nr. 16b BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        Literal["1000", "1100", "1200", "1300", "1400", "1500", "9999"] | None,
        Field(
            description="Zweckbestimmung der Fläche.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "HochwasserRueckhaltebecken",
                        "description": "Hochwasser-Rückhaltebecken",
                    },
                    "1100": {
                        "name": "Ueberschwemmgebiet",
                        "description": "Überschwemmungsgefährdetes Gebiet nach §31c des vor dem 1.10.2010 gültigen WHG",
                    },
                    "1200": {
                        "name": "Versickerungsflaeche",
                        "description": "Versickerungsfläche",
                    },
                    "1300": {
                        "name": "Entwaesserungsgraben",
                        "description": "Entwässerungsgraben",
                    },
                    "1400": {"name": "Deich", "description": "Deich"},
                    "1500": {
                        "name": "RegenRueckhaltebecken",
                        "description": "Regen-Rückhaltebecken",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Wasserwirtschaftsfläche, sofern keiner der anderen Codes zutreffend ist.",
                    },
                },
                "typename": "XP_ZweckbestimmungWasserwirtschaft",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Zweckbestimmung der Fläche.",
            json_schema_extra={
                "typename": "BP_DetailZweckbestWasserwirtschaft",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPWegerecht(BPGeometrieobjekt):
    """
    Festsetzung von Flächen, die mit Geh-, Fahr-, und Leitungsrechten zugunsten der Allgemeinheit, eines Erschließungsträgers, oder eines beschränkten Personenkreises belastet sind  (§ 9 Abs. 1 Nr. 21 und Abs. 6 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000", "2000", "2500", "3000", "4000", "4100", "4200", "5000", "9999"
            ]
        ]
        | None,
        Field(
            description="Typ des Wegerechts",
            json_schema_extra={
                "typename": "BP_WegerechtTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Gehrecht", "description": "Gehrecht"},
                    "2000": {"name": "Fahrrecht", "description": "Fahrrecht"},
                    "2500": {"name": "Radfahrrecht", "description": "Radfahrrecht"},
                    "3000": {
                        "name": "GehFahrrecht",
                        "description": "Geh- und Fahrrecht.\r\n\r\nDieser Enumerationswert ist veraltet und wird in in Version 6.0 wegfallen. Stattdessen sollte das Attribut typ zweimal mit den Codes 1000 und 2000 belegt werden.",
                    },
                    "4000": {"name": "Leitungsrecht", "description": "Leitungsrecht"},
                    "4100": {
                        "name": "GehLeitungsrecht",
                        "description": "Geh- und Leitungsrecht\r\n\r\nDieser Enumerationswert ist veraltet und wird in in Version 6.0 wegfallen. Stattdessen sollte das Attribut typ zweimal mit den Codes 1000 und 4000 belegt werden.",
                    },
                    "4200": {
                        "name": "FahrLeitungsrecht",
                        "description": "Fahr- und Leitungsrecht\r\n\r\nDieser Enumerationswert ist veraltet und wird in in Version 6.0 wegfallen. Stattdessen sollte das Attribut typ zweimal mit den Codes 2000 und 4000 belegt werden.",
                    },
                    "5000": {
                        "name": "GehFahrLeitungsrecht",
                        "description": "Geh-, Fahr- und Leitungsrecht\r\n\r\nDieser Enumerationswert ist veraltet und wird in in Version 6.0 wegfallen. Stattdessen sollte das Attribut typ  dreimal mit den Codes 1000, 2000 und 4000 belegt werden.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges Nutzungsrecht",
                    },
                },
            },
        ),
    ] = None
    zugunstenVon: Annotated[
        str | None,
        Field(
            description="Inhaber der Rechte.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    thema: Annotated[
        str | None,
        Field(
            description="Beschreibung des Rechtes.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    breite: Annotated[
        definitions.Length | None,
        Field(
            description="Breite des Wegerechts bei linienförmiger Ausweisung der Geometrie.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    istSchmal: Annotated[
        bool | None,
        Field(
            description='Gibt an, ob es sich um eine "schmale Fläche" handelt  gem. Planzeichen 15.5 der PlanZV handelt.',
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPWohngebaeudeFlaeche(BPFlaechenschlussobjekt):
    """
    Fläche für die Errichtung von Wohngebäuden in einem Bebauungsplan zur Wohnraumversorgung gemäß §9 Absatz 2d BauGB.
    Das Maß der baulichen Nutzung sowie Festsetzungen zur Bauweise oder Grenzbebauung können innerhalb einer BP_WohngebaeudeFlaeche unterschiedlich sein (BP_UeberbaubareGrundstueckeFlaeche). Dabei sollte die gleichzeitige Belegung desselben Attributs in BP_WohngebaeudeFlaeche und einem überlagernden Objekt BP_UeberbaubareGrunsdstuecksFlaeche verzichtet werden.  Ab Version 6.0 wird dies evtl. durch eine Konformitätsregel erzwungen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    dachgestaltung: Annotated[
        list[BPDachgestaltung] | None,
        Field(
            description="Parameter zur Einschränkung der zulässigen Dachformen.",
            json_schema_extra={
                "typename": "BP_Dachgestaltung",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    DNmin: Annotated[
        definitions.Angle | None,
        Field(
            description="Minimal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNmax: Annotated[
        definitions.Angle | None,
        Field(
            description="Maxmal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DN: Annotated[
        definitions.Angle | None,
        Field(
            description="Maximal zulässige Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNZwingend: Annotated[
        definitions.Angle | None,
        Field(
            description="Zwingend vorgeschriebene Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    FR: Annotated[
        definitions.Angle | None,
        Field(
            description="Vorgeschriebene Firstrichtung",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    dachform: Annotated[
        list[
            Literal[
                "1000",
                "2100",
                "2200",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "3600",
                "3700",
                "3800",
                "3900",
                "4000",
                "4100",
                "5000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Erlaubte Dachformen.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "BP_Dachform",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Flachdach",
                        "description": "Flachdach\r\nEmpfohlene Abkürzung: FD",
                    },
                    "2100": {
                        "name": "Pultdach",
                        "description": "Pultdach\r\nEmpfohlene Abkürzung: PD",
                    },
                    "2200": {
                        "name": "VersetztesPultdach",
                        "description": "Versetztes Pultdach\r\nEmpfohlene Abkürzung: VPD",
                    },
                    "3000": {
                        "name": "GeneigtesDach",
                        "description": "Kein Flachdach\r\nEmpfohlene Abkürzung: GD",
                    },
                    "3100": {
                        "name": "Satteldach",
                        "description": "Satteldach\r\nEmpfohlene Abkürzung: SD",
                    },
                    "3200": {
                        "name": "Walmdach",
                        "description": "Walmdach\r\nEmpfohlene Abkürzung: WD",
                    },
                    "3300": {
                        "name": "Krueppelwalmdach",
                        "description": "Krüppelwalmdach\r\nEmpfohlene Abkürzung: KWD",
                    },
                    "3400": {
                        "name": "Mansarddach",
                        "description": "Mansardendach\r\nEmpfohlene Abkürzung: MD",
                    },
                    "3500": {
                        "name": "Zeltdach",
                        "description": "Zeltdach\r\nEmpfohlene Abkürzung: ZD",
                    },
                    "3600": {
                        "name": "Kegeldach",
                        "description": "Kegeldach\r\nEmpfohlene Abkürzung: KeD",
                    },
                    "3700": {
                        "name": "Kuppeldach",
                        "description": "Kuppeldach\r\nEmpfohlene Abkürzung: KuD",
                    },
                    "3800": {
                        "name": "Sheddach",
                        "description": "Sheddach\r\nEmpfohlene Abkürzung: ShD",
                    },
                    "3900": {
                        "name": "Bogendach",
                        "description": "Bogendach\r\nEmpfohlene Abkürzung: BD",
                    },
                    "4000": {
                        "name": "Turmdach",
                        "description": "Turmdach\r\nEmpfohlene Abkürzung: TuD",
                    },
                    "4100": {
                        "name": "Tonnendach",
                        "description": "Tonnendach\r\nEmpfohlene Abkürzung: ToD",
                    },
                    "5000": {
                        "name": "Mischform",
                        "description": "Gemischte Dachform\r\nEmpfohlene Abkürzung: GDF",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Dachform\r\nEmpfohlene Abkürzung: SDF",
                    },
                },
            },
        ),
    ] = None
    detaillierteDachform: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definiertere detailliertere Dachform.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteDachform" bezieht sich auf den an gleicher Position stehenden Attributwert von dachform.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.',
            json_schema_extra={
                "typename": "BP_DetailDachform",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    abweichungText: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Texliche Beschreibung der abweichenden Bauweise.",
            json_schema_extra={
                "typename": "BP_TextAbschnitt",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    wohnnutzungEGStrasse: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung nach §6a Abs. (4) Nr. 1 BauNVO: Für urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass in Gebäuden \r\nim Erdgeschoss an der Straßenseite eine Wohnnutzung nicht oder nur ausnahmsweise zulässig ist.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Zulaessig",
                        "description": "Generelle Zulässigkeit",
                    },
                    "2000": {
                        "name": "NichtZulaessig",
                        "description": "Generelle Nicht-Zulässigkeit.",
                    },
                    "3000": {
                        "name": "AusnahmsweiseZulaessig",
                        "description": "Ausnahmsweise Zulässigkeit",
                    },
                },
                "typename": "BP_Zulaessigkeit",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZWohn: Annotated[
        int | None,
        Field(
            description="Festsetzung nach §4a Abs. (4) Nr. 1 bzw. nach  §6a Abs. (4) Nr. 2 BauNVO: Für besondere Wohngebiete und  urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass in Gebäuden oberhalb eines im Bebauungsplan bestimmten Geschosses nur Wohnungen zulässig sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFAntWohnen: Annotated[
        definitions.Scale | None,
        Field(
            description="Festsetzung nach §4a Abs. (4) Nr. 2 bzw. §6a Abs. (4) Nr. 3 BauNVO: Für besondere Wohngebiete und urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden ein im Bebauungsplan bestimmter Anteil der zulässigen \r\nGeschossfläche für Wohnungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Scale",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "vH",
            },
        ),
    ] = None
    GFWohnen: Annotated[
        definitions.Area | None,
        Field(
            description="Festsetzung nach §4a Abs. (4) Nr. 2 bzw. §6a Abs. (4) Nr. 3 BauNVO: Für besondere Wohngebiete und urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden eine im Bebauungsplan bestimmte Größe der Geschossfläche für Wohnungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFAntGewerbe: Annotated[
        definitions.Scale | None,
        Field(
            description="Festsetzung nach §6a Abs. (4) Nr. 4 BauNVO: Für urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden ein im Bebauungsplan bestimmter Anteil der zulässigen \r\nGeschossfläche für gewerbliche Nutzungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Scale",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "vH",
            },
        ),
    ] = None
    GFGewerbe: Annotated[
        definitions.Area | None,
        Field(
            description="Festsetzung nach §6a Abs. (4) Nr. 4 BauNVO: Für urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden eine im Bebauungsplan bestimmte Größe der Geschossfläche für gewerbliche Nutzungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    VF: Annotated[
        definitions.Area | None,
        Field(
            description="Festsetzung der maximal zulässigen Verkaufsfläche in einem Sondergebiet",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    typ: Annotated[
        Literal["1000", "2000", "3000"],
        Field(
            description="Festlegung der zu errichtenden Gebäude gemäß  §9 Absatz 2d Nr. 1 - 3 BauGB",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "WohnGebaeude",
                        "description": "Flächen, auf denen Wohngebäude errichtet werden dürfen",
                    },
                    "2000": {
                        "name": "GebaeudeFoerderung",
                        "description": "Flächen, auf denen nur Gebäude errichtet werden dürfen, bei denen einzelne oder alle Wohnungen die baulichen Voraussetzungen für eine Förderung mit Mitteln der sozialen Wohnraumförderung erfüllen",
                    },
                    "3000": {
                        "name": "GebaeudeStaedtebaulicherVertrag",
                        "description": "Flächen, auf denen nur Gebäude errichtet werden dürfen, bei denen sich ein Vorhabenträger hinsichtlich einzelner oder aller Wohnungen in einem städtebaulichen Vertrag verpflichtet, zum Zeitpunkt des Vertragsschlusses geltende Förderbedingungen der sozialen Wohnraumförderung, insbesondere die Mietpreisbindung, einzuhalten und die Einhaltung dieser Verpflichtung in geeigneter Weise sichergestellt wird",
                    },
                },
                "typename": "BP_TypWohngebaeudeFlaeche",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    abweichungBauNVO: Annotated[
        Literal["1000", "2000", "3000", "9999"] | None,
        Field(
            description="Art der zulässigen Abweichung von der BauNVO.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "EinschraenkungNutzung",
                        "description": "Einschränkung einer generell erlaubten Nutzung.",
                    },
                    "2000": {
                        "name": "AusschlussNutzung",
                        "description": "Ausschluss einer generell erlaubten Nutzung.",
                    },
                    "3000": {
                        "name": "AusweitungNutzung",
                        "description": "Eine nur ausnahmsweise zulässige Nutzung wird generell zulässig.",
                    },
                    "9999": {
                        "name": "SonstAbweichung",
                        "description": "Sonstige Abweichung.",
                    },
                },
                "typename": "XP_AbweichungBauNVOTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bauweise: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bauweise  ( §9 Absatz 2d  BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "OffeneBauweise",
                        "description": "Offene Bauweise",
                    },
                    "2000": {
                        "name": "GeschlosseneBauweise",
                        "description": "Geschlossene Bauweise",
                    },
                    "3000": {
                        "name": "AbweichendeBauweise",
                        "description": "Abweichende Bauweise",
                    },
                },
                "typename": "BP_Bauweise",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    abweichendeBauweise: Annotated[
        AnyUrl | None,
        Field(
            description='Nähere Bezeichnung einer "Abweichenden Bauweise" ("bauweise" == 3000).',
            json_schema_extra={
                "typename": "BP_AbweichendeBauweise",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    vertikaleDifferenzierung: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob eine vertikale Differenzierung der Gebäude vorgeschrieben ist.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    bebauungsArt: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "6000", "7000", "8000"] | None,
        Field(
            description="Detaillierte Festsetzung der Bauweise (§9, Abs. 1, Nr. 2d BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Einzelhaeuser",
                        "description": "Nur Einzelhäuser zulässig.",
                    },
                    "2000": {
                        "name": "Doppelhaeuser",
                        "description": "Nur Doppelhäuser zulässig.",
                    },
                    "3000": {
                        "name": "Hausgruppen",
                        "description": "Nur Hausgruppen zulässig.",
                    },
                    "4000": {
                        "name": "EinzelDoppelhaeuser",
                        "description": "Nur Einzel- oder Doppelhäuser zulässig.",
                    },
                    "5000": {
                        "name": "EinzelhaeuserHausgruppen",
                        "description": "Nur Einzelhäuser oder Hausgruppen zulässig.",
                    },
                    "6000": {
                        "name": "DoppelhaeuserHausgruppen",
                        "description": "Nur Doppelhäuser oder Hausgruppen zulässig.",
                    },
                    "7000": {
                        "name": "Reihenhaeuser",
                        "description": "Nur Reihenhäuser zulässig.",
                    },
                    "8000": {
                        "name": "EinzelhaeuserDoppelhaeuserHausgruppen",
                        "description": "Es sind Einzelhäuser, Doppelhäuser und Hausgruppen zulässig.",
                    },
                },
                "typename": "BP_BebauungsArt",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungVordereGrenze: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bebauung der vorderen Grundstücksgrenze (§9, Abs. 1, Nr. 2d BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Verboten",
                        "description": "Eine Bebauung der Grenze ist verboten.",
                    },
                    "2000": {
                        "name": "Erlaubt",
                        "description": "Eine Bebauung der Grenze ist erlaubt.",
                    },
                    "3000": {
                        "name": "Erzwungen",
                        "description": "Eine Bebauung der Grenze ist vorgeschrieben.",
                    },
                },
                "typename": "BP_GrenzBebauung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungRueckwaertigeGrenze: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bebauung der rückwärtigen Grundstücksgrenze (§9, Abs. 1, Nr. 2d BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Verboten",
                        "description": "Eine Bebauung der Grenze ist verboten.",
                    },
                    "2000": {
                        "name": "Erlaubt",
                        "description": "Eine Bebauung der Grenze ist erlaubt.",
                    },
                    "3000": {
                        "name": "Erzwungen",
                        "description": "Eine Bebauung der Grenze ist vorgeschrieben.",
                    },
                },
                "typename": "BP_GrenzBebauung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungSeitlicheGrenze: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bebauung der seitlichen Grundstücksgrenze (§9, Abs. 1, Nr. 2d BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Verboten",
                        "description": "Eine Bebauung der Grenze ist verboten.",
                    },
                    "2000": {
                        "name": "Erlaubt",
                        "description": "Eine Bebauung der Grenze ist erlaubt.",
                    },
                    "3000": {
                        "name": "Erzwungen",
                        "description": "Eine Bebauung der Grenze ist vorgeschrieben.",
                    },
                },
                "typename": "BP_GrenzBebauung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refGebaeudequerschnitt: Annotated[
        list[XPExterneReferenz] | None,
        Field(
            description="Referenz auf ein Dokument mit vorgeschriebenen Gebäudequerschnitten.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    zugunstenVon: Annotated[
        str | None,
        Field(
            description="Angabe des Begünstigten einer Ausweisung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPZentralerVersorgungsbereich(BPUeberlagerungsobjekt):
    """
    Zentraler Versorgungsbereich gem. § 9 Abs. 2a BauGB
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPZusatzkontingentLaermFlaeche(BPUeberlagerungsobjekt):
    """
    Flächenhafte Spezifikation von zusätzlichen Lärmemissionskontingenten für einzelne Richtungssektoren (DIN 45691, Anhang 2).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    bezeichnung: Annotated[
        str | None,
        Field(
            description="Bezeichnung des Kontingentes",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    richtungssektor: Annotated[
        BPRichtungssektor,
        Field(
            description="Spezifikation des zugehörigen Richtungssektors",
            json_schema_extra={
                "typename": "BP_Richtungssektor",
                "stereotype": "DataType",
                "multiplicity": "1",
            },
        ),
    ]


class FPFlaechenobjekt(FPObjekt):
    """
    Basisklasse für alle Objekte eines Flächennutzungsplans mit flächenhaftem Raumbezug (eine Einzelfläche oder eine Menge von Flächen, die sich nicht überlappen dürfen).  Die von FP_Flaechenobjekt abgeleiteten Fachobjekte können sowohl als Flächenschlussobjekte als auch als Überlagerungsobjekte auftreten.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Polygon | definitions.MultiPolygon,
        Field(
            description="Flächenhafter Raumbezug des Objektes (Eine Einzelfläche oder eine Menge von Flächen, die sich nicht überlappen dürfen).",
            json_schema_extra={
                "typename": "XP_Flaechengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    flaechenschluss: Annotated[
        bool,
        Field(
            description="Zeigt an, ob das Objekt als Flächenschlussobjekt oder Überlagerungsobjekt gebildet werden soll. Flächenschlussobjekte dürfen sich nicht überlappen, sondern nur an den Flächenrändern berühren, wobei die jeweiligen Stützpunkte der Randkurven übereinander liegen müssen. Die Vereinigung der Flächenschlussobjekte überdeckt den Geltungsbereich des Flächennutzungsplans vollständig.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class FPFlaechenschlussobjekt(FPFlaechenobjekt):
    """
    Basisklasse für alle Objekte eines Flächennutzungsplans mit flächenhaftem Raumbezug, die auf Ebene 0 immer Flächenschlussobjekte sind.
    Flächenschlussobjekte dürfen sich nicht überlappen, sondern nur an den Flächenrändern berühren, wobei die jeweiligen Stützpunkte der Randkurven übereinander liegen müssen. Die Vereinigung der Flächenschlussobjekte überdeckt den Geltungsbereich des Flächennutzungsplans vollständig.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class FPGeometrieobjekt(FPObjekt):
    """
    Basisklasse für alle Objekte eines Flächennutzungsplans mit variablem Raumbezug. Ein konkretes Objekt muss entweder punktförmigen, linienförmigen oder flächenhaften Raumbezug haben, gemischte Geometrie ist nicht zugelassen.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point
        | definitions.MultiPoint
        | definitions.Line
        | definitions.MultiLine
        | definitions.Polygon
        | definitions.MultiPolygon,
        Field(
            description="Raumbezug - Entweder punktförmig, linienförmig oder flächenhaft, gemischte Geometrie ist nicht zugelassen.",
            json_schema_extra={
                "typename": "XP_VariableGeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    flaechenschluss: Annotated[
        bool | None,
        Field(
            description="Zeigt bei flächenhaftem Raumbezug an, ob das Objekt als Flächenschlussobjekt oder Überlagerungsobjekt gebildet werden soll.\r\nFlächenschlussobjekte dürfen sich nicht überlappen, sondern nur an den Flächenrändern berühren, wobei die jeweiligen Stützpunkte der Randkurven übereinander liegen müssen. Die Vereinigung der Flächenschlussobjekte überdeckt den Geltungsbereich des Flächennutzungsplans vollständig.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    flussrichtung: Annotated[
        bool | None,
        Field(
            description="Das Attribut ist nur relevant, wenn ein Geometrieobjekt einen linienhaften Raumbezug hat. Ist es mit dem Wert true belegt, wird damit ausgedrückt, dass der Linie eine Flussrichtung  in Digitalisierungsrichtung zugeordnet ist. In diesem Fall darf bei Im- und Export die Digitalisierungsreihenfolge der Stützpunkte nicht geändert werden. Wie eine definierte Flussrichtung  zu interpretieren oder bei einer Plandarstellung zu visualisieren ist, bleibt der Implementierung überlassen.\r\nIst der Attributwert false oder das Attribut nicht belegt, ist die Digitalisierungsreihenfolge der Stützpunkte irrelevant.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nordwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Orientierung des Objektes bei punkförmigem Raumbezug als Winkel gegen die Nordrichtung. Zählweise im geographischen Sinn (von Nord über Ost nach Süd und West).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class FPGewaesser(FPGeometrieobjekt):
    """
    Darstellung von Wasserflächen nach §5, Abs. 2, Nr. 7 BauGB.
    Diese Klasse wird in der nächsten Hauptversion des Standards eventuell wegfallen und durch SO_Gewaesser ersetzt werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        Literal["1000", "10000", "1100", "1200", "9999"] | None,
        Field(
            description="Zweckbestimmung des Gewässers.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Hafen", "description": "Hafen"},
                    "10000": {
                        "name": "Sportboothafen",
                        "description": "Sportboothafen",
                    },
                    "1100": {
                        "name": "Wasserflaeche",
                        "description": "Stehende Wasserfläche, auch See, Teich.",
                    },
                    "1200": {
                        "name": "Fliessgewaesser",
                        "description": "Fließgewässer, auch Fluss, Bach",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges Gewässer, sofern keiner der anderen Codes zutreffend ist.",
                    },
                },
                "typename": "XP_ZweckbestimmungGewaesser",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        AnyUrl | None,
        Field(
            description='Über eine Codelist definierte detailliertere Zweckbestimmung des Objektes.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestGewaesser",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPGruen(FPGeometrieobjekt):
    """
    Darstellung einer Grünfläche nach § 5, Abs. 2, Nr. 5 BauGB,
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "10001",
                "10002",
                "10003",
                "1200",
                "12000",
                "1400",
                "14000",
                "14001",
                "14002",
                "14003",
                "14004",
                "14005",
                "14006",
                "14007",
                "1600",
                "16000",
                "16001",
                "1800",
                "18000",
                "2000",
                "2200",
                "22000",
                "22001",
                "2400",
                "24000",
                "24001",
                "24002",
                "24003",
                "24004",
                "24005",
                "24006",
                "2600",
                "2700",
                "9999",
                "99990",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Grünfläche.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungGruen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Parkanlage",
                        "description": "Parkanlage; auch: Erholungsgrün, Grünanlage, Naherholung.",
                    },
                    "10000": {
                        "name": "ParkanlageHistorisch",
                        "description": "Historische Parkanlage",
                    },
                    "10001": {
                        "name": "ParkanlageNaturnah",
                        "description": "Naturnahe Parkanlage",
                    },
                    "10002": {
                        "name": "ParkanlageWaldcharakter",
                        "description": "Parkanlage mit Waldcharakter",
                    },
                    "10003": {
                        "name": "NaturnaheUferParkanlage",
                        "description": "Ufernahe Parkanlage",
                    },
                    "1200": {
                        "name": "Dauerkleingarten",
                        "description": "Dauerkleingarten; auch: Gartenfläche, Hofgärten, Gartenland.",
                    },
                    "12000": {
                        "name": "ErholungsGaerten",
                        "description": "Erholungsgarten",
                    },
                    "1400": {"name": "Sportplatz", "description": "Sportplatz"},
                    "14000": {
                        "name": "Reitsportanlage",
                        "description": "Reitsportanlage",
                    },
                    "14001": {
                        "name": "Hundesportanlage",
                        "description": "Hundesportanlage",
                    },
                    "14002": {
                        "name": "Wassersportanlage",
                        "description": "Wassersportanlage",
                    },
                    "14003": {"name": "Schiessstand", "description": "Schießstand"},
                    "14004": {"name": "Golfplatz", "description": "Golfplatz"},
                    "14005": {"name": "Skisport", "description": "Anlage für Skisport"},
                    "14006": {"name": "Tennisanlage", "description": "Tennisanlage"},
                    "14007": {
                        "name": "SonstigerSportplatz",
                        "description": "Sonstiger Sportplatz\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1400 verwendet werden.",
                    },
                    "1600": {"name": "Spielplatz", "description": "Spielplatz"},
                    "16000": {"name": "Bolzplatz", "description": "Bolzplatz"},
                    "16001": {
                        "name": "Abenteuerspielplatz",
                        "description": "Abenteuerspielplatz",
                    },
                    "1800": {"name": "Zeltplatz", "description": "Zeltplatz"},
                    "18000": {"name": "Campingplatz", "description": "Campingplatz"},
                    "2000": {
                        "name": "Badeplatz",
                        "description": "Badeplatz, auch Schwimmbad, Liegewiese.",
                    },
                    "2200": {
                        "name": "FreizeitErholung",
                        "description": "Anlage für Freizeit und Erholung.",
                    },
                    "22000": {
                        "name": "Kleintierhaltung",
                        "description": "Anlage für Kleintierhaltung",
                    },
                    "22001": {"name": "Festplatz", "description": "Festplatz"},
                    "2400": {
                        "name": "SpezGruenflaeche",
                        "description": "Spezielle Grünfläche",
                    },
                    "24000": {
                        "name": "StrassenbegleitGruen",
                        "description": "Straßenbegleitgrün",
                    },
                    "24001": {
                        "name": "BoeschungsFlaeche",
                        "description": "Böschungsfläche",
                    },
                    "24002": {
                        "name": "FeldWaldWiese",
                        "description": "Feld, Wald, Wiese allgemein\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2400 verwendet werden.",
                    },
                    "24003": {
                        "name": "Uferschutzstreifen",
                        "description": "Uferstreifen",
                    },
                    "24004": {"name": "Abschirmgruen", "description": "Abschirmgrün"},
                    "24005": {
                        "name": "UmweltbildungsparkSchaugatter",
                        "description": "Umweltbildungspark, Schaugatter",
                    },
                    "24006": {
                        "name": "RuhenderVerkehr",
                        "description": "Fläche für den ruhenden Verkehr.",
                    },
                    "2600": {"name": "Friedhof", "description": "Friedhof"},
                    "2700": {
                        "name": "Naturerfahrungsraum",
                        "description": "Naturerfahrungsräume sollen insbesondere Kindern und Jugendlichen die Möglichkeit geben, in ihrem direkten Umfeld Natur vorzufinden, um eigenständig Erfahrung mit Pflanzen und Tieren sammeln zu können.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Zweckbestimmung, falls keine der aufgeführten Klassifikationen anwendbar ist.",
                    },
                    "99990": {"name": "Gaertnerei", "description": "Gärtnerei"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestGruen",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    nutzungsform: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Nutzungsform der Grünfläche.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Privat", "description": "Private Nutzung"},
                    "2000": {
                        "name": "Oeffentlich",
                        "description": "Öffentliche Nutzung",
                    },
                },
                "typename": "XP_Nutzungsform",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPKeineZentrAbwasserBeseitigungFlaeche(FPFlaechenobjekt):
    """
    Baufläche, für die eine zentrale Abwasserbeseitigung nicht vorgesehen ist (§ 5, Abs. 2, Nr. 1 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class FPKennzeichnung(FPGeometrieobjekt):
    """
    Kennzeichnung gemäß §5 Abs. 3 BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000", "2000", "3000", "4000", "5000", "6000", "7000", "8000", "9999"
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Kennzeichnung.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungKennzeichnung",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Naturgewalten",
                        "description": "Flächen, bei deren Bebauung besondere bauliche Sicherungsmaßnahmen gegen Naturgewalten erforderlich sind (§5, Abs. 3, Nr. 1 BauGB).",
                    },
                    "2000": {
                        "name": "Abbauflaeche",
                        "description": "Flächen, die für den Abbau von Mineralien bestimmt sind (§5, Abs. 3, Nr. 2 und §9, Abs. 5, Nr. 2. BauGB).",
                    },
                    "3000": {
                        "name": "AeussereEinwirkungen",
                        "description": "Flächen, bei deren Bebauung besondere bauliche Sicherungsmaßnahmen gegen äußere Einwirkungen erforderlich sind (§5, Abs. 3, Nr. 1 BauGB).",
                    },
                    "4000": {
                        "name": "SchadstoffBelastBoden",
                        "description": "Für bauliche Nutzung vorgesehene Flächen, deren Böden erheblich mit umweltgefährdenden Stoffen belastet sind (§5, Abs. 3, Nr. 3 BauGB).",
                    },
                    "5000": {
                        "name": "LaermBelastung",
                        "description": "Für bauliche Nutzung vorgesehene Flächen, die erheblicher Lärmbelastung ausgesetzt sind.",
                    },
                    "6000": {
                        "name": "Bergbau",
                        "description": "Flächen, unter denen der Bergbau umgeht  (§5, Abs. 3, Nr. 2 und §9, Abs. 5, Nr. 2. BauGB).",
                    },
                    "7000": {
                        "name": "Bodenordnung",
                        "description": "Für Bodenordnungsmaßnahmen vorgesehene Gebiete, \r\nz.B. Gebiete für Umlegungen oder Flurbereinigung",
                    },
                    "8000": {
                        "name": "Vorhabensgebiet",
                        "description": "Räumlich besonders gekennzeichnetes Vorhabengebiets, das kleiner als der Geltungsbereich ist, innerhalb eines vorhabenbezogenen BPlans.",
                    },
                    "9999": {
                        "name": "AndereGesetzlVorschriften",
                        "description": "Kennzeichnung nach anderen gesetzlichen Vorschriften.",
                    },
                },
            },
        ),
    ] = None
    istVerdachtsflaeche: Annotated[
        bool | None,
        Field(
            description="Legt fest, ob eine Altlast-Verdachtsfläche vorliegt",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Nummer in einem Altlastkataster",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPLandwirtschaft(FPGeometrieobjekt):
    """
    Darstellung einer Landwirtschaftsfläche nach §5, Abs. 2, Nr. 9a.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "9999"
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Fläche.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungLandwirtschaft",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "LandwirtschaftAllgemein",
                        "description": "Allgemeine Landwirtschaft",
                    },
                    "1100": {"name": "Ackerbau", "description": "Ackerbau"},
                    "1200": {
                        "name": "WiesenWeidewirtschaft",
                        "description": "Wiesen- und Weidewirtschaft",
                    },
                    "1300": {
                        "name": "GartenbaulicheErzeugung",
                        "description": "Gartenbauliche Erzeugung",
                    },
                    "1400": {"name": "Obstbau", "description": "Obstbau"},
                    "1500": {"name": "Weinbau", "description": "Weinbau"},
                    "1600": {"name": "Imkerei", "description": "Imkerei"},
                    "1700": {
                        "name": "Binnenfischerei",
                        "description": "Binnenfischerei",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestLandwirtschaftsFlaeche",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class FPLandwirtschaftsFlaeche(FPFlaechenschlussobjekt):
    """
    Darstellung einer Landwirtschaftsfläche nach §5, Abs. 2, Nr. 9a.

    Die Klasse ist als veraltet gekennzeinet und wird in Version 6.0 wegfallen. Es sollte stattdessen die Klasse FP_Landwirtschaft verwendet werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "9999"
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Fläche.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungLandwirtschaft",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "LandwirtschaftAllgemein",
                        "description": "Allgemeine Landwirtschaft",
                    },
                    "1100": {"name": "Ackerbau", "description": "Ackerbau"},
                    "1200": {
                        "name": "WiesenWeidewirtschaft",
                        "description": "Wiesen- und Weidewirtschaft",
                    },
                    "1300": {
                        "name": "GartenbaulicheErzeugung",
                        "description": "Gartenbauliche Erzeugung",
                    },
                    "1400": {"name": "Obstbau", "description": "Obstbau"},
                    "1500": {"name": "Weinbau", "description": "Weinbau"},
                    "1600": {"name": "Imkerei", "description": "Imkerei"},
                    "1700": {
                        "name": "Binnenfischerei",
                        "description": "Binnenfischerei",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestLandwirtschaftsFlaeche",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class FPLinienobjekt(FPObjekt):
    """
    Basisklasse für alle Objekte eines Flächennutzungsplans mit linienförmigem Raumbezug (eine einzelne zusammenhängende Kurve, die aus Linienstücken und Kreisbögen zusammengesetzt sein kann, oder eine Menge derartiger Kurven).
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Line | definitions.MultiLine,
        Field(
            description="Linienförmiger Raumbezug (Einzelne zusammenhängende Kurve, die aus Linienstücken und Kreisbögen aufgebaut ist, oder eine Menge derartiger Kurven).",
            json_schema_extra={
                "typename": "XP_Liniengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]


class FPPrivilegiertesVorhaben(FPGeometrieobjekt):
    """
    Standorte für privilegierte Außenbereichsvorhaben und für sonstige Anlagen in Außenbereichen gem. § 35 Abs. 1 und 2 BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "10001",
                "10002",
                "10003",
                "10004",
                "1200",
                "12000",
                "12001",
                "12002",
                "12003",
                "12004",
                "12005",
                "1400",
                "1600",
                "16000",
                "16001",
                "16002",
                "1800",
                "18000",
                "18001",
                "18002",
                "18003",
                "2000",
                "20000",
                "20001",
                "9999",
                "99990",
                "99991",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmungen des Vorhabens.",
            json_schema_extra={
                "typename": "FP_ZweckbestimmungPrivilegiertesVorhaben",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "LandForstwirtschaft",
                        "description": 'Allgemeines Vorhaben nach §35 Abs. 1 Nr. 1 oder 2 BauGB: Vorhaben, dass "einem land- oder forstwirtschaftlichen Betrieb dient und nur einen untergeordneten Teil der Betriebsfläche einnimmt", oder "einem Betrieb der gartenbaulichen Erzeugung dient".',
                    },
                    "10000": {"name": "Aussiedlerhof", "description": "Aussiedlerhof"},
                    "10001": {"name": "Altenteil", "description": "Altenteil"},
                    "10002": {"name": "Reiterhof", "description": "Reiterhof"},
                    "10003": {
                        "name": "Gartenbaubetrieb",
                        "description": "Gartenbaubetrieb",
                    },
                    "10004": {"name": "Baumschule", "description": "Baumschule"},
                    "1200": {
                        "name": "OeffentlicheVersorgung",
                        "description": 'Allgemeines Vorhaben nach § 35 Abs. 1 Nr. 3 BauBG: Vorhaben dass "der öffentlichen Versorgung mit Elektrizität, Gas,\r\nTelekommunikationsdienstleistungen, Wärme und Wasser, der Abwasserwirtschaft" ... dient.',
                    },
                    "12000": {
                        "name": "Wasser",
                        "description": "Öffentliche Wasserversorgung",
                    },
                    "12001": {"name": "Gas", "description": "Gasversorgung"},
                    "12002": {
                        "name": "Waerme",
                        "description": "Versorgung mit Fernwärme",
                    },
                    "12003": {
                        "name": "Elektrizitaet",
                        "description": "Versorgung mit Elektrizität.",
                    },
                    "12004": {
                        "name": "Telekommunikation",
                        "description": "Versorgung mit Telekommunikations-Dienstleistungen.",
                    },
                    "12005": {"name": "Abwasser", "description": "Abwasser Entsorgung"},
                    "1400": {
                        "name": "OrtsgebundenerGewerbebetrieb",
                        "description": 'Vorhaben nach §35 Abs. 1 Nr. 3 BauGB: Vorhaben das ...."einem ortsgebundenen gewerblichen Betrieb dient".',
                    },
                    "1600": {
                        "name": "BesonderesVorhaben",
                        "description": 'Vorhaben nach §35 Abs. 1 Nr. 4 BauGB: Vorhaben, dass "wegen seiner besonderen Anforderungen an die Umgebung, wegen seiner nachteiligen Wirkung auf die Umgebung oder wegen seiner besonderen Zweckbestimmung nur im Außenbereich ausgeführt werden soll".',
                    },
                    "16000": {
                        "name": "BesondereUmgebungsAnforderung",
                        "description": "Vorhaben dass wegen seiner besonderen Anforderungen an die Umgebung nur im Außenbereich durchgeführt werden soll.",
                    },
                    "16001": {
                        "name": "NachteiligeUmgebungsWirkung",
                        "description": "Vorhaben dass wegen seiner nachteiligen Wirkung auf die Umgebung nur im Außenbereich durchgeführt werden soll.",
                    },
                    "16002": {
                        "name": "BesondereZweckbestimmung",
                        "description": "Vorhaben dass wegen seiner besonderen Zweckbestimmung nur im Außenbereich durchgeführt werden soll.",
                    },
                    "1800": {
                        "name": "ErneuerbareEnergien",
                        "description": 'Allgemeine Vorhaben nach §35 Abs. 1 Nr. 4 BauGB: Vorhaben, dass "wegen seiner besonderen Anforderungen an die Umgebung, wegen seiner nachteiligen Wirkung auf die Umgebung oder wegen seiner besonderen Zweckbestimmung nur im Außenbereich ausgeführt werden soll".',
                    },
                    "18000": {
                        "name": "Windenergie",
                        "description": "Vorhaben zur Erforschung, Entwicklung oder Nutzung der Windenergie.",
                    },
                    "18001": {
                        "name": "Wasserenergie",
                        "description": "Vorhaben zur Erforschung, Entwicklung oder Nutzung der Wasserenergie.",
                    },
                    "18002": {
                        "name": "Solarenergie",
                        "description": "Vorhaben zur Erforschung, Entwicklung oder Nutzung der Solarenergie.",
                    },
                    "18003": {
                        "name": "Biomasse",
                        "description": "Vorhaben zur energetischen Nutzung der Biomasse.",
                    },
                    "2000": {
                        "name": "Kernenergie",
                        "description": 'Vorhaben nach §35 Abs. 1 Nr. 7 BauGB: Vorhaben das "der Erforschung, Entwicklung oder Nutzung der Kernenergie zu friedlichen Zwecken oder der Entsorgung radioaktiver Abfälle dient".',
                    },
                    "20000": {
                        "name": "NutzungKernerergie",
                        "description": "Vorhaben der Erforschung, Entwicklung oder Nutzung der Kernenergie zu friedlichen Zwecken.",
                    },
                    "20001": {
                        "name": "EntsorgungRadioaktiveAbfaelle",
                        "description": "Vorhaben zur Entsorgung radioaktiver Abfälle.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges Vorhaben im Aussenbereich nach §35 Abs. 2 BauGB.",
                    },
                    "99990": {"name": "StandortEinzelhof", "description": "Einzelhof"},
                    "99991": {
                        "name": "BebauteFlaecheAussenbereich",
                        "description": "Bebaute Fläche im Außenbereich",
                    },
                },
            },
        ),
    ] = None
    vorhaben: Annotated[
        str | None,
        Field(
            description="Nähere Beschreibung des Vorhabens.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPSchutzPflegeEntwicklung(FPGeometrieobjekt):
    """
    Umgrenzung von Flächen für Maßnahmen zum Schutz, zur Pflege und zur Entwicklung von Natur und Landschaft (§5 Abs. 2, Nr. 10 BauGB)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der Maßnahmen",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstZiel: Annotated[
        str | None,
        Field(
            description="Textlich formuliertes Ziel, wenn das Attribut ziel den Wert 9999 (Sonstiges) hat.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahme: Annotated[
        list[XPSPEMassnahmenDaten] | None,
        Field(
            description="Durchzuführende Maßnahme.",
            json_schema_extra={
                "typename": "XP_SPEMassnahmenDaten",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    istAusgleich: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob die Maßnahme zum Ausgleich eines Eingriffs benutzt wird.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False


class FPSpielSportanlage(FPGeometrieobjekt):
    """
    Darstellung von Flächen für Spiel- und Sportanlagen nach §5,  Abs. 2, Nr. 2 BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[Literal["1000", "2000", "3000", "9999"]] | None,
        Field(
            description="Zweckbestimmung der Fläche.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungSpielSportanlage",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Sportanlage", "description": "Sportanlage"},
                    "2000": {"name": "Spielanlage", "description": "Spielanlage"},
                    "3000": {
                        "name": "SpielSportanlage",
                        "description": "Spiel- und/oder Sportanlage.",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestSpielSportanlage",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class FPStrassenverkehr(FPGeometrieobjekt):
    """
    Darstellung von Flächen für den überörtlichen Verkehr und für die örtlichen Hauptverkehrszüge ( §5, Abs. 2, Nr. 3 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "1200",
                "1300",
                "1400",
                "14000",
                "14001",
                "14002",
                "14003",
                "14004",
                "14005",
                "14006",
                "14007",
                "14008",
                "14009",
                "140010",
                "140011",
                "140012",
                "140013",
                "1600",
                "16000",
                "16001",
                "16002",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung des Objektes.",
            json_schema_extra={
                "typename": "FP_ZweckbestimmungStrassenverkehr",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Autobahn",
                        "description": "Autobahn und autobahnähnliche Straße.",
                    },
                    "1200": {
                        "name": "Hauptverkehrsstrasse",
                        "description": "Sonstige örtliche oder überörtliche Hauptverkehrsstraße bzw. Weg.",
                    },
                    "1300": {"name": "Ortsdurchfahrt", "description": "Ortsdurchfahrt"},
                    "1400": {
                        "name": "SonstigerVerkehrswegAnlage",
                        "description": "Sonstiger Verkehrsweg oder Anlage.",
                    },
                    "14000": {
                        "name": "VerkehrsberuhigterBereich",
                        "description": "Verkehrsberuhigter Bereich",
                    },
                    "14001": {"name": "Platz", "description": "Platz"},
                    "14002": {
                        "name": "Fussgaengerbereich",
                        "description": "Fußgängerbereich",
                    },
                    "14003": {"name": "RadGehweg", "description": "Rad- und Fußweg"},
                    "14004": {"name": "Radweg", "description": "Radweg"},
                    "14005": {"name": "Gehweg", "description": "Fußweg"},
                    "14006": {"name": "Wanderweg", "description": "Wanderweg"},
                    "14007": {
                        "name": "ReitKutschweg",
                        "description": "Reit- und Kutschweg",
                    },
                    "14008": {"name": "Rastanlage", "description": "Rastanlage"},
                    "14009": {
                        "name": "Busbahnhof",
                        "description": "Busbahnhof, auch zentraler Omnibusbahnhof (ZOB)",
                    },
                    "140010": {
                        "name": "UeberfuehrenderVerkehrsweg",
                        "description": "Brückenbereich, hier: Überführender Verkehrsweg.",
                    },
                    "140011": {
                        "name": "UnterfuehrenderVerkehrsweg",
                        "description": "Brückenbereich, hier: Unterführender Verkehrsweg.",
                    },
                    "140012": {
                        "name": "Wirtschaftsweg",
                        "description": "Wirtschaftsweg",
                    },
                    "140013": {
                        "name": "LandwirtschaftlicherVerkehr",
                        "description": "Landwirtschaftlicher Verkehr",
                    },
                    "1600": {
                        "name": "RuhenderVerkehr",
                        "description": "Fläche oder Anlage für den ruhenden Verkehr",
                    },
                    "16000": {"name": "Parkplatz", "description": "Parkplatz"},
                    "16001": {
                        "name": "FahrradAbstellplatz",
                        "description": "Abstellplatz für Fahräder",
                    },
                    "16002": {
                        "name": "P_RAnlage",
                        "description": "Park- and Ride-Anlage",
                    },
                    "3000": {
                        "name": "CarSharing",
                        "description": "Fläche zum Car-Sharing",
                    },
                    "3100": {
                        "name": "BikeSharing",
                        "description": "Fläche zum Abstellen gemeinschaftlich genutzter Fahrräder",
                    },
                    "3200": {
                        "name": "B_RAnlage",
                        "description": "Bike and Ride Anlage",
                    },
                    "3300": {"name": "Parkhaus", "description": "Parkhaus"},
                    "3400": {
                        "name": "Mischverkehrsflaeche",
                        "description": "Mischverkehrsfläche",
                    },
                    "3500": {
                        "name": "Ladestation",
                        "description": "Ladestation für Elektrofahrzeuge",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Zweckbestimmung",
                    },
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestStrassenverkehr",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    nutzungsform: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Nutzungsform",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Privat", "description": "Private Nutzung"},
                    "2000": {
                        "name": "Oeffentlich",
                        "description": "Öffentliche Nutzung",
                    },
                },
                "typename": "XP_Nutzungsform",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPUeberlagerungsobjekt(FPFlaechenobjekt):
    """
    Basisklasse für alle Objekte eines Flächennutzungsplans mit flächenhaftem Raumbezug, die immer Überlagerungsobjekte sind.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class FPUnverbindlicheVormerkung(FPGeometrieobjekt):
    """
    Unverbindliche Vormerkung späterer Planungsabsichten
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    vormerkung: Annotated[
        str | None,
        Field(
            description="Text der Vormerkung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPVerEntsorgung(FPGeometrieobjekt):
    """
    Flächen für Versorgungsanlagen, für die Abfallentsorgung und Abwasserbeseitigung sowie für Ablagerungen (§5, Abs. 2, Nr. 4 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "10001",
                "10002",
                "10003",
                "10004",
                "10005",
                "10006",
                "10007",
                "10008",
                "10009",
                "100010",
                "100011",
                "100012",
                "100013",
                "1200",
                "12000",
                "12001",
                "12002",
                "12003",
                "12004",
                "12005",
                "1300",
                "13000",
                "13001",
                "13002",
                "13003",
                "1400",
                "14000",
                "14001",
                "14002",
                "1600",
                "16000",
                "16001",
                "16002",
                "16003",
                "16004",
                "16005",
                "1800",
                "18000",
                "18001",
                "18002",
                "18003",
                "18004",
                "18005",
                "18006",
                "2000",
                "20000",
                "20001",
                "2200",
                "22000",
                "22001",
                "22002",
                "22003",
                "2400",
                "24000",
                "24001",
                "24002",
                "24003",
                "24004",
                "24005",
                "2600",
                "26000",
                "26001",
                "26002",
                "2800",
                "3000",
                "9999",
                "99990",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Fläche.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungVerEntsorgung",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Elektrizitaet",
                        "description": "Elektrizität allgemein",
                    },
                    "10000": {
                        "name": "Hochspannungsleitung",
                        "description": "Hochspannungsleitung",
                    },
                    "10001": {
                        "name": "TrafostationUmspannwerk",
                        "description": "Trafostation, auch Umspannwerk",
                    },
                    "10002": {
                        "name": "Solarkraftwerk",
                        "description": "Solarkraftwerk",
                    },
                    "10003": {
                        "name": "Windkraftwerk",
                        "description": "Windkraftwerk, Windenergieanlage, Windrad.",
                    },
                    "10004": {
                        "name": "Geothermiekraftwerk",
                        "description": "Geothermie Kraftwerk",
                    },
                    "10005": {
                        "name": "Elektrizitaetswerk",
                        "description": "Elektrizitätswerk allgemein",
                    },
                    "10006": {
                        "name": "Wasserkraftwerk",
                        "description": "Wasserkraftwerk",
                    },
                    "10007": {
                        "name": "BiomasseKraftwerk",
                        "description": "Biomasse-Kraftwerk",
                    },
                    "10008": {"name": "Kabelleitung", "description": "Kabelleitung"},
                    "10009": {
                        "name": "Niederspannungsleitung",
                        "description": "Niederspannungsleitung",
                    },
                    "100010": {"name": "Leitungsmast", "description": "Leitungsmast"},
                    "100011": {"name": "Kernkraftwerk", "description": "Kernkraftwerk"},
                    "100012": {
                        "name": "Kohlekraftwerk",
                        "description": "Kohlekraftwerk",
                    },
                    "100013": {"name": "Gaskraftwerk", "description": "Kohlekraftwerk"},
                    "1200": {"name": "Gas", "description": "Gas allgemein"},
                    "12000": {
                        "name": "Ferngasleitung",
                        "description": "Ferngasleitung",
                    },
                    "12001": {"name": "Gaswerk", "description": "Gaswerk"},
                    "12002": {"name": "Gasbehaelter", "description": "Gasbehälter"},
                    "12003": {
                        "name": "Gasdruckregler",
                        "description": "Gasdruckregler",
                    },
                    "12004": {"name": "Gasstation", "description": "Gasstation"},
                    "12005": {"name": "Gasleitung", "description": "Gasleitung"},
                    "1300": {"name": "Erdoel", "description": "Erdöl allgemein"},
                    "13000": {"name": "Erdoelleitung", "description": "Erdölleitung"},
                    "13001": {"name": "Bohrstelle", "description": "Bohrstelle"},
                    "13002": {
                        "name": "Erdoelpumpstation",
                        "description": "Erdölpumpstation",
                    },
                    "13003": {"name": "Oeltank", "description": "Öltank"},
                    "1400": {
                        "name": "Waermeversorgung",
                        "description": "Wärmeversorgung allgemein",
                    },
                    "14000": {
                        "name": "Blockheizkraftwerk",
                        "description": "Blockheizkraftwerk",
                    },
                    "14001": {
                        "name": "Fernwaermeleitung",
                        "description": "Fernwärmeleitung",
                    },
                    "14002": {"name": "Fernheizwerk", "description": "Fernheizwerk"},
                    "1600": {
                        "name": "Wasser",
                        "description": "Trink- und Brauchwasser allgemein",
                    },
                    "16000": {"name": "Wasserwerk", "description": "Wasserwerk"},
                    "16001": {
                        "name": "Wasserleitung",
                        "description": "Trinkwasserleitung",
                    },
                    "16002": {
                        "name": "Wasserspeicher",
                        "description": "Wasserspeicher",
                    },
                    "16003": {"name": "Brunnen", "description": "Brunnen"},
                    "16004": {"name": "Pumpwerk", "description": "Pumpwerk"},
                    "16005": {"name": "Quelle", "description": "Quelle"},
                    "1800": {"name": "Abwasser", "description": "Abwasser allgemein"},
                    "18000": {
                        "name": "Abwasserleitung",
                        "description": "Abwasserleitung",
                    },
                    "18001": {
                        "name": "Abwasserrueckhaltebecken",
                        "description": "Abwasserrückhaltebecken",
                    },
                    "18002": {
                        "name": "Abwasserpumpwerk",
                        "description": "Abwasserpumpwerk, auch Abwasserhebeanlage",
                    },
                    "18003": {"name": "Klaeranlage", "description": "Kläranlage"},
                    "18004": {
                        "name": "AnlageKlaerschlamm",
                        "description": "Anlage zur Speicherung oder Behandlung von Klärschlamm.",
                    },
                    "18005": {
                        "name": "SonstigeAbwasserBehandlungsanlage",
                        "description": "Sonstige Abwasser-Behandlungsanlage.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1800 verwendet werden.",
                    },
                    "18006": {
                        "name": "SalzOderSoleleitungen",
                        "description": "Salz- oder Sole-Leitungen",
                    },
                    "2000": {
                        "name": "Regenwasser",
                        "description": "Regenwasser allgemein",
                    },
                    "20000": {
                        "name": "RegenwasserRueckhaltebecken",
                        "description": "Regenwasser Rückhaltebecken",
                    },
                    "20001": {
                        "name": "Niederschlagswasserleitung",
                        "description": "Niederschlagswasser-Leitung",
                    },
                    "2200": {
                        "name": "Abfallentsorgung",
                        "description": "Abfallentsorgung allgemein",
                    },
                    "22000": {
                        "name": "Muellumladestation",
                        "description": "Müll-Umladestation",
                    },
                    "22001": {
                        "name": "Muellbeseitigungsanlage",
                        "description": "Müllbeseitigungsanlage",
                    },
                    "22002": {
                        "name": "Muellsortieranlage",
                        "description": "Müllsortieranlage",
                    },
                    "22003": {"name": "Recyclinghof", "description": "Recyclinghof"},
                    "2400": {
                        "name": "Ablagerung",
                        "description": "Ablagerung allgemein",
                    },
                    "24000": {
                        "name": "Erdaushubdeponie",
                        "description": "Erdaushub-Deponie",
                    },
                    "24001": {
                        "name": "Bauschuttdeponie",
                        "description": "Bauschutt-Deponie",
                    },
                    "24002": {
                        "name": "Hausmuelldeponie",
                        "description": "Hausmüll-Deponie",
                    },
                    "24003": {
                        "name": "Sondermuelldeponie",
                        "description": "Sondermüll-Deponie",
                    },
                    "24004": {
                        "name": "StillgelegteDeponie",
                        "description": "Stillgelegte Deponie",
                    },
                    "24005": {
                        "name": "RekultivierteDeponie",
                        "description": "Rekultivierte Deponie",
                    },
                    "2600": {
                        "name": "Telekommunikation",
                        "description": "Telekommunikation allgemein",
                    },
                    "26000": {
                        "name": "Fernmeldeanlage",
                        "description": "Fernmeldeanlage",
                    },
                    "26001": {
                        "name": "Mobilfunkanlage",
                        "description": "Mobilfunkanlage",
                    },
                    "26002": {
                        "name": "Fernmeldekabel",
                        "description": "Fernmeldekabel",
                    },
                    "2800": {
                        "name": "ErneuerbareEnergien",
                        "description": "Erneuerbare Energien allgemein",
                    },
                    "3000": {
                        "name": "KraftWaermeKopplung",
                        "description": "Fläche oder Anlage für Kraft-Wärme Kopplung",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige, durch keinen anderen Code abbildbare Ver- oder Entsorgungsfläche bzw. -Anlage.",
                    },
                    "99990": {
                        "name": "Produktenleitung",
                        "description": "Produktenleitung",
                    },
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestVerEntsorgung",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    textlicheErgaenzung: Annotated[
        str | None,
        Field(
            description="Textliche Ergänzung der Flächenausweisung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zugunstenVon: Annotated[
        str | None,
        Field(
            description="Angabe des Begünstigten der Ausweisung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPVorbehalteFlaeche(FPFlaechenobjekt):
    """
    Flächen auf denen bestimmte Vorbehalte wirksam sind.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    vorbehalt: Annotated[
        str | None,
        Field(
            description="Textliche Formulierung des Vorbehalts.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPWaldFlaeche(FPFlaechenschlussobjekt):
    """
    Darstellung von Waldflächen nach §5, Abs. 2, Nr. 9b,
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "1200",
                "1400",
                "1600",
                "16000",
                "16001",
                "16002",
                "16003",
                "16004",
                "1700",
                "1800",
                "1900",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Funktion der Waldfläche.",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungWald",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Naturwald", "description": "Naturwald"},
                    "10000": {
                        "name": "Waldschutzgebiet",
                        "description": "Waldschutzgebiet",
                    },
                    "1200": {"name": "Nutzwald", "description": "Nutzwald"},
                    "1400": {"name": "Erholungswald", "description": "Erholungswald"},
                    "1600": {"name": "Schutzwald", "description": "Schutzwald"},
                    "16000": {
                        "name": "Bodenschutzwald",
                        "description": "Bodenschutzwald",
                    },
                    "16001": {
                        "name": "Biotopschutzwald",
                        "description": "Biotopschutzwald",
                    },
                    "16002": {
                        "name": "NaturnaherWald",
                        "description": "Naturnaher Wald",
                    },
                    "16003": {
                        "name": "SchutzwaldSchaedlicheUmwelteinwirkungen",
                        "description": "Wald zum Schutz vor schädlichen Umwelteinwirkungen",
                    },
                    "16004": {"name": "Schonwald", "description": "Schonwald"},
                    "1700": {"name": "Bannwald", "description": "Bannwald"},
                    "1800": {
                        "name": "FlaecheForstwirtschaft",
                        "description": "Fläche für die Forstwirtschaft.",
                    },
                    "1900": {
                        "name": "ImmissionsgeschaedigterWald",
                        "description": "Immissionsgeschädigter Wald",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstigr Wald"},
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Funktion des Waldes.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestWaldFlaeche",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    eigentumsart: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "12000",
            "12001",
            "2000",
            "20000",
            "20001",
            "3000",
            "9999",
        ]
        | None,
        Field(
            description="Festlegung der Eigentumsart des Waldes",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "OeffentlicherWald",
                        "description": "Öffentlicher Wald allgemein",
                    },
                    "1100": {"name": "Staatswald", "description": "Staatswald"},
                    "1200": {
                        "name": "Koerperschaftswald",
                        "description": "Körperschaftswald",
                    },
                    "12000": {"name": "Kommunalwald", "description": "Kommunalwald"},
                    "12001": {"name": "Stiftungswald", "description": "Stiftungswald"},
                    "2000": {
                        "name": "Privatwald",
                        "description": "Privatwald allgemein",
                    },
                    "20000": {
                        "name": "Gemeinschaftswald",
                        "description": "Gemeinschaftswald",
                    },
                    "20001": {
                        "name": "Genossenschaftswald",
                        "description": "Genossenschaftswald",
                    },
                    "3000": {"name": "Kirchenwald", "description": "Kirchenwald"},
                    "9999": {"name": "Sonstiges", "description": "Sonstiger Wald"},
                },
                "typename": "XP_EigentumsartWald",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    betreten: Annotated[
        list[Literal["1000", "2000", "3000", "4000"]] | None,
        Field(
            description="Festlegung zusätzlicher, normalerweise nicht-gestatteter Aktivitäten, die in dem Wald ausgeführt werden dürfen, nach §14 Abs. 2 Bundeswaldgesetz.",
            json_schema_extra={
                "typename": "XP_WaldbetretungTyp",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Radfahren", "description": "Radfahren"},
                    "2000": {"name": "Reiten", "description": "Reiten"},
                    "3000": {"name": "Fahren", "description": "Fahren"},
                    "4000": {"name": "Hundesport", "description": "Hundesport"},
                },
            },
        ),
    ] = None


class FPWasserwirtschaft(FPGeometrieobjekt):
    """
    Die für die Wasserwirtschaft vorgesehenen Flächen sowie Flächen, die im Interesse des Hochwasserschutzes und der Regelung des Wasserabflusses freizuhalten sind (§5 Abs. 2 Nr. 7 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        Literal["1000", "1100", "1200", "1300", "1400", "1500", "9999"] | None,
        Field(
            description="Zweckbestimmung des Objektes",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "HochwasserRueckhaltebecken",
                        "description": "Hochwasser-Rückhaltebecken",
                    },
                    "1100": {
                        "name": "Ueberschwemmgebiet",
                        "description": "Überschwemmungsgefährdetes Gebiet nach §31c des vor dem 1.10.2010 gültigen WHG",
                    },
                    "1200": {
                        "name": "Versickerungsflaeche",
                        "description": "Versickerungsfläche",
                    },
                    "1300": {
                        "name": "Entwaesserungsgraben",
                        "description": "Entwässerungsgraben",
                    },
                    "1400": {"name": "Deich", "description": "Deich"},
                    "1500": {
                        "name": "RegenRueckhaltebecken",
                        "description": "Regen-Rückhaltebecken",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Wasserwirtschaftsfläche, sofern keiner der anderen Codes zutreffend ist.",
                    },
                },
                "typename": "XP_ZweckbestimmungWasserwirtschaft",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        AnyUrl | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung des Objektes.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestWasserwirtschaft",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPZentralerVersorgungsbereich(FPUeberlagerungsobjekt):
    """
    Darstellung nach § 5 Abs. 2 Nr. 2d (Ausstattung des Gemeindegebietes mit zentralen Versorgungsbereichen).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    auspraegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte Ausprägung eines zentralen Versorgungsbereiches.",
            json_schema_extra={
                "typename": "FP_ZentralerVersorgungsbereichAuspraegung",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPFlaechenobjekt(LPObjekt):
    """
    Basisklasse für alle Objekte eines Landschaftsplans mit flächenhaftem Raumbezug (eine Einzelfläche oder eine Menge von Flächen, die sich nicht überlappen dürfen).
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Polygon | definitions.MultiPolygon,
        Field(
            description="Flächenhafter Raumbezug des Objektes (Eine Einzelfläche oder eine Menge von Flächen, die sich nicht überlappen dürfen). .",
            json_schema_extra={
                "typename": "XP_Flaechengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]


class LPGeometrieobjekt(LPObjekt):
    """
    Basisklasse für alle Objekte eines Landschaftsplans mit variablem Raumbezug. Ein konkretes Objekt muss entweder punktförmigen, linienförmigen oder flächenhaften Raumbezug haben, gemischte Geometrie ist nicht zugelassen.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point
        | definitions.MultiPoint
        | definitions.Line
        | definitions.MultiLine
        | definitions.Polygon
        | definitions.MultiPolygon,
        Field(
            description="Raumbezug - Entweder punktförmig, linienförmig oder flächenhaft, gemischte Geometrie ist nicht zugelassen.",
            json_schema_extra={
                "typename": "XP_VariableGeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    flussrichtung: Annotated[
        bool | None,
        Field(
            description="Das Attribut ist nur relevant, wenn ein Geometrieobjekt einen linienhaften Raumbezug hat. Ist es mit dem Wert true belegt, wird damit ausgedrückt, dass der Linie eine Flussrichtung  in Digitalisierungsrichtung zugeordnet ist. In diesem Fall darf bei Im- und Export die Digitalisierungsreihenfolge der Stützpunkte nicht geändert werden. Wie eine definierte Flussrichtung  zu interpretieren oder bei einer Plandarstellung zu visualisieren ist, bleibt der Implementierung überlassen.\r\nIst der Attributwert false oder das Attribut nicht belegt, ist die Digitalisierungsreihenfolge der Stützpunkte irrelevant.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nordwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Orientierung des Objektes bei punkförmigem Raumbezug als Winkel gegen die Nordrichtung. Zählweise im geographischen Sinn (von Nord über Ost nach Süd und West).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class LPLandschaftsbild(LPGeometrieobjekt):
    """
    Festlegung, Darstellung bzw. Festsetzung zum Landschaftsbild in einem  landschaftsplanerischen Planwerk.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    massnahme: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte Spezifizierung der Maßnahme zum Landschaftsbild.",
            json_schema_extra={
                "typename": "LP_MassnahmeLandschaftsbild",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPLinienobjekt(LPObjekt):
    """
    Basisklasse für alle Objekte eines Landschaftsplans mit linienförmigem Raumbezug (eine einzelne zusammenhängende Kurve, die aus Linienstücken und Kreisbögen zusammengesetzt sein kann, oder eine Menge derartiger Kurven).
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Line | definitions.MultiLine,
        Field(
            description="Linienförmiger Raumbezug (Einzelne zusammenhängende Kurve, die aus Linienstücken und Kreisbögen aufgebaut sit, oder eine Menge derartiger Kurven),",
            json_schema_extra={
                "typename": "XP_Liniengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]


class LPNutzungsAusschluss(LPGeometrieobjekt):
    """
    Flächen und Objekte die bestimmte geplante oder absehbare Nutzungsänderungen nicht erfahren sollen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    auszuschliessendeNutzungen: Annotated[
        str | None,
        Field(
            description="Auszuschließende Nutzungen (Textform).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    auszuschliessendeNutzungenKuerzel: Annotated[
        str | None,
        Field(
            description="Auszuschließende Nutzungen (Kürzel).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    begruendung: Annotated[
        str | None,
        Field(
            description="Begründung des Ausschlusses (Textform).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    begruendungKuerzel: Annotated[
        str | None,
        Field(
            description="Begründung des Ausschlusses (Kürzel)",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPNutzungserfordernisRegelung(LPGeometrieobjekt):
    """
    Flächen mit Nutzungserfordernissen und Nutzungsregelungen zum Schutz, zur Pflege und zur Entwicklung von Natur und Landschaft.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der Nutzungserfordernis oder Regelung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    regelung: Annotated[
        Literal["1000", "9999"] | None,
        Field(
            description="Nutzungsregelung (Klassifikation).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Gruenlandumbruchverbot",
                        "description": "Grünland-Umbruchverbot",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstige Regelung"},
                },
                "typename": "LP_Regelungen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    erfordernisRegelung: Annotated[
        str | None,
        Field(
            description="Nutzungserfordernis oder -Regelung (Textform).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    erfordernisRegelungKuerzel: Annotated[
        str | None,
        Field(
            description="Nutzungserfordernis oder -Regelung (Kürzel).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPPlanerischeVertiefung(LPGeometrieobjekt):
    """
    Bereiche, die einer planerischen Vertiefung bedürfen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    vertiefung: Annotated[
        str | None,
        Field(
            description="Textliche Formulierung der Vertiefung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPSchutzPflegeEntwicklung(LPGeometrieobjekt):
    """
    Sonstige Flächen und Maßnahmen zum Schutz, zur Pflege und zur Entwicklung von Natur und Landschaft, soweit sie nicht durch die Klasse LP_NutzungserfordernisRegelung modelliert werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der Maßnahme",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahme: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "1300",
            "1400",
            "1500",
            "1600",
            "1700",
            "1800",
            "1900",
            "2000",
            "2100",
            "2200",
            "2300",
            "9999",
        ]
        | None,
        Field(
            description="Durchzuführende Maßnahme (Klassifikation).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "ArtentreicherGehoelzbestand",
                        "description": "Artenreicher Gehölzbestand ist aus unterschiedlichen, standortgerechten Gehölzarten aufgebaut und weist einen Strauchanteil auf.",
                    },
                    "1100": {
                        "name": "NaturnaherWald",
                        "description": "Naturnahe Wälder zeichnen sich durch eine standortgemäße Gehölzzusammensetzung unterschiedlicher Altersstufen, durch eine Schichtung der Gehölze (z.B. Strauchschicht, sich überlagernder erster Baumschicht in 10-15 m Höhe und zweiter Baumschicht in 20-25 m Höhe) sowie durch eine in der Regeln artenreiche Krautschicht aus. Kennzeichnend sind zudem das gleichzeitige Nebeneinander von aufwachsenden Gehölzen, Altbäumen und Lichtungen in kleinräumigen Wechsel sowie ein gewisser Totholzanteil.",
                    },
                    "1200": {
                        "name": "ExtensivesGruenland",
                        "description": "Gegenüber einer intensiven Nutzung sind bei extensiver Grünlandnutzung sowohl Beweidungsintensitäten als auch der Düngereinsatz deutlich geringer. Als Folge finden eine Reihe von eher konkurrenzschwachen, oft auch trittempflindlichen Pflanzenarten Möglichkeiten, sich neben den in der Regel sehr robusten, wuchskräftigen, jedoch sehr nährstoffbedürftigen Pflanzen intensiver Wirtschaftsflächen zu behaupten.  Dadurch kommt es zur Ausprägung von standortbedingt unterschiedlichen Grünlandgesellschaften mit deutlichen höheren Artenzahlen (größere Vielfalt).",
                    },
                    "1300": {
                        "name": "Feuchtgruenland",
                        "description": "Artenreiches Feuchtgrünland entwickelt sich bei extensiver Bewirtschaftung auf feuchten bis wechselnassen Standorten. Die geringe Tragfähigkeit des vielfach anstehenden Niedermoorbodens erschwert den Einsatz von Maschinen, so dass die Flächen vorwiegend beweidet bzw. erst spät im Jahr gemäht werden.",
                    },
                    "1400": {
                        "name": "Obstwiese",
                        "description": "Obstwiesen umfassen mittel- oder hochstämmige, großkronige Obstbäume auf beweidetem (Obstweide) oder gemähtem (obstwiese) Grünland. Im Optimalfall setzt sich der aufgelockerte Baumbestand aus verschiedenen, möglichst alten, regional-typischen Kultursorten zusammen.",
                    },
                    "1500": {
                        "name": "NaturnaherUferbereich",
                        "description": "Naturahne Uferbereiche umfassen unterschiedlich zusammengesetzte Röhrichte und Hochstaudenrieder oder Seggen-Gesellschaften sowie Ufergehölze, die sich vorwiegend aus strauch- oder baumförmigen Weiden, Erlen oder Eschen zusammensetzen.",
                    },
                    "1600": {
                        "name": "Roehrichtzone",
                        "description": "Im flachen Wasser oder auf nassen Böden bilden sich hochwüchsige, oft artenarme Bestände aus überwiegend windblütigen Röhrichtarten aus. Naturliche Bestände finden sich im Uferbereich von Still- und Fließgewässern.",
                    },
                    "1700": {
                        "name": "Ackerrandstreifen",
                        "description": "Ackerrandstreifen sind breite Streifen im Randbereich eines konventionell oder ökologisch genutzten Ackerschlages.",
                    },
                    "1800": {
                        "name": "Ackerbrache",
                        "description": "Als Ackerbrachflächen werden solche Biotope angesprochen, die seit kurzer Zeit aus der Nutzung herausgenommen worden sind. Sie entstehen, indem Ackerflächen mindestens eine Vegetationsperiode nicht mehr bewirtschaftet werden.",
                    },
                    "1900": {
                        "name": "Gruenlandbrache",
                        "description": "Als Grünlandbrachen werden solche Biotope angesprochen, die seit kurzer Zeit aus der Nutzung herausgenommen worden sind. Sie entstehen, indem Grünland mindestens eine Vegetationsperiode nicht mehr bewirtschaftet wird.",
                    },
                    "2000": {
                        "name": "Sukzessionsflaeche",
                        "description": "Sukzessionsflächen umfassen dauerhaft ungenutzte, der natürlichen Entwicklung überlassene Vegetationsbestände auf trockenen bis feuchten Standorten.",
                    },
                    "2100": {
                        "name": "Hochstaudenflur",
                        "description": "Hochwüchsige, zumeist artenreiche Staudenfluren feuchter bis nasser Standorte entwickeln sich in der Regel auf Feuchtgrünland-Brachen, an gehölzfreien Uferstreifen oder an anderen zeitweilig gestörten Standorten mit hohen Grundwasserständen.",
                    },
                    "2200": {
                        "name": "Trockenrasen",
                        "description": "Trockenrasen sind durch zumindest zeitweilige extreme Trockenheit (Regelwasser versickert rasch) sowie durch Nährstoffarmut charakterisiert, die nur Arten mit speziell angepassten Lebensstrategien Entwicklungsmöglichkeiten bieten.",
                    },
                    "2300": {
                        "name": "Heide",
                        "description": "Heiden sind Zwergstrauchgesellschaften auf nährstoffarmen, sauren, trockenen (Calluna-Heide) oder feuchten (Erica-Heide) Standorten. Im Binnenland haben sie in der Regel nach Entwaldung (Abholzung) und langer Übernutzung (Beweidung) primär nährstoffarmer Standorte entwickelt.",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
                "typename": "XP_SPEMassnahmenTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahmeText: Annotated[
        str | None,
        Field(
            description="Durchzuführende Maßnahme (Textform).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahmeKuerzel: Annotated[
        str | None,
        Field(
            description="Kürzel der durchzuführenden Maßnahme.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    istAusgleich: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob die Maßnahme zum Ausgleich von Eingriffen genutzt wird.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False


class LPSchutzobjektInternatRecht(LPGeometrieobjekt):
    """
    Sonstige Schutzgebiete und Schutzobjekte nach internationalem Recht.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "9999"] | None,
        Field(
            description="Typ der Schutzgebietes.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Feuchtgebiet", "description": "Feuchtgebiet"},
                    "2000": {
                        "name": "VogelschutzgebietInternat",
                        "description": "Internationales Vogelschutzgebiet",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges internationales Schutzobjekt",
                    },
                },
                "typename": "LP_InternatSchutzobjektTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter zusätzlicher Typ des Schutzobjektes, wenn typ == 9999 ist.",
            json_schema_extra={
                "typename": "LP_InternatSchutzobjektDetailTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    eigenname: Annotated[
        str | None,
        Field(
            description="Eigennahme des Schutzgebietes.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPSchutzobjektLandesrecht(LPGeometrieobjekt):
    """
    Sonstige Schutzgebiete und Schutzobjekte nach Landesrecht.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    detailTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter Typ des Schutzobjektes.",
            json_schema_extra={
                "typename": "LP_SchutzobjektLandesrechtDetailTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPSonstigesRecht(LPGeometrieobjekt):
    """
    Gebiete und Gebietsteile mit rechtlichen Bindungen nach anderen Fachgesetzen (soweit sie für den Schutz, die Pflege und die Entwicklung von Natur und Landschaft bedeutsam sind). Hier: Sonstige Flächen und Gebiete (z.B. nach Jagdrecht).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "9999"] | None,
        Field(
            description="Typ des Schutzobjektes.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Jagdgesetz", "description": "Jagdgesetz"},
                    "2000": {
                        "name": "Fischereigesetz",
                        "description": "Fischereigesetz",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Recht"},
                },
                "typename": "LP_SonstRechtTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter detaillierterer Typ des Schutzobjektes.",
            json_schema_extra={
                "typename": "LP_SonstRechtDetailTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPTextlicheFestsetzungsFlaeche(LPFlaechenobjekt):
    """
    Bereich, in dem bestimmte textliche Festsetzungen gültig sind, die über die Relation "refTextInhalt" (Basisklasse LP_Objekt) spezifiziert werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class LPWasserrechtGemeingebrEinschraenkungNaturschutz(LPGeometrieobjekt):
    """
    Gebiete und Gebietsteile mit rechtlichen Bindungen nach anderen Fachgesetzen (soweit sie für den Schutz, die Pflege und die Entwicklung von Natur und Landschaft bedeutsam sind). Hier: Flächen mit Einschränkungen des wasserrechtlichen Gemeingebrauchs aus Gründen des Naturschutzes.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    detailTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter Typ des Schutzobjektes.",
            json_schema_extra={
                "typename": "LP_WasserrechtGemeingebrEinschraenkungNaturschutzDetailTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPWasserrechtSchutzgebiet(LPGeometrieobjekt):
    """
    Wasserrechtliches Schutzgebiet
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000", "9999"] | None,
        Field(
            description="Typ des Schutzobjektes.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "GrundQuellwasser",
                        "description": "Grund- oder Quellwasser",
                    },
                    "2000": {
                        "name": "Oberflaechengewaesser",
                        "description": "Oberflächenwasser",
                    },
                    "3000": {"name": "Heilquellen", "description": "Heilquelle"},
                    "9999": {"name": "Sonstiges", "description": "Sonstiger Typ"},
                },
                "typename": "LP_WasserrechtSchutzgebietTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter detaillierterer Typ des Schutzobjektes.",
            json_schema_extra={
                "typename": "LP_WasserrechtSchutzgebietDetailTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    eigenname: Annotated[
        str | None,
        Field(
            description="Eigenname des Schutzgebietes.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPWasserrechtSonstige(LPGeometrieobjekt):
    """
    Gebiete und Gebietsteile mit rechtlichen Bindungen nach anderen Fachgesetzen (soweit sie für den Schutz, die Pflege und die Entwicklung von Natur und Landschaft bedeutsam sind). Hier: Sonstige wasserrechtliche Flächen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter Typ des Schutzobjektes.",
            json_schema_extra={
                "typename": "LP_WasserrechtSonstigeTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPWasserrechtWirtschaftAbflussHochwSchutz(LPGeometrieobjekt):
    """
    Gebiete und Gebietsteile mit rechtlichen Bindungen nach anderen Fachgesetzen (soweit sie für den Schutz, die Pflege und die Entwicklung von Natur und Landschaft bedeutsam sind). Hier: Flächen für die Wasserwirtschaft, den Hochwasserschutz und die Regelung des Wasserabflusses nach dem Wasserhaushaltsgesetz.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "9999"] | None,
        Field(
            description="Typ des Schutzobjektes.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Hochwasserrueckhaltebecken",
                        "description": "Hochwasser-Rückhaltebecken",
                    },
                    "2000": {
                        "name": "UeberschwemmGebiet",
                        "description": "Überschwemmungsgebiet",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiger Typ."},
                },
                "typename": "LP_WasserrechtWirtschaftAbflussHochwSchutzTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter detaillierterer Typ des Schutzobjektes.",
            json_schema_extra={
                "typename": "LP_WasserrechtWirtschaftAbflussHochwSchutzDetailTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPZuBegruenendeGrundstueckflaeche(LPFlaechenobjekt):
    """
    Zu begrünende Grundstücksfläche
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    gruenflaechenFaktor: Annotated[
        float | None,
        Field(
            description="Angabe des Verhältnisses zwischen einem Flächenanteil Grün und einer bebauten Fläche (auch als Biotopflächenfaktor bekannt)",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gaertnerischanzulegen: Annotated[
        bool | None,
        Field(
            description="Angabe in wie weit ein Grünfläche gärtnerisch anzulegen ist.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPZwischennutzung(LPGeometrieobjekt):
    """
    Flächen und Maßnahmen mit zeitlich befristeten Bindungen zum Schutz, zur Pflege und zur Entwicklung von Natur und Landschaft ("Zwischennutzungsvorgaben").
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der Maßnahme.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bindung: Annotated[
        str | None,
        Field(
            description="Beschreibung der Bindung (Textform).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bindungKuerzel: Annotated[
        str | None,
        Field(
            description="Beschreibung der Bindung (Kürzel).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPGeometrieobjekt(RPObjekt):
    """
    Basisklasse für alle Objekte eines Raumordnungsplans mit variablem Raumbezug. Ein konkretes Objekt muss entweder punktförmigen, linienförmigen oder flächenhaften Raumbezug haben, gemischte Geometrie ist nicht zugelassen. RP_Geometrieobjekt selbst ist abstrakt.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point
        | definitions.MultiPoint
        | definitions.Line
        | definitions.MultiLine
        | definitions.Polygon
        | definitions.MultiPolygon,
        Field(
            description="Variabler Raumbezug.",
            json_schema_extra={
                "typename": "XP_VariableGeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    flaechenschluss: Annotated[
        bool | None,
        Field(
            description="Zeigt an, ob für das Objekt Flächenschluss vorliegt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    flussrichtung: Annotated[
        bool | None,
        Field(
            description="Das Attribut ist nur relevant, wenn ein Geometrieobjekt einen linienhaften Raumbezug hat. Ist es mit dem Wert true belegt, wird damit ausgedrückt, dass der Linie eine Flussrichtung  in Digitalisierungsrichtung zugeordnet ist. In diesem Fall darf bei Im- und Export die Digitalisierungsreihenfolge der Stützpunkte nicht geändert werden. Wie eine definierte Flussrichtung  zu interpretieren oder bei einer Plandarstellung zu visualisieren ist, bleibt der Implementierung überlassen.\r\nIst der Attributwert false oder das Attribut nicht belegt, ist die Digitalisierungsreihenfolge der Stützpunkte irrelevant.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nordwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Orientierung des Objektes bei punktförmigem Raumbezug als Winkel gegen die Nordrichtung. Zählweise im geographischen Sinn (von Nord über Ost nach Süd und West).",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class RPGrenze(RPGeometrieobjekt):
    """
    Grenzen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "1250",
                "1300",
                "1400",
                "1450",
                "1500",
                "1510",
                "1550",
                "1600",
                "2000",
                "2100",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Typ der Grenze",
            json_schema_extra={
                "typename": "XP_GrenzeTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Bundesgrenze", "description": "Bundesgrenze"},
                    "1100": {
                        "name": "Landesgrenze",
                        "description": "Grenze eines Bundeslandes",
                    },
                    "1200": {
                        "name": "Regierungsbezirksgrenze",
                        "description": "Grenze eines Regierungsbezirks",
                    },
                    "1250": {
                        "name": "Bezirksgrenze",
                        "description": "Grenze eines Bezirks.",
                    },
                    "1300": {
                        "name": "Kreisgrenze",
                        "description": "Grenze eines Kreises.",
                    },
                    "1400": {
                        "name": "Gemeindegrenze",
                        "description": "Grenze einer Gemeinde.",
                    },
                    "1450": {
                        "name": "Verbandsgemeindegrenze",
                        "description": "Grenze einer Verbandsgemeinde",
                    },
                    "1500": {
                        "name": "Samtgemeindegrenze",
                        "description": "Grenze einer Samtgemeinde",
                    },
                    "1510": {
                        "name": "Mitgliedsgemeindegrenze",
                        "description": "Mitgliedsgemeindegrenze",
                    },
                    "1550": {"name": "Amtsgrenze", "description": "Amtsgrenze"},
                    "1600": {
                        "name": "Stadtteilgrenze",
                        "description": "Stadtteilgrenze",
                    },
                    "2000": {
                        "name": "VorgeschlageneGrundstuecksgrenze",
                        "description": "Hinweis auf eine vorgeschlagene Grundstücksgrenze im BPlan.",
                    },
                    "2100": {
                        "name": "GrenzeBestehenderBebauungsplan",
                        "description": "Hinweis auf den Geltungsbereich eines bestehenden BPlan.",
                    },
                    "9999": {"name": "SonstGrenze", "description": "Sonstige Grenze"},
                },
            },
        ),
    ] = None
    spezifischerTyp: Annotated[
        Literal["1000", "1001", "2000", "3000", "4000", "5000", "6000", "7000", "8000"]
        | None,
        Field(
            description="Spezifischer Typ der Grenze",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Zwoelfmeilenzone",
                        "description": "Grenze der Zwölf-Seemeilen-Zone, in der Küstenstaaten das Recht haben, ihre Hoheitsgewässer auf bis zu 12 Seemeilen auszudehnen (nach Seerechtsübereinkommen der UN vom 10. Dezember 1982).",
                    },
                    "1001": {
                        "name": "BegrenzungDesKuestenmeeres",
                        "description": "Begrenzung des Küstenmeeres.",
                    },
                    "2000": {
                        "name": "VerlaufUmstritten",
                        "description": "Grenze mit umstrittenem Verlauf, beispielsweise zwischen Deutschland und den Niederlanden im Ems-Ästuar.",
                    },
                    "3000": {
                        "name": "GrenzeDtAusschlWirtschaftszone",
                        "description": "Grenze der Deutschen Ausschließlichen Wirtschaftszone (AWZ).",
                    },
                    "4000": {
                        "name": "MittlereTideHochwasserlinie",
                        "description": "Maß von Küstenlinien bei langjährig gemitteltem Küstenhochwasser.",
                    },
                    "5000": {
                        "name": "PlanungsregionsgrenzeRegion",
                        "description": "Grenze einer regionalen Planungsregion (z.B. Grenze eines Regionalplans).",
                    },
                    "6000": {
                        "name": "PlanungsregionsgrenzeLand",
                        "description": "Grenze einer landesweiten Planungsregion (z.B. Grenze eines Landesentwicklungsplans).",
                    },
                    "7000": {
                        "name": "GrenzeBraunkohlenplan",
                        "description": "Grenze eines Braunkohlenplans.",
                    },
                    "8000": {
                        "name": "Grenzuebergangsstelle",
                        "description": "Grenzübergangsstelle",
                    },
                },
                "typename": "RP_SpezifischeGrenzeTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Erweiterter Typ.",
            json_schema_extra={
                "typename": "RP_SonstGrenzeTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPKommunikation(RPGeometrieobjekt):
    """
    Infrastruktur zur Telekommunikation, digitale Infrastruktur oder Kommunikationsinfrastruktur.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "2001", "2002", "9999"] | None,
        Field(
            description="Klassifikation von Kommunikations-Infrastruktur.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Richtfunkstrecke",
                        "description": "Richtfunkstrecke.",
                    },
                    "2000": {
                        "name": "Fernmeldeanlage",
                        "description": "Fernmeldeanlage.",
                    },
                    "2001": {
                        "name": "SendeEmpfangsstation",
                        "description": "Sende- und/oder Empfangsstation.",
                    },
                    "2002": {
                        "name": "TonFernsehsender",
                        "description": "Ton- und/oder Fernsehsender.",
                    },
                    "9999": {
                        "name": "SonstigeKommunikation",
                        "description": "Sonstige Kommunikationstypen.",
                    },
                },
                "typename": "RP_KommunikationTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPLaermschutzBauschutz(RPGeometrieobjekt):
    """
    Infrastruktur zum Lärmschutz und/oder Bauschutz.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "1001", "2000", "3000", "4000", "5000", "9999"] | None,
        Field(
            description="Klassifikation von Lärmschutztypen.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Laermbereich", "description": "Lärmbereich."},
                    "1001": {
                        "name": "Laermschutzbereich",
                        "description": "Lärmschutzbereich",
                    },
                    "2000": {
                        "name": "Siedlungsbeschraenkungsbereich",
                        "description": "Siedlungsbeschränkungsbereich.",
                    },
                    "3000": {"name": "ZoneA", "description": "Zone A."},
                    "4000": {"name": "ZoneB", "description": "Zone B."},
                    "5000": {"name": "ZoneC", "description": "Zone C."},
                    "9999": {
                        "name": "SonstigerLaermschutzBauschutz",
                        "description": "Sonstiger Lärmschutz oder Bauschutz.",
                    },
                },
                "typename": "RP_LaermschutzTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPPlanungsraum(RPGeometrieobjekt):
    """
    Modelliert einen allgemeinen Planungsraum.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    planungsraumBeschreibung: Annotated[
        str | None,
        Field(
            description="Textliche Beschreibung eines Planungsrauminhalts.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPRaumkategorie(RPGeometrieobjekt):
    """
    Raumkategorien sind nach bestimmten Kriterien abgegrenze Gebiete, in denen vergleichbare Strukturen bestehen und in denen die Raumordnung gleichartige Ziele verfolgt. Kriterien können z.B. siedlungsstrukturell, qualitativ oder potentialorientiert sein.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    besondererTyp: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Klassifikation verschiedener besonderer Raumkategorien.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Grenzgebiet", "description": "Grenzgebiete."},
                    "2000": {
                        "name": "Bergbaufolgelandschaft",
                        "description": "Bergbaufolgelandschaft.",
                    },
                    "3000": {
                        "name": "Braunkohlenfolgelandschaft",
                        "description": "Braunkohlenfolgelandschaften.",
                    },
                },
                "typename": "RP_BesondereRaumkategorieTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1100",
                "1101",
                "1102",
                "1103",
                "1104",
                "1105",
                "1106",
                "1200",
                "1201",
                "1202",
                "1203",
                "1300",
                "1301",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "1900",
                "2000",
                "2100",
                "2200",
                "2300",
                "2400",
                "2500",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation verschiedener Raumkategorien.",
            json_schema_extra={
                "typename": "RP_RaumkategorieTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Ordnungsraum",
                        "description": "Ordnungsraum. Von der Ministerkonferenz für Raumordnung nach einheitlichen Abgrenzungskritierien definierter Strukturraum. Besteht aus Verdichtungsraum und der Randzone des Verdichtungsraums.",
                    },
                    "1001": {
                        "name": "OrdnungsraumTourismusErholung",
                        "description": "Ordnungsraum in Bezug auf Tourismus und Erholung.",
                    },
                    "1100": {
                        "name": "Verdichtungsraum",
                        "description": "Verdichtungsraum mit höherer Dichte an Siedlungen und Infrastruktur.",
                    },
                    "1101": {
                        "name": "KernzoneVerdichtungsraum",
                        "description": "Kernzone des Verdichtungsraum.",
                    },
                    "1102": {
                        "name": "RandzoneVerdichtungsraum",
                        "description": "Randzone des Verdichtungsraums.",
                    },
                    "1103": {
                        "name": "Ballungskernzone",
                        "description": "Ballungskernzone.",
                    },
                    "1104": {
                        "name": "Ballungsrandzone",
                        "description": "Ballungsrandzone.",
                    },
                    "1105": {
                        "name": "HochverdichteterRaum",
                        "description": "Hochverdichteter Raum",
                    },
                    "1106": {
                        "name": "StadtUmlandBereichVerdichtungsraum",
                        "description": "Stadt-Umland-Bereich im Verdichtungsraum",
                    },
                    "1200": {
                        "name": "LaendlicherRaum",
                        "description": "Ländlicher Raum.",
                    },
                    "1201": {
                        "name": "VerdichteterBereichimLaendlichenRaum",
                        "description": "Verdichteter Bereich im ländlichen Raum.",
                    },
                    "1202": {
                        "name": "Gestaltungsraum",
                        "description": "Gestaltungsraum.",
                    },
                    "1203": {
                        "name": "LaendlicherGestaltungsraum",
                        "description": "Ländlicher Gestaltungsraum.",
                    },
                    "1300": {
                        "name": "StadtUmlandRaum",
                        "description": "Stadt-Umland-Raum",
                    },
                    "1301": {
                        "name": "StadtUmlandBereichLaendlicherRaum",
                        "description": "Stadt-Umland-Bereich im ländlichen Raum.",
                    },
                    "1400": {
                        "name": "AbgrenzungOrdnungsraum",
                        "description": "Abgrenzung eines Ordnungsraums.",
                    },
                    "1500": {
                        "name": "DuennbesiedeltesAbgelegenesGebiet",
                        "description": "Dünnbesiedeltes, abgelegenes Gebiet.",
                    },
                    "1600": {
                        "name": "Umkreis10KM",
                        "description": "Umkreis von zehn Kilometern.",
                    },
                    "1700": {
                        "name": "RaummitbesonderemHandlungsbedarf",
                        "description": "Raum mit besonderem Handlungsbedarf, zum Beispiel vor dem Hintergrund des demographischen Wandels.",
                    },
                    "1800": {"name": "Funktionsraum", "description": "Funktionsraum."},
                    "1900": {
                        "name": "GrenzeWirtschaftsraum",
                        "description": "Grenze eines Wirtschaftsraums.",
                    },
                    "2000": {
                        "name": "Funktionsschwerpunkt",
                        "description": "Funktionsschwerpunkt.",
                    },
                    "2100": {
                        "name": "Grundversorgung",
                        "description": "Grundversorgung-Raumkategorie",
                    },
                    "2200": {
                        "name": "Alpengebiet",
                        "description": "Alpengebiet-Raumkategorie.",
                    },
                    "2300": {
                        "name": "RaeumeMitGuenstigenEntwicklungsvoraussetzungen",
                        "description": "Räume mit günstigen Entwicklungsaufgaben.",
                    },
                    "2400": {
                        "name": "RaeumeMitAusgeglichenenEntwicklungspotenzialen",
                        "description": "Raeume mit ausgeglichenen Entwicklungsvoraussetzungen.",
                    },
                    "2500": {
                        "name": "RaeumeMitBesonderenEntwicklungsaufgaben",
                        "description": "Räume mit besonderen Entwicklungspotentialen.",
                    },
                    "9999": {
                        "name": "SonstigeRaumkategorie",
                        "description": "Sonstige Raumkategorien",
                    },
                },
            },
        ),
    ] = None


class RPSiedlung(RPGeometrieobjekt):
    """
    Allgemeines Siedlungsobjekt. Dieses vererbt an mehrere Spezialisierungen, ist aber selbst nicht abstrakt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    bauhoehenbeschraenkung: Annotated[
        int | None,
        Field(
            description="Assoziierte Bauhöhenbeschränkung.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    istSiedlungsbeschraenkung: Annotated[
        bool | None,
        Field(
            description="Abfrage, ob der FeatureType eine Siedlungsbeschränkung ist.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False


class RPSonstigeInfrastruktur(RPGeometrieobjekt):
    """
    Sonstige Infrastruktur.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class RPSonstigerSiedlungsbereich(RPSiedlung):
    """
    Sonstiger Siedlungsbereich.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class RPSozialeInfrastruktur(RPGeometrieobjekt):
    """
    Soziale Infrastruktur ist ein (unpräziser) Sammelbegriff für Einrichtungen, Leistungen und Dienste in den Kommunen, distinkt von Verkehr, Energieversorgung und Entsorgung. Sie umfasst u.a. Bildung, Gesundheit, Sozialeinrichtungen, Kultureinrichtungen und Einrichtungen der öffentlichen Verwaltung.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[Literal["1000", "2000", "3000", "3001", "4000", "4001", "5000", "9999"]]
        | None,
        Field(
            description="Klassifikation von Sozialer Infrastruktur.",
            json_schema_extra={
                "typename": "RP_SozialeInfrastrukturTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Kultur",
                        "description": "Kulturbezogene Infrastruktur.",
                    },
                    "2000": {
                        "name": "Sozialeinrichtung",
                        "description": "Sozialeinrichtung.",
                    },
                    "3000": {
                        "name": "Gesundheit",
                        "description": "Gesundheitsinfrastruktur.",
                    },
                    "3001": {"name": "Krankenhaus", "description": "Krankenhaus."},
                    "4000": {
                        "name": "BildungForschung",
                        "description": "Bildungs- und/oder Forschungsinfrastruktur.",
                    },
                    "4001": {"name": "Hochschule", "description": "Hochschule."},
                    "5000": {
                        "name": "Polizei",
                        "description": "Polizeiliche Infrastruktur",
                    },
                    "9999": {
                        "name": "SonstigeSozialeInfrastruktur",
                        "description": "Sonstige Soziale Infrastruktur.",
                    },
                },
            },
        ),
    ] = None


class RPSperrgebiet(RPGeometrieobjekt):
    """
    Sperrgebiet, Gelände oder Areal, das für die Zivilbevölkerung überhaupt nicht oder zeitweise nicht zugänglich ist.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000", "4000", "4001", "5000", "6000", "9999"] | None,
        Field(
            description="Klassifikation verschiedener Sperrgebiettypen.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Verteidigung", "description": "Verteidigung."},
                    "2000": {
                        "name": "SondergebietBund",
                        "description": "Sondergebiet Bund.",
                    },
                    "3000": {"name": "Warngebiet", "description": "Warngebiet."},
                    "4000": {
                        "name": "MilitaerischeEinrichtung",
                        "description": "Militärische Einrichtung.",
                    },
                    "4001": {
                        "name": "GrosseMilitaerischeAnlage",
                        "description": "Große militärische Anlage.",
                    },
                    "5000": {
                        "name": "MilitaerischeLiegenschaft",
                        "description": "Militärische Liegenschaft.",
                    },
                    "6000": {
                        "name": "Konversionsflaeche",
                        "description": "Konversionsfläche.",
                    },
                    "9999": {
                        "name": "SonstigesSperrgebiet",
                        "description": "Sonstige Sperrgebiete.",
                    },
                },
                "typename": "RP_SperrgebietTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPVerkehr(RPGeometrieobjekt):
    """
    Enthält allgemeine Verkehrs-Infrastruktur, die auch multiple Typen (etwa Straße und Schiene) beinhalten kann. Die Klasse selbst vererbt an spezialisierte Verkehrsarten, ist aber nicht abstrakt (d.h. sie kann selbst auch verwendet werden).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    allgemeinerTyp: Annotated[
        list[Literal["1000", "2000", "3000", "4000", "9999"]] | None,
        Field(
            description="Allgemeine Klassifikation der Verkehrs-Arten.",
            json_schema_extra={
                "typename": "RP_VerkehrTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Schienenverkehr",
                        "description": "Schienenverkehr.",
                    },
                    "2000": {
                        "name": "Strassenverkehr",
                        "description": "Straßenverkehr.",
                    },
                    "3000": {"name": "Luftverkehr", "description": "Luftverkehr."},
                    "4000": {"name": "Wasserverkehr", "description": "Wasserverkehr."},
                    "9999": {
                        "name": "SonstigerVerkehr",
                        "description": "Sonstiger Verkehr.",
                    },
                },
            },
        ),
    ] = None
    status: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "2000",
                "3000",
                "4000",
                "5000",
                "6000",
                "7000",
                "8000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Verkehrsstati.",
            json_schema_extra={
                "typename": "RP_VerkehrStatus",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Ausbau", "description": "Ausbau."},
                    "1001": {
                        "name": "LinienfuehrungOffen",
                        "description": "Linienführung offen.",
                    },
                    "2000": {"name": "Sicherung", "description": "Sicherung."},
                    "3000": {"name": "Neubau", "description": "Neubau."},
                    "4000": {
                        "name": "ImBau",
                        "description": "Im Bau befindliche Verkehrsinfrastruktur.",
                    },
                    "5000": {
                        "name": "VorhPlanfestgestLinienbestGrobtrasse",
                        "description": "Vorhandene planfestgestellte linienbestimmte Grobtrasse.",
                    },
                    "6000": {
                        "name": "BedarfsplanmassnahmeOhneRaeumlFestlegung",
                        "description": "Bedarfsplanmassnahme ohne räumliche Festlegung.",
                    },
                    "7000": {"name": "Korridor", "description": "Korridor."},
                    "8000": {"name": "Verlegung", "description": "Verlegung."},
                    "9999": {
                        "name": "SonstigerVerkehrStatus",
                        "description": "Sonstiger Verkehrsstatus.",
                    },
                },
            },
        ),
    ] = None
    bezeichnung: Annotated[
        str | None,
        Field(
            description="Bezeichnung eines Verkehrstyps.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPWasserverkehr(RPVerkehr):
    """
    Wasserverkehr-Infrastruktur.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1002",
                "1003",
                "1004",
                "2000",
                "3000",
                "4000",
                "4001",
                "4002",
                "4003",
                "5000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Wasserverkehr-Infrastruktur.",
            json_schema_extra={
                "typename": "RP_WasserverkehrTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Hafen", "description": "Hafen."},
                    "1001": {"name": "Seehafen", "description": "Seehafen."},
                    "1002": {"name": "Binnenhafen", "description": "Binnenhafen."},
                    "1003": {
                        "name": "Sportboothafen",
                        "description": "Sportboothafen.",
                    },
                    "1004": {"name": "Laende", "description": "Lände."},
                    "2000": {"name": "Umschlagplatz", "description": "Umschlagplatz."},
                    "3000": {
                        "name": "SchleuseHebewerk",
                        "description": "Schleuse und/oder Hebewerk.",
                    },
                    "4000": {"name": "Schifffahrt", "description": "Schifffahrt."},
                    "4001": {
                        "name": "WichtigerSchifffahrtsweg",
                        "description": "Wichtiger Schifffahrtsweg.",
                    },
                    "4002": {
                        "name": "SonstigerSchifffahrtsweg",
                        "description": "Sonstiger Schifffahrtsweg.",
                    },
                    "4003": {"name": "Wasserstrasse", "description": "Wasserstraße."},
                    "5000": {"name": "Reede", "description": "Reede."},
                    "9999": {
                        "name": "SonstigerWasserverkehr",
                        "description": "Sonstiger Wasserverkehr.",
                    },
                },
            },
        ),
    ] = None


class RPWasserwirtschaft(RPGeometrieobjekt):
    """
    Wasserwirtschaft beinhaltet die zielbewusste Ordnung aller menschlichen Einwirkungen auf das ober- und unterirdische Wasser. Im Datenschema werden Gewässer, Wasserschutz, Hochwasserschutz und Wasserverkehr in gesonderten Klassen gehalten.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "3000",
                "4000",
                "5000",
                "6000",
                "7000",
                "8000",
                "8100",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Anlagen und Einrichtungen der Wasserwirtschaft",
            json_schema_extra={
                "typename": "RP_WasserwirtschaftTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Wasserleitung", "description": "Wasserleitung."},
                    "2000": {"name": "Wasserwerk", "description": "Wasserwerk."},
                    "3000": {
                        "name": "StaudammDeich",
                        "description": "Staudamm und/oder Deich.",
                    },
                    "4000": {
                        "name": "Speicherbecken",
                        "description": "Speicherbecken.",
                    },
                    "5000": {
                        "name": "Rueckhaltebecken",
                        "description": "Rückhaltebecken.",
                    },
                    "6000": {"name": "Talsperre", "description": "Talsperre."},
                    "7000": {
                        "name": "PumpwerkSchoepfwerk",
                        "description": "Pumpwerk und/oder Schöpfwerk.",
                    },
                    "8000": {
                        "name": "Zuwaesserungskanal",
                        "description": "Ein Entwässerungskanal, der gleichzeitig auch der Zuwässerung landwirtschaftlicher Flächen speziell zur Viehkehrung, als Viehtränke und zur Spülung des Systems dient.",
                    },
                    "8100": {
                        "name": "Entwaesserungskanal",
                        "description": "Künstlich angelegtes bzw. ausgebautes Netz von Wasserläufen (Tiefs), welche die Entwässerung des Binnenlandes über Sielbauwerke bzw. Schöpfbauwerke übernehmen, zum Teil auch mit der Funktion der Zwischenspeicherung des Niederschlagswassers.",
                    },
                    "9999": {
                        "name": "SonstigeWasserwirtschaft",
                        "description": "Sonstige Wasserwirtschaft.",
                    },
                },
            },
        ),
    ] = None


class RPWohnenSiedlung(RPSiedlung):
    """
    Wohn- und Siedlungsstruktur und -funktionen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "3000",
                "3001",
                "3002",
                "3003",
                "3004",
                "4000",
                "5000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Wohnen- und Siedlungstypen.",
            json_schema_extra={
                "typename": "RP_WohnenSiedlungTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Wohnen", "description": "Wohnen"},
                    "2000": {
                        "name": "Baugebietsgrenze",
                        "description": "Baugebietsgrenze.",
                    },
                    "3000": {
                        "name": "Siedlungsgebiet",
                        "description": "Siedlungsgebiet.",
                    },
                    "3001": {
                        "name": "Siedlungsschwerpunkt",
                        "description": "Siedlungsschwerpunkt.",
                    },
                    "3002": {
                        "name": "Siedlungsentwicklung",
                        "description": "Siedlungsentwicklung.",
                    },
                    "3003": {
                        "name": "Siedlungsbeschraenkung",
                        "description": "Siedlungsbeschränkung.",
                    },
                    "3004": {
                        "name": "Siedlungsnutzung",
                        "description": "Sonstige WohnenSiedlungstypen.",
                    },
                    "4000": {
                        "name": "SicherungEntwicklungWohnstaetten",
                        "description": "Sicherung der Entwicklung von Wohnstätten",
                    },
                    "5000": {
                        "name": "AllgemeinerSiedlungsbereichASB",
                        "description": "Allgemeiner Siedlungsbereich",
                    },
                    "9999": {
                        "name": "SonstigeWohnenSiedlung",
                        "description": "Sonstiges",
                    },
                },
            },
        ),
    ] = None


class RPZentralerOrt(RPGeometrieobjekt):
    """
    Zentrale Orte übernehmen die Versorgung ihrer Einwohner sowie Versorgungs und Entwicklungsfunktionen für den Einzugsbereich des Zentralen Ortes. Das zentralörtliche System ist hierarchisch gegliedert.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1500",
                "2000",
                "2500",
                "3000",
                "3001",
                "3500",
                "4000",
                "5000",
                "6000",
                "6001",
                "7000",
                "8000",
                "9000",
                "9999",
            ]
        ],
        Field(
            description="Klassifikation von Zentralen Orten.",
            json_schema_extra={
                "typename": "RP_ZentralerOrtTypen",
                "stereotype": "Enumeration",
                "multiplicity": "1..*",
                "enumDescription": {
                    "1000": {"name": "Oberzentrum", "description": "Oberzentrum."},
                    "1001": {
                        "name": "GemeinsamesOberzentrum",
                        "description": "Gemeinsames Oberzentrum.",
                    },
                    "1500": {"name": "Oberbereich", "description": "Oberbereich."},
                    "2000": {"name": "Mittelzentrum", "description": "Mittelzentrum."},
                    "2500": {"name": "Mittelbereich", "description": "Mittelbereich."},
                    "3000": {"name": "Grundzentrum", "description": "Grundzentrum"},
                    "3001": {"name": "Unterzentrum", "description": "Unterzentrum."},
                    "3500": {"name": "Nahbereich", "description": "Nahbereich."},
                    "4000": {"name": "Kleinzentrum", "description": "Kleinzentrum."},
                    "5000": {
                        "name": "LaendlicherZentralort",
                        "description": "Ländlicher Zentralort.",
                    },
                    "6000": {
                        "name": "Stadtrandkern1Ordnung",
                        "description": "Stadtrandkern 1. Ordnung",
                    },
                    "6001": {
                        "name": "Stadtrandkern2Ordnung",
                        "description": "Stadtrandkern 2. Ordnung",
                    },
                    "7000": {
                        "name": "VersorgungskernSiedlungskern",
                        "description": "Versorgungskern und/oder Siedlungskern",
                    },
                    "8000": {
                        "name": "ZentralesSiedlungsgebiet",
                        "description": "Zentrales Siedlungsgebiet.",
                    },
                    "9000": {"name": "Metropole", "description": "Metropole."},
                    "9999": {
                        "name": "SonstigerZentralerOrt",
                        "description": "Sonstiger Zentraler Ort.",
                    },
                },
            },
            min_length=1,
        ),
    ]
    sonstigerTyp: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1101",
                "1102",
                "1200",
                "1300",
                "1301",
                "1302",
                "1400",
                "1500",
                "1501",
                "1600",
                "1700",
                "1800",
                "1900",
                "2000",
                "2100",
                "2101",
                "2200",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Sonstige Klassifikation von Zentralen Orten.",
            json_schema_extra={
                "typename": "RP_ZentralerOrtSonstigeTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Doppelzentrum", "description": "Doppelzentrum."},
                    "1100": {
                        "name": "Funktionsteilig",
                        "description": "Funktionsteiliger Zentraler Ort.",
                    },
                    "1101": {
                        "name": "MitOberzentralerTeilfunktion",
                        "description": "Zentraler Ort mit oberzentraler Teilfunktion.",
                    },
                    "1102": {
                        "name": "MitMittelzentralerTeilfunktion",
                        "description": "Zentraler Ort mit mittelzentraler Teilfunktion.",
                    },
                    "1200": {
                        "name": "ImVerbund",
                        "description": "Zentraler Ort im Verbund.",
                    },
                    "1300": {
                        "name": "Kooperierend",
                        "description": "Kooperierender Zentraler Ort.",
                    },
                    "1301": {
                        "name": "KooperierendFreiwillig",
                        "description": "Freiwillig kooperierender Zentraler Ort.",
                    },
                    "1302": {
                        "name": "KooperierendVerpflichtend",
                        "description": "Verpflichtend kooperierender Zentraler Ort.",
                    },
                    "1400": {
                        "name": "ImVerdichtungsraum",
                        "description": "Zentraler Ort im Verdichtungsraum.",
                    },
                    "1500": {
                        "name": "SiedlungsGrundnetz",
                        "description": "Siedlungsgrundnetz.",
                    },
                    "1501": {
                        "name": "SiedlungsErgaenzungsnetz",
                        "description": "Siedlungsergänzungsnetz.",
                    },
                    "1600": {
                        "name": "Entwicklungsschwerpunkt",
                        "description": "Entwicklungsschwerpunkt.",
                    },
                    "1700": {
                        "name": "Ueberschneidungsbereich",
                        "description": "Überschneidungsbereich.",
                    },
                    "1800": {
                        "name": "Ergaenzungsfunktion",
                        "description": "Zentraler Ort mit Ergänzungsfunktion.",
                    },
                    "1900": {
                        "name": "Nachbar",
                        "description": "Zentraler Ort in Nachbarregionen oder Ländern.",
                    },
                    "2000": {
                        "name": "MoeglichesZentrum",
                        "description": 'Mögliches Zentrum, zum Beispiel "mögliches Mittelzentrum".',
                    },
                    "2100": {
                        "name": "FunktionsraumEindeutigeAusrichtung",
                        "description": "Funktionsraum, eindeutige Ausrichtung.",
                    },
                    "2101": {
                        "name": "FunktionsraumBilateraleAusrichtung",
                        "description": "Funktionsraum, bilaterale Ausrichtung.",
                    },
                    "2200": {
                        "name": "Kongruenzraum",
                        "description": "Der Kongruenzraum ist ein Bezugsraum zur Anwendung des \r\nKongruenzgebots. Der Kongruenzraum beschreibt den Raum im Umfeld eines Zentralen Ortes, den Einzelhandelsgroßprojekte, die im Zentralen Ort angesiedelt werden sollen oder bereits bestehen, im Wesentlichen versorgen sollen.",
                    },
                    "9999": {
                        "name": "SonstigeSonstigerZentralerOrt",
                        "description": "Sonstiger Sonstiger Zentraler Ort.",
                    },
                },
            },
        ),
    ] = None


class SOFlaechenobjekt(SOObjekt):
    """
    Basisklasse für alle Objekte mit flächenhaftem Raumbezug (eine Einzelfläche oder eine Menge von Flächen, die sich nicht überlappen dürfen).
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Polygon | definitions.MultiPolygon,
        Field(
            description="Flächenhafter Raumbezug des Objektes (Eine Einzelfläche oder eine Menge von Flächen, die sich nicht überlappen dürfen).",
            json_schema_extra={
                "typename": "XP_Flaechengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    flaechenschluss: Annotated[
        bool,
        Field(
            description="Zeigt an, ob das Objekt als Flächenschlussobjekt oder Überlagerungsobjekt gebildet werden soll. Flächenschlussobjekte dürfen sich nicht überlappen, sondern nur an den Flächenrändern berühren, wobei die jeweiligen Stützpunkte der Randkurven übereinander liegen müssen. Die Vereinigung der Flächenschlussobjekte überdeckt den Geltungsbereich des sonstigen raumbezogenen Plans vollständig.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "1",
            },
        ),
    ]


class SOGebiet(SOFlaechenobjekt):
    """
    Umgrenzung eines sonstigen Gebietes nach BauGB
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    gemeinde: Annotated[
        XPGemeinde | None,
        Field(
            description="Zuständige Gemeinde",
            json_schema_extra={
                "typename": "XP_Gemeinde",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gebietsArt: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "1300",
            "1400",
            "1500",
            "1600",
            "1999",
            "2000",
            "2100",
            "2200",
            "2300",
            "2400",
            "2500",
            "9999",
        ]
        | None,
        Field(
            description="Klassifikation des Gebietes nach BauGB.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Umlegungsgebiet",
                        "description": "Umlegungsgebiet (§ 45 ff BauGB).",
                    },
                    "1100": {
                        "name": "StaedtebaulicheSanierung",
                        "description": "Gebiet nach § 136 ff BauGB",
                    },
                    "1200": {
                        "name": "StaedtebaulicheEntwicklungsmassnahme",
                        "description": "Gebiet nach § 165 ff BauGB",
                    },
                    "1300": {
                        "name": "Stadtumbaugebiet",
                        "description": "Gebiet nach § 171 a-d BauGB",
                    },
                    "1400": {
                        "name": "SozialeStadt",
                        "description": "Gebiet nach § 171 e BauGB",
                    },
                    "1500": {
                        "name": "BusinessImprovementDistrict",
                        "description": "Gebiet nach §171 f BauGB",
                    },
                    "1600": {
                        "name": "HousingImprovementDistrict",
                        "description": "Gebiet nach §171 f BauGB",
                    },
                    "1999": {
                        "name": "Erhaltungsverordnung",
                        "description": "Allgemeine Erhaltungsverordnung",
                    },
                    "2000": {
                        "name": "ErhaltungsverordnungStaedtebaulicheGestalt",
                        "description": "Gebiet einer Satzung nach § 172 Abs. 1.1 BauGB",
                    },
                    "2100": {
                        "name": "ErhaltungsverordnungWohnbevoelkerung",
                        "description": "Gebiet einer Satzung nach § 172 Abs. 1.2 BauGB",
                    },
                    "2200": {
                        "name": "ErhaltungsverordnungUmstrukturierung",
                        "description": "Gebiet einer Satzung nach § 172 Abs. 1.2 BauGB",
                    },
                    "2300": {
                        "name": "StaedtebaulEntwicklungskonzeptInnenentwicklung",
                        "description": "Städtebauliches Entwicklungskonzept zur Stärkung der Innenentwicklung",
                    },
                    "2400": {
                        "name": "GebietMitAngespanntemWohnungsmarkt",
                        "description": "Gebiet mit einem angespannten Wohnungsmarkt",
                    },
                    "2500": {
                        "name": "GenehmigungWohnungseigentum",
                        "description": "Gebiet mit angespanntem Wohnungsmarkt, in dem die Begründung oder Teilung von Wohnungseigentum oder Teileigentum der Genehmigung bedarf.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiger Gebietstyp",
                    },
                },
                "typename": "SO_GebietsArt",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstGebietsArt: Annotated[
        AnyUrl | None,
        Field(
            description='Über eine Codeliste definierte Klassifikation einer nicht auf dem BauGB beruhenden, z.B. länderspezifischen Gebietsausweisung. In dem Fall muss das Attribut "gebietsArt" den Wert 9999 (Sonstiges) haben.',
            json_schema_extra={
                "typename": "SO_SonstGebietsArt",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rechtsstandGebiet: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "9999"] | None,
        Field(
            description="Rechtsstand der Gebietsausweisung",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "VorbereitendeUntersuchung",
                        "description": "Vorbereitende Untersuchung",
                    },
                    "2000": {"name": "Aufstellung", "description": "Aufstellung"},
                    "3000": {"name": "Festlegung", "description": "Festlegung"},
                    "4000": {"name": "Abgeschlossen", "description": "Abgeschlossen"},
                    "5000": {"name": "Verstetigung", "description": "Verstetigung"},
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
                "typename": "SO_RechtsstandGebietTyp",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstRechtsstandGebiet: Annotated[
        AnyUrl | None,
        Field(
            description='Über eine Codeliste definierter sonstiger Rechtsstand der Gebietsausweisung, der nicht durch die Liste SO_RechtsstandGebietTyp wiedergegeben werden kann. Das Attribut "rechtsstandGebiet" muss in diesem Fall den Wert 9999 (Sonstiges) haben.',
            json_schema_extra={
                "typename": "SO_SonstRechtsstandGebietTyp",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    aufstellungsbeschhlussDatum: Annotated[
        date_aliased | None,
        Field(
            description="Datum des Aufstellungsbeschlusses",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    durchfuehrungStartDatum: Annotated[
        date_aliased | None,
        Field(
            description="Start-Datum der Durchführung",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    durchfuehrungEndDatum: Annotated[
        date_aliased | None,
        Field(
            description="End-Datum der Durchführung",
            json_schema_extra={
                "typename": "Date",
                "stereotype": "Temporal",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    traegerMassnahme: Annotated[
        str | None,
        Field(
            description="Maßnahmen-Träger",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOGeometrieobjekt(SOObjekt):
    """
    Basisklasse für alle Objekte mit variablem Raumbezug. Ein konkretes Objekt muss entweder punktförmigen, linienförmigen oder flächenhaften Raumbezug haben, gemischte Geometrie ist nicht zugelassen.
    """

    abstract: ClassVar[bool] = True
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Point
        | definitions.MultiPoint
        | definitions.Line
        | definitions.MultiLine
        | definitions.Polygon
        | definitions.MultiPolygon,
        Field(
            description="Raumbezug - Entweder punktförmig, linienförmig oder flächenhaft, gemischte Geometrie ist nicht zugelassen.",
            json_schema_extra={
                "typename": "XP_VariableGeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]
    flaechenschluss: Annotated[
        bool | None,
        Field(
            description="Zeigt bei flächenhaftem Raumbezug an, ob das Objekt als Flächenschlussobjekt oder Überlagerungsobjekt gebildet werden soll. Flächenschlussobjekte dürfen sich nicht überlappen, sondern nur an den Flächenrändern berühren, wobei die jeweiligen Stützpunkte der Randkurven übereinander liegen müssen. Die Vereinigung der Flächenschlussobjekte überdeckt den Geltungsbereich des sonstigen raumbezogenen Plans vollständig.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    flussrichtung: Annotated[
        bool | None,
        Field(
            description="Das Attribut ist nur relevant, wenn ein Geometrieobjekt einen linienhaften Raumbezug hat. Ist es mit dem Wert true belegt, wird damit ausgedrückt, dass der Linie eine Flussrichtung  in Digitalisierungsrichtung zugeordnet ist. In diesem Fall darf bei Im- und Export die Digitalisierungsreihenfolge der Stützpunkte nicht geändert werden. Wie eine definierte Flussrichtung  zu interpretieren oder bei einer Plandarstellung zu visualisieren ist, bleibt der Implementierung überlassen.\r\nIst der Attributwert false oder das Attribut nicht belegt, ist die Digitalisierungsreihenfolge der Stützpunkte irrelevant.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nordwinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Orientierung des Objektes bei punktförmigem Raumbezug als Winkel gegen die Nordrichtung. Zählweise im geographischen Sinn (von Nord über Ost nach Süd und West)",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class SOGewaesser(SOGeometrieobjekt):
    """
    Abbildung eines bestehenden Gewässers
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal["1000", "10000", "10001", "10002", "10003", "2000", "9999"] | None,
        Field(
            description="Klassifizierung des Gewässers",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Gewaesser",
                        "description": "Allgemeines, bestehendes Gewässer",
                    },
                    "10000": {
                        "name": "Gewaesser1Ordnung",
                        "description": "Bestehendes Gewässer 1. Ordnung",
                    },
                    "10001": {
                        "name": "Gewaesser2Ordnung",
                        "description": "Bestehendes Gewässer 2. Ordnung",
                    },
                    "10002": {
                        "name": "Gewaesser3Odrnung",
                        "description": "Bestehendes Gewässer 3. Ordnung",
                    },
                    "10003": {
                        "name": "StehendesGewaesser",
                        "description": "Stehendes Gewässer",
                    },
                    "2000": {"name": "Hafen", "description": "Hafen"},
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges bestehendes Gewässer",
                    },
                },
                "typename": "SO_KlassifizGewaesser",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Klassifizierung des Gewässers",
            json_schema_extra={
                "typename": "SO_DetailKlassifizGewaesser",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung dees Gewässers",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer des Gewässers.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOLinienobjekt(SOObjekt):
    """
    Basisklasse für Objekte mit linienförmigem Raumbezug (eine einzelne zusammenhängende Kurve, die aus Linienstücken und Kreisbögen zusammengesetzt sein kann, oder eine Menge derartiger Kurven).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    position: Annotated[
        definitions.Line | definitions.MultiLine,
        Field(
            description="Linienförmiger Raumbezug (Einzelne zusammenhängende Kurve, die aus Linienstücken und Kreisbögen aufgebaut ist, oder eine Menge derartiger Kurven),",
            json_schema_extra={
                "typename": "XP_Liniengeometrie",
                "stereotype": "Geometry",
                "multiplicity": "1",
            },
        ),
    ]


class SOLuftverkehrsrecht(SOGeometrieobjekt):
    """
    Festlegung nach Luftverkehrsrecht.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal[
            "1000",
            "2000",
            "3000",
            "4000",
            "5000",
            "5200",
            "5400",
            "6000",
            "7000",
            "9999",
        ]
        | None,
        Field(
            description="Rechtliche Klassifizierung der Festlegung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Flughafen", "description": "Flughafen"},
                    "2000": {"name": "Landeplatz", "description": "Landeplatz"},
                    "3000": {
                        "name": "Segelfluggelaende",
                        "description": "Segelfluggelände",
                    },
                    "4000": {
                        "name": "HubschrauberLandeplatz",
                        "description": "Hubschrauber Landeplatz",
                    },
                    "5000": {
                        "name": "Ballonstartplatz",
                        "description": "Ballon Startplatz",
                    },
                    "5200": {
                        "name": "Haengegleiter",
                        "description": "Startplatz für Hängegleiter",
                    },
                    "5400": {
                        "name": "Gleitsegler",
                        "description": "Startplatz für Gleitsegler",
                    },
                    "6000": {
                        "name": "Laermschutzbereich",
                        "description": "Lärmschutzbereich nach LuftVG",
                    },
                    "7000": {
                        "name": "Baubeschraenkungsbereich",
                        "description": "Höhenbeschränkung nach §12 LuftVG.\r\nDieser Enumerationswert ist veraltet und wird in der nächsten Hauptversion des Standards wegfallen. Es sollte stattdessen die Klasse BP_Bauverbotszone mit artDerFelegung = 2000 verwendet werden.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Klassifizierung nach Luftverkehrsrecht.",
                    },
                },
                "typename": "SO_KlassifizNachLuftverkehrsrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Klassifizierung der Festlegung.",
            json_schema_extra={
                "typename": "SO_DetailKlassifizNachLuftverkehrsrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    laermschutzzone: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Lärmschutzzone nach LuftVG.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "TagZone1", "description": "Tag-Zone 1"},
                    "2000": {"name": "TagZone2", "description": "Tag-Zone 2"},
                    "3000": {"name": "Nacht", "description": "Nacht-Zone"},
                },
                "typename": "SO_LaermschutzzoneTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOSchienenverkehrsrecht(SOGeometrieobjekt):
    """
    Festlegung nach Schienenverkehrsrecht.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal[
            "1000",
            "10000",
            "10001",
            "10002",
            "10003",
            "1200",
            "12000",
            "12001",
            "12002",
            "12003",
            "12004",
            "12005",
            "1400",
            "14000",
            "14001",
            "14002",
            "14003",
            "9999",
        ]
        | None,
        Field(
            description="Rechtliche Klassifizierung der Festlegung",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Bahnanlage",
                        "description": "Bahnanlage allgemein",
                    },
                    "10000": {
                        "name": "DB_Bahnanlage",
                        "description": "Bahnanlage der DB",
                    },
                    "10001": {
                        "name": "Personenbahnhof",
                        "description": "Personenbahnhof",
                    },
                    "10002": {"name": "Fernbahnhof", "description": "Fernbahnhof"},
                    "10003": {"name": "Gueterbahnhof", "description": "Güterbahnhof"},
                    "1200": {"name": "Bahnlinie", "description": "Bahnlinie allgemein"},
                    "12000": {
                        "name": "Personenbahnlinie",
                        "description": "Personenbahnlinie",
                    },
                    "12001": {"name": "Regionalbahn", "description": "Regionalbahn"},
                    "12002": {"name": "Kleinbahn", "description": "Kleinbahn"},
                    "12003": {
                        "name": "Gueterbahnlinie",
                        "description": "Güterbahnlinie",
                    },
                    "12004": {
                        "name": "WerksHafenbahn",
                        "description": "Werks- oder Hafenbahnlinie.",
                    },
                    "12005": {"name": "Seilbahn", "description": "Seilbahn"},
                    "1400": {
                        "name": "OEPNV",
                        "description": "Schienengebundener ÖPNV allgemein.",
                    },
                    "14000": {"name": "Strassenbahn", "description": "Straßenbahn"},
                    "14001": {"name": "UBahn", "description": "U-Bahn"},
                    "14002": {"name": "SBahn", "description": "S-Bahn"},
                    "14003": {
                        "name": "OEPNV_Haltestelle",
                        "description": "Haltestelle im ÖPNV",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Klassifizierung nach Schienenverkehrsrecht.",
                    },
                },
                "typename": "SO_KlassifizNachSchienenverkehrsrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere rechtliche Klassifizierung der Festlegung.",
            json_schema_extra={
                "typename": "SO_DetailKlassifizNachSchienenverkehrsrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung der Festlegung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Festlegung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOSchutzgebietNaturschutzrecht(SOGeometrieobjekt):
    """
    Schutzgebiet nach Naturschutzrecht.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "1300",
            "1400",
            "1500",
            "1600",
            "1700",
            "1800",
            "18000",
            "18001",
            "2000",
            "9999",
        ]
        | None,
        Field(
            description="Klassifizierung des Schutzgebietes",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Naturschutzgebiet",
                        "description": "Naturschutzgebiet gemäß §23 BNatSchG.",
                    },
                    "1100": {
                        "name": "Nationalpark",
                        "description": "Nationalpark gemäß §24 BNatSchG",
                    },
                    "1200": {
                        "name": "Biosphaerenreservat",
                        "description": "Biosphärenreservat gemäß §25 BNatSchG.",
                    },
                    "1300": {
                        "name": "Landschaftsschutzgebiet",
                        "description": "Landschaftsschutzgebiet gemäß §65 BNatSchG.",
                    },
                    "1400": {
                        "name": "Naturpark",
                        "description": "Naturpark gemäß §27 BNatSchG.",
                    },
                    "1500": {
                        "name": "Naturdenkmal",
                        "description": "Naturdenkmal gemäß §28 BNatSchG.",
                    },
                    "1600": {
                        "name": "GeschuetzterLandschaftsBestandteil",
                        "description": "Geschützter Bestandteil der Landschaft gemäß §29 BNatSchG.",
                    },
                    "1700": {
                        "name": "GesetzlichGeschuetztesBiotop",
                        "description": "Gesetzlich geschützte Biotope gemäß §30 BNatSchG.",
                    },
                    "1800": {
                        "name": "Natura2000",
                        "description": 'Schutzgebiet nach Europäischem Recht. Dies umfasst das "Gebiet Gemeinschaftlicher Bedeutung" (FFH-Gebiet) und das "Europäische Vogelschutzgebiet"',
                    },
                    "18000": {
                        "name": "GebietGemeinschaftlicherBedeutung",
                        "description": "Gebiete von gemeinschaftlicher Bedeutung",
                    },
                    "18001": {
                        "name": "EuropaeischesVogelschutzgebiet",
                        "description": "Europäische Vogelschutzgebiete",
                    },
                    "2000": {
                        "name": "NationalesNaturmonument",
                        "description": "Nationales Naturmonument gemäß §24 Abs. (4)  BNatSchG.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges Naturschutzgebiet",
                    },
                },
                "typename": "XP_KlassifizSchutzgebietNaturschutzrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Klassifizierung",
            json_schema_extra={
                "typename": "SO_DetailKlassifizSchutzgebietNaturschutzrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zone: Annotated[
        Literal["1000", "1100", "1200", "2000", "2100", "2200", "2300"] | None,
        Field(
            description="Klassifizierung der Schutzzone",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Schutzzone_1", "description": "Schutzzone 1"},
                    "1100": {"name": "Schutzzone_2", "description": "Schutzzone 2"},
                    "1200": {"name": "Schutzzone_3", "description": "Schutzzone 3"},
                    "2000": {"name": "Kernzone", "description": "Kernzone"},
                    "2100": {"name": "Pflegezone", "description": "Pflegezone"},
                    "2200": {
                        "name": "Entwicklungszone",
                        "description": "Entwicklungszone",
                    },
                    "2300": {
                        "name": "Regenerationszone",
                        "description": "Regenerationszone",
                    },
                },
                "typename": "SO_SchutzzonenNaturschutzrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informeller Name des Schutzgebiets",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtlicher Name / Kennziffer des Gebiets.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOSchutzgebietSonstigesRecht(SOGeometrieobjekt):
    """
    Sonstige Schutzgebiete nach unterschiedlichen rechtlichen Bestimmungen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal["1000", "2000", "9999"] | None,
        Field(
            description="Klassifizierung des Schutzgebietes oder Schutzbereichs.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Laermschutzbereich",
                        "description": "Lärmschutzbereich nach anderen gesetzlichen Regelungen als dem Luftverkehrsrecht.",
                    },
                    "2000": {
                        "name": "SchutzzoneLeitungstrasse",
                        "description": "Schutzzone um eine Leitungstrasse nach Bundes-Immissionsschutzgesetz.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Klassifizierung",
                    },
                },
                "typename": "SO_KlassifizSchutzgebietSonstRecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Klassifizierung.",
            json_schema_extra={
                "typename": "SO_DetailKlassifizSchutzgebietSonstRecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung des Gebiets",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer des Gebiets",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOSchutzgebietWasserrecht(SOGeometrieobjekt):
    """
    Schutzgebiet nach WasserSchutzGesetz (WSG) bzw. HeilQuellenSchutzGesetz (HQSG).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal["1000", "10000", "10001", "2000", "9999"] | None,
        Field(
            description="Klassifizierung des Schutzgebietes",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Wasserschutzgebiet",
                        "description": "Wasserschutzgebiet",
                    },
                    "10000": {
                        "name": "QuellGrundwasserSchutzgebiet",
                        "description": "Ausgewiesenes Schutzgebiet für Quell- und Grundwasser",
                    },
                    "10001": {
                        "name": "OberflaechengewaesserSchutzgebiet",
                        "description": "Ausgewiesenes Schutzgebiet für Oberflächengewässer",
                    },
                    "2000": {
                        "name": "Heilquellenschutzgebiet",
                        "description": "Heilquellen Schutzgebiet",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges Schutzgebiet nach Wasserrecht.",
                    },
                },
                "typename": "SO_KlassifizSchutzgebietWasserrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codelieste definierte detailliertere Klassifizierung",
            json_schema_extra={
                "typename": "SO_DetailKlassifizSchutzgebietWasserrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zone: Annotated[
        Literal["1000", "1100", "1200", "1300", "1400", "1500"] | None,
        Field(
            description="Klassifizierung der Schutzzone",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Zone_1", "description": "Zone 1"},
                    "1100": {"name": "Zone_2", "description": "Zone 2"},
                    "1200": {"name": "Zone_3", "description": "Zone 3"},
                    "1300": {
                        "name": "Zone_3a",
                        "description": "Zone 3a e(xistiert nur bei Wasserschutzgebieten).",
                    },
                    "1400": {
                        "name": "Zone_3b",
                        "description": "Zone 3b (existiert nur bei Wasserschutzgebieten).",
                    },
                    "1500": {
                        "name": "Zone_4",
                        "description": "Zone 4 e(xistiert nur bei Heilquellen).",
                    },
                },
                "typename": "SO_SchutzzonenWasserrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung des Gebiets",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer des Gebiets.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOSonstigesRecht(SOGeometrieobjekt):
    """
    Sonstige Festlegung.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    artDerFestlegung: Annotated[
        Literal["1000", "1100", "1200", "1300", "1400", "1500", "1600", "9999"] | None,
        Field(
            description="Rechtliche Klassifizierung der Festlegung",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Bauschutzbereich",
                        "description": "Bauschutzbereich nach anderen Rechtsverordnungen als dem LuftVG.\r\nDieser Enumerationswert ist veraltet und wird in der nächsten Hauptversion des Standards wegfallen. Es sollte stattdessen die Klasse BP_Bauverbotszone mit artDerFelegung = 9999 verwendet werden.",
                    },
                    "1100": {
                        "name": "Berggesetz",
                        "description": "Beschränkung nach Berggesetz",
                    },
                    "1200": {
                        "name": "Richtfunkverbindung",
                        "description": "Baubeschränkungen durch Richtfunkverbindungen",
                    },
                    "1300": {
                        "name": "Truppenuebungsplatz",
                        "description": "Truppenübungsplatz",
                    },
                    "1400": {
                        "name": "VermessungsKatasterrecht",
                        "description": "Beschränkungen nach Vermessungs- und Katasterrecht",
                    },
                    "1500": {
                        "name": "Rekultivierungsflaeche",
                        "description": "Zu rekultivierende Fläche",
                    },
                    "1600": {
                        "name": "Renaturierungsflaeche",
                        "description": "Zu renaturierende Fläche",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Klassifizierung",
                    },
                },
                "typename": "SO_KlassifizNachSonstigemRecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere rechtliche Klassifizierung der Festlegung.",
            json_schema_extra={
                "typename": "SO_DetailKlassifizNachSonstigemRecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOStrassenverkehrsrecht(SOGeometrieobjekt):
    """
    Festlegung nach Straßenverkehrsrecht.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal["1000", "1100", "1200", "1300", "9999"] | None,
        Field(
            description="Rechtliche Klassifizierung der Festlegung",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Bundesautobahn", "description": "Bundesautobahn"},
                    "1100": {"name": "Bundesstrasse", "description": "Bundesstraße"},
                    "1200": {
                        "name": "LandesStaatsstrasse",
                        "description": "Landes- oder Staatsstraße",
                    },
                    "1300": {"name": "Kreisstrasse", "description": "Kreisstraße"},
                    "9999": {
                        "name": "SonstOeffentlStrasse",
                        "description": "Sonstige öffentliche Straße",
                    },
                },
                "typename": "SO_KlassifizNachStrassenverkehrsrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere rechtliche Klassifizierung der Festlegung.",
            json_schema_extra={
                "typename": "SO_DetailKlassifizNachStrassenverkehrsrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung der Festlegung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Festlegung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOWasserrecht(SOGeometrieobjekt):
    """
    Festlegung nach Wasserhaushaltsgesetz (WHG)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal[
            "1000",
            "10000",
            "10001",
            "10002",
            "2000",
            "20000",
            "20001",
            "20002",
            "3000",
            "4000",
            "5000",
            "9999",
        ]
        | None,
        Field(
            description="Rechtliche Klassifizierung der Festlegung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Gewaesser",
                        "description": "Allgemeines Gewässer\r\nDieser Eintrag ist veraltet und wird in der nächsten Hauptversion des Standards wegfallen. Es sollte stattdessen die Klasse SO_Gewaesser verwendet werden.",
                    },
                    "10000": {
                        "name": "Gewaesser1Ordnung",
                        "description": "Gewässer 1. Ordnung.\r\nAllgemeines Gewässer\r\nDieser Eintrag ist veraltet und wird in der nächsten Hauptversion des Standards wegfallen. Es sollte stattdessen die Klasse SO_Gewaesser verwendet werden.",
                    },
                    "10001": {
                        "name": "Gewaesser2Ordnung",
                        "description": "Gewässer 2. Ordnung.\r\nAllgemeines Gewässer\r\nDieser Eintrag ist veraltet und wird in der nächsten Hauptversion des Standards wegfallen. Es sollte stattdessen die Klasse SO_Gewaesser verwendet werden.",
                    },
                    "10002": {
                        "name": "Gewaesser3Ordnung",
                        "description": "Gewässer 3. Ordnung\r\nAllgemeines Gewässer\r\nDieser Eintrag ist veraltet und wird in der nächsten Hauptversion des Standards wegfallen. Es sollte stattdessen die Klasse SO_Gewaesser verwendet werden.",
                    },
                    "2000": {
                        "name": "Ueberschwemmungsgebiet",
                        "description": "Allgemeines Überschwemmungsgebiet nach WHG",
                    },
                    "20000": {
                        "name": "FestgesetztesUeberschwemmungsgebiet",
                        "description": "Überschwemmungsgebiet nach §76 Abs.2 WHG",
                    },
                    "20001": {
                        "name": "NochNichtFestgesetztesUeberschwemmungsgebiet",
                        "description": "N Noch nicht festgesetztes Überschwemmungsgebiet, das vorläufig gesichert ist nach. § 76 Abs. 3 WHG",
                    },
                    "20002": {
                        "name": "UeberschwemmGefaehrdetesGebiet",
                        "description": "Überschwemmungsgefährdetes Gebiet nach §31c des vor dem 1.3.2010 gültigen WHG",
                    },
                    "3000": {
                        "name": "Risikogebiet",
                        "description": "Risikogebiet nach § 76 Abs. 3 WHG",
                    },
                    "4000": {
                        "name": "RisikogebietAusserhUeberschwemmgebiet",
                        "description": "Risikogebiet außerhalb von Überschwemmungsgebieten  nach. § 78b Abs. 1 WHG",
                    },
                    "5000": {
                        "name": "Hochwasserentstehungsgebiet",
                        "description": "Hochwasserentstehungsgebiet nach § 78d Abs. 1 WHG",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Klassifizierung nach Wasserrecht.",
                    },
                },
                "typename": "SO_KlassifizNachWasserrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere rechtliche Klassifizierung der Festlegung.",
            json_schema_extra={
                "typename": "SO_DetailKlassifizNachWasserrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    istNatuerlichesUberschwemmungsgebiet: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob es sich bei der Fläche um ein natürliches Überschwemmungsgebiet handelt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPAbgrabungsFlaeche(BPFlaechenobjekt):
    """
    Flächen für Aufschüttungen, Abgrabungen oder für die Gewinnung von Bodenschätzen (§9, Abs. 1, Nr. 17 BauGB)). Hier: Flächen für Abgrabungen und die Gewinnung von Bodenschätzen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    abbaugut: Annotated[
        str | None,
        Field(
            description="Bezeichnung des Abbauguts.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPAbstandsFlaeche(BPUeberlagerungsobjekt):
    """
    Festsetzung eines vom Bauordnungsrecht abweichenden Maßes der Tiefe der Abstandsfläche gemäß § 9 Abs 1. Nr. 2a BauGB
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    tiefe: Annotated[
        definitions.Length | None,
        Field(
            description="Absolute Angabe der Tiefe.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None


class BPAbstandsMass(BPGeometrieobjekt):
    """
    Darstellung von Maßpfeilen oder Maßkreisen in BPlänen, um eine eindeutige Vermassung einzelner Festsetzungen zu erreichen.
    Bei Masspfeilen (typ == 1000) sollte das Geometrie-Attribut position nur eine einfache Linien (gml:LineString mit 2 Punkten) enthalten
    Bei Maßkreisen (typ == 2000) sollte position nur einen einfachen Kreisbogen (gml:Curve mit genau einem gml:Arc enthalten.
    In der nächsten Hauptversion von XPlanGML werden diese Empfehlungen zu verpflichtenden Konformitätsbedingungen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Typ der Massangabe (Maßpfeil oder Maßkreis).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Masspfeil",
                        "description": "Das Objekt definiert einen Maßpfeil",
                    },
                    "2000": {
                        "name": "Masskreis",
                        "description": "Das Objekt definiert einen Maßkreis",
                    },
                },
                "typename": "BP_AbstandsMassTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    wert: Annotated[
        definitions.GenericMeasure | None,
        Field(
            description='Wertangabe des Abstandsmaßes. Bei Maßpfeilen (typ == 1000) enthält das Attribut die Länge des Maßpfeilen (uom = "m"), bei Maßkreisen den von startWinkel und endWinkel eingeschlossenen Winkel (uom = "grad").',
            json_schema_extra={
                "typename": "Measure",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "tbd",
            },
        ),
    ] = None
    startWinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Startwinkel für die Plandarstellung des Abstandsmaßes (nur relevant für Maßkreise). Die Winkelwerte beziehen sich auf den Rechtswert (Ost-Richtung)",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    endWinkel: Annotated[
        definitions.Angle | None,
        Field(
            description="Endwinkel für die Planarstellung des Abstandsmaßes (nur relevant für Maßkreise). Die Winkelwerte beziehen sich auf den Rechtswert (Ost-Richtung)",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None


class BPAbweichungVonBaugrenze(BPLinienobjekt):
    """
    Linienhafte Festlegung des Umfangs der Abweichung von der Baugrenze (§23 Abs. 3 Satz 3 BauNVO).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPAbweichungVonUeberbaubererGrundstuecksFlaeche(BPUeberlagerungsobjekt):
    """
    Flächenhafte Festlegung des Umfangs der Abweichung von der überbaubaren Grundstücksfläche (§23 Abs. 3 Satz 3 BauNVO).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPAnpflanzungBindungErhaltung(BPGeometrieobjekt):
    """
    Festsetzung des Anpflanzens von Bäumen, Sträuchern und sonstigen Bepflanzungen;
    Festsetzung von Bindungen für Bepflanzungen und für die Erhaltung von Bäumen, Sträuchern und sonstigen Bepflanzungen sowie von Gewässern;  (§9 Abs. 1 Nr. 25 und Abs. 4 BauGB)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    massnahme: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Art der Maßnahme",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "BindungErhaltung",
                        "description": "Bindungen für Bepflanzungen und für die Erhaltung von Bäumen, Sträuchern und sonstigen Bepflanzungen sowie von Gewässern. Dies entspricht dem Planzeichen 13.2.2 der PlanzV 1990.",
                    },
                    "2000": {
                        "name": "Anpflanzung",
                        "description": "Anpflanzung von Bäumen, Sträuchern oder sonstigen Bepflanzungen. Dies entspricht dem Planzeichen 13.2.1 der PlanzV 1990.",
                    },
                    "3000": {
                        "name": "AnpflanzungBindungErhaltung",
                        "description": "Anpflanzen von Bäumen, Sträuchern und sonstigen Bepflanzungen, sowie Bindungen für Bepflanzungen und für die Erhaltung von Bäumen, Sträuchern und sonstigen Bepflanzungen sowie von Gewässern",
                    },
                },
                "typename": "XP_ABEMassnahmenTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gegenstand: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "2000",
                "2050",
                "2100",
                "2200",
                "3000",
                "4000",
                "5000",
                "6000",
            ]
        ]
        | None,
        Field(
            description="Gegenstand der Maßnahme.",
            json_schema_extra={
                "typename": "XP_AnpflanzungBindungErhaltungsGegenstand",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Baeume", "description": "Bäume"},
                    "1100": {"name": "Kopfbaeume", "description": "Kopfbäume"},
                    "1200": {"name": "Baumreihe", "description": "Baumreihe"},
                    "2000": {"name": "Straeucher", "description": "Sträucher"},
                    "2050": {
                        "name": "BaeumeUndStraeucher",
                        "description": "Bäume und Sträucher",
                    },
                    "2100": {"name": "Hecke", "description": "Hecke"},
                    "2200": {"name": "Knick", "description": "Knick"},
                    "3000": {
                        "name": "SonstBepflanzung",
                        "description": "Sonstige Bepflanzung",
                    },
                    "4000": {
                        "name": "Gewaesser",
                        "description": "Gewässer (nur Erhaltung)",
                    },
                    "5000": {
                        "name": "Fassadenbegruenung",
                        "description": "Fassadenbegrünung",
                    },
                    "6000": {"name": "Dachbegruenung", "description": "Dachbegrünung"},
                },
            },
        ),
    ] = None
    kronendurchmesser: Annotated[
        definitions.Length | None,
        Field(
            description="Durchmesser der Baumkrone bei zu erhaltenden Bäumen.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    pflanztiefe: Annotated[
        definitions.Length | None,
        Field(
            description="Pflanztiefe",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    istAusgleich: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob die Fläche oder Maßnahme zum Ausgleich von Eingriffen genutzt wird.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    baumArt: Annotated[
        AnyUrl | None,
        Field(
            description="Textliche Spezifikation einer Baumart.",
            json_schema_extra={
                "typename": "BP_VegetationsobjektTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    mindesthoehe: Annotated[
        definitions.Length | None,
        Field(
            description="Mindesthöhe des Gegenstands der Festsetzung",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    anzahl: Annotated[
        int | None,
        Field(
            description="Anzahl der anzupflanzenden Objekte",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPAufschuettungsFlaeche(BPFlaechenobjekt):
    """
    Flächen für Aufschüttungen, Abgrabungen oder für die Gewinnung von Bodenschätzen (§ 9 Abs. 1 Nr. 17 und Abs. 6 BauGB). Hier: Flächen für Aufschüttungen
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    aufschuettungsmaterial: Annotated[
        str | None,
        Field(
            description="Bezeichnung des aufgeschütteten Materials",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPAusgleichsFlaeche(BPFlaechenobjekt):
    """
    Festsetzung einer Fläche zum Ausgleich im Sinne des § 1a Abs.3 und §9 Abs. 1a BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der Ausgleichsmaßnahme",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstZiel: Annotated[
        str | None,
        Field(
            description="Textlich formuliertes Ziel, wenn das Attribut ziel den Wert 9999 (Sonstiges) hat.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahme: Annotated[
        list[XPSPEMassnahmenDaten] | None,
        Field(
            description="Auf der Fläche durchzuführende Maßnahmen.",
            json_schema_extra={
                "typename": "XP_SPEMassnahmenDaten",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    refMassnahmenText: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf ein Dokument, das die durchzuführenden Maßnahmen beschreibt.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refLandschaftsplan: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf den Landschaftsplan.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPAusgleichsMassnahme(BPGeometrieobjekt):
    """
    Festsetzung einer Einzelmaßnahme zum Ausgleich im Sinne des § 1a Abs.3 und §9 Abs. 1a BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der Ausgleichsmaßnahme",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstZiel: Annotated[
        str | None,
        Field(
            description="Textlich formuliertes Ziel, wenn das Attribut ziel den Wert 9999 (Sonstiges) hat.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahme: Annotated[
        list[XPSPEMassnahmenDaten] | None,
        Field(
            description="Durchzuführende Ausgleichsmaßnahme.",
            json_schema_extra={
                "typename": "XP_SPEMassnahmenDaten",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    refMassnahmenText: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf ein Dokument, das die durchzuführenden Maßnahmen beschreibt.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refLandschaftsplan: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf den Landschaftsplan.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPBauGrenze(BPLinienobjekt):
    """
    Festsetzung einer Baugrenze (§9 Abs. 1 Nr. 2 BauGB, §22 und 23 BauNVO). Über die Attribute geschossMin und geschossMax kann die Festsetzung auf einen Bereich von Geschossen beschränkt werden. Wenn eine Einschränkung der Festsetzung durch expliziter Höhenangaben erfolgen soll, ist dazu die Oberklassen-Relation hoehenangabe auf den komplexen Datentyp XP_Hoehenangabe zu verwenden.
    Durch die Digitalisierungsreihenfolge der Linienstützpunkte muss sichergestellt sein, dass die überbaute Fläche (BP_UeberbaubareGrundstuecksFlaeche) relativ zur Laufrichtung auf der linken Seite liegt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    bautiefe: Annotated[
        definitions.Length | None,
        Field(
            description="Angabe einer Bautiefe.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    geschossMin: Annotated[
        int | None,
        Field(
            description='Gibt bei geschossweiser Festsetzung die Nummer des Geschosses an, ab den die Festsetzung gilt. Wenn das Attribut nicht belegt ist, gilt die Festsetzung für alle Geschosse bis einschl. "geschossMax".',
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    geschossMax: Annotated[
        int | None,
        Field(
            description='Gibt bei geschossweiser Festsetzung die Nummer des Geschosses an, bis zu der die Festsetzung gilt. Wenn das Attribut nicht belegt ist, gilt die Festsetzung für alle Geschosse ab einschl. "geschossMin".',
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPBauLinie(BPLinienobjekt):
    """
    Festsetzung einer Baulinie (§9 Abs. 1 Nr. 2 BauGB, §22 und 23 BauNVO). Über die Attribute geschossMin und geschossMax kann die Festsetzung auf einen Bereich von Geschossen beschränkt werden. Wenn eine Einschränkung der Festsetzung durch explizite Höhenangaben erfolgen soll, ist dazu die Oberklassen-Relation hoehenangabe auf den komplexen Datentyp XP_Hoehenangabe zu verwenden.
    Durch die Digitalisierungsreihenfolge der Linienstützpunkte muss sichergestellt sein, dass die überbaute Fläche (BP_UeberbaubareGrundstuecksFlaeche) relativ zur Laufrichtung auf der linken Seite liegt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    bautiefe: Annotated[
        definitions.Length | None,
        Field(
            description="Angabe einer Bautiefe.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    geschossMin: Annotated[
        int | None,
        Field(
            description='Gibt bei geschossweiser Festsetzung die Nummer des Geschosses an, ab den die Festsetzung gilt. Wenn das Attribut nicht belegt ist, gilt die Festsetzung für alle Geschosse bis einschl. "geschossMax".',
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    geschossMax: Annotated[
        int | None,
        Field(
            description='Gibt bei geschossweiser Feststzung die Nummer des Geschosses an, bis zu der die Festsetzung gilt. Wenn das Attribut nicht belegt ist, gilt die Festsetzung für alle Geschosse ab einschl. "geschossMin".',
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPBaugebietsTeilFlaeche(BPFlaechenschlussobjekt):
    """
    Teil eines Baugebiets mit einheitlicher Art der baulichen Nutzung. Das Maß der baulichen Nutzung sowie Festsetzungen zur Bauweise oder Grenzbebauung können innerhalb einer BP_BaugebietsTeilFlaeche unterschiedlich sein (BP_UeberbaubareGrundstueckeFlaeche). Dabei sollte die gleichzeitige Belegung desselben Attributs in BP_BaugebietsTeilFlaeche und einem überlagernden Objekt BP_UeberbaubareGrunsdstuecksFlaeche verzichtet werden.  Ab Version 6.0 wird dies evtl. durch eine Konformitätsregel erzwungen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    dachgestaltung: Annotated[
        list[BPDachgestaltung] | None,
        Field(
            description="Parameter zur Einschränkung der zulässigen Dachformen.",
            json_schema_extra={
                "typename": "BP_Dachgestaltung",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    DNmin: Annotated[
        definitions.Angle | None,
        Field(
            description="Minimal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNmax: Annotated[
        definitions.Angle | None,
        Field(
            description="Maxmal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DN: Annotated[
        definitions.Angle | None,
        Field(
            description="Maximal zulässige Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNZwingend: Annotated[
        definitions.Angle | None,
        Field(
            description="Zwingend vorgeschriebene Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    FR: Annotated[
        definitions.Angle | None,
        Field(
            description="Vorgeschriebene Firstrichtung",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    dachform: Annotated[
        list[
            Literal[
                "1000",
                "2100",
                "2200",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "3600",
                "3700",
                "3800",
                "3900",
                "4000",
                "4100",
                "5000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Erlaubte Dachformen.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "BP_Dachform",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Flachdach",
                        "description": "Flachdach\r\nEmpfohlene Abkürzung: FD",
                    },
                    "2100": {
                        "name": "Pultdach",
                        "description": "Pultdach\r\nEmpfohlene Abkürzung: PD",
                    },
                    "2200": {
                        "name": "VersetztesPultdach",
                        "description": "Versetztes Pultdach\r\nEmpfohlene Abkürzung: VPD",
                    },
                    "3000": {
                        "name": "GeneigtesDach",
                        "description": "Kein Flachdach\r\nEmpfohlene Abkürzung: GD",
                    },
                    "3100": {
                        "name": "Satteldach",
                        "description": "Satteldach\r\nEmpfohlene Abkürzung: SD",
                    },
                    "3200": {
                        "name": "Walmdach",
                        "description": "Walmdach\r\nEmpfohlene Abkürzung: WD",
                    },
                    "3300": {
                        "name": "Krueppelwalmdach",
                        "description": "Krüppelwalmdach\r\nEmpfohlene Abkürzung: KWD",
                    },
                    "3400": {
                        "name": "Mansarddach",
                        "description": "Mansardendach\r\nEmpfohlene Abkürzung: MD",
                    },
                    "3500": {
                        "name": "Zeltdach",
                        "description": "Zeltdach\r\nEmpfohlene Abkürzung: ZD",
                    },
                    "3600": {
                        "name": "Kegeldach",
                        "description": "Kegeldach\r\nEmpfohlene Abkürzung: KeD",
                    },
                    "3700": {
                        "name": "Kuppeldach",
                        "description": "Kuppeldach\r\nEmpfohlene Abkürzung: KuD",
                    },
                    "3800": {
                        "name": "Sheddach",
                        "description": "Sheddach\r\nEmpfohlene Abkürzung: ShD",
                    },
                    "3900": {
                        "name": "Bogendach",
                        "description": "Bogendach\r\nEmpfohlene Abkürzung: BD",
                    },
                    "4000": {
                        "name": "Turmdach",
                        "description": "Turmdach\r\nEmpfohlene Abkürzung: TuD",
                    },
                    "4100": {
                        "name": "Tonnendach",
                        "description": "Tonnendach\r\nEmpfohlene Abkürzung: ToD",
                    },
                    "5000": {
                        "name": "Mischform",
                        "description": "Gemischte Dachform\r\nEmpfohlene Abkürzung: GDF",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Dachform\r\nEmpfohlene Abkürzung: SDF",
                    },
                },
            },
        ),
    ] = None
    detaillierteDachform: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definiertere detailliertere Dachform.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteDachform" bezieht sich auf den an gleicher Position stehenden Attributwert von dachform.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.',
            json_schema_extra={
                "typename": "BP_DetailDachform",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    abweichungText: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Texliche Beschreibung der abweichenden Bauweise",
            json_schema_extra={
                "typename": "BP_TextAbschnitt",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    wohnnutzungEGStrasse: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung nach §6a Abs. (4) Nr. 1 BauNVO: Für urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass in Gebäuden \r\nim Erdgeschoss an der Straßenseite eine Wohnnutzung nicht oder nur ausnahmsweise zulässig ist.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Zulaessig",
                        "description": "Generelle Zulässigkeit",
                    },
                    "2000": {
                        "name": "NichtZulaessig",
                        "description": "Generelle Nicht-Zulässigkeit.",
                    },
                    "3000": {
                        "name": "AusnahmsweiseZulaessig",
                        "description": "Ausnahmsweise Zulässigkeit",
                    },
                },
                "typename": "BP_Zulaessigkeit",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZWohn: Annotated[
        int | None,
        Field(
            description="Festsetzung nach §4a Abs. (4) Nr. 1 bzw. nach  §6a Abs. (4) Nr. 2 BauNVO: Für besondere Wohngebiete und  urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass in Gebäuden oberhalb eines im Bebauungsplan bestimmten Geschosses nur Wohnungen zulässig sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFAntWohnen: Annotated[
        definitions.Scale | None,
        Field(
            description="Festsetzung nach §4a Abs. (4) Nr. 2 bzw. §6a Abs. (4) Nr. 3 BauNVO: Für besondere Wohngebiete und urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden ein im Bebauungsplan bestimmter Anteil der zulässigen \r\nGeschossfläche für Wohnungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Scale",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "vH",
            },
        ),
    ] = None
    GFWohnen: Annotated[
        definitions.Area | None,
        Field(
            description="Festsetzung nach §4a Abs. (4) Nr. 2 bzw. §6a Abs. (4) Nr. 3 BauNVO: Für besondere Wohngebiete und urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden eine im Bebauungsplan bestimmte Größe der Geschossfläche für Wohnungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFAntGewerbe: Annotated[
        definitions.Scale | None,
        Field(
            description="Festsetzung nach §6a Abs. (4) Nr. 4 BauNVO: Für urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden ein im Bebauungsplan bestimmter Anteil der zulässigen \r\nGeschossfläche für gewerbliche Nutzungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Scale",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "vH",
            },
        ),
    ] = None
    GFGewerbe: Annotated[
        definitions.Area | None,
        Field(
            description="Festsetzung nach §6a Abs. (4) Nr. 4 BauNVO: Für urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden eine im Bebauungsplan bestimmte Größe der Geschossfläche für gewerbliche Nutzungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    VF: Annotated[
        definitions.Area | None,
        Field(
            description="Festsetzung der maximal zulässigen Verkaufsfläche in einem Sondergebiet",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    allgArtDerBaulNutzung: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description='Spezifikation der allgemeinen Art der baulichen N utzung.\r\nDies Attribut ist als "veraltet" gekennzeichnet und wird in Version 6.0 evtl. wegfallen.',
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "WohnBauflaeche",
                        "description": "Wohnbaufläche nach §1 Abs. (1) BauNVO",
                    },
                    "2000": {
                        "name": "GemischteBauflaeche",
                        "description": "Gemischte Baufläche nach §1 Abs. (1) BauNVO.",
                    },
                    "3000": {
                        "name": "GewerblicheBauflaeche",
                        "description": "Gewerbliche Baufläche nach §1 Abs. (1) BauNVO.",
                    },
                    "4000": {
                        "name": "SonderBauflaeche",
                        "description": "Sonderbaufläche nach §1 Abs. (1) BauNVO.",
                    },
                    "9999": {
                        "name": "SonstigeBauflaeche",
                        "description": "Sonstige Baufläche",
                    },
                },
                "typename": "XP_AllgArtDerBaulNutzung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    besondereArtDerBaulNutzung: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "1300",
            "1400",
            "1450",
            "1500",
            "1550",
            "1600",
            "1700",
            "1800",
            "2000",
            "2100",
            "3000",
            "4000",
            "9999",
        ]
        | None,
        Field(
            description="Festsetzung der Art der baulichen Nutzung (§9, Abs. 1, Nr. 1 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Kleinsiedlungsgebiet",
                        "description": "Kleinsiedlungsgebiet nach § 2 BauNVO.",
                    },
                    "1100": {
                        "name": "ReinesWohngebiet",
                        "description": "Reines Wohngebiet nach § 3 BauNVO.",
                    },
                    "1200": {
                        "name": "AllgWohngebiet",
                        "description": "Allgemeines Wohngebiet nach § 4 BauNVO.",
                    },
                    "1300": {
                        "name": "BesonderesWohngebiet",
                        "description": "Gebiet zur Erhaltung und Entwicklung der Wohnnutzung (Besonderes Wohngebiet) nach § 4a BauNVO.",
                    },
                    "1400": {
                        "name": "Dorfgebiet",
                        "description": "Dorfgebiet nach $ 5 BauNVO.",
                    },
                    "1450": {
                        "name": "DoerflichesWohngebiet",
                        "description": "Dörfliches Wohngebiet nach §5a BauNVO",
                    },
                    "1500": {
                        "name": "Mischgebiet",
                        "description": "Mischgebiet nach $ 6 BauNVO.",
                    },
                    "1550": {
                        "name": "UrbanesGebiet",
                        "description": "Urbanes Gebiet nach § 6a BauNVO",
                    },
                    "1600": {
                        "name": "Kerngebiet",
                        "description": "Kerngebiet nach § 7 BauNVO.",
                    },
                    "1700": {
                        "name": "Gewerbegebiet",
                        "description": "Gewerbegebiet nach § 8 BauNVO.",
                    },
                    "1800": {
                        "name": "Industriegebiet",
                        "description": "Industriegebiet nach § 9 BauNVO.",
                    },
                    "2000": {
                        "name": "SondergebietErholung",
                        "description": "Sondergebiet, das der Erholung dient nach § 10 BauNVO von 1977 und 1990.",
                    },
                    "2100": {
                        "name": "SondergebietSonst",
                        "description": "Sonstiges Sondergebiet nach§ 11 BauNVO 1977 und 1990; z.B. Klinikgebiet",
                    },
                    "3000": {
                        "name": "Wochenendhausgebiet",
                        "description": "Wochenendhausgebiet nach §10 der BauNVO von 1962 und 1968",
                    },
                    "4000": {
                        "name": "Sondergebiet",
                        "description": "Sondergebiet nach §11der BauNVO von 1962 und 1968",
                    },
                    "9999": {
                        "name": "SonstigesGebiet",
                        "description": "Sonstiges Gebiet",
                    },
                },
                "typename": "XP_BesondereArtDerBaulNutzung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sondernutzung: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "1300",
                "1400",
                "1500",
                "1600",
                "16000",
                "16001",
                "16002",
                "1700",
                "1800",
                "1900",
                "2000",
                "2100",
                "2200",
                "2300",
                "23000",
                "2400",
                "2500",
                "2600",
                "2700",
                "2720",
                "2800",
                "2900",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Differenziert Sondernutzungen nach §10 und §11 der BauNVO von 1977 und 1990. Das Attribut wird nur benutzt, wenn besondereArtDerBaulNutzung unbelegt ist oder einen der Werte 2000 bzw. 2100 hat.",
            json_schema_extra={
                "typename": "XP_Sondernutzungen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Wochenendhausgebiet",
                        "description": "Wochenendhausgebiet",
                    },
                    "1100": {
                        "name": "Ferienhausgebiet",
                        "description": "Ferienhausgebiet",
                    },
                    "1200": {
                        "name": "Campingplatzgebiet",
                        "description": "Campingplatzgebiet",
                    },
                    "1300": {"name": "Kurgebiet", "description": "Kurgebiet"},
                    "1400": {
                        "name": "SonstSondergebietErholung",
                        "description": "Sonstiges Sondergebiet für Erholung",
                    },
                    "1500": {
                        "name": "Einzelhandelsgebiet",
                        "description": "Einzelhandelsgebiet",
                    },
                    "1600": {
                        "name": "GrossflaechigerEinzelhandel",
                        "description": "Gebiet für großflächigen Einzelhandel",
                    },
                    "16000": {"name": "Ladengebiet", "description": "Ladengebiet"},
                    "16001": {
                        "name": "Einkaufszentrum",
                        "description": "Einkaufszentrum",
                    },
                    "16002": {
                        "name": "SonstGrossflEinzelhandel",
                        "description": "Sonstiges Gebiet für großflächigen Einzelhandel",
                    },
                    "1700": {
                        "name": "Verkehrsuebungsplatz",
                        "description": "Verkehrsübungsplatz",
                    },
                    "1800": {"name": "Hafengebiet", "description": "Hafengebiet"},
                    "1900": {
                        "name": "SondergebietErneuerbareEnergie",
                        "description": "Sondergebiet für Erneuerbare Energien",
                    },
                    "2000": {
                        "name": "SondergebietMilitaer",
                        "description": "Militärisches Sondergebiet",
                    },
                    "2100": {
                        "name": "SondergebietLandwirtschaft",
                        "description": "Sondergebiet Landwirtschaft",
                    },
                    "2200": {
                        "name": "SondergebietSport",
                        "description": "Sondergebiet Sport",
                    },
                    "2300": {
                        "name": "SondergebietGesundheitSoziales",
                        "description": "Sondergebiet für Gesundheit und Soziales",
                    },
                    "23000": {"name": "Klinikgebiet", "description": "Klinikgebiet"},
                    "2400": {"name": "Golfplatz", "description": "Golfplatz"},
                    "2500": {
                        "name": "SondergebietKultur",
                        "description": "Sondergebiet für Kultur",
                    },
                    "2600": {
                        "name": "SondergebietTourismus",
                        "description": "Sondergebiet Tourismus",
                    },
                    "2700": {
                        "name": "SondergebietBueroUndVerwaltung",
                        "description": "Sondergebiet für Büros und Verwaltung",
                    },
                    "2720": {
                        "name": "SondergebietJustiz",
                        "description": "Sondergebiet für Einrichtungen der Justiz",
                    },
                    "2800": {
                        "name": "SondergebietHochschuleForschung",
                        "description": "Sondergebiet Hochschule",
                    },
                    "2900": {
                        "name": "SondergebietMesse",
                        "description": "Sondergebiet für Messe",
                    },
                    "9999": {
                        "name": "SondergebietAndereNutzungen",
                        "description": "Sonstiges Sondergebiet",
                    },
                },
            },
        ),
    ] = None
    detaillierteArtDerBaulNutzung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Nutzungsart.",
            json_schema_extra={
                "typename": "BP_DetailArtDerBaulNutzung",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detaillierteSondernutzung: Annotated[
        list[AnyUrl] | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Sondernutzungsart.",
            json_schema_extra={
                "typename": "BP_DetailSondernutzung",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    nutzungText: Annotated[
        str | None,
        Field(
            description='Bei Nutzungsform "Sondergebiet" ("besondereArtDerBaulNutzung" == 4000): Kurzform der besonderen Art der baulichen Nutzung.',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    abweichungBauNVO: Annotated[
        Literal["1000", "2000", "3000", "9999"] | None,
        Field(
            description="Art der zulässigen Abweichung von der BauNVO.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "EinschraenkungNutzung",
                        "description": "Einschränkung einer generell erlaubten Nutzung.",
                    },
                    "2000": {
                        "name": "AusschlussNutzung",
                        "description": "Ausschluss einer generell erlaubten Nutzung.",
                    },
                    "3000": {
                        "name": "AusweitungNutzung",
                        "description": "Eine nur ausnahmsweise zulässige Nutzung wird generell zulässig.",
                    },
                    "9999": {
                        "name": "SonstAbweichung",
                        "description": "Sonstige Abweichung.",
                    },
                },
                "typename": "XP_AbweichungBauNVOTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bauweise: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bauweise  (§9, Abs. 1, Nr. 2 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "OffeneBauweise",
                        "description": "Offene Bauweise",
                    },
                    "2000": {
                        "name": "GeschlosseneBauweise",
                        "description": "Geschlossene Bauweise",
                    },
                    "3000": {
                        "name": "AbweichendeBauweise",
                        "description": "Abweichende Bauweise",
                    },
                },
                "typename": "BP_Bauweise",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    abweichendeBauweise: Annotated[
        AnyUrl | None,
        Field(
            description='Nähere Bezeichnung einer "Abweichenden Bauweise" ("bauweise" == 3000).',
            json_schema_extra={
                "typename": "BP_AbweichendeBauweise",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    vertikaleDifferenzierung: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob eine vertikale Differenzierung der Gebäude vorgeschrieben ist.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    bebauungsArt: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "6000", "7000", "8000"] | None,
        Field(
            description="Detaillierte Festsetzung der Bauweise (§9, Abs. 1, Nr. 2 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Einzelhaeuser",
                        "description": "Nur Einzelhäuser zulässig.",
                    },
                    "2000": {
                        "name": "Doppelhaeuser",
                        "description": "Nur Doppelhäuser zulässig.",
                    },
                    "3000": {
                        "name": "Hausgruppen",
                        "description": "Nur Hausgruppen zulässig.",
                    },
                    "4000": {
                        "name": "EinzelDoppelhaeuser",
                        "description": "Nur Einzel- oder Doppelhäuser zulässig.",
                    },
                    "5000": {
                        "name": "EinzelhaeuserHausgruppen",
                        "description": "Nur Einzelhäuser oder Hausgruppen zulässig.",
                    },
                    "6000": {
                        "name": "DoppelhaeuserHausgruppen",
                        "description": "Nur Doppelhäuser oder Hausgruppen zulässig.",
                    },
                    "7000": {
                        "name": "Reihenhaeuser",
                        "description": "Nur Reihenhäuser zulässig.",
                    },
                    "8000": {
                        "name": "EinzelhaeuserDoppelhaeuserHausgruppen",
                        "description": "Es sind Einzelhäuser, Doppelhäuser und Hausgruppen zulässig.",
                    },
                },
                "typename": "BP_BebauungsArt",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungVordereGrenze: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bebauung der vorderen Grundstücksgrenze (§9, Abs. 1, Nr. 2 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Verboten",
                        "description": "Eine Bebauung der Grenze ist verboten.",
                    },
                    "2000": {
                        "name": "Erlaubt",
                        "description": "Eine Bebauung der Grenze ist erlaubt.",
                    },
                    "3000": {
                        "name": "Erzwungen",
                        "description": "Eine Bebauung der Grenze ist vorgeschrieben.",
                    },
                },
                "typename": "BP_GrenzBebauung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungRueckwaertigeGrenze: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bebauung der rückwärtigen Grundstücksgrenze (§9, Abs. 1, Nr. 2 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Verboten",
                        "description": "Eine Bebauung der Grenze ist verboten.",
                    },
                    "2000": {
                        "name": "Erlaubt",
                        "description": "Eine Bebauung der Grenze ist erlaubt.",
                    },
                    "3000": {
                        "name": "Erzwungen",
                        "description": "Eine Bebauung der Grenze ist vorgeschrieben.",
                    },
                },
                "typename": "BP_GrenzBebauung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungSeitlicheGrenze: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bebauung der seitlichen Grundstücksgrenze (§9, Abs. 1, Nr. 2 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Verboten",
                        "description": "Eine Bebauung der Grenze ist verboten.",
                    },
                    "2000": {
                        "name": "Erlaubt",
                        "description": "Eine Bebauung der Grenze ist erlaubt.",
                    },
                    "3000": {
                        "name": "Erzwungen",
                        "description": "Eine Bebauung der Grenze ist vorgeschrieben.",
                    },
                },
                "typename": "BP_GrenzBebauung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refGebaeudequerschnitt: Annotated[
        list[XPExterneReferenz] | None,
        Field(
            description="Referenz auf ein Dokument mit vorgeschriebenen Gebäudequerschnitten.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    zugunstenVon: Annotated[
        str | None,
        Field(
            description="Angabe des Begünstigten einer Ausweisung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPBereichOhneEinAusfahrtLinie(BPLinienobjekt):
    """
    Bereich ohne Ein- und Ausfahrt (§ 9 Abs. 1 Nr. 11 und Abs. 6 BauGB).
    Durch die Digitalisierungsreihenfolge der Linienstützpunkte muss sichergestellt sein, dass der angrenzende Bereich ohne Ein- und Ausfahrt relativ zur Laufrichtung auf der linken Seite liegt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Typ des Bereiches ohne Ein- und Ausfahrt",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "KeineEinfahrt",
                        "description": "Bereich ohne Einfahrt",
                    },
                    "2000": {
                        "name": "KeineAusfahrt",
                        "description": "Bereich ohne Ausfahrt",
                    },
                    "3000": {
                        "name": "KeineEinAusfahrt",
                        "description": "Bereich ohne Ein- und Ausfahrt.",
                    },
                },
                "typename": "BP_BereichOhneEinAusfahrtTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPBesondererNutzungszweckFlaeche(BPFlaechenobjekt):
    """
    Festsetzung einer Fläche mit besonderem Nutzungszweck, der durch besondere städtebauliche Gründe erfordert wird (§9 Abs. 1 Nr. 9 BauGB.)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    dachgestaltung: Annotated[
        list[BPDachgestaltung] | None,
        Field(
            description="Parameter zur Einschränkung der zulässigen Dachformen.",
            json_schema_extra={
                "typename": "BP_Dachgestaltung",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    DNmin: Annotated[
        definitions.Angle | None,
        Field(
            description="Minimal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNmax: Annotated[
        definitions.Angle | None,
        Field(
            description="Maxmal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DN: Annotated[
        definitions.Angle | None,
        Field(
            description="Maximal zulässige Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNZwingend: Annotated[
        definitions.Angle | None,
        Field(
            description="Zwingend vorgeschriebene Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    FR: Annotated[
        definitions.Angle | None,
        Field(
            description="Vorgeschriebene Firstrichtung",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    dachform: Annotated[
        list[
            Literal[
                "1000",
                "2100",
                "2200",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "3600",
                "3700",
                "3800",
                "3900",
                "4000",
                "4100",
                "5000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Erlaubte Dachformen.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "BP_Dachform",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Flachdach",
                        "description": "Flachdach\r\nEmpfohlene Abkürzung: FD",
                    },
                    "2100": {
                        "name": "Pultdach",
                        "description": "Pultdach\r\nEmpfohlene Abkürzung: PD",
                    },
                    "2200": {
                        "name": "VersetztesPultdach",
                        "description": "Versetztes Pultdach\r\nEmpfohlene Abkürzung: VPD",
                    },
                    "3000": {
                        "name": "GeneigtesDach",
                        "description": "Kein Flachdach\r\nEmpfohlene Abkürzung: GD",
                    },
                    "3100": {
                        "name": "Satteldach",
                        "description": "Satteldach\r\nEmpfohlene Abkürzung: SD",
                    },
                    "3200": {
                        "name": "Walmdach",
                        "description": "Walmdach\r\nEmpfohlene Abkürzung: WD",
                    },
                    "3300": {
                        "name": "Krueppelwalmdach",
                        "description": "Krüppelwalmdach\r\nEmpfohlene Abkürzung: KWD",
                    },
                    "3400": {
                        "name": "Mansarddach",
                        "description": "Mansardendach\r\nEmpfohlene Abkürzung: MD",
                    },
                    "3500": {
                        "name": "Zeltdach",
                        "description": "Zeltdach\r\nEmpfohlene Abkürzung: ZD",
                    },
                    "3600": {
                        "name": "Kegeldach",
                        "description": "Kegeldach\r\nEmpfohlene Abkürzung: KeD",
                    },
                    "3700": {
                        "name": "Kuppeldach",
                        "description": "Kuppeldach\r\nEmpfohlene Abkürzung: KuD",
                    },
                    "3800": {
                        "name": "Sheddach",
                        "description": "Sheddach\r\nEmpfohlene Abkürzung: ShD",
                    },
                    "3900": {
                        "name": "Bogendach",
                        "description": "Bogendach\r\nEmpfohlene Abkürzung: BD",
                    },
                    "4000": {
                        "name": "Turmdach",
                        "description": "Turmdach\r\nEmpfohlene Abkürzung: TuD",
                    },
                    "4100": {
                        "name": "Tonnendach",
                        "description": "Tonnendach\r\nEmpfohlene Abkürzung: ToD",
                    },
                    "5000": {
                        "name": "Mischform",
                        "description": "Gemischte Dachform\r\nEmpfohlene Abkürzung: GDF",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Dachform\r\nEmpfohlene Abkürzung: SDF",
                    },
                },
            },
        ),
    ] = None
    detaillierteDachform: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definiertere detailliertere Dachform.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteDachform" bezieht sich auf den an gleicher Position stehenden Attributwert von dachform.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.',
            json_schema_extra={
                "typename": "BP_DetailDachform",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zweckbestimmung: Annotated[
        str | None,
        Field(
            description="Angabe des besonderen Nutzungszwecks.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bauweise: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bauweise  (§9, Abs. 1, Nr. 2 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "OffeneBauweise",
                        "description": "Offene Bauweise",
                    },
                    "2000": {
                        "name": "GeschlosseneBauweise",
                        "description": "Geschlossene Bauweise",
                    },
                    "3000": {
                        "name": "AbweichendeBauweise",
                        "description": "Abweichende Bauweise",
                    },
                },
                "typename": "BP_Bauweise",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    abweichendeBauweise: Annotated[
        AnyUrl | None,
        Field(
            description='Nähere Bezeichnung einer "Abweichenden Bauweise" ("bauweise" == 3000).',
            json_schema_extra={
                "typename": "BP_AbweichendeBauweise",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungsArt: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "6000", "7000", "8000"] | None,
        Field(
            description="Detaillierte Festsetzung der Bauweise (§9, Abs. 1, Nr. 2 BauGB).",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Einzelhaeuser",
                        "description": "Nur Einzelhäuser zulässig.",
                    },
                    "2000": {
                        "name": "Doppelhaeuser",
                        "description": "Nur Doppelhäuser zulässig.",
                    },
                    "3000": {
                        "name": "Hausgruppen",
                        "description": "Nur Hausgruppen zulässig.",
                    },
                    "4000": {
                        "name": "EinzelDoppelhaeuser",
                        "description": "Nur Einzel- oder Doppelhäuser zulässig.",
                    },
                    "5000": {
                        "name": "EinzelhaeuserHausgruppen",
                        "description": "Nur Einzelhäuser oder Hausgruppen zulässig.",
                    },
                    "6000": {
                        "name": "DoppelhaeuserHausgruppen",
                        "description": "Nur Doppelhäuser oder Hausgruppen zulässig.",
                    },
                    "7000": {
                        "name": "Reihenhaeuser",
                        "description": "Nur Reihenhäuser zulässig.",
                    },
                    "8000": {
                        "name": "EinzelhaeuserDoppelhaeuserHausgruppen",
                        "description": "Es sind Einzelhäuser, Doppelhäuser und Hausgruppen zulässig.",
                    },
                },
                "typename": "BP_BebauungsArt",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPBodenschaetzeFlaeche(BPFlaechenobjekt):
    """
    Flächen für Aufschüttungen, Abgrabungen oder für die Gewinnung von Bodenschätzen (§ 9 Abs. 1 Nr. 17 und Abs. 6 BauGB). Hier: Flächen für Gewinnung von Bodenschätzen

    Die Klasse wird als veraltet gekennzeichnet und wird in XPlanGML V. 6.0 wegfallen. Es sollte stattdessen die Klasse BP_AbgrabungsFlaeche verwendet werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    abbaugut: Annotated[
        str | None,
        Field(
            description="Bezeichnung des Abbauguts.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPEinfahrtsbereichLinie(BPLinienobjekt):
    """
    Linienhaft modellierter Einfahrtsbereich (§9 Abs. 1 Nr. 11 und Abs. 6 BauGB).
    Durch die Digitalisierungsreihenfolge der Linienstützpunkte muss sichergestellt sein, dass die  angrenzende Einfahrt relativ zur Laufrichtung auf der linken Seite liegt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Typ der Einfahrt",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Einfahrt", "description": "Nur Einfahrt möglich"},
                    "2000": {"name": "Ausfahrt", "description": "Nur Ausfahrt möglich"},
                    "3000": {
                        "name": "EinAusfahrt",
                        "description": "Ein- und Ausfahrt möglich",
                    },
                },
                "typename": "BP_EinfahrtTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPEingriffsBereich(BPUeberlagerungsobjekt):
    """
    Bestimmt einen Bereich, in dem ein Eingriff nach dem Naturschutzrecht zugelassen wird, der durch geeignete Flächen oder Maßnahmen ausgeglichen werden muss.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPErhaltungsBereichFlaeche(BPUeberlagerungsobjekt):
    """
    Fläche, auf denen der Rückbau, die Änderung oder die Nutzungsänderung baulichen Anlagen der Genehmigung durch die Gemeinde bedarf (§172 BauGB)

    Die Klasse wird als veraltet gekennzeichnet und fällt in XPlanGML V. 6.0 weg. Stattdessen sollte die Klasse SO_Gebiet verwendet werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    grund: Annotated[
        Literal["1000", "2000", "3000"],
        Field(
            description="Erhaltungsgrund",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "StaedtebaulicheGestalt",
                        "description": "Erhaltung der städtebaulichen Eigenart des Gebiets auf Grund seiner städtebaulichen Gestalt",
                    },
                    "2000": {
                        "name": "Wohnbevoelkerung",
                        "description": "Erhaltung der Zusammensetzung der Wohnbevölkerung",
                    },
                    "3000": {
                        "name": "Umstrukturierung",
                        "description": "Erhaltung bei städtebaulichen Umstrukturierungen",
                    },
                },
                "typename": "BP_ErhaltungsGrund",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]


class BPFestsetzungNachLandesrecht(BPGeometrieobjekt):
    """
    Festsetzung nach § 9 Nr. (4) BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    kurzbeschreibung: Annotated[
        str | None,
        Field(
            description="Kurzbeschreibung der Festsetzung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPFirstRichtungsLinie(BPLinienobjekt):
    """
    Gestaltungs-Festsetzung der Firstrichtung, beruhend auf Landesrecht, gemäß §9 Abs. 4 BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPFlaecheOhneFestsetzung(BPFlaechenschlussobjekt):
    """
    Fläche, für die keine geplante Nutzung angegeben werden kann
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPFoerderungsFlaeche(BPUeberlagerungsobjekt):
    """
    Fläche, auf der ganz oder teilweise nur Wohngebäude, die mit Mitteln der sozialen Wohnraumförderung gefördert werden könnten, errichtet werden dürfen (§9, Abs. 1, Nr. 7 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPFreiFlaeche(BPUeberlagerungsobjekt):
    """
    Umgrenzung der Flächen, die von der Bebauung freizuhalten sind, und ihre Nutzung (§ 9 Abs. 1 Nr. 10 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    nutzung: Annotated[
        str | None,
        Field(
            description="Festgesetzte Nutzung der Freifläche.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPGebaeudeFlaeche(BPUeberlagerungsobjekt):
    """
    Grundrissfläche eines existierenden Gebäudes
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPGemeinschaftsanlagenFlaeche(BPUeberlagerungsobjekt):
    """
    Fläche für Gemeinschaftsanlagen für bestimmte räumliche Bereiche wie Kinderspielplätze, Freizeiteinrichtungen, Stellplätze und Garagen (§ 9 Abs. 1 Nr. 22 BauGB)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "3600",
                "3700",
                "3800",
                "3900",
                "4000",
                "9999",
                "4100",
                "4200",
                "4300",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Fläche",
            json_schema_extra={
                "typename": "BP_ZweckbestimmungGemeinschaftsanlagen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Gemeinschaftsstellplaetze",
                        "description": "Gemeinschaftliche Stellplätze",
                    },
                    "2000": {
                        "name": "Gemeinschaftsgaragen",
                        "description": "Gemeinschaftsgaragen",
                    },
                    "3000": {"name": "Spielplatz", "description": "Spielplatz"},
                    "3100": {"name": "Carport", "description": "Carport"},
                    "3200": {
                        "name": "GemeinschaftsTiefgarage",
                        "description": "Gemeinschafts-Tiefgarage",
                    },
                    "3300": {"name": "Nebengebaeude", "description": "Nebengebäude"},
                    "3400": {
                        "name": "AbfallSammelanlagen",
                        "description": "Abfall-Sammelanlagen",
                    },
                    "3500": {
                        "name": "EnergieVerteilungsanlagen",
                        "description": "Energie-Verteilungsanlagen",
                    },
                    "3600": {
                        "name": "AbfallWertstoffbehaelter",
                        "description": "Abfall-Wertstoffbehälter",
                    },
                    "3700": {
                        "name": "Freizeiteinrichtungen",
                        "description": "Freizeiteinrichtungen",
                    },
                    "3800": {
                        "name": "Laermschutzanlagen",
                        "description": "Lärmschutz-Anlagen",
                    },
                    "3900": {
                        "name": "AbwasserRegenwasser",
                        "description": "Anlagen für Abwasser oder Regenwasser",
                    },
                    "4000": {
                        "name": "Ausgleichsmassnahmen",
                        "description": "Fläche für Ausgleichsmaßnahmen",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Zweckbestimmung",
                    },
                    "4100": {
                        "name": "Fahrradstellplaetze",
                        "description": "Fahrrad Stellplätze",
                    },
                    "4200": {
                        "name": "Gemeinschaftsdachgaerten",
                        "description": "Gemeinschaftlich genutzter Dachgarten",
                    },
                    "4300": {
                        "name": "GemeinschaftlichNutzbareDachflaechen",
                        "description": "Gemeinschaftlich nutzbare Dachflächen.",
                    },
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codelist definierte detailliertere Festlegung der Zweckbestimmung. Der an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestGemeinschaftsanlagen",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximale Anzahl von Garagen-Geschossen",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    eigentuemer: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Relation auf die Baugebietsfläche, zu der die Gemeinschaftsanlagen-Fläche gehört.",
            json_schema_extra={
                "typename": "BP_BaugebietsTeilFlaeche",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPGemeinschaftsanlagenZuordnung(BPGeometrieobjekt):
    """
    Zuordnung von Gemeinschaftsanlagen zu Grundstücken.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zuordnung: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Relation auf die zugeordneten Gemeinschaftsanlagen-Flächen, die außerhalb des Baugebiets liegen.",
            json_schema_extra={
                "typename": "BP_GemeinschaftsanlagenFlaeche",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPGenerischesObjekt(BPGeometrieobjekt):
    """
    Klasse zur Modellierung aller Inhalte des Bebauungsplans,die durch keine andere spezifische XPlanung Klasse repräsentiert werden können.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description="Über eine CodeList definierte Zweckbestimmung des Objektes.",
            json_schema_extra={
                "typename": "BP_ZweckbestimmungGenerischeObjekte",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPNebenanlagenAusschlussFlaeche(BPUeberlagerungsobjekt):
    """
    Festsetzung einer Fläche für die Einschränkung oder den Ausschluss von Nebenanlagen nach §14 Absatz 1 Satz 3 BauNVO.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Art des Ausschlusses.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Einschraenkung",
                        "description": "Die Errichtung bestimmter Nebenanlagen ist eingeschränkt.",
                    },
                    "2000": {
                        "name": "Ausschluss",
                        "description": "Die Errichtung bestimmter Nebenanlagen ist ausgeschlossen.",
                    },
                },
                "typename": "BP_NebenanlagenAusschlussTyp",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    abweichungText: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Textliche Beschreibung der Einschränkung oder des Ausschlusses.",
            json_schema_extra={
                "typename": "BP_TextAbschnitt",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPNebenanlagenFlaeche(BPUeberlagerungsobjekt):
    """
    Fläche für Nebenanlagen, die auf Grund anderer Vorschriften für die Nutzung von Grundstücken erforderlich sind, wie Spiel-, Freizeit- und Erholungsflächen sowie die Fläche für Stellplätze und Garagen mit ihren Einfahrten (§9 Abs. 1 Nr. 4 BauGB)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "3600",
                "3700",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Nebenanlagen-Fläche",
            json_schema_extra={
                "typename": "BP_ZweckbestimmungNebenanlagen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Stellplaetze", "description": "Stellplätze"},
                    "2000": {"name": "Garagen", "description": "Garagen"},
                    "3000": {"name": "Spielplatz", "description": "Spielplatz"},
                    "3100": {"name": "Carport", "description": "Carport"},
                    "3200": {"name": "Tiefgarage", "description": "Tiefgarage"},
                    "3300": {"name": "Nebengebaeude", "description": "Nebengebäude"},
                    "3400": {
                        "name": "AbfallSammelanlagen",
                        "description": "Sammelanlagen für Abfall.",
                    },
                    "3500": {
                        "name": "EnergieVerteilungsanlagen",
                        "description": "Energie-Verteilungsanlagen",
                    },
                    "3600": {
                        "name": "AbfallWertstoffbehaelter",
                        "description": "Abfall-Wertstoffbehälter",
                    },
                    "3700": {
                        "name": "Fahrradstellplaetze",
                        "description": "Fahrrad Stellplätze",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Zweckbestimmung",
                    },
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine CodeList definierte detailliertere Festlegung der Zweckbestimmung. \r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "BP_DetailZweckbestNebenanlagen",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximale Anzahl der Garagengeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPNichtUeberbaubareGrundstuecksflaeche(BPUeberlagerungsobjekt):
    """
    Festlegung der nicht-überbaubaren Grundstücksfläche
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    nutzung: Annotated[
        AnyUrl | None,
        Field(
            description="Zulässige Nutzung der Fläche",
            json_schema_extra={
                "typename": "BP_NutzungNichUueberbaubGrundstFlaeche",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPPersGruppenBestimmteFlaeche(BPUeberlagerungsobjekt):
    """
    Fläche, auf denen ganz oder teilweise nur Wohngebäude errichtet werden dürfen, die für Personengruppen mit besonderem Wohnbedarf bestimmt sind (§9, Abs. 1, Nr. 8 BauGB)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPRegelungVergnuegungsstaetten(BPUeberlagerungsobjekt):
    """
    Festsetzung nach §9 Abs. 2b BauGB (Zulässigkeit von Vergnügungsstätten).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zulaessigkeit: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Zulässigkeit von Vergnügungsstätten.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Zulaessig",
                        "description": "Generelle Zulässigkeit",
                    },
                    "2000": {
                        "name": "NichtZulaessig",
                        "description": "Generelle Nicht-Zulässigkeit.",
                    },
                    "3000": {
                        "name": "AusnahmsweiseZulaessig",
                        "description": "Ausnahmsweise Zulässigkeit",
                    },
                },
                "typename": "BP_Zulaessigkeit",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPSichtflaeche(BPUeberlagerungsobjekt):
    """
    Flächenhafte Festlegung einer Sichtfläche bzw. eines Sichtdreiecks

    In Version 6.0 wird diese Klasse evtl. in der Modellbereich "Sonstige Planwerke" transferiert.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    art: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description='Klassifikation der Einmündung einer untergeordneten auf eine übergeordnete Straße gemäß den "Richtlinien für die Anlage von Stadtstraßen" (TAST 06)',
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Haltesichtweite",
                        "description": "Haltesichtweite",
                    },
                    "2000": {
                        "name": "Anfahrsichtfeld",
                        "description": "Anfahrsichtfeld",
                    },
                    "3000": {
                        "name": "Annaeherungssichtfeld",
                        "description": "Annäherungssichtfeld",
                    },
                    "4000": {
                        "name": "Ueberquerung",
                        "description": "Sichtfeld an Überquerungsstellen",
                    },
                    "9999": {
                        "name": "SonstigeSichtflaeche",
                        "description": "Sonstige Sichtfläche",
                    },
                },
                "typename": "BP_SichtflaecheArt",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    knotenpunkt: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "6000", "9999"] | None,
        Field(
            description="Klassifikation des Knotenpunktes, dem die Sichtfläche zugeordnet ist",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "AnlgStr-AnlgWeg",
                        "description": "Knotenpunkt Anliegerstraße - Anliegerweg",
                    },
                    "2000": {
                        "name": "AnlgStr-AnlgStr",
                        "description": "Knotenpunkt Anliegerstraße - Anliegerstraße",
                    },
                    "3000": {
                        "name": "SammelStr-AnlgStr",
                        "description": "Knotenpunkt Sammelstraße - Anliegerstraße",
                    },
                    "4000": {
                        "name": "HauptSammelStr",
                        "description": "Knotenpunkt mit einer Haupt-Sammelstraße",
                    },
                    "5000": {
                        "name": "HauptVerkStrAngeb",
                        "description": "Knotenpunkt mit einer angebaute Hauptverkehrsstraße (Bebauung parallel zur Straße ist vorhanden)",
                    },
                    "6000": {
                        "name": "HauptVerkStrNichtAngeb",
                        "description": "Knotenpunkt mit einer nicht angebaute Hauptverkehrsstraße (Keine Bebauung parallel zur Straße )",
                    },
                    "9999": {
                        "name": "SonstigerKnotenpunkt",
                        "description": "Sonstiger Knotenpunkt",
                    },
                },
                "typename": "BP_SichtflaecheKnotenpunktTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    geschwindigkeit: Annotated[
        definitions.GenericMeasure | None,
        Field(
            description="Zulässige Geschwindigkeit in der übergeordneten Straße, im km/h",
            json_schema_extra={
                "typename": "Measure",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "kmh",
            },
        ),
    ] = None
    schenkellaenge: Annotated[
        definitions.Length | None,
        Field(
            description="Schenkellänge des Sichtdreiecks gemäß RAST 06",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None


class BPSpezielleBauweise(BPUeberlagerungsobjekt):
    """
    Festsetzung der speziellen Bauweise / baulichen Besonderheit eines Gebäudes oder Bauwerks.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "1300",
            "1400",
            "1500",
            "1600",
            "1700",
            "1800",
            "9999",
        ]
        | None,
        Field(
            description="Typ der speziellen Bauweise.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Durchfahrt", "description": "Durchfahrt"},
                    "1100": {"name": "Durchgang", "description": "Durchgang"},
                    "1200": {
                        "name": "DurchfahrtDurchgang",
                        "description": "Durchfahrt oder Durchgang",
                    },
                    "1300": {"name": "Auskragung", "description": "Auskragung"},
                    "1400": {"name": "Arkade", "description": "Arkade"},
                    "1500": {"name": "Luftgeschoss", "description": "Luftgeschoss"},
                    "1600": {"name": "Bruecke", "description": "Brücke"},
                    "1700": {"name": "Tunnel", "description": "Tunnel"},
                    "1800": {"name": "Rampe", "description": "Rampe"},
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige spezielle Bauweise.",
                    },
                },
                "typename": "BP_SpezielleBauweiseTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter Typ der speziellen Bauweise, wenn typ den Wert 9999 (Sonstiges) hat.",
            json_schema_extra={
                "typename": "BP_SpezielleBauweiseSonstTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    wegerecht: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Relation auf Angaben zu Wegerechten.",
            json_schema_extra={
                "typename": "BP_Wegerecht",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class BPTechnischeMassnahmenFlaeche(BPUeberlagerungsobjekt):
    """
    Fläche für technische oder bauliche Maßnahmen nach § 9, Abs. 1, Nr. 23 BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        Literal["1000", "2000", "3000"],
        Field(
            description="Klassifikation der durchzuführenden Maßnahmen nach §9, Abs. 1, Nr. 23 BauGB.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Luftreinhaltung",
                        "description": "Gebiete, in denen zum Schutz vor schädlichen Umwelteinwirkungen im Sinne des Bundes-Immissionsschutzgesetzes bestimmte Luft-verunreinigende Stoffe nicht oder nur beschränkt verwendet werden dürfen (§9, Abs. 1, Nr. 23a BauGB).",
                    },
                    "2000": {
                        "name": "NutzungErneurerbarerEnergien",
                        "description": "Gebiete in denen bei der Errichtung von Gebäuden bestimmte bauliche Maßnahmen für den Einsatz erneuerbarer Energien wie insbesondere Solarenergie getroffen werden müssen (§9, Abs. 1, Nr. 23b BauGB).",
                    },
                    "3000": {
                        "name": "MinderungStoerfallfolgen",
                        "description": "Gebiete, in denen bei der Errichtung von nach Art, Maß oder Nutzungsintensität zu bestimmenden Gebäuden oder sonstigen baulichen Anlagen in der Nachbarschaft von Betriebsbereichen nach § 3 Absatz 5a des Bundes-Immissionsschutzgesetzes bestimmte bauliche und sonstige technische Maßnahmen, die der Vermeidung oder Minderung der Folgen von Störfällen dienen, getroffen werden müssen (§9, Abs. 1, Nr. 23c BauGB).",
                    },
                },
                "typename": "BP_ZweckbestimmungenTMF",
                "stereotype": "Enumeration",
                "multiplicity": "1",
            },
        ),
    ]
    technischeMassnahme: Annotated[
        str | None,
        Field(
            description="Beschreibung der Maßnahme",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class BPTextlicheFestsetzungsFlaeche(BPUeberlagerungsobjekt):
    """
    Bereich, in dem bestimmte Textliche Festsetzungen gültig sind, die über die Relation "refTextInhalt" (Basisklasse BP_Objekt) spezifiziert werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class BPUeberbaubareGrundstuecksFlaeche(BPUeberlagerungsobjekt):
    """
    Festsetzung der überbaubaren Grundstücksfläche (§9, Abs. 1, Nr. 2 BauGB). Über die Attribute geschossMin und geschossMax kann die Festsetzung auf einen Bereich von Geschossen beschränkt werden. Wenn eine Einschränkung der Festsetzung durch expliziter Höhenangaben erfolgen soll, ist dazu die Oberklassen-Relation hoehenangabe auf den komplexen Datentyp XP_Hoehenangabe zu verwenden.

    Die gleichzeitige Belegung desselben Attributs in BP_BaugebietsTeilFlaeche und einem überlagernden Objekt BP_UeberbaubareGrunsdstuecksFlaeche sollte verzichtet werden.  Ab Version 6.0 wird dies evtl. durch eine Konformitätsregel erzwungen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    dachgestaltung: Annotated[
        list[BPDachgestaltung] | None,
        Field(
            description="Parameter zur Einschränkung der zulässigen Dachformen.",
            json_schema_extra={
                "typename": "BP_Dachgestaltung",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    DNmin: Annotated[
        definitions.Angle | None,
        Field(
            description="Minimal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNmax: Annotated[
        definitions.Angle | None,
        Field(
            description="Maxmal zulässige Dachneigung bei einer Bereichsangabe.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DN: Annotated[
        definitions.Angle | None,
        Field(
            description="Maximal zulässige Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    DNZwingend: Annotated[
        definitions.Angle | None,
        Field(
            description="Zwingend vorgeschriebene Dachneigung.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    FR: Annotated[
        definitions.Angle | None,
        Field(
            description="Vorgeschriebene Firstrichtung",
            json_schema_extra={
                "typename": "Angle",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "grad",
            },
        ),
    ] = None
    dachform: Annotated[
        list[
            Literal[
                "1000",
                "2100",
                "2200",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "3600",
                "3700",
                "3800",
                "3900",
                "4000",
                "4100",
                "5000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Erlaubte Dachformen.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.",
            json_schema_extra={
                "typename": "BP_Dachform",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Flachdach",
                        "description": "Flachdach\r\nEmpfohlene Abkürzung: FD",
                    },
                    "2100": {
                        "name": "Pultdach",
                        "description": "Pultdach\r\nEmpfohlene Abkürzung: PD",
                    },
                    "2200": {
                        "name": "VersetztesPultdach",
                        "description": "Versetztes Pultdach\r\nEmpfohlene Abkürzung: VPD",
                    },
                    "3000": {
                        "name": "GeneigtesDach",
                        "description": "Kein Flachdach\r\nEmpfohlene Abkürzung: GD",
                    },
                    "3100": {
                        "name": "Satteldach",
                        "description": "Satteldach\r\nEmpfohlene Abkürzung: SD",
                    },
                    "3200": {
                        "name": "Walmdach",
                        "description": "Walmdach\r\nEmpfohlene Abkürzung: WD",
                    },
                    "3300": {
                        "name": "Krueppelwalmdach",
                        "description": "Krüppelwalmdach\r\nEmpfohlene Abkürzung: KWD",
                    },
                    "3400": {
                        "name": "Mansarddach",
                        "description": "Mansardendach\r\nEmpfohlene Abkürzung: MD",
                    },
                    "3500": {
                        "name": "Zeltdach",
                        "description": "Zeltdach\r\nEmpfohlene Abkürzung: ZD",
                    },
                    "3600": {
                        "name": "Kegeldach",
                        "description": "Kegeldach\r\nEmpfohlene Abkürzung: KeD",
                    },
                    "3700": {
                        "name": "Kuppeldach",
                        "description": "Kuppeldach\r\nEmpfohlene Abkürzung: KuD",
                    },
                    "3800": {
                        "name": "Sheddach",
                        "description": "Sheddach\r\nEmpfohlene Abkürzung: ShD",
                    },
                    "3900": {
                        "name": "Bogendach",
                        "description": "Bogendach\r\nEmpfohlene Abkürzung: BD",
                    },
                    "4000": {
                        "name": "Turmdach",
                        "description": "Turmdach\r\nEmpfohlene Abkürzung: TuD",
                    },
                    "4100": {
                        "name": "Tonnendach",
                        "description": "Tonnendach\r\nEmpfohlene Abkürzung: ToD",
                    },
                    "5000": {
                        "name": "Mischform",
                        "description": "Gemischte Dachform\r\nEmpfohlene Abkürzung: GDF",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Dachform\r\nEmpfohlene Abkürzung: SDF",
                    },
                },
            },
        ),
    ] = None
    detaillierteDachform: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definiertere detailliertere Dachform.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteDachform" bezieht sich auf den an gleicher Position stehenden Attributwert von dachform.\r\n\r\nDies Attribut ist veraltet und wird in Version 6.0 wegfallen. Es sollte stattdessen der Datentyp BP_Dachgestaltung (Attribut dachgestaltung) verwendet werden.',
            json_schema_extra={
                "typename": "BP_DetailDachform",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    MaxZahlWohnungen: Annotated[
        int | None,
        Field(
            description="Höchstzulässige Zahl der Wohnungen in Wohngebäuden",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    MinGRWohneinheit: Annotated[
        definitions.Area | None,
        Field(
            description="Minimale Größe eines Grundstücks pro Wohneinheit",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmin: Annotated[
        definitions.Area | None,
        Field(
            description="Mindestmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Fmax: Annotated[
        definitions.Area | None,
        Field(
            description="Höchstmaß für die Größe (Fläche) eines Baugrundstücks.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Bmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Breite von Baugrundstücken",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Bmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Breite von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmin: Annotated[
        definitions.Length | None,
        Field(
            description="Minimale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    Tmax: Annotated[
        definitions.Length | None,
        Field(
            description="Maximale Tiefe von Baugrundstücken.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Geschossflächenzahl .",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl bei einer Bereichsangabe. Das Attribut GFZmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZ_Ausn: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Geschossflächenzahl als Ausnahme.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Geschossfläche",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche bei einer Bereichsabgabe. Das Attribut GFmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GF_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Geschossfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumassenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BM: Annotated[
        definitions.Volume | None,
        Field(
            description="Maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    BM_Ausn: Annotated[
        definitions.Volume | None,
        Field(
            description="Ausnahmsweise maximal zulässige Baumasse.",
            json_schema_extra={
                "typename": "Volume",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m3",
            },
        ),
    ] = None
    GRZmin: Annotated[
        float | None,
        Field(
            description="Minimal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZmax: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl bei einer Bereichsangabe.  Das Attribut GRZmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Maximal zulässige Grundflächenzahl",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ_Ausn: Annotated[
        float | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundflächenzahl.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRmin: Annotated[
        definitions.Area | None,
        Field(
            description="Minimal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GRmax: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche bei einer Bereichsangabe. Das Attribut GRmin muss ebenfalls spezifiziert werden.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR: Annotated[
        definitions.Area | None,
        Field(
            description="Maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GR_Ausn: Annotated[
        definitions.Area | None,
        Field(
            description="Ausnahmsweise maximal zulässige Grundfläche.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    Zmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der oberirdischen Vollgeschosse bei einer Bereichsangabe. Das Attribut Zmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Zzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z: Annotated[
        int | None,
        Field(
            description="Maximalzahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der oberirdischen Vollgeschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Staffel: Annotated[
        int | None,
        Field(
            description="Maximalzahl von oberirdischen zurückgesetzten Vollgeschossen als Staffelgeschoss..",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    Z_Dach: Annotated[
        int | None,
        Field(
            description="Maximalzahl der zusätzlich erlaubten Dachgeschosse, die gleichzeitig Vollgeschosse sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmin: Annotated[
        int | None,
        Field(
            description="Minimal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUmax: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse bei einer Bereichsangabe. Das Attribut ZUmin muss ebenfalls belegt sein.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZUzwingend: Annotated[
        int | None,
        Field(
            description="Zwingend vorgeschriebene Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU: Annotated[
        int | None,
        Field(
            description="Maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZU_Ausn: Annotated[
        int | None,
        Field(
            description="Ausnahmsweise maximal zulässige Zahl der unterirdischen Geschosse.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    wohnnutzungEGStrasse: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung nach §6a Abs. (4) Nr. 1 BauNVO: Für urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass in Gebäuden \r\nim Erdgeschoss an der Straßenseite eine Wohnnutzung nicht oder nur ausnahmsweise zulässig ist.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Zulaessig",
                        "description": "Generelle Zulässigkeit",
                    },
                    "2000": {
                        "name": "NichtZulaessig",
                        "description": "Generelle Nicht-Zulässigkeit.",
                    },
                    "3000": {
                        "name": "AusnahmsweiseZulaessig",
                        "description": "Ausnahmsweise Zulässigkeit",
                    },
                },
                "typename": "BP_Zulaessigkeit",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    ZWohn: Annotated[
        int | None,
        Field(
            description="Festsetzung nach §4a Abs. (4) Nr. 1 bzw. nach  §6a Abs. (4) Nr. 2 BauNVO: Für besondere Wohngebiete und  urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass in Gebäuden oberhalb eines im Bebauungsplan bestimmten Geschosses nur Wohnungen zulässig sind.",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFAntWohnen: Annotated[
        definitions.Scale | None,
        Field(
            description="Festsetzung nach §4a Abs. (4) Nr. 2 bzw. §6a Abs. (4) Nr. 3 BauNVO: Für besondere Wohngebiete und urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden ein im Bebauungsplan bestimmter Anteil der zulässigen \r\nGeschossfläche für Wohnungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Scale",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "vH",
            },
        ),
    ] = None
    GFWohnen: Annotated[
        definitions.Area | None,
        Field(
            description="Festsetzung nach §4a Abs. (4) Nr. 2 bzw. §6a Abs. (4) Nr. 3 BauNVO: Für besondere Wohngebiete und urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden eine im Bebauungsplan bestimmte Größe der Geschossfläche für Wohnungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    GFAntGewerbe: Annotated[
        definitions.Scale | None,
        Field(
            description="Festsetzung nach §6a Abs. (4) Nr. 4 BauNVO: Für urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden ein im Bebauungsplan bestimmter Anteil der zulässigen \r\nGeschossfläche für gewerbliche Nutzungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Scale",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "vH",
            },
        ),
    ] = None
    GFGewerbe: Annotated[
        definitions.Area | None,
        Field(
            description="Festsetzung nach §6a Abs. (4) Nr. 4 BauNVO: Für urbane Gebiete oder Teile solcher Gebiete kann festgesetzt werden, dass \r\nin Gebäuden eine im Bebauungsplan bestimmte Größe der Geschossfläche für gewerbliche Nutzungen zu verwenden ist.",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    VF: Annotated[
        definitions.Area | None,
        Field(
            description="Festsetzung der maximal zulässigen Verkaufsfläche in einem Sondergebiet",
            json_schema_extra={
                "typename": "Area",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m2",
            },
        ),
    ] = None
    bauweise: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bauweise  (§9, Abs. 1, Nr. 2 BauGB).\r\nDieser Wert hat Priorität gegenüber einer im umschließenden Baugebiet (BP_BaugebietsTeilFlaeche) getroffenen Festsetzung",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "OffeneBauweise",
                        "description": "Offene Bauweise",
                    },
                    "2000": {
                        "name": "GeschlosseneBauweise",
                        "description": "Geschlossene Bauweise",
                    },
                    "3000": {
                        "name": "AbweichendeBauweise",
                        "description": "Abweichende Bauweise",
                    },
                },
                "typename": "BP_Bauweise",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    abweichendeBauweise: Annotated[
        AnyUrl | None,
        Field(
            description='Nähere Bezeichnung einer "Abweichenden Bauweise" ("bauweise == 3000").\r\nDieser Wert hat Priorität gegenüber einer im umschließenden Baugebiet (BP_BaugebietsTeilFlaeche) getroffenen Festsetzung',
            json_schema_extra={
                "typename": "BP_AbweichendeBauweise",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    vertikaleDifferenzierung: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob eine vertikale Differenzierung der Gebäude vorgeschrieben ist.\r\nDieser Wert hat Priorität gegenüber einer im umschließenden Baugebiet (BP_BaugebietsTeilFlaeche) getroffenen Festsetzung.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    bebauungsArt: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "6000", "7000", "8000"] | None,
        Field(
            description="Detaillierte Festsetzung der Bauweise (§9, Abs. 1, Nr. 2 BauGB).\r\nDieser Wert hat Priorität gegenüber einer im umschließenden Baugebiet (BP_BaugebietsTeilFlaeche) getroffenen Festsetzung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Einzelhaeuser",
                        "description": "Nur Einzelhäuser zulässig.",
                    },
                    "2000": {
                        "name": "Doppelhaeuser",
                        "description": "Nur Doppelhäuser zulässig.",
                    },
                    "3000": {
                        "name": "Hausgruppen",
                        "description": "Nur Hausgruppen zulässig.",
                    },
                    "4000": {
                        "name": "EinzelDoppelhaeuser",
                        "description": "Nur Einzel- oder Doppelhäuser zulässig.",
                    },
                    "5000": {
                        "name": "EinzelhaeuserHausgruppen",
                        "description": "Nur Einzelhäuser oder Hausgruppen zulässig.",
                    },
                    "6000": {
                        "name": "DoppelhaeuserHausgruppen",
                        "description": "Nur Doppelhäuser oder Hausgruppen zulässig.",
                    },
                    "7000": {
                        "name": "Reihenhaeuser",
                        "description": "Nur Reihenhäuser zulässig.",
                    },
                    "8000": {
                        "name": "EinzelhaeuserDoppelhaeuserHausgruppen",
                        "description": "Es sind Einzelhäuser, Doppelhäuser und Hausgruppen zulässig.",
                    },
                },
                "typename": "BP_BebauungsArt",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungVordereGrenze: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bebauung der vorderen Grundstücksgrenze (§9, Abs. 1, Nr. 2 BauGB).\r\nDieser Wert hat Priorität gegenüber einer im umschließenden Baugebiet (BP_BaugebietsTeilFlaeche) getroffenen Festsetzung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Verboten",
                        "description": "Eine Bebauung der Grenze ist verboten.",
                    },
                    "2000": {
                        "name": "Erlaubt",
                        "description": "Eine Bebauung der Grenze ist erlaubt.",
                    },
                    "3000": {
                        "name": "Erzwungen",
                        "description": "Eine Bebauung der Grenze ist vorgeschrieben.",
                    },
                },
                "typename": "BP_GrenzBebauung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungRueckwaertigeGrenze: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bebauung der rückwärtigen Grundstücksgrenze (§9, Abs. 1, Nr. 2 BauGB).\r\nDieser Wert hat Priorität gegenüber einer im umschließenden Baugebiet (BP_BaugebietsTeilFlaeche) getroffenen Festsetzung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Verboten",
                        "description": "Eine Bebauung der Grenze ist verboten.",
                    },
                    "2000": {
                        "name": "Erlaubt",
                        "description": "Eine Bebauung der Grenze ist erlaubt.",
                    },
                    "3000": {
                        "name": "Erzwungen",
                        "description": "Eine Bebauung der Grenze ist vorgeschrieben.",
                    },
                },
                "typename": "BP_GrenzBebauung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bebauungSeitlicheGrenze: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Festsetzung der Bebauung der seitlichen Grundstücksgrenze (§9, Abs. 1, Nr. 2 BauGB).\r\nDieser Wert hat Priorität gegenüber einer im umschließenden Baugebiet (BP_BaugebietsTeilFlaeche) getroffenen Festsetzung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Verboten",
                        "description": "Eine Bebauung der Grenze ist verboten.",
                    },
                    "2000": {
                        "name": "Erlaubt",
                        "description": "Eine Bebauung der Grenze ist erlaubt.",
                    },
                    "3000": {
                        "name": "Erzwungen",
                        "description": "Eine Bebauung der Grenze ist vorgeschrieben.",
                    },
                },
                "typename": "BP_GrenzBebauung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refGebaeudequerschnitt: Annotated[
        list[XPExterneReferenz] | None,
        Field(
            description="Referenz auf ein Dokument mit vorgeschriebenen Gebäudequerschnitten.\r\nDieser Wert hat Priorität gegenüber einer im umschließenden Baugebiet (BP_BaugebietsTeilFlaeche) getroffenen Festsetzung.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    baugrenze: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf eine Baugrenze, die auf der Randkurve der Fläche verläuft.",
            json_schema_extra={
                "typename": "BP_BauGrenze",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    baulinie: Annotated[
        list[AnyUrl | UUID] | None,
        Field(
            description="Referenz auf eine Bauliniedie auf der Randkurve der Fläche verläuft.",
            json_schema_extra={
                "typename": "BP_BauLinie",
                "stereotype": "Association",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    geschossMin: Annotated[
        int | None,
        Field(
            description='Gibt bei geschossweiser Festsetzung die Nummer des Geschosses an, ab den die Festsetzung gilt. Wenn das Attribut nicht belegt ist, gilt die Festsetzung für alle Geschosse bis einschl. "geschossMax".',
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    geschossMax: Annotated[
        int | None,
        Field(
            description='Gibt bei geschossweiser Festsetzung die Nummer des Geschosses an, bis zu der die Festsetzung gilt. Wenn das Attribut nicht belegt ist, gilt die Festsetzung für alle Geschosse ab einschl. "geschossMin".',
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPAbgrabung(FPGeometrieobjekt):
    """
    Flächen für Aufschüttungen, Abgrabungen oder für die Gewinnung von Bodenschätzen (§5, Abs. 2, Nr. 8 BauGB). Hier: Flächen für Abgrabungen und die Gewinnung von Bodenschätzen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    abbaugut: Annotated[
        str | None,
        Field(
            description="Bezeichnung des Abbauguts.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPAnpassungKlimawandel(FPGeometrieobjekt):
    """
    Anlagen, Einrichtungen und sonstige Maßnahmen, die der Anpassung an den Klimawandel dienen nach §5 Abs.2 Nr.2c BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    massnahme: Annotated[
        Literal["1000", "10000", "10001", "9999"] | None,
        Field(
            description="Klassifikation der Massnahme",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "ErhaltFreiflaechen",
                        "description": "Erhalt vegetationsbestandener Freiflächen",
                    },
                    "10000": {
                        "name": "ErhaltPrivGruen",
                        "description": "Erhalt privater Grünflächen",
                    },
                    "10001": {
                        "name": "ErhaltOeffentlGruen",
                        "description": "Erhalt öffentlicher Grünflächen",
                    },
                    "9999": {
                        "name": "SonstMassnahme",
                        "description": "Sonstige Massnahme",
                    },
                },
                "typename": "FP_MassnahmeKlimawandelTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailMassnahme: Annotated[
        AnyUrl | None,
        Field(
            description="Detaillierung der durch das Attribut massnahme festgelegten Maßnahme über eine Codeliste.",
            json_schema_extra={
                "typename": "FP_DetailMassnahmeKlimawandel",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPAufschuettung(FPGeometrieobjekt):
    """
    Flächen für Aufschüttungen, Abgrabungen oder für die Gewinnung von Bodenschätzen (§5, Abs. 2, Nr. 8 BauGB). Hier: Flächen für Aufschüttungen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    aufschuettungsmaterial: Annotated[
        str | None,
        Field(
            description="Bezeichnung des aufgeschütteten Materials",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPAusgleichsFlaeche(FPFlaechenobjekt):
    """
    Flächen und Maßnahmen zum Ausgleich gemäß § 5, Abs. 2a  BauBG.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der auf der Fläche durchzuführenden Maßnahmen.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstZiel: Annotated[
        str | None,
        Field(
            description="Textlich formuliertes Ziel, wenn das Attribut ziel den Wert 9999 (Sonstiges) hat.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahme: Annotated[
        list[XPSPEMassnahmenDaten] | None,
        Field(
            description="Auf der Fläche durchzuführende Maßnahme.",
            json_schema_extra={
                "typename": "XP_SPEMassnahmenDaten",
                "stereotype": "DataType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    refMassnahmenText: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf ein Dokument in dem die Massnahmen beschrieben werden.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    refLandschaftsplan: Annotated[
        XPExterneReferenz | None,
        Field(
            description="Referenz auf den Landschaftsplan.",
            json_schema_extra={
                "typename": "XP_ExterneReferenz",
                "stereotype": "DataType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPBebauungsFlaeche(FPFlaechenschlussobjekt):
    """
    Darstellung einer für die Bebauung vorgesehenen Fläche (§ 5, Abs. 2, Nr. 1 BauGB).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    GFZ: Annotated[
        float | None,
        Field(
            description="Angabe einer maximalen Geschossflächenzahl als Maß der baulichen Nutzung.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmin: Annotated[
        float | None,
        Field(
            description="Minimale Geschossflächenzahl bei einer Bereichsangabe (GFZmax muss ebenfalls spezifiziert werden).",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GFZmax: Annotated[
        float | None,
        Field(
            description="Maximale Geschossflächenzahl bei einer Bereichsangabe (GFZmin muss ebenfalls spezifiziert werden).",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    BMZ: Annotated[
        float | None,
        Field(
            description="Angabe einer maximalen Baumassenzahl als Maß der baulichen Nutzung.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    GRZ: Annotated[
        float | None,
        Field(
            description="Angabe einer maximalen Grundflächenzahl als Maß der baulichen Nutzung.",
            json_schema_extra={
                "typename": "Decimal",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    allgArtDerBaulNutzung: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Angabe der allgemeinen Art der baulichen Nutzung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "WohnBauflaeche",
                        "description": "Wohnbaufläche nach §1 Abs. (1) BauNVO",
                    },
                    "2000": {
                        "name": "GemischteBauflaeche",
                        "description": "Gemischte Baufläche nach §1 Abs. (1) BauNVO.",
                    },
                    "3000": {
                        "name": "GewerblicheBauflaeche",
                        "description": "Gewerbliche Baufläche nach §1 Abs. (1) BauNVO.",
                    },
                    "4000": {
                        "name": "SonderBauflaeche",
                        "description": "Sonderbaufläche nach §1 Abs. (1) BauNVO.",
                    },
                    "9999": {
                        "name": "SonstigeBauflaeche",
                        "description": "Sonstige Baufläche",
                    },
                },
                "typename": "XP_AllgArtDerBaulNutzung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    besondereArtDerBaulNutzung: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "1300",
            "1400",
            "1450",
            "1500",
            "1550",
            "1600",
            "1700",
            "1800",
            "2000",
            "2100",
            "3000",
            "4000",
            "9999",
        ]
        | None,
        Field(
            description="Angabe der besonderen Art der baulichen Nutzung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Kleinsiedlungsgebiet",
                        "description": "Kleinsiedlungsgebiet nach § 2 BauNVO.",
                    },
                    "1100": {
                        "name": "ReinesWohngebiet",
                        "description": "Reines Wohngebiet nach § 3 BauNVO.",
                    },
                    "1200": {
                        "name": "AllgWohngebiet",
                        "description": "Allgemeines Wohngebiet nach § 4 BauNVO.",
                    },
                    "1300": {
                        "name": "BesonderesWohngebiet",
                        "description": "Gebiet zur Erhaltung und Entwicklung der Wohnnutzung (Besonderes Wohngebiet) nach § 4a BauNVO.",
                    },
                    "1400": {
                        "name": "Dorfgebiet",
                        "description": "Dorfgebiet nach $ 5 BauNVO.",
                    },
                    "1450": {
                        "name": "DoerflichesWohngebiet",
                        "description": "Dörfliches Wohngebiet nach §5a BauNVO",
                    },
                    "1500": {
                        "name": "Mischgebiet",
                        "description": "Mischgebiet nach $ 6 BauNVO.",
                    },
                    "1550": {
                        "name": "UrbanesGebiet",
                        "description": "Urbanes Gebiet nach § 6a BauNVO",
                    },
                    "1600": {
                        "name": "Kerngebiet",
                        "description": "Kerngebiet nach § 7 BauNVO.",
                    },
                    "1700": {
                        "name": "Gewerbegebiet",
                        "description": "Gewerbegebiet nach § 8 BauNVO.",
                    },
                    "1800": {
                        "name": "Industriegebiet",
                        "description": "Industriegebiet nach § 9 BauNVO.",
                    },
                    "2000": {
                        "name": "SondergebietErholung",
                        "description": "Sondergebiet, das der Erholung dient nach § 10 BauNVO von 1977 und 1990.",
                    },
                    "2100": {
                        "name": "SondergebietSonst",
                        "description": "Sonstiges Sondergebiet nach§ 11 BauNVO 1977 und 1990; z.B. Klinikgebiet",
                    },
                    "3000": {
                        "name": "Wochenendhausgebiet",
                        "description": "Wochenendhausgebiet nach §10 der BauNVO von 1962 und 1968",
                    },
                    "4000": {
                        "name": "Sondergebiet",
                        "description": "Sondergebiet nach §11der BauNVO von 1962 und 1968",
                    },
                    "9999": {
                        "name": "SonstigesGebiet",
                        "description": "Sonstiges Gebiet",
                    },
                },
                "typename": "XP_BesondereArtDerBaulNutzung",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonderNutzung: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "1300",
                "1400",
                "1500",
                "1600",
                "16000",
                "16001",
                "16002",
                "1700",
                "1800",
                "1900",
                "2000",
                "2100",
                "2200",
                "2300",
                "23000",
                "2400",
                "2500",
                "2600",
                "2700",
                "2720",
                "2800",
                "2900",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Differenziert Sondernutzungen nach §10 und §11 der BauNVO von 1977 und 1990. Das Attribut wird nur benutzt, wenn besondereArtDerBaulNutzung unbelegt ist oder einen der Werte 2000 bzw. 2100 hat",
            json_schema_extra={
                "typename": "XP_Sondernutzungen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Wochenendhausgebiet",
                        "description": "Wochenendhausgebiet",
                    },
                    "1100": {
                        "name": "Ferienhausgebiet",
                        "description": "Ferienhausgebiet",
                    },
                    "1200": {
                        "name": "Campingplatzgebiet",
                        "description": "Campingplatzgebiet",
                    },
                    "1300": {"name": "Kurgebiet", "description": "Kurgebiet"},
                    "1400": {
                        "name": "SonstSondergebietErholung",
                        "description": "Sonstiges Sondergebiet für Erholung",
                    },
                    "1500": {
                        "name": "Einzelhandelsgebiet",
                        "description": "Einzelhandelsgebiet",
                    },
                    "1600": {
                        "name": "GrossflaechigerEinzelhandel",
                        "description": "Gebiet für großflächigen Einzelhandel",
                    },
                    "16000": {"name": "Ladengebiet", "description": "Ladengebiet"},
                    "16001": {
                        "name": "Einkaufszentrum",
                        "description": "Einkaufszentrum",
                    },
                    "16002": {
                        "name": "SonstGrossflEinzelhandel",
                        "description": "Sonstiges Gebiet für großflächigen Einzelhandel",
                    },
                    "1700": {
                        "name": "Verkehrsuebungsplatz",
                        "description": "Verkehrsübungsplatz",
                    },
                    "1800": {"name": "Hafengebiet", "description": "Hafengebiet"},
                    "1900": {
                        "name": "SondergebietErneuerbareEnergie",
                        "description": "Sondergebiet für Erneuerbare Energien",
                    },
                    "2000": {
                        "name": "SondergebietMilitaer",
                        "description": "Militärisches Sondergebiet",
                    },
                    "2100": {
                        "name": "SondergebietLandwirtschaft",
                        "description": "Sondergebiet Landwirtschaft",
                    },
                    "2200": {
                        "name": "SondergebietSport",
                        "description": "Sondergebiet Sport",
                    },
                    "2300": {
                        "name": "SondergebietGesundheitSoziales",
                        "description": "Sondergebiet für Gesundheit und Soziales",
                    },
                    "23000": {"name": "Klinikgebiet", "description": "Klinikgebiet"},
                    "2400": {"name": "Golfplatz", "description": "Golfplatz"},
                    "2500": {
                        "name": "SondergebietKultur",
                        "description": "Sondergebiet für Kultur",
                    },
                    "2600": {
                        "name": "SondergebietTourismus",
                        "description": "Sondergebiet Tourismus",
                    },
                    "2700": {
                        "name": "SondergebietBueroUndVerwaltung",
                        "description": "Sondergebiet für Büros und Verwaltung",
                    },
                    "2720": {
                        "name": "SondergebietJustiz",
                        "description": "Sondergebiet für Einrichtungen der Justiz",
                    },
                    "2800": {
                        "name": "SondergebietHochschuleForschung",
                        "description": "Sondergebiet Hochschule",
                    },
                    "2900": {
                        "name": "SondergebietMesse",
                        "description": "Sondergebiet für Messe",
                    },
                    "9999": {
                        "name": "SondergebietAndereNutzungen",
                        "description": "Sonstiges Sondergebiet",
                    },
                },
            },
        ),
    ] = None
    detaillierteArtDerBaulNutzung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Art der baulichen Nutzung.",
            json_schema_extra={
                "typename": "FP_DetailArtDerBaulNutzung",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detaillierteSondernutzung: Annotated[
        list[AnyUrl] | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Sondernutzung.",
            json_schema_extra={
                "typename": "FP_DetailSondernutzung",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    nutzungText: Annotated[
        str | None,
        Field(
            description='Bei Nutzungsform "Sondergebiet": Kurzform der besonderen Art der baulichen Nutzung.',
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPBodenschaetze(FPGeometrieobjekt):
    """
    Flächen für Aufschüttungen, Abgrabungen oder für die Gewinnung von Bodenschätzen (§5, Abs. 2, Nr. 8 BauGB. Hier: Flächen für Bodenschätze.

    Die Klasse wird als veraltet gekennzeichnet und wird in XPlanGML V. 6.0 wegfallen. Es sollte stattdessen die Klasse FP_Abgrabung verwendet werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    abbaugut: Annotated[
        str | None,
        Field(
            description="Bezeichnung des Abbauguts.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPDarstellungNachLandesrecht(FPGeometrieobjekt):
    """
    Inhalt des Flächennutzungsplans, der auf einer spezifischen Rechtsverordnung eines Bundeslandes beruht.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    detailZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description="Über eine Codeliste definierte detaillierte Zweckbestimmung der Planinhalts-",
            json_schema_extra={
                "typename": "FP_DetailZweckbestimmungNachLandesrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    kurzbeschreibung: Annotated[
        str | None,
        Field(
            description="Textuelle Beschreibung des Planinhalts.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class FPFlaecheOhneDarstellung(FPFlaechenschlussobjekt):
    """
    Fläche, für die keine geplante Nutzung angegben werden kann
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class FPGemeinbedarf(FPGeometrieobjekt):
    """
    Darstellung von Flächen für den Gemeinbedarf nach § 5,  Abs. 2, Nr. 2 BauGB.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "10001",
                "10002",
                "10003",
                "1200",
                "12000",
                "12001",
                "12002",
                "12003",
                "12004",
                "1400",
                "14000",
                "14001",
                "14002",
                "14003",
                "1600",
                "16000",
                "16001",
                "16002",
                "16003",
                "16004",
                "16005",
                "1800",
                "18000",
                "18001",
                "2000",
                "20000",
                "20001",
                "20002",
                "2200",
                "22000",
                "22001",
                "22002",
                "2400",
                "24000",
                "24001",
                "24002",
                "24003",
                "2600",
                "26000",
                "26001",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Zweckbestimmung der Fläche",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungGemeinbedarf",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "OeffentlicheVerwaltung",
                        "description": "Einrichtungen und Anlagen für öffentliche Verwaltung",
                    },
                    "10000": {
                        "name": "KommunaleEinrichtung",
                        "description": "Kommunale Einrichtung wie z. B. Rathaus, Gesundheitsamt, Gesundheitsfürsorgestelle, Gartenbauamt, Gartenarbeitsstützpunkt, Fuhrpark.",
                    },
                    "10001": {
                        "name": "BetriebOeffentlZweckbestimmung",
                        "description": "Betrieb mit öffentlicher Zweckbestimmung wie z.B. ein Stadtreinigungsbetrieb, Autobusbetriebshof, Omnibusbahnhof.",
                    },
                    "10002": {
                        "name": "AnlageBundLand",
                        "description": "Eine Anlage des Bundes oder eines Bundeslandes wie z. B.  Arbeitsamt, Autobahnmeisterei, Brückenmeisterei, Patentamt, Wasserbauhof, Finanzamt.",
                    },
                    "10003": {
                        "name": "SonstigeOeffentlicheVerwaltung",
                        "description": "Sonstige Einrichtung oder Anlage der öffentlichen Verwaltung wie z. B. die Industrie und Handelskammer oder Handwerkskammer.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1000 verwendet werden.",
                    },
                    "1200": {
                        "name": "BildungForschung",
                        "description": "Einrichtungen und Anlagen für Bildung und Forschung",
                    },
                    "12000": {
                        "name": "Schule",
                        "description": "Schulische Einrichtung. Darunter fallen u. a. Allgemeinbildende Schule, Oberstufenzentrum, Sonderschule, Fachschule, Volkshochschule,\r\nKonservatorium.",
                    },
                    "12001": {
                        "name": "Hochschule",
                        "description": "Hochschule, Fachhochschule, Berufsakademie, o. Ä.",
                    },
                    "12002": {
                        "name": "BerufsbildendeSchule",
                        "description": "Berufsbildende Schule",
                    },
                    "12003": {
                        "name": "Forschungseinrichtung",
                        "description": "Forschungseinrichtung, Forschungsinstitut.",
                    },
                    "12004": {
                        "name": "SonstigesBildungForschung",
                        "description": "Sonstige Anlage oder Einrichtung aus Bildung und Forschung.\r\n\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1200 verwendet werden.",
                    },
                    "1400": {"name": "Kirche", "description": "Religiöse Einrichtung"},
                    "14000": {
                        "name": "Sakralgebaeude",
                        "description": "Religiösen Zwecken dienendes Gebäude wie z. B. Kirche, \r\n Kapelle, Moschee, Synagoge, Gebetssaal.",
                    },
                    "14001": {
                        "name": "KirchlicheVerwaltung",
                        "description": "Religiöses Verwaltungsgebäude, z. B. Pfarramt, Bischöfliches Ordinariat, Konsistorium.",
                    },
                    "14002": {
                        "name": "Kirchengemeinde",
                        "description": "Religiöse Gemeinde- oder Versammlungseinrichtung, z. B. Gemeindehaus, Gemeindezentrum.",
                    },
                    "14003": {
                        "name": "SonstigesKirche",
                        "description": "Sonstige religiösen Zwecken dienende Anlage oder Einrichtung.\r\n\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1400 verwendet werden.",
                    },
                    "1600": {
                        "name": "Sozial",
                        "description": "Einrichtungen und Anlagen für soziale Zwecke.",
                    },
                    "16000": {
                        "name": "EinrichtungKinder",
                        "description": "Soziale Einrichtung für Kinder, wie z. B. Kinderheim, Kindertagesstätte, Kindergarten.",
                    },
                    "16001": {
                        "name": "EinrichtungJugendliche",
                        "description": "Soziale Einrichtung für Jugendliche, wie z. B. Jugendfreizeitheim/-stätte, Jugendgästehaus, Jugendherberge, Jugendheim.",
                    },
                    "16002": {
                        "name": "EinrichtungFamilienErwachsene",
                        "description": "Soziale Einrichtung für Familien und Erwachsene, wie z. B. Bildungszentrum, Volkshochschule, Kleinkinderfürsorgestelle, Säuglingsfürsorgestelle, Nachbarschaftsheim.",
                    },
                    "16003": {
                        "name": "EinrichtungSenioren",
                        "description": "Soziale Einrichtung für Senioren, wie z. B. Alten-/Seniorentagesstätte, Alten-/Seniorenheim, Alten-/Seniorenwohnheim, Altersheim.",
                    },
                    "16004": {
                        "name": "SonstigeSozialeEinrichtung",
                        "description": "Sonstige soziale Einrichtung, z. B. Pflegeheim, Schwesternwohnheim, Studentendorf, Studentenwohnheim. Tierheim, Übergangsheim.\r\n\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1600 verwendet werden.",
                    },
                    "16005": {
                        "name": "EinrichtungBehinderte",
                        "description": "Soziale Einrichtung für Menschen mit Beeinträchtigung, wie z. B. Behindertentagesstätte, Behindertenwohnheim, Behindertenwerkstatt",
                    },
                    "1800": {
                        "name": "Gesundheit",
                        "description": "Einrichtungen und Anlagen für gesundheitliche Zwecke.",
                    },
                    "18000": {
                        "name": "Krankenhaus",
                        "description": "Krankenhaus oder vergleichbare Einrichtung (z. B. Klinik, Hospital, Krankenheim, Heil- und Pflegeanstalt),",
                    },
                    "18001": {
                        "name": "SonstigesGesundheit",
                        "description": "Sonstige Gesundheits-Einrichtung, z. B. Sanatorium, Kurklinik, Desinfektionsanstalt.\r\n\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 1800 verwendet werden.",
                    },
                    "2000": {
                        "name": "Kultur",
                        "description": "Einrichtungen und Anlagen für kulturelle Zwecke.",
                    },
                    "20000": {
                        "name": "MusikTheater",
                        "description": "Kulturelle Einrichtung aus dem Bereich Musik oder Theater (z. B. Theater, Konzerthaus, Musikhalle, Oper).",
                    },
                    "20001": {
                        "name": "Bildung",
                        "description": "Kulturelle Einrichtung mit Bildungsfunktion ( z. B. Museum, Bibliothek, Bücherei, Stadtbücherei, Volksbücherei).",
                    },
                    "20002": {
                        "name": "SonstigeKultur",
                        "description": "Sonstige kulturelle Einrichtung, wie z. B. Archiv, Landesbildstelle, Rundfunk und Fernsehen, Kongress- und Veranstaltungshalle, Mehrzweckhalle..\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2000 verwendet werden.",
                    },
                    "2200": {
                        "name": "Sport",
                        "description": "Einrichtungen und Anlagen für sportliche Zwecke.",
                    },
                    "22000": {
                        "name": "Bad",
                        "description": "Schwimmbad, Freibad, Hallenbad, Schwimmhalle o. Ä..",
                    },
                    "22001": {
                        "name": "SportplatzSporthalle",
                        "description": "Sportplatz, Sporthalle, Tennishalle o. Ä.",
                    },
                    "22002": {
                        "name": "SonstigerSport",
                        "description": "Sonstige Sporteinrichtung.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2200 verwendet werden.",
                    },
                    "2400": {
                        "name": "SicherheitOrdnung",
                        "description": "Einrichtungen und Anlagen für Sicherheit und Ordnung.",
                    },
                    "24000": {
                        "name": "Feuerwehr",
                        "description": "Einrichtung oder Anlage der Feuerwehr.",
                    },
                    "24001": {"name": "Schutzbauwerk", "description": "Schutzbauwerk"},
                    "24002": {
                        "name": "Justiz",
                        "description": "Einrichtung der Justiz, wie z. B. Justizvollzug, Gericht, Haftanstalt.",
                    },
                    "24003": {
                        "name": "SonstigeSicherheitOrdnung",
                        "description": "Sonstige Anlage oder Einrichtung für Sicherheit und Ordnung, z. B. Polizei, Zoll, Feuerwehr, Zivilschutz, Bundeswehr, Landesverteidigung.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2400 verwendet werden.",
                    },
                    "2600": {
                        "name": "Infrastruktur",
                        "description": "Einrichtungen und Anlagen der Infrastruktur.",
                    },
                    "26000": {"name": "Post", "description": "Einrichtung der Post."},
                    "26001": {
                        "name": "SonstigeInfrastruktur",
                        "description": "Sonstige Anlage oder Einrichtung der Infrastruktur.\r\n\r\nDer Eintrag ist veraltet und wird in XPlanGML V. 6.0 entfernt. Es sollte stattdessen der Code 2600 verwendet werden.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Einrichtungen und Anlagen, die keiner anderen Kategorie zuzuordnen sind.",
                    },
                },
            },
        ),
    ] = None
    detaillierteZweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Zweckbestimmung.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteZweckbestimmung" bezieht sich auf den an gleicher Position stehenden Attributwert von "zweckbestimmung".',
            json_schema_extra={
                "typename": "FP_DetailZweckbestGemeinbedarf",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class FPGenerischesObjekt(FPGeometrieobjekt):
    """
    Klasse zur Modellierung aller Inhalte des FPlans, die durch keine spezifische XPlanung-Klasse repräsentiert werden können.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description="Über eine Codeliste definierte Zweckbestimmung des Generischen Objekts.",
            json_schema_extra={
                "typename": "FP_ZweckbestimmungGenerischeObjekte",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class FPNutzungsbeschraenkungsFlaeche(FPUeberlagerungsobjekt):
    """
    Umgrenzungen der Flächen für besondere Anlagen und Vorkehrungen zum Schutz vor schädlichen Umwelteinwirkungen im Sinne des Bundes-
    Immissionsschutzgesetzes (§ 5, Abs. 2, Nr. 6 BauGB)
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class FPTextlicheDarstellungsFlaeche(FPUeberlagerungsobjekt):
    """
    Bereich, in dem bestimmte Textliche Darstellungen gültig sind, die über die Relation "refTextInhalt" (Basisklasse FP_Objekt) spezifiziert werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class LPAbgrenzung(LPLinienobjekt):
    """
    Abgrenzungen unterschiedlicher Ziel- und Zweckbestimmungen und Nutzungsarten, Abgrenzungen unterschiedlicher Biotoptypen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class LPAllgGruenflaeche(LPFlaechenobjekt):
    """
    Allgemeine Grünflächen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class LPAnpflanzungBindungErhaltung(LPGeometrieobjekt):
    """
    Festsetzungen zum Erhalten und Anpflanzen von Bäumen, Sträuchern und sonstigen Bepflanzungen in einem Planwerk mit landschaftsplanerischen Festsetzungen. Die Festsetzungen können durch eine Spezifizierung eines Kronendurchmessers (z.B. für Baumpflanzungen), die Pflanztiefe und Mindesthöhe von Anpflanzungen (z.B. bei der Anpflanzung von Hecken) oder durch botanische Spezifizierung differenziert werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    massnahme: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Art der Maßnahme",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "BindungErhaltung",
                        "description": "Bindungen für Bepflanzungen und für die Erhaltung von Bäumen, Sträuchern und sonstigen Bepflanzungen sowie von Gewässern. Dies entspricht dem Planzeichen 13.2.2 der PlanzV 1990.",
                    },
                    "2000": {
                        "name": "Anpflanzung",
                        "description": "Anpflanzung von Bäumen, Sträuchern oder sonstigen Bepflanzungen. Dies entspricht dem Planzeichen 13.2.1 der PlanzV 1990.",
                    },
                    "3000": {
                        "name": "AnpflanzungBindungErhaltung",
                        "description": "Anpflanzen von Bäumen, Sträuchern und sonstigen Bepflanzungen, sowie Bindungen für Bepflanzungen und für die Erhaltung von Bäumen, Sträuchern und sonstigen Bepflanzungen sowie von Gewässern",
                    },
                },
                "typename": "XP_ABEMassnahmenTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    gegenstand: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "2000",
                "2050",
                "2100",
                "2200",
                "3000",
                "4000",
                "5000",
                "6000",
            ]
        ]
        | None,
        Field(
            description="Gegenstand der Maßnahme.",
            json_schema_extra={
                "typename": "XP_AnpflanzungBindungErhaltungsGegenstand",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Baeume", "description": "Bäume"},
                    "1100": {"name": "Kopfbaeume", "description": "Kopfbäume"},
                    "1200": {"name": "Baumreihe", "description": "Baumreihe"},
                    "2000": {"name": "Straeucher", "description": "Sträucher"},
                    "2050": {
                        "name": "BaeumeUndStraeucher",
                        "description": "Bäume und Sträucher",
                    },
                    "2100": {"name": "Hecke", "description": "Hecke"},
                    "2200": {"name": "Knick", "description": "Knick"},
                    "3000": {
                        "name": "SonstBepflanzung",
                        "description": "Sonstige Bepflanzung",
                    },
                    "4000": {
                        "name": "Gewaesser",
                        "description": "Gewässer (nur Erhaltung)",
                    },
                    "5000": {
                        "name": "Fassadenbegruenung",
                        "description": "Fassadenbegrünung",
                    },
                    "6000": {"name": "Dachbegruenung", "description": "Dachbegrünung"},
                },
            },
        ),
    ] = None
    kronendurchmesser: Annotated[
        definitions.Length | None,
        Field(
            description="Durchmesser der Baumkrone bei zu erhaltenden Bäumen.",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    pflanztiefe: Annotated[
        definitions.Length | None,
        Field(
            description="Pflanztiefe",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    istAusgleich: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob die Fläche oder Maßnahme zum Ausgleich von Eingriffen genutzt wird.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    pflanzart: Annotated[
        list[AnyUrl] | None,
        Field(
            description="Botanische Angabe der zu erhaltenden bzw. der zu pflanzenden Pflanzen.",
            json_schema_extra={
                "typename": "LP_Pflanzart",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    mindesthoehe: Annotated[
        definitions.Length | None,
        Field(
            description="Mindesthöhe einer Pflanze (z.B. Mindesthöhe einer zu pflanzenden Hecke)",
            json_schema_extra={
                "typename": "Length",
                "stereotype": "Measure",
                "multiplicity": "0..1",
                "uom": "m",
            },
        ),
    ] = None
    anzahl: Annotated[
        int | None,
        Field(
            description="Anzahl der zu pflanzenden Objekte",
            json_schema_extra={
                "typename": "Integer",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPAusgleich(LPGeometrieobjekt):
    """
    Flächen und Maßnahmen zum Ausgleich von Eingriffen im Sinne des § 8 und 8a BNatSchG (in Verbindung mit § 1a BauGB, Ausgleichs- und Ersatzmaßnahmen).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    ziel: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Ziel der Maßnahme",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchutzPflege",
                        "description": "Schutz und Pflege",
                    },
                    "2000": {"name": "Entwicklung", "description": "Entwicklung"},
                    "3000": {"name": "Anlage", "description": "Neu-Anlage"},
                    "4000": {
                        "name": "SchutzPflegeEntwicklung",
                        "description": "Schutz, Pflege und Entwicklung",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges Ziel"},
                },
                "typename": "XP_SPEZiele",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahme: Annotated[
        str | None,
        Field(
            description="Durchzuführende Maßnahme (Textform)",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    massnahmeKuerzel: Annotated[
        str | None,
        Field(
            description="Kürzel der durchzuführenden Maßnahme.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPBiotopverbundflaeche(LPGeometrieobjekt):
    """
    Biotop-Verbundfläche
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class LPBodenschutzrecht(LPGeometrieobjekt):
    """
    Gebiete und Gebietsteile mit rechtlichen Bindungen nach anderen Fachgesetzen (soweit sie für den Schutz, die Pflege und die Entwicklung von Natur und Landschaft bedeutsam sind). Hier: Flächen mit schädlichen Bodenveränderungen nach dem Bodenschutzgesetz.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "9999"] | None,
        Field(
            description="Typ des Schutzobjektes",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Altlastenflaeche",
                        "description": "Altlastenfläche",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiger Typ."},
                },
                "typename": "LP_BodenschutzrechtTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter detaillierterer Typ des Schutzobjektes",
            json_schema_extra={
                "typename": "LP_BodenschutzrechtDetailTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPErholungFreizeit(LPGeometrieobjekt):
    """
    Sonstige Gebiete, Objekte, Zweckbestimmungen oder Maßnahmen mit besonderen Funktionen für die landschaftsgebundene Erholung und Freizeit.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    funktion: Annotated[
        list[
            Literal[
                "1000",
                "1030",
                "1050",
                "1100",
                "1200",
                "1300",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "1900",
                "2000",
                "2100",
                "2200",
                "2300",
                "2400",
                "2500",
                "2600",
                "2700",
                "2800",
                "2900",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "3600",
                "3700",
                "3800",
                "3900",
                "4000",
                "4100",
                "5000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Funktion der Fläche.",
            json_schema_extra={
                "typename": "LP_ErholungFreizeitFunktionen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Parkanlage", "description": "Parkanlage"},
                    "1030": {
                        "name": "Dauerkleingaerten",
                        "description": "Dauerkleingarten",
                    },
                    "1050": {"name": "Sportplatz", "description": "Sportplatz"},
                    "1100": {"name": "Spielplatz", "description": "Spielplatz"},
                    "1200": {"name": "Zeltplatz", "description": "Zeltplatz"},
                    "1300": {
                        "name": "BadeplatzFreibad",
                        "description": "Badeplatz, Freibad",
                    },
                    "1400": {"name": "Schutzhuette", "description": "Schutzhütte"},
                    "1500": {"name": "Rastplatz", "description": "Rastplatz"},
                    "1600": {
                        "name": "Informationstafel",
                        "description": "Informationstafel",
                    },
                    "1700": {
                        "name": "FeuerstelleGrillplatz",
                        "description": "Feuerstelle, Grillplatz",
                    },
                    "1800": {"name": "Liegewiese", "description": "Liegewiese"},
                    "1900": {"name": "Aussichtsturm", "description": "Aussichtsturm"},
                    "2000": {"name": "Aussichtspunkt", "description": "Aussichtspunkt"},
                    "2100": {"name": "Angelteich", "description": "Angelteich"},
                    "2200": {
                        "name": "Modellflugplatz",
                        "description": "Modellflugplatz",
                    },
                    "2300": {
                        "name": "WildgehegeSchaugatter",
                        "description": "Wildgehege, Schaugatter",
                    },
                    "2400": {
                        "name": "JugendzeltplatzEinzelcamp",
                        "description": "Jugendzeltplatz, Jugendcamp",
                    },
                    "2500": {
                        "name": "Gleitschirmplatz",
                        "description": "Gleitschirmplatz",
                    },
                    "2600": {"name": "Wandern", "description": "Wandern allgemein"},
                    "2700": {"name": "Wanderweg", "description": "Wanderweg"},
                    "2800": {"name": "Lehrpfad", "description": "Lehrpfad"},
                    "2900": {"name": "Reitweg", "description": "Reitweg"},
                    "3000": {"name": "Radweg", "description": "Radweg"},
                    "3100": {
                        "name": "Wintersport",
                        "description": "Wintersport allgemein",
                    },
                    "3200": {"name": "Skiabfahrt", "description": "Skiabfahrt"},
                    "3300": {
                        "name": "Skilanglaufloipe",
                        "description": "Langlaufloipe",
                    },
                    "3400": {
                        "name": "RodelbahnBobbahn",
                        "description": "Rodelbahn, Bobbahn",
                    },
                    "3500": {
                        "name": "Wassersport",
                        "description": "Wassersport allgemein",
                    },
                    "3600": {
                        "name": "Wasserwanderweg",
                        "description": "Wasserwanderweg",
                    },
                    "3700": {
                        "name": "Schifffahrtsroute",
                        "description": "Schifffahrtsroute",
                    },
                    "3800": {
                        "name": "AnlegestelleMitMotorbooten",
                        "description": "Schiffsanlegestelle mit Motorbooten",
                    },
                    "3900": {
                        "name": "AnlegestelleOhneMotorboote",
                        "description": "Schiffsanlegestelle ohne Motorboote",
                    },
                    "4000": {
                        "name": "SesselliftSchlepplift",
                        "description": "Sessellift, Schlepplift",
                    },
                    "4100": {
                        "name": "Kabinenseilbahn",
                        "description": "Kabinenseilbahn",
                    },
                    "5000": {"name": "Parkplatz", "description": "Parkplatz"},
                    "9999": {"name": "Sonstiges", "description": "Sonstiges"},
                },
            },
        ),
    ] = None
    detaillierteFunktion: Annotated[
        list[AnyUrl] | None,
        Field(
            description='Über eine Codeliste definierte detailliertere Funktion eines Freizeit- oder Erholungs-Objektes.\r\nDer an einer bestimmten Listenposition aufgeführte Wert von "detaillierteFunktion" bezieht sich auf den an gleicher Position stehenden Attributwert von "funktion".',
            json_schema_extra={
                "typename": "LP_ErholungFreizeitDetailFunktionen",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class LPForstrecht(LPGeometrieobjekt):
    """
    Gebiete und Gebietsteile mit rechtlichen Bindungen nach anderen Fachgesetzen (soweit sie für den Schutz, die Pflege und die Entwicklung von Natur und Landschaft bedeutsam sind). Hier: Schutzgebiete und sonstige Flächen nach dem Bundeswaldgesetz.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal[
            "1000",
            "2000",
            "2100",
            "2200",
            "2300",
            "2400",
            "2500",
            "3000",
            "3100",
            "3200",
            "9999",
        ]
        | None,
        Field(
            description="Typ des Schutzobjektes.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Naturwaldreservat",
                        "description": "Naturwaldreservat",
                    },
                    "2000": {
                        "name": "SchutzwaldAllgemein",
                        "description": "Allgemeiner Schutzwald",
                    },
                    "2100": {
                        "name": "Lawinenschutzwald",
                        "description": "Lawinenschutzwald",
                    },
                    "2200": {
                        "name": "Bodenschutzwald",
                        "description": "Bodenschutzwald",
                    },
                    "2300": {
                        "name": "Klimaschutzwald",
                        "description": "Klimaschutzwald",
                    },
                    "2400": {
                        "name": "Immissionsschutzwald",
                        "description": "Immissionsschutzwald",
                    },
                    "2500": {
                        "name": "Biotopschutzwald",
                        "description": "Biotopschutzwald",
                    },
                    "3000": {
                        "name": "ErholungswaldAllgemein",
                        "description": "Allgemeiner Erholungswald",
                    },
                    "3100": {
                        "name": "ErholungswaldHeilbaeder",
                        "description": "Erholungswald in Heilbädern",
                    },
                    "3200": {
                        "name": "ErholungswaldBallungsraeume",
                        "description": "Erholungswald in Ballungsräumen",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiger Typ."},
                },
                "typename": "LP_ForstrechtTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierter detaillierterer Typ des Schutzobjektes.",
            json_schema_extra={
                "typename": "LP_WaldschutzDetailTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class LPGenerischesObjekt(LPGeometrieobjekt):
    """
    Klasse zur Modellierung aller Inhalte des Landschaftsplans, die durch keine spezifische XPlanung-Klasse repräsentiert werden können.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    zweckbestimmung: Annotated[
        list[AnyUrl] | None,
        Field(
            description="Über eine Codeliste definierte Zweckbestimmung des Generischen Objektes.",
            json_schema_extra={
                "typename": "LP_ZweckbestimmungGenerischeObjekte",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class RPAchse(RPGeometrieobjekt):
    """
    Achsen bündeln i.d.R. Verkehrs- und Versorgungsinfrastruktur und enthalten eine relativ dichte Folge von Siedlungskonzentrationen und Zentralen Orten.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "3000",
                "3001",
                "3002",
                "3003",
                "4000",
                "5000",
                "6000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation verschiedener Achsen.",
            json_schema_extra={
                "typename": "RP_AchsenTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Achse", "description": "Achsen."},
                    "2000": {
                        "name": "Siedlungsachse",
                        "description": "Siedlungsachsen sind Achsen in Verdichtungsräumen, oft entlang von Strecken des öffentlichen Nahverkehrs.",
                    },
                    "3000": {
                        "name": "Entwicklungsachse",
                        "description": "Entwicklungsachse.",
                    },
                    "3001": {
                        "name": "Landesentwicklungsachse",
                        "description": "Landesentwicklungsachse.",
                    },
                    "3002": {
                        "name": "Verbindungsachse",
                        "description": "Verbindungsachsen sind durch Verkehrsbeziehungen zwischen zentralen Orten verschiedener Stufen gekennzeichnet.",
                    },
                    "3003": {
                        "name": "Entwicklungskorridor",
                        "description": "Entwicklungskorridor.",
                    },
                    "4000": {
                        "name": "AbgrenzungEntwicklungsEntlastungsorte",
                        "description": "Abgrenzung von Entwicklungs- und Entlastungsorten.",
                    },
                    "5000": {
                        "name": "Achsengrundrichtung",
                        "description": "Achsengrundrichtung.",
                    },
                    "6000": {
                        "name": "AuessererAchsenSchwerpunkt",
                        "description": "Äußerer Achsenschwerpunkt.",
                    },
                    "9999": {"name": "SonstigeAchse", "description": "Sonstige Achse."},
                },
            },
        ),
    ] = None


class RPEinzelhandel(RPSiedlung):
    """
    Einzelhandelsstruktur und -funktionen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "3000",
                "4000",
                "5000",
                "6000",
                "7000",
                "8000",
                "9000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Einzelhandelstypen.",
            json_schema_extra={
                "typename": "RP_EinzelhandelTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Einzelhandel", "description": "Einzelhandel."},
                    "2000": {
                        "name": "ZentralerVersorgungsbereich",
                        "description": "Zentraler Versorgungsbereich.",
                    },
                    "3000": {
                        "name": "ZentralerEinkaufsbereich",
                        "description": "Zentraler Einkaufsbereich.",
                    },
                    "4000": {
                        "name": "ZentrenrelevantesGrossprojekt",
                        "description": "Zentrenrelevantes Großprojekt.",
                    },
                    "5000": {
                        "name": "NichtzentrenrelevantesGrossprojekt",
                        "description": "Nichtzentrenrelevantes Großprojekt.",
                    },
                    "6000": {
                        "name": "GrossflaechigerEinzelhandel",
                        "description": "Großflächiger Einzelhandel.",
                    },
                    "7000": {
                        "name": "Fachmarktstandort",
                        "description": "Fachmarktstandort.",
                    },
                    "8000": {
                        "name": "Ergaenzungsstandort",
                        "description": "Ergänzungsstandort.",
                    },
                    "9000": {
                        "name": "StaedtischerKernbereich",
                        "description": "Städtischer Kernbereich.",
                    },
                    "9999": {
                        "name": "SonstigerEinzelhandel",
                        "description": "Sonstiger Einzelhandel.",
                    },
                },
            },
        ),
    ] = None


class RPEnergieversorgung(RPGeometrieobjekt):
    """
    Infrastruktur zur Energieversorgung. Beinhaltet Energieerzeugung und die Belieferung von Verbrauchern mit Nutzenergie. Erneuerbare Energie wie Windkraft wird im Normalfall auf die Klasse RP_ErneuerbareEnergie im Unterpaket Freiraumstruktur zugeordnet. Je nach Kontext kann aber auch eine Zuordnung auf RP_Energieversorgung stattfinden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1002",
                "2000",
                "2001",
                "3000",
                "3001",
                "3002",
                "4000",
                "4001",
                "4002",
                "5000",
                "6000",
                "7000",
                "8000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Energieversorgungs-Einrichtungen.",
            json_schema_extra={
                "typename": "RP_EnergieversorgungTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Leitungstrasse",
                        "description": "Leitungstrasse.",
                    },
                    "1001": {
                        "name": "Hochspannungsleitung",
                        "description": "Hochspannungsleitung.",
                    },
                    "1002": {
                        "name": "KabeltrasseNetzanbindung",
                        "description": "Kabeltrasse-Netzanbindung.",
                    },
                    "2000": {"name": "Pipeline", "description": "Pipeline."},
                    "2001": {
                        "name": "Uebergabestation",
                        "description": "Übergabestation.",
                    },
                    "3000": {"name": "Kraftwerk", "description": "Kraftwerk."},
                    "3001": {"name": "Grosskraftwerk", "description": "Großkraftwerk."},
                    "3002": {
                        "name": "Energiegewinnung",
                        "description": "Energiegewinnung.",
                    },
                    "4000": {
                        "name": "Energiespeicherung",
                        "description": "Energiespeicherung.",
                    },
                    "4001": {
                        "name": "VerstetigungSpeicherung",
                        "description": "Verstetigung-Speicherung.",
                    },
                    "4002": {
                        "name": "Untergrundspeicher",
                        "description": "Untergrundspeicher.",
                    },
                    "5000": {"name": "Umspannwerk", "description": "Umspannwerk."},
                    "6000": {"name": "Raffinerie", "description": "Raffinerie."},
                    "7000": {"name": "Leitungsabbau", "description": "Leitungsabbau."},
                    "8000": {"name": "Korridor", "description": "Korridor"},
                    "9999": {
                        "name": "SonstigeEnergieversorgung",
                        "description": "Sonstige Energieversorgung.",
                    },
                },
            },
        ),
    ] = None
    primaerenergieTyp: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "2001",
                "3000",
                "4000",
                "5000",
                "6000",
                "7000",
                "8000",
                "9000",
                "9001",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von der mit der Infrastruktur in Beziehung stehenden Primärenergie.",
            json_schema_extra={
                "typename": "RP_PrimaerenergieTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Erdoel", "description": "Erdöl."},
                    "2000": {"name": "Gas", "description": "Gas."},
                    "2001": {"name": "Ferngas", "description": "Ferngas."},
                    "3000": {"name": "Fernwaerme", "description": "Fernwärme."},
                    "4000": {"name": "Kraftstoff", "description": "Kraftstoff."},
                    "5000": {"name": "Kohle", "description": "Kohle."},
                    "6000": {"name": "Wasser", "description": "Wasser."},
                    "7000": {"name": "Kernenergie", "description": "Kernenergie."},
                    "8000": {
                        "name": "Reststoffverwertung",
                        "description": "Reststoffverwertung.",
                    },
                    "9000": {
                        "name": "ErneuerbareEnergie",
                        "description": "Erneuerbare Energie.",
                    },
                    "9001": {"name": "Windenergie", "description": "Windenergie."},
                    "9999": {
                        "name": "SonstigePrimaerenergie",
                        "description": "Sonstige Primärenergie.",
                    },
                },
            },
        ),
    ] = None
    spannung: Annotated[
        Literal["1000", "2000", "3000", "4000"] | None,
        Field(
            description="Klassifikation von Spannungen.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "110KV", "description": "110 Kilovolt."},
                    "2000": {"name": "220KV", "description": "220 Kilovolt."},
                    "3000": {"name": "330KV", "description": "330 Kilovolt."},
                    "4000": {"name": "380KV", "description": "380 Kilovolt."},
                },
                "typename": "RP_SpannungTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPEntsorgung(RPGeometrieobjekt):
    """
    Entsorgungs-Infrastruktur Beinhaltet Abfallentsorgung und Abwasserentsorgung.
    Abfälle sind Gegenstände, Stoffe oder Rückstände, deren sich der Besitzer entledigen will. Sie können verwertet oder beseitigt werden.
    Abwasser beinhaltet durch häuslichen, gewerblichen, landwirtschaftlichen oder sonstigen Gebrauch verunreinigtes Wasser sowie abfließendes Niederschlagswasser bzw. in die Kanalisation fließendes Wasser.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typAE: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1101",
                "1200",
                "1300",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Abfallentsorgung-Infrastruktur.",
            json_schema_extra={
                "typename": "RP_AbfallentsorgungTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "BeseitigungEntsorgung",
                        "description": "Beseitung beziehungsweise Entsorgung von Abfall.",
                    },
                    "1100": {
                        "name": "Abfallbeseitigungsanlage",
                        "description": "Abfallbeseitigungsanlage",
                    },
                    "1101": {
                        "name": "ZentraleAbfallbeseitigungsanlage",
                        "description": "Zentrale Abfallbeseitungsanlage.",
                    },
                    "1200": {"name": "Deponie", "description": "Deponie."},
                    "1300": {
                        "name": "Untertageeinlagerung",
                        "description": "Untertageeinlagerung von Abfall.",
                    },
                    "1400": {
                        "name": "Behandlung",
                        "description": "Behandlung von Abfall.",
                    },
                    "1500": {
                        "name": "Kompostierung",
                        "description": "Kompostierung von Abfall.",
                    },
                    "1600": {
                        "name": "Verbrennung",
                        "description": "Verbrennung von Abfall.",
                    },
                    "1700": {"name": "Umladestation", "description": "Umladestation."},
                    "1800": {
                        "name": "Standortsicherung",
                        "description": "Standortsicherung.",
                    },
                    "9999": {
                        "name": "SonstigeAbfallentsorgung",
                        "description": "Sonstige Abfallentsorgung.",
                    },
                },
            },
        ),
    ] = None
    abfallTyp: Annotated[
        list[Literal["1000", "2000", "3000", "4000", "5000", "9999"]] | None,
        Field(
            description="Klassifikation von mit der Entsorgungsinfrastruktur in Beziehung stehenden Abfalltypen",
            json_schema_extra={
                "typename": "RP_AbfallTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Siedlungsabfall",
                        "description": "Siedlungsabfall.",
                    },
                    "2000": {
                        "name": "Mineralstoffabfall",
                        "description": "Mineralstoffabfall.",
                    },
                    "3000": {
                        "name": "Industrieabfall",
                        "description": "Industrieabfall.",
                    },
                    "4000": {"name": "Sonderabfall", "description": "Sonderabfall."},
                    "5000": {
                        "name": "RadioaktiverAbfall",
                        "description": "Radioaktiver Abfall.",
                    },
                    "9999": {
                        "name": "SonstigerAbfall",
                        "description": "Sonstiger Abfall.",
                    },
                },
            },
        ),
    ] = None
    typAW: Annotated[
        list[Literal["1000", "1001", "1002", "2000", "3000", "4000", "9999"]] | None,
        Field(
            description="Klassifikation von Abwasser-Infrastruktur.",
            json_schema_extra={
                "typename": "RP_AbwasserTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Klaeranlage", "description": "Kläranlage."},
                    "1001": {
                        "name": "ZentraleKlaeranlage",
                        "description": "Zentrale Kläranlage.",
                    },
                    "1002": {"name": "Grossklaerwerk", "description": "Großklärwerk."},
                    "2000": {
                        "name": "Hauptwasserableitung",
                        "description": "Hauptwasserableitung.",
                    },
                    "3000": {
                        "name": "Abwasserverwertungsflaeche",
                        "description": "Abwasserverwertungsfläche.",
                    },
                    "4000": {
                        "name": "Abwasserbehandlungsanlage",
                        "description": "Abwasserbehandlungsanlage.",
                    },
                    "9999": {
                        "name": "SonstigeAbwasserinfrastruktur",
                        "description": "Sonstige Abwasserinfrastruktur.",
                    },
                },
            },
        ),
    ] = None
    istAufschuettungAblagerung: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob die Entsorgung in Form einer Aufschüttung oder Ablagerung erfolgt",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False


class RPFreiraum(RPGeometrieobjekt):
    """
    Allgemeines Freiraumobjekt.
    Freiräume sind naturnahem Zustand, oder beinhalten Nutzungsformen, die mit seinen ökologischen Grundfunktionen überwiegend verträglich sind (z.B. Land- oder Forstwirtschaft). Freiraum ist somit ein Gegenbegriff zur Siedlungsstruktur.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    istAusgleichsgebiet: Annotated[
        bool | None,
        Field(
            description="Zeigt an, ob das Objekt ein Ausgleichsgebiet ist.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    imVerbund: Annotated[
        bool | None,
        Field(
            description="Zeigt an, ob das Objekt in einem (Freiraum-)Verbund liegt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False


class RPFunktionszuweisung(RPGeometrieobjekt):
    """
    Gebiets- und Gemeindefunktionen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "3000",
                "4000",
                "5000",
                "6000",
                "7000",
                "8000",
                "9000",
                "9999",
            ]
        ],
        Field(
            description="Klassifikation des Gebietes nach Bundesraumordnungsgesetz.",
            json_schema_extra={
                "typename": "RP_FunktionszuweisungTypen",
                "stereotype": "Enumeration",
                "multiplicity": "1..*",
                "enumDescription": {
                    "1000": {"name": "Wohnen", "description": "Wohnfunktion."},
                    "2000": {"name": "Arbeit", "description": "Arbeitsfunktion."},
                    "3000": {
                        "name": "GewerbeDienstleistung",
                        "description": "Gewerbe- und/oder Dienstleistungsfunktion.",
                    },
                    "4000": {
                        "name": "Einzelhandel",
                        "description": "Einzelhandelsfunktion.",
                    },
                    "5000": {
                        "name": "Landwirtschaft",
                        "description": "Landwirtschaftliche Funktion.",
                    },
                    "6000": {
                        "name": "ErholungFremdenverkehr",
                        "description": "Erholungs-, Fremdenverkehrs- und/oder Tourismusfunktion.",
                    },
                    "7000": {
                        "name": "Verteidigung",
                        "description": "Verteidigungsfunktion.",
                    },
                    "8000": {
                        "name": "UeberoertlicheVersorgungsfunktionLaendlicherRaum",
                        "description": "Überörtliche Versorgungsfunktion.",
                    },
                    "9000": {
                        "name": "LaendlicheSiedlung",
                        "description": "Ländliche Siedlung",
                    },
                    "9999": {
                        "name": "SonstigeFunktion",
                        "description": "Sonstige Funktion.",
                    },
                },
            },
            min_length=1,
        ),
    ]
    bezeichnung: Annotated[
        str | None,
        Field(
            description="Bezeichnung und/oder Erörterung einer Gebietsfunktion.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPGenerischesObjekt(RPGeometrieobjekt):
    """
    Klasse zur Modellierung aller Inhalte des Raumordnungsplans, die durch keine andere Klasse des RPlan-Fachschemas dargestellt werden können.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[AnyUrl] | None,
        Field(
            description="Über eine CodeList definierte Zweckbestimmung der Festlegung.",
            json_schema_extra={
                "typename": "RP_GenerischesObjektTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..*",
            },
        ),
    ] = None


class RPGewaesser(RPFreiraum):
    """
    Gewässer, die nicht andersweitig erfasst werden, zum Beispiel Flüsse oder Seen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    gewaesserTyp: Annotated[
        str | None,
        Field(
            description="Spezifiziert den Typ des Gewässers.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPGruenzugGruenzaesur(RPFreiraum):
    """
    Grünzüge und kleinräumigere Grünzäsuren sind Ordnungsinstrumente zur Freiraumsicherung. Teilweise werden Grünzüge auch Trenngrün genannt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[Literal["1000", "2000", "3000"]] | None,
        Field(
            description="Klassifikation von Zäsurtypen.",
            json_schema_extra={
                "typename": "RP_ZaesurTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Gruenzug", "description": "Grünzug."},
                    "2000": {"name": "Gruenzaesur", "description": "Grünzäsur."},
                    "3000": {
                        "name": "Siedlungszaesur",
                        "description": "Siedlungszäsur.",
                    },
                },
            },
        ),
    ] = None


class RPHochwasserschutz(RPFreiraum):
    """
    Die Klasse RP_Hochwasserschutz enthält Hochwasserschutz und vorbeugenden Hochwasserschutz.
    Hochwasserschutz und vorbeugender Hochwasserschutz beinhaltet den Schutz von Siedlungen, Nutz- und Verkehrsflächen vor Überschwemmungen. Im Binnenland besteht der Hochwasserschutz vor allem in der Sicherung und Rückgewinnung von Auen, Wasserrückhalteflächen (Retentionsflächen) und überschwemmungsgefährdeten Bereichen. An der Nord- und Ostsee erfolgt der Schutz vor Sturmfluten hauptsächlich durch Deiche und Siele (Küstenschutz).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1100",
                "1101",
                "1102",
                "1200",
                "1300",
                "1301",
                "1302",
                "1303",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "1801",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Hochwasserschutztypen.",
            json_schema_extra={
                "typename": "RP_HochwasserschutzTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Hochwasserschutz",
                        "description": "Hochwasserschutz.",
                    },
                    "1001": {
                        "name": "TechnischerHochwasserschutz",
                        "description": "Technischer Hochwasserschutz.",
                    },
                    "1100": {
                        "name": "Hochwasserrueckhaltebecken",
                        "description": "Hochwasserrückhaltebecken.",
                    },
                    "1101": {
                        "name": "HochwasserrueckhaltebeckenPolder",
                        "description": "Hochwasserrückhaltebecken: Polder.",
                    },
                    "1102": {
                        "name": "HochwasserrueckhaltebeckenBauwerk",
                        "description": "Hochwasserrückhaltebecken: Bauwerk.",
                    },
                    "1200": {
                        "name": "RisikobereichHochwasser",
                        "description": "Risikobereich Hochwasser.",
                    },
                    "1300": {
                        "name": "Kuestenhochwasserschutz",
                        "description": "Küstenhochwasserschutz.",
                    },
                    "1301": {"name": "Deich", "description": "Deich."},
                    "1302": {
                        "name": "Deichrueckverlegung",
                        "description": "Deichrückverlegung.",
                    },
                    "1303": {
                        "name": "DeichgeschuetztesGebiet",
                        "description": "Deichgeschütztes Gebiet",
                    },
                    "1400": {"name": "Sperrwerk", "description": "Sperrwerk."},
                    "1500": {
                        "name": "HochwGefaehrdeteKuestenniederung",
                        "description": "Hochwassergefährdete Küstenniederung.",
                    },
                    "1600": {
                        "name": "Ueberschwemmungsgebiet",
                        "description": "Überschwemmungsgebiet.",
                    },
                    "1700": {
                        "name": "UeberschwemmungsgefaehrdeterBereich",
                        "description": "Überschwemmungsgefährdeter Bereich.",
                    },
                    "1800": {
                        "name": "Retentionsraum",
                        "description": "Retentionsraum.",
                    },
                    "1801": {
                        "name": "PotenziellerRetentionsraum",
                        "description": "Potenzieller Retentionsraum.",
                    },
                    "9999": {
                        "name": "SonstigerHochwasserschutz",
                        "description": "Sonstiger Hochwasserschutz.",
                    },
                },
            },
        ),
    ] = None


class RPIndustrieGewerbe(RPSiedlung):
    """
    Industrie- und Gewerbestrukturen und -funktionen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "2000",
                "2001",
                "2002",
                "2003",
                "3000",
                "3001",
                "4000",
                "5000",
                "6000",
                "7000",
                "8000",
                "9000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Industrie- und Gewerbetypen.",
            json_schema_extra={
                "typename": "RP_IndustrieGewerbeTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Industrie", "description": "Industrie."},
                    "1001": {
                        "name": "IndustrielleAnlage",
                        "description": "Industrielle Anlage.",
                    },
                    "2000": {"name": "Gewerbe", "description": "Gewerbe"},
                    "2001": {
                        "name": "GewerblicherBereich",
                        "description": "Gewerblicher Bereich.",
                    },
                    "2002": {"name": "Gewerbepark", "description": "Gewerbepark."},
                    "2003": {
                        "name": "DienstleistungGewerbeZentrum",
                        "description": "Dienstleistungs- oder gewerbezentrum",
                    },
                    "3000": {
                        "name": "GewerbeIndustrie",
                        "description": "Gewerbe-Industrie.",
                    },
                    "3001": {
                        "name": "BedeutsamerEntwicklungsstandortGewerbeIndustrie",
                        "description": "Bedeutsamer Entwicklungsstandort von Gewerbe-Industrie.",
                    },
                    "4000": {
                        "name": "SicherungundEntwicklungvonArbeitsstaetten",
                        "description": "Sicherung und Entwicklung von Arbeitsstätten.",
                    },
                    "5000": {
                        "name": "FlaechenintensivesGrossvorhaben",
                        "description": "Flächenintensives Großvorhaben.",
                    },
                    "6000": {
                        "name": "BetriebsanlageBergbau",
                        "description": "Betriebsanlage des Bergbaus.",
                    },
                    "7000": {
                        "name": "HafenorientierteWirtschaftlicheAnlage",
                        "description": "Hafenorientierte wirtschaftliche Anlage.",
                    },
                    "8000": {
                        "name": "TankRastanlage",
                        "description": "Tankanlagen und Rastanlagen.",
                    },
                    "9000": {
                        "name": "BereichFuerGewerblicheUndIndustrielleNutzungGIB",
                        "description": "Sonstige Typen von Industrie und Gewerbe.",
                    },
                    "9999": {
                        "name": "SonstigeIndustrieGewerbe",
                        "description": "Sonstiges",
                    },
                },
            },
        ),
    ] = None


class RPKlimaschutz(RPFreiraum):
    """
    (Siedlungs-) Klimaschutz. Beinhaltet zum Beispiel auch Kalt- und Frischluftschneisen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[Literal["1000", "2000", "3000", "9999"]] | None,
        Field(
            description="Klassifikation von Lufttypen.",
            json_schema_extra={
                "typename": "RP_KlimaschutzTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Kaltluft", "description": "Kaltluft."},
                    "2000": {"name": "Frischluft", "description": "Frischluft."},
                    "3000": {
                        "name": "BesondereKlimaschutzfunktion",
                        "description": "Besondere Klimaschutzfunktion",
                    },
                    "9999": {
                        "name": "SonstigeLufttypen",
                        "description": "Sonstige Lufttypen.",
                    },
                },
            },
        ),
    ] = None


class RPKulturlandschaft(RPFreiraum):
    """
    Landschaftsbereich mit überwiegend anthropogenen Ökosystemen (historisch geprägt und gewachsen). Sie sind nach §2, Nr. 5 des ROG mit ihren Kultur- und Naturdenkmälern zu erhalten und zu entwickeln.
    Beinhaltet unter anderem die Begriffe Kulturlandschaft, kulturelle Sachgüter und Welterbestätten.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Klassifikation von Kulturlandschaftstypen.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "KulturellesSachgut",
                        "description": "Kulturelles Sachgut.",
                    },
                    "2000": {
                        "name": "Welterbe",
                        "description": 'Welterbe. Von der UNESCO verliehener Titel an Stätten mit außergewöhnlichem, universellem Wert, die als "Teile des Kultur- und Naturerbes von außergewöhnlicher Bedeutung sind und daher als Bestandteil des Welterbes der ganzen Menschheit erhalten werden müssen" (Präambel der Welterbekonvention von 1972)',
                    },
                    "3000": {
                        "name": "KulturerbeLandschaft",
                        "description": "Landschaftliches Kulturerbe.",
                    },
                    "4000": {
                        "name": "KulturDenkmalpflege",
                        "description": "Pflege von Kulturdenkmälern",
                    },
                    "9999": {
                        "name": "SonstigeKulturlandschaftTypen",
                        "description": "Sonstige Kulturlandschafttypen.",
                    },
                },
                "typename": "RP_KulturlandschaftTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPLandwirtschaft(RPFreiraum):
    """
    Landwirtschaft, hauptsächlich im ländlichen Raum angesiedelt, erfüllt für die Gesellschaft wichtige Funktionen in der Produktion- und Versorgung mit Lebensmitteln, für Freizeit und Freiraum oder zur Biodiversität.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal[
            "1000",
            "1001",
            "2000",
            "3000",
            "4000",
            "5000",
            "6000",
            "7000",
            "8000",
            "9999",
        ]
        | None,
        Field(
            description="Klassifikation von Landwirtschaftstypen.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "LandwirtschaftlicheNutzung",
                        "description": "Allgemeine Landwirtschaftliche Nutzung.",
                    },
                    "1001": {
                        "name": "KernzoneLandwirtschaft",
                        "description": "Kernzone Landwirtschaft.",
                    },
                    "2000": {
                        "name": "IntensivLandwirtschaft",
                        "description": "Intensive Landwirtschaft.",
                    },
                    "3000": {"name": "Fischerei", "description": "Fischerei."},
                    "4000": {"name": "Weinbau", "description": "Weinbau."},
                    "5000": {
                        "name": "AufGrundHohenErtragspotenzials",
                        "description": "Landwirtschaft auf Grund hohen Ertragspotenzials.",
                    },
                    "6000": {
                        "name": "AufGrundBesondererFunktionen",
                        "description": "Landwirtschaft auf Grund besonderer Funktionen.",
                    },
                    "7000": {
                        "name": "Gruenlandbewirtschaftung",
                        "description": "Grünlandbewirtschaftung.",
                    },
                    "8000": {"name": "Sonderkultur", "description": "Sonderkuluren"},
                    "9999": {
                        "name": "SonstigeLandwirtschaft",
                        "description": "Sonstige Landwirtschaft",
                    },
                },
                "typename": "RP_LandwirtschaftTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPLuftverkehr(RPVerkehr):
    """
    Luftverkehr-Infrastruktur ist Infrastruktur, die  im Zusammenhang mit der Beförderung von Personen, Gepäck, Fracht und Post mit staatlich zugelassenen Luftfahrzeugen, besonders Flugzeugen steht.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1002",
                "1003",
                "1004",
                "1005",
                "2000",
                "2001",
                "2002",
                "2003",
                "3000",
                "4000",
                "5000",
                "5001",
                "5002",
                "5003",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Luftverkehr-Infrastruktur.",
            json_schema_extra={
                "typename": "RP_LuftverkehrTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Flughafen", "description": "Flughafen."},
                    "1001": {
                        "name": "Verkehrsflughafen",
                        "description": "Verkehrsflughafen.",
                    },
                    "1002": {
                        "name": "Regionalflughafen",
                        "description": "Regionalflughafen.",
                    },
                    "1003": {
                        "name": "InternationalerFlughafen",
                        "description": "Internationaler Flughafen.",
                    },
                    "1004": {
                        "name": "InternationalerVerkehrsflughafen",
                        "description": "Internationaler Verkehrsflughafen.",
                    },
                    "1005": {
                        "name": "Flughafenentwicklung",
                        "description": "Flughafenentwicklung.",
                    },
                    "2000": {"name": "Flugplatz", "description": "Flugplatz."},
                    "2001": {
                        "name": "Regionalflugplatz",
                        "description": "Regionalflugplatz.",
                    },
                    "2002": {
                        "name": "Segelflugplatz",
                        "description": "Segelflugplatz.",
                    },
                    "2003": {
                        "name": "SonstigerFlugplatz",
                        "description": "Sonstiger Flugplatz.",
                    },
                    "3000": {
                        "name": "Bauschutzbereich",
                        "description": "Bauschutzbereich.",
                    },
                    "4000": {
                        "name": "Militaerflughafen",
                        "description": "Militärflughafen.",
                    },
                    "5000": {"name": "Landeplatz", "description": "Landeplatz."},
                    "5001": {
                        "name": "Verkehrslandeplatz",
                        "description": "Verkehrslandeplatz.",
                    },
                    "5002": {
                        "name": "Hubschrauberlandeplatz",
                        "description": "Hubschrauberlandeplatz.",
                    },
                    "5003": {"name": "Landebahn", "description": "Landebahn."},
                    "9999": {
                        "name": "SonstigerLuftverkehr",
                        "description": "Sonstiger Luftverkehr.",
                    },
                },
            },
        ),
    ] = None


class RPNaturLandschaft(RPFreiraum):
    """
    Naturlandschaften sind von umitellbaren menschlichen Aktivitäten weitestgehend unbeeinflusst gebliebene Landschaft.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1101",
                "1200",
                "1300",
                "1301",
                "1400",
                "1500",
                "1501",
                "1600",
                "1700",
                "1701",
                "1702",
                "1703",
                "1704",
                "1705",
                "1706",
                "1707",
                "1708",
                "1800",
                "1900",
                "2000",
                "2100",
                "2200",
                "2300",
                "2400",
                "2500",
                "2600",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Naturschutz, Landschaftsschutz und Naturlandschafttypen.",
            json_schema_extra={
                "typename": "RP_NaturLandschaftTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "NaturLandschaft",
                        "description": "NaturLandschaft.",
                    },
                    "1100": {
                        "name": "NaturschutzLandschaftspflege",
                        "description": "Naturschutz und Landschaftspflege.",
                    },
                    "1101": {
                        "name": "NaturschutzLandschaftspflegeAufGewaessern",
                        "description": "Naturschutz und Landschaftspflege auf Gewässern.",
                    },
                    "1200": {
                        "name": "Flurdurchgruenung",
                        "description": "Flurdurchgrünung.",
                    },
                    "1300": {
                        "name": "UnzerschnitteneRaeume",
                        "description": "Unzerschnittene Räume.",
                    },
                    "1301": {
                        "name": "UnzerschnitteneVerkehrsarmeRaeume",
                        "description": "Unzerschnittene verkehrsarme Räume.",
                    },
                    "1400": {"name": "Feuchtgebiet", "description": "Feuchtgebiet."},
                    "1500": {
                        "name": "OekologischesVerbundssystem",
                        "description": "Ökologisches Verbundssystem.",
                    },
                    "1501": {
                        "name": "OekologischerRaum",
                        "description": "Ökologischer Raum.",
                    },
                    "1600": {
                        "name": "VerbesserungLandschaftsstrukturNaturhaushalt",
                        "description": "Verbesserung der Landschaftsstruktur und des Naturhaushalts.",
                    },
                    "1700": {"name": "Biotop", "description": "Biotop."},
                    "1701": {"name": "Biotopverbund", "description": "Biotopverbund."},
                    "1702": {
                        "name": "Biotopverbundachse",
                        "description": "Biotopverbundsachse.",
                    },
                    "1703": {
                        "name": "ArtenBiotopschutz",
                        "description": "Arten- und/oder Biotopschutz.",
                    },
                    "1704": {"name": "Regionalpark", "description": "Regionalpark."},
                    "1705": {
                        "name": "Waldlebensraum",
                        "description": "Teil eines Biotop(verbund)s von Waldlebensräumen",
                    },
                    "1706": {
                        "name": "Feuchtlebensraum",
                        "description": "Teil eines Biotop(verbund)s von Feuchtlebensräumen (insbesondere Auen) mit dem angrenzenden Bereich des Grünlandes",
                    },
                    "1707": {
                        "name": "Trockenlebensraum",
                        "description": "Teil eines Biotop(verbunds) von Trockenlebensräumen",
                    },
                    "1708": {
                        "name": "LebensraumLaenderuebergreifendeVernetzung",
                        "description": "Länderübergreifender Teil eines Biotop(verbund)s",
                    },
                    "1800": {
                        "name": "KompensationEntwicklung",
                        "description": "Kompensation für Entwicklung.",
                    },
                    "1900": {
                        "name": "GruenlandBewirtschaftungPflegeEntwicklung",
                        "description": "Grünlandbewirtschaftung, -pflege und -entwicklung.",
                    },
                    "2000": {
                        "name": "Landschaftsstruktur",
                        "description": "Landschaftsstruktur.",
                    },
                    "2100": {
                        "name": "LandschaftErholung",
                        "description": "Landschaftsgebiet für Erholung.",
                    },
                    "2200": {
                        "name": "Landschaftspraegend",
                        "description": "Landschaftsprägend.",
                    },
                    "2300": {
                        "name": "SchutzderNatur",
                        "description": "Schutz der Natur.",
                    },
                    "2400": {
                        "name": "SchutzdesLandschaftsbildes",
                        "description": "Schutz des Landschaftsbildes.",
                    },
                    "2500": {"name": "Alpenpark", "description": "Alpenpark."},
                    "2600": {
                        "name": "Freiraumfunktionen",
                        "description": 'Vorranggebiet Freiraumfunktionen gemäß Planzeichenkatalog "Planzeichen in der Regionalplanung“ vom niedersächsischem Landkreistag.',
                    },
                    "9999": {
                        "name": "SonstigerNaturLandschaftSchutz",
                        "description": "Sonstiger NaturLandschaftsschutz.",
                    },
                },
            },
        ),
    ] = None


class RPNaturschutzrechtlichesSchutzgebiet(RPFreiraum):
    """
    Schutzgebiet nach Bundes-Naturschutzgesetz.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "1300",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "18000",
                "18001",
                "2000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation des Naturschutzgebietes.",
            json_schema_extra={
                "typename": "XP_KlassifizSchutzgebietNaturschutzrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Naturschutzgebiet",
                        "description": "Naturschutzgebiet gemäß §23 BNatSchG.",
                    },
                    "1100": {
                        "name": "Nationalpark",
                        "description": "Nationalpark gemäß §24 BNatSchG",
                    },
                    "1200": {
                        "name": "Biosphaerenreservat",
                        "description": "Biosphärenreservat gemäß §25 BNatSchG.",
                    },
                    "1300": {
                        "name": "Landschaftsschutzgebiet",
                        "description": "Landschaftsschutzgebiet gemäß §65 BNatSchG.",
                    },
                    "1400": {
                        "name": "Naturpark",
                        "description": "Naturpark gemäß §27 BNatSchG.",
                    },
                    "1500": {
                        "name": "Naturdenkmal",
                        "description": "Naturdenkmal gemäß §28 BNatSchG.",
                    },
                    "1600": {
                        "name": "GeschuetzterLandschaftsBestandteil",
                        "description": "Geschützter Bestandteil der Landschaft gemäß §29 BNatSchG.",
                    },
                    "1700": {
                        "name": "GesetzlichGeschuetztesBiotop",
                        "description": "Gesetzlich geschützte Biotope gemäß §30 BNatSchG.",
                    },
                    "1800": {
                        "name": "Natura2000",
                        "description": 'Schutzgebiet nach Europäischem Recht. Dies umfasst das "Gebiet Gemeinschaftlicher Bedeutung" (FFH-Gebiet) und das "Europäische Vogelschutzgebiet"',
                    },
                    "18000": {
                        "name": "GebietGemeinschaftlicherBedeutung",
                        "description": "Gebiete von gemeinschaftlicher Bedeutung",
                    },
                    "18001": {
                        "name": "EuropaeischesVogelschutzgebiet",
                        "description": "Europäische Vogelschutzgebiete",
                    },
                    "2000": {
                        "name": "NationalesNaturmonument",
                        "description": "Nationales Naturmonument gemäß §24 Abs. (4)  BNatSchG.",
                    },
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstiges Naturschutzgebiet",
                    },
                },
            },
        ),
    ] = None
    istKernzone: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob es sich um eine Kernzone handelt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False


class RPRadwegWanderweg(RPFreiraum):
    """
    Radwege und Wanderwege. Straßenbegleitend oder selbstständig geführt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[Literal["1000", "1001", "2000", "2001", "3000", "4000", "9999"]] | None,
        Field(
            description="Klassifikation von Radwegen und Wanderwegen.",
            json_schema_extra={
                "typename": "RP_RadwegWanderwegTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Wanderweg", "description": "Wanderweg."},
                    "1001": {"name": "Fernwanderweg", "description": "Fernwanderweg."},
                    "2000": {"name": "Radwandern", "description": "Radwandern."},
                    "2001": {"name": "Fernradweg", "description": "Fernradweg."},
                    "3000": {"name": "Reiten", "description": "Reiten."},
                    "4000": {"name": "Wasserwandern", "description": "Wasserwandern."},
                    "9999": {
                        "name": "SonstigerWanderweg",
                        "description": "Sonstiger Wanderweg.",
                    },
                },
            },
        ),
    ] = None


class RPRohstoff(RPFreiraum):
    """
    Rohstoff, inklusive Rohstoffprospektion, Rohstoffsicherung, Rohstoffabbau, Bergbau und Bergbaufolgelandschaft.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    rohstoffTyp: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "1300",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "1900",
                "2000",
                "2100",
                "2200",
                "2300",
                "2400",
                "2500",
                "2600",
                "2700",
                "2800",
                "2900",
                "3000",
                "3100",
                "3200",
                "3300",
                "3400",
                "3500",
                "3600",
                "3700",
                "3800",
                "3900",
                "4000",
                "4100",
                "4200",
                "4300",
                "4400",
                "4500",
                "4600",
                "4700",
                "4800",
                "4900",
                "5000",
                "5100",
                "5200",
                "5300",
                "5400",
                "5500",
                "5600",
                "5700",
                "5800",
                "5900",
                "6000",
                "6100",
                "6200",
                "6300",
                "6400",
                "6500",
                "6600",
                "6700",
                "6800",
                "6900",
                "7000",
                "7100",
                "7200",
                "7300",
                "7400",
                "7500",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Abgebauter Rohstoff.",
            json_schema_extra={
                "typename": "RP_RohstoffTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Anhydritstein", "description": "Anhydritstein."},
                    "1100": {"name": "Baryt", "description": "Baryt."},
                    "1200": {"name": "BasaltDiabas", "description": "BasaltDiabas."},
                    "1300": {"name": "Bentonit", "description": "Bentonit."},
                    "1400": {"name": "Blaehton", "description": "Blaehton."},
                    "1500": {"name": "Braunkohle", "description": "Braunkohle."},
                    "1600": {"name": "Buntsandstein", "description": "Buntsandstein."},
                    "1700": {"name": "Dekostein", "description": "Dekostein"},
                    "1800": {"name": "Diorit", "description": "Diorit."},
                    "1900": {"name": "Dolomitstein", "description": "Dolomitstein."},
                    "2000": {"name": "Erdgas", "description": "Erdgas."},
                    "2100": {"name": "Erdoel", "description": "Erdöl."},
                    "2200": {"name": "Erz", "description": "Erz."},
                    "2300": {"name": "Feldspat", "description": "Feldspat."},
                    "2400": {"name": "Festgestein", "description": "Festgestein."},
                    "2500": {"name": "Flussspat", "description": "Flussspat."},
                    "2600": {"name": "Gangquarz", "description": "Gangquarz."},
                    "2700": {"name": "Gipsstein", "description": "Gipsstein."},
                    "2800": {"name": "Gneis", "description": "Gneis."},
                    "2900": {"name": "Granit", "description": "Granit."},
                    "3000": {"name": "Grauwacke", "description": "Grauwacke."},
                    "3100": {"name": "Hartgestein", "description": "Hartgestein"},
                    "3200": {
                        "name": "KalkKalktuffKreide",
                        "description": "KalkKalktuffKreide.",
                    },
                    "3300": {
                        "name": "Kalkmergelstein",
                        "description": "Kalkmergelstein.",
                    },
                    "3400": {"name": "Kalkstein", "description": "Kalkstein."},
                    "3500": {"name": "Kaolin", "description": "Kaolin."},
                    "3600": {
                        "name": "Karbonatgestein",
                        "description": "Karbonatgestein.",
                    },
                    "3700": {"name": "Kies", "description": "Kies."},
                    "3800": {"name": "Kieselgur", "description": "Kieselgur."},
                    "3900": {
                        "name": "KieshaltigerSand",
                        "description": "KieshaltigerSand.",
                    },
                    "4000": {"name": "KiesSand", "description": "KiesSand."},
                    "4100": {"name": "Klei", "description": "Klei."},
                    "4200": {"name": "Kristallin", "description": "Kristallin."},
                    "4300": {"name": "Kupfer", "description": "Kupfer."},
                    "4400": {"name": "Lehm", "description": "Lehm."},
                    "4500": {"name": "Marmor", "description": "Marmor."},
                    "4600": {"name": "Mergel", "description": "Mergel."},
                    "4700": {"name": "Mergelstein", "description": "Mergelstein."},
                    "4800": {
                        "name": "MikrogranitGranitporphyr",
                        "description": "MikrogranitGranitporphyr.",
                    },
                    "4900": {"name": "Monzonit", "description": "Monzonit."},
                    "5000": {"name": "Muschelkalk", "description": "Muschelkalk."},
                    "5100": {"name": "Naturstein", "description": "Naturstein."},
                    "5200": {
                        "name": "Naturwerkstein",
                        "description": "Naturwerkstein.",
                    },
                    "5300": {"name": "Oelschiefer", "description": "Ölschiefer."},
                    "5400": {"name": "Pegmatitsand", "description": "Pegmatitsand."},
                    "5500": {"name": "Quarzit", "description": "Quarzit."},
                    "5600": {"name": "Quarzsand", "description": "Quarzsand."},
                    "5700": {"name": "Rhyolith", "description": "Rhyolith."},
                    "5800": {
                        "name": "RhyolithQuarzporphyr",
                        "description": "RhyolithQuarzporphyr.",
                    },
                    "5900": {"name": "Salz", "description": "Salz."},
                    "6000": {"name": "Sand", "description": "Sand."},
                    "6100": {"name": "Sandstein", "description": "Sandstein."},
                    "6200": {"name": "Spezialton", "description": "Spezialton."},
                    "6300": {
                        "name": "SteineundErden",
                        "description": "Steine und Erden.",
                    },
                    "6400": {"name": "Steinkohle", "description": "Steinkohle."},
                    "6500": {"name": "Ton", "description": "Ton."},
                    "6600": {"name": "Tonstein", "description": "Tonstein."},
                    "6700": {"name": "Torf", "description": "Torf."},
                    "6800": {"name": "TuffBimsstein", "description": "TuffBimsstein."},
                    "6900": {"name": "Uran", "description": "Uran."},
                    "7000": {"name": "Vulkanit", "description": "Vulkanit."},
                    "7100": {"name": "Werkstein", "description": "Werkstein"},
                    "7200": {"name": "Andesit", "description": "Andesit"},
                    "7300": {"name": "Formsand", "description": "Formsand"},
                    "7400": {"name": "Gabbro", "description": "Gabbro"},
                    "7500": {
                        "name": "MikrodioritKuselit",
                        "description": "Mikrodiorit Kuselit",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstiges."},
                },
            },
        ),
    ] = None
    detaillierterRohstoffTyp: Annotated[
        list[str] | None,
        Field(
            description="Abgebauer Rohstoff in Textform",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..*",
            },
        ),
    ] = None
    folgenutzung: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "3000",
                "4000",
                "5000",
                "6000",
                "7000",
                "8000",
                "9000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Folgenutzungen bestimmter bergbaulicher Maßnahmen.",
            json_schema_extra={
                "typename": "RP_BergbauFolgenutzung",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Landwirtschaft",
                        "description": "Folgenutzung Landwirtschaft.",
                    },
                    "2000": {
                        "name": "Forstwirtschaft",
                        "description": "Folgenutzung Forstwirtschaft.",
                    },
                    "3000": {
                        "name": "Gruenlandbewirtschaftung",
                        "description": "Folgenutzung Grünlandbewirtschaftung.",
                    },
                    "4000": {
                        "name": "NaturLandschaft",
                        "description": "Folgenutzung NaturLandschaft.",
                    },
                    "5000": {
                        "name": "Naturschutz",
                        "description": "Folgenutzung Naturschutz.",
                    },
                    "6000": {
                        "name": "Erholung",
                        "description": "Folgenutzung Erholung.",
                    },
                    "7000": {
                        "name": "Gewaesser",
                        "description": "Folgenutzung Gewässer.",
                    },
                    "8000": {"name": "Verkehr", "description": "Folgenutzung Verkehr."},
                    "9000": {
                        "name": "Altbergbau",
                        "description": "Folgenutzung Altbergbau.",
                    },
                    "9999": {
                        "name": "SonstigeNutzung",
                        "description": "Sonstige Folgenutzung.",
                    },
                },
            },
        ),
    ] = None
    folgenutzungText: Annotated[
        str | None,
        Field(
            description="Textliche Festlegungen und Spezifizierungen zur Folgenutzung einer Bergbauplanung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zeitstufe: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Zeitstufe des Rohstoffabbaus.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Zeitstufe1", "description": "Zeitstufe 1."},
                    "2000": {"name": "Zeitstufe2", "description": "Zeitstufe 2."},
                },
                "typename": "RP_Zeitstufen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zeitstufeText: Annotated[
        str | None,
        Field(
            description="Textliche Spezifizierung einer Rohstoffzeitstufe, zum Beispiel kurzfristiger Abbau (Zeitstufe I) und langfristige Sicherung für mindestens 25-30 Jahre (Zeitstufe II).",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    tiefe: Annotated[
        Literal["1000", "2000"] | None,
        Field(
            description="Tiefe eines Rohstoffes",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Oberflaechennah",
                        "description": "Oberflächennaher Bodenschatz.",
                    },
                    "2000": {
                        "name": "Tiefliegend",
                        "description": "Tiefliegender Bodenschatz.",
                    },
                },
                "typename": "RP_BodenschatzTiefen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    bergbauplanungTyp: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "1300",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "1900",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Bergbauplanungstypen.",
            json_schema_extra={
                "typename": "RP_BergbauplanungTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Lagerstaette", "description": "Lagerstätte."},
                    "1100": {"name": "Sicherung", "description": "Sicherung."},
                    "1200": {"name": "Gewinnung", "description": "Gewinnung."},
                    "1300": {"name": "Abbau", "description": "Abbaubereich."},
                    "1400": {
                        "name": "Sicherheitszone",
                        "description": "Sicherheitszone.",
                    },
                    "1500": {
                        "name": "AnlageEinrichtungBergbau",
                        "description": "Anlage und/oder Einrichtung des Bergbaus.",
                    },
                    "1600": {
                        "name": "Halde",
                        "description": "Halde, Aufschüttung und/oder Ablagerung.",
                    },
                    "1700": {
                        "name": "Sanierungsflaeche",
                        "description": "Sanierungsfläche.",
                    },
                    "1800": {
                        "name": "AnsiedlungUmsiedlung",
                        "description": "Ansiedlung und/oder Umsiedlung.",
                    },
                    "1900": {
                        "name": "Bergbaufolgelandschaft",
                        "description": "Bergbaufolgelandschaft.",
                    },
                    "9999": {
                        "name": "SonstigeBergbauplanung",
                        "description": "Sonstige Bergbauplanung.",
                    },
                },
            },
        ),
    ] = None
    istAufschuettungAblagerung: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob der Rohstoff aus einer Aufschüttung oder Ablagerung gewonnen wird",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False


class RPSchienenverkehr(RPVerkehr):
    """
    Schienenverkehr-Infrastruktur.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1002",
                "1100",
                "1200",
                "1300",
                "1301",
                "1302",
                "1303",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "1801",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Schienenverkehr-Infrastruktur.",
            json_schema_extra={
                "typename": "RP_SchienenverkehrTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Schienenverkehr",
                        "description": "Schienenverkehr.",
                    },
                    "1001": {
                        "name": "Eisenbahnstrecke",
                        "description": "Eisenbahnstrecke.",
                    },
                    "1002": {
                        "name": "Haupteisenbahnstrecke",
                        "description": "Haupteisenbahnstrecke.",
                    },
                    "1100": {"name": "Trasse", "description": "Trasse."},
                    "1200": {"name": "Schienennetz", "description": "Schienennetz."},
                    "1300": {"name": "Stadtbahn", "description": "Stadtbahn."},
                    "1301": {"name": "Strassenbahn", "description": "Straßenbahn."},
                    "1302": {"name": "SBahn", "description": "S-Bahn."},
                    "1303": {"name": "UBahn", "description": "U-Bahn."},
                    "1400": {
                        "name": "AnschlussgleisIndustrieGewerbe",
                        "description": "Anschlussgleis für Industrie und Gewerbe.",
                    },
                    "1500": {"name": "Haltepunkt", "description": "Haltepunkt."},
                    "1600": {"name": "Bahnhof", "description": "Bahnhof."},
                    "1700": {
                        "name": "Hochgeschwindigkeitsverkehr",
                        "description": "Hochgeschwindigkeitsverkehr.",
                    },
                    "1800": {
                        "name": "Bahnbetriebsgelaende",
                        "description": "Bahnbetriebsgelände.",
                    },
                    "1801": {
                        "name": "AnlagemitgrossemFlaechenbedarf",
                        "description": "Anlage mit großem Flächenbedarf.",
                    },
                    "9999": {
                        "name": "SonstigerSchienenverkehr",
                        "description": "Sonstiger Schienenverkehr.",
                    },
                },
            },
        ),
    ] = None
    besondererTyp: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1002",
                "2000",
                "3000",
                "3001",
                "4000",
                "4001",
                "5000",
                "6000",
                "6001",
                "7000",
                "7001",
                "8000",
                "8001",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von besonderer Schienenverkehr-Infrastruktur.",
            json_schema_extra={
                "typename": "RP_BesondererSchienenverkehrTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Eingleisig", "description": "Eingleisig."},
                    "1001": {"name": "Zweigleisig", "description": "Zweigleisig."},
                    "1002": {"name": "Mehrgleisig", "description": "Mehrgleisig."},
                    "2000": {
                        "name": "OhneBetrieb",
                        "description": "Schienenverkehrsinfrastruktur ohne Betrieb.",
                    },
                    "3000": {
                        "name": "MitFernverkehrsfunktion",
                        "description": "Schienenverkehrsinfrastruktur mit Fernverkehrsfunktion.",
                    },
                    "3001": {
                        "name": "MitVerknuepfungsfunktionFuerOEPNV",
                        "description": "Schienenverkehrsinfrastruktur mit Verknüpfungsfunktion für den öffentlichen Personennahverkehr.",
                    },
                    "4000": {
                        "name": "ElektrischerBetrieb",
                        "description": "Elektrischer Betrieb.",
                    },
                    "4001": {
                        "name": "ZuElektrifizieren",
                        "description": "Zu Elektrifizieren.",
                    },
                    "5000": {
                        "name": "VerbesserungLeistungsfaehigkeit",
                        "description": "Verbesserung der Leistungsfähigkeit.",
                    },
                    "6000": {
                        "name": "RaeumlicheFreihaltungentwidmeterBahntrassen",
                        "description": "Räumliche Freihaltung entwidmeter Bahntrassen.",
                    },
                    "6001": {
                        "name": "NachnutzungstillgelegterStrecken",
                        "description": "Nachnutzung stillgelegter Strecken.",
                    },
                    "7000": {
                        "name": "Personenverkehr",
                        "description": "Personenverkehr.",
                    },
                    "7001": {"name": "Gueterverkehr", "description": "Güterverkehr."},
                    "8000": {"name": "Nahverkehr", "description": "Nahverkehr."},
                    "8001": {"name": "Fernverkehr", "description": "Fernverkehr."},
                },
            },
        ),
    ] = None


class RPSonstVerkehr(RPVerkehr):
    """
    Sonstige Verkehrsinfrastruktur, die sich nicht eindeutig einem anderen Typ zuordnen lässt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1100",
                "1200",
                "1300",
                "1400",
                "1500",
                "1600",
                "1700",
                "1800",
                "1900",
                "2000",
                "2001",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Sonstige Klassifikation von Verkehrs-Infrastruktur.",
            json_schema_extra={
                "typename": "RP_SonstVerkehrTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Verkehrsanlage",
                        "description": "Verkehrsanlage.",
                    },
                    "1100": {
                        "name": "Gueterverkehrszentrum",
                        "description": "Güterverkehrszentrum.",
                    },
                    "1200": {
                        "name": "Logistikzentrum",
                        "description": "Logistikzentrum.",
                    },
                    "1300": {
                        "name": "TerminalkombinierterVerkehr",
                        "description": "Terminal des kombinierten Verkehrs.",
                    },
                    "1400": {"name": "OEPNV", "description": "ÖPNV."},
                    "1500": {
                        "name": "VerknuepfungspunktBahnBus",
                        "description": "Verknüpfungspunkt Bahn-Bus.",
                    },
                    "1600": {
                        "name": "ParkandRideBikeandRide",
                        "description": "Park-and-Ride und/oder Bike-and-Ride.",
                    },
                    "1700": {"name": "Faehrverkehr", "description": "Fährverkehr."},
                    "1800": {
                        "name": "Infrastrukturkorridor",
                        "description": "Infrastrukturkorridor.",
                    },
                    "1900": {"name": "Tunnel", "description": "Tunnel."},
                    "2000": {
                        "name": "NeueVerkehrstechniken",
                        "description": "Neue Verkehrstechniken.",
                    },
                    "2001": {
                        "name": "Teststrecke",
                        "description": "Sicherung von Teststrecken für die Fahrzeugindustrie und Sicherung von Gebieten zur Entwicklung damit verbundener neuer Verkehrssysteme und -techniken.",
                    },
                    "9999": {
                        "name": "SonstigerVerkehr",
                        "description": "Sonstiger Verkehr.",
                    },
                },
            },
        ),
    ] = None


class RPSonstigerFreiraumschutz(RPFreiraum):
    """
    Sonstiger Freiraumschutz. Nicht anderweitig zuzuordnende Freiraumstrukturen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"


class RPSportanlage(RPFreiraum):
    """
    Sportanlagen und -bereiche.
    Sportanlagen sind ortsfeste Einrichtungen, die zur Sportausübung bestimmt sind. Zur Sportanlage zählen auch Einrichtungen, die mit der Sportanlage in einem engen räumlichen und betrieblichen Zusammenhang stehen (nach BImSchV 18 §1).
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "6000", "7000", "9999"] | None,
        Field(
            description="Klassifikation von Sportanlagen.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Sportanlage", "description": "Sportanlage."},
                    "2000": {"name": "Wassersport", "description": "Wassersport."},
                    "3000": {"name": "Motorsport", "description": "Motorsport."},
                    "4000": {"name": "Flugsport", "description": "Flugsport."},
                    "5000": {"name": "Reitsport", "description": "Reitsport."},
                    "6000": {"name": "Golfsport", "description": "Golfsport."},
                    "7000": {"name": "Sportzentrum", "description": "Sportzentrum."},
                    "9999": {
                        "name": "SonstigeSportanlage",
                        "description": "Sonstige Sportanlage.",
                    },
                },
                "typename": "RP_SportanlageTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPStrassenverkehr(RPVerkehr):
    """
    Strassenverkehr-Infrastruktur.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        list[
            Literal[
                "1000",
                "1001",
                "1002",
                "1003",
                "1004",
                "1005",
                "1006",
                "1007",
                "2000",
                "3000",
                "4000",
                "5000",
                "6000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Strassenverkehr-Infrastruktur.",
            json_schema_extra={
                "typename": "RP_StrassenverkehrTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Strassenverkehr",
                        "description": "Straßenverkehr.",
                    },
                    "1001": {
                        "name": "Hauptverkehrsstrasse",
                        "description": "Hauptverkehrsstraße.",
                    },
                    "1002": {"name": "Autobahn", "description": "Autobahn."},
                    "1003": {"name": "Bundesstrasse", "description": "Bundesstraße."},
                    "1004": {"name": "Staatsstrasse", "description": "Staatsstraße."},
                    "1005": {"name": "Landesstrasse", "description": "Landesstraße."},
                    "1006": {"name": "Kreisstrasse", "description": "Kreisstraße."},
                    "1007": {"name": "Fernstrasse", "description": "Fernstraße."},
                    "2000": {"name": "Trasse", "description": "Trasse."},
                    "3000": {"name": "Strassennetz", "description": "Straßennetz."},
                    "4000": {"name": "Busverkehr", "description": "Busverkehr."},
                    "5000": {
                        "name": "Anschlussstelle",
                        "description": "Anschlussstelle.",
                    },
                    "6000": {"name": "Strassentunnel", "description": "Straßentunnel."},
                    "9999": {
                        "name": "SonstigerStrassenverkehr",
                        "description": "Sonstiger Straßenverkehr.",
                    },
                },
            },
        ),
    ] = None
    besondererTyp: Annotated[
        list[Literal["1000", "1001", "1002", "1003", "2000", "3000"]] | None,
        Field(
            description="Klassifikation von besonderer Strassenverkehr-Infrastruktur.",
            json_schema_extra={
                "typename": "RP_BesondererStrassenverkehrTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Zweistreifig", "description": "Zweistreifig."},
                    "1001": {"name": "Dreistreifig", "description": "Dreistreifig."},
                    "1002": {"name": "Vierstreifig", "description": "Vierstreifig."},
                    "1003": {"name": "Sechsstreifig", "description": "Sechsstreifig."},
                    "2000": {
                        "name": "Problembereich",
                        "description": "Problembereich.",
                    },
                    "3000": {
                        "name": "GruenbrueckeQuerungsmoeglichkeit",
                        "description": "Grünbrückenquerungsmöglichkeit.",
                    },
                },
            },
        ),
    ] = None


class RPWasserschutz(RPFreiraum):
    """
    Grund-, Trink- und Oberflächenwasserschutz.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal[
            "1000",
            "2000",
            "2001",
            "2002",
            "3000",
            "4000",
            "5000",
            "6000",
            "7000",
            "9999",
        ]
        | None,
        Field(
            description="Klassifikation des Wasserschutztyps.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Wasserschutzgebiet",
                        "description": 'Wasserschutzgebiet.\r\nNach DIN 4046 "Einzugsgebiet oder Teil des Einzugsgebietes einer Wassergewinnungsanlage, das zum Schutz des Wassers Nutzungsbeschränkungen unterliegt."',
                    },
                    "2000": {
                        "name": "Grundwasserschutz",
                        "description": "Grundwasserschutz.",
                    },
                    "2001": {
                        "name": "Grundwasservorkommen",
                        "description": "Grundwasservorkommen.",
                    },
                    "2002": {
                        "name": "Gewaesserschutz",
                        "description": "Einzugsgebiet einer Talsperre.",
                    },
                    "3000": {
                        "name": "Trinkwasserschutz",
                        "description": "Trinkwasserschutz.",
                    },
                    "4000": {
                        "name": "Trinkwassergewinnung",
                        "description": "Trinkwassergewinnung.",
                    },
                    "5000": {
                        "name": "Oberflaechenwasserschutz",
                        "description": "Oberflächenwasserschutz.",
                    },
                    "6000": {"name": "Heilquelle", "description": "Heilquelle."},
                    "7000": {
                        "name": "Wasserversorgung",
                        "description": "Wasserversorgung.",
                    },
                    "9999": {
                        "name": "SonstigerWasserschutz",
                        "description": "Sonstiger Wasserschutz.",
                    },
                },
                "typename": "RP_WasserschutzTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    zone: Annotated[
        list[Literal["1000", "2000", "3000"]] | None,
        Field(
            description="Wasserschutzzone",
            json_schema_extra={
                "typename": "RP_WasserschutzZonen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {
                        "name": "Zone1",
                        "description": "Zone 1.\r\nFür Grundwasser beinhaltet die Zone 1 den Fassungsbereich. In diesem Bereich und der unmittelbaren Umgebung um die Wassergewinnungsanlage muss jegliche Verunreinigung unterbleiben. Bei Talsperren  beinhaltet die Zone 1 den Stauraum mit Uferzone. Diese soll den Schutz vor unmittelbaren Verunreinigungen und sonstigen Beeinträchtigungen des Talsperrenwassers gewährleisten.\r\nDie Ausdehnung der Zone I sollte im allgemeinen von Brunnen allseitig 10 m, von Quellen in Richtung des ankommenden Grundwassers mindestens 20 m und von Kaarstgrundwasserleitern mindestens 30 m betragen",
                    },
                    "2000": {
                        "name": "Zone2",
                        "description": "Zone 2.\r\nDie engere Schutzzone.\r\nDie Zone II reicht von der Grenze der Zone I bis zu einer Linie, von der aus das Grundwasser etwa 50 Tage bis zum Eintreffen in die Trinkwassergewinnungsanlage benötigt. Eine Zone II kann entfallen, wenn nur tiefere, abgedichtete Grundwasserstockwerke oder solche genutzt werden, die von der 50 Tage-Linie bis zur Fassung von undurchlässigen Schichten gegenüber der Mächtigkeit abgedeckt sind.",
                    },
                    "3000": {
                        "name": "Zone3",
                        "description": "Zone 3.\r\nDie Weitere Schutzzone.\r\nDie Zone III reicht von der Grenze des Einzugsgebietes bis zur Außengrenze der Zone II. Wenn das Einzugsgebiet weiter als 2 km reicht, so kann eine Aufgliederung in eine Zone III A bis etwa 2 km Entfernung ab Fassung und eine Zone III B etwa 2 km bis zur Grenze des Einzugsgebietes zweckmäßig sein.",
                    },
                },
            },
        ),
    ] = None


class SOBauverbotszone(SOGeometrieobjekt):
    """
    Bereich, in denen Verbote oder Beschränkungen für die Errichtung baulicher Anlagen bestehen
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal["1000", "2000", "3000", "9999"] | None,
        Field(
            description="Klassifizierung des Bauverbots bzw. der Baubeschränkung",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Bauverbotszone",
                        "description": "Bereich, in denen keine baulichen Anlagen errichtet werden dürfen",
                    },
                    "2000": {
                        "name": "Baubeschraenkungszone",
                        "description": "Bereich, in denen Bau-Beschränkungen bestehen.",
                    },
                    "3000": {
                        "name": "Waldabstand",
                        "description": "Bereich um Wälder, Moore und Heiden, in dem aus Brandschutzgründen keinen baulichen Anlagen errichtet werden dürfen.",
                    },
                    "9999": {
                        "name": "SonstigeBeschraenkung",
                        "description": "Bereich mit sonstigen Baubeschränkungen.",
                    },
                },
                "typename": "SO_KlassifizBauverbot",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Detaillierte Klassifizierung des Bauverbots bzw. der Baubeschränkung über eine Codeliste",
            json_schema_extra={
                "typename": "SO_DetailKlassifizBauverbot",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    rechtlicheGrundlage: Annotated[
        Literal["1000", "2000", "9999"] | None,
        Field(
            description="Rechtliche Grundlage des Bauverbots bzw. der Baubeschränkung",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Luftverkehrsrecht",
                        "description": "Luftverkehrsrecht",
                    },
                    "2000": {
                        "name": "Strassenverkehrsrecht",
                        "description": "Strassenverkehrsrecht",
                    },
                    "9999": {
                        "name": "SonstigesRecht",
                        "description": "Sonstige Rechtsverordnung",
                    },
                },
                "typename": "SO_RechtlicheGrundlageBauverbot",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle bezeichnung der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOBodenschutzrecht(SOGeometrieobjekt):
    """
    Festlegung nach Bodenschutzrecht.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal["1000", "2000", "20000", "20001", "20002"] | None,
        Field(
            description="Klassifizierung der Festlegung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "SchaedlicheBodenveraenderung",
                        "description": "Schädliche Bodenveränderung",
                    },
                    "2000": {"name": "Altlast", "description": "Altlast"},
                    "20000": {"name": "Altablagerung", "description": "Altablagerung"},
                    "20001": {"name": "Altstandort", "description": "Altstandort"},
                    "20002": {
                        "name": "AltstandortAufAltablagerung",
                        "description": "Altstandort einer Altablagerung",
                    },
                },
                "typename": "SO_KlassifizNachBodenschutzrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Klassifizierung der Festlegung.",
            json_schema_extra={
                "typename": "SO_DetailKlassifizNachBodenschutzrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    istVerdachtsflaeche: Annotated[
        bool | None,
        Field(
            description="Angabe ob es sich um eine Verdachtsfläche handelt.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung der Festlegung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Festlegung. bzw. Nummer in einem Altlast-Kataster",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SODenkmalschutzrecht(SOGeometrieobjekt):
    """
    Festlegung nach Denkmalschutzrecht
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal["1000", "1100", "1200", "1300", "1400", "1500", "1600", "9999"] | None,
        Field(
            description="Rechtliche Klassifizierung der Festlegung",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "DenkmalschutzEnsemble",
                        "description": "Denkmalschutz Ensemble",
                    },
                    "1100": {
                        "name": "DenkmalschutzEinzelanlage",
                        "description": "Denkmalschutz Einzelanlage",
                    },
                    "1200": {
                        "name": "Grabungsschutzgebiet",
                        "description": "Grabungsschutzgebiet",
                    },
                    "1300": {
                        "name": "PufferzoneWeltkulturerbeEnger",
                        "description": "Engere Pufferzone um eine Welterbestätte",
                    },
                    "1400": {
                        "name": "PufferzoneWeltkulturerbeWeiter",
                        "description": "Weitere Pufferzone um eine Welterbestätte",
                    },
                    "1500": {
                        "name": "ArcheologischesDenkmal",
                        "description": "Archäologisches Denkmal",
                    },
                    "1600": {"name": "Bodendenkmal", "description": "Bodendenkmal"},
                    "9999": {
                        "name": "Sonstiges",
                        "description": "Sonstige Klassifizierung nach Denkmalschutzrecht.",
                    },
                },
                "typename": "SO_KlassifizNachDenkmalschutzrecht",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere rechtliche Klassifizierung der Festlegung.",
            json_schema_extra={
                "typename": "SO_DetailKlassifizNachDenkmalschutzrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    weltkulturerbe: Annotated[
        bool | None,
        Field(
            description="Gibt an, ob das geschützte Objekt zum Weltkulturerbe gehört.",
            json_schema_extra={
                "typename": "Boolean",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = False
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Festlegung.",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOForstrecht(SOGeometrieobjekt):
    """
    Festlegung nach Forstrecht
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "12000",
            "12001",
            "2000",
            "20000",
            "20001",
            "3000",
            "9999",
        ]
        | None,
        Field(
            description="Klassifizierung der Eigentumsart des Waldes.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "OeffentlicherWald",
                        "description": "Öffentlicher Wald allgemein",
                    },
                    "1100": {"name": "Staatswald", "description": "Staatswald"},
                    "1200": {
                        "name": "Koerperschaftswald",
                        "description": "Körperschaftswald",
                    },
                    "12000": {"name": "Kommunalwald", "description": "Kommunalwald"},
                    "12001": {"name": "Stiftungswald", "description": "Stiftungswald"},
                    "2000": {
                        "name": "Privatwald",
                        "description": "Privatwald allgemein",
                    },
                    "20000": {
                        "name": "Gemeinschaftswald",
                        "description": "Gemeinschaftswald",
                    },
                    "20001": {
                        "name": "Genossenschaftswald",
                        "description": "Genossenschaftswald",
                    },
                    "3000": {"name": "Kirchenwald", "description": "Kirchenwald"},
                    "9999": {"name": "Sonstiges", "description": "Sonstiger Wald"},
                },
                "typename": "XP_EigentumsartWald",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Klassifizierung der Eigentumsart des Waldes",
            json_schema_extra={
                "typename": "SO_DetailKlassifizNachForstrecht",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    funktion: Annotated[
        list[
            Literal[
                "1000",
                "10000",
                "1200",
                "1400",
                "1600",
                "16000",
                "16001",
                "16002",
                "16003",
                "16004",
                "1700",
                "1800",
                "1900",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifizierung der Fukktion des Waldes",
            json_schema_extra={
                "typename": "XP_ZweckbestimmungWald",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Naturwald", "description": "Naturwald"},
                    "10000": {
                        "name": "Waldschutzgebiet",
                        "description": "Waldschutzgebiet",
                    },
                    "1200": {"name": "Nutzwald", "description": "Nutzwald"},
                    "1400": {"name": "Erholungswald", "description": "Erholungswald"},
                    "1600": {"name": "Schutzwald", "description": "Schutzwald"},
                    "16000": {
                        "name": "Bodenschutzwald",
                        "description": "Bodenschutzwald",
                    },
                    "16001": {
                        "name": "Biotopschutzwald",
                        "description": "Biotopschutzwald",
                    },
                    "16002": {
                        "name": "NaturnaherWald",
                        "description": "Naturnaher Wald",
                    },
                    "16003": {
                        "name": "SchutzwaldSchaedlicheUmwelteinwirkungen",
                        "description": "Wald zum Schutz vor schädlichen Umwelteinwirkungen",
                    },
                    "16004": {"name": "Schonwald", "description": "Schonwald"},
                    "1700": {"name": "Bannwald", "description": "Bannwald"},
                    "1800": {
                        "name": "FlaecheForstwirtschaft",
                        "description": "Fläche für die Forstwirtschaft.",
                    },
                    "1900": {
                        "name": "ImmissionsgeschaedigterWald",
                        "description": "Immissionsgeschädigter Wald",
                    },
                    "9999": {"name": "Sonstiges", "description": "Sonstigr Wald"},
                },
            },
        ),
    ] = None
    betreten: Annotated[
        list[Literal["1000", "2000", "3000", "4000"]] | None,
        Field(
            description="Festlegung zusätzlicher, normalerweise nicht-gestatteter Aktivitäten, die in dem Wald ausgeführt werden dürfen, nach §14 Abs. 2 Bundeswaldgesetz.",
            json_schema_extra={
                "typename": "XP_WaldbetretungTyp",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Radfahren", "description": "Radfahren"},
                    "2000": {"name": "Reiten", "description": "Reiten"},
                    "3000": {"name": "Fahren", "description": "Fahren"},
                    "4000": {"name": "Hundesport", "description": "Hundesport"},
                },
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Festlegung",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOGelaendemorphologie(SOGeometrieobjekt):
    """
    Das Landschaftsbild prägende Geländestruktur
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    artDerFestlegung: Annotated[
        Literal["1000", "1100", "1200", "9999"] | None,
        Field(
            description="Klassifikation der Geländestruktur",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Terassenkante", "description": "Terrassenkante"},
                    "1100": {
                        "name": "Rinne",
                        "description": "Trockengefallene Gewässerrinne",
                    },
                    "1200": {
                        "name": "EhemMaeander",
                        "description": "Ehemalige Fluss- und Bachmäander",
                    },
                    "9999": {
                        "name": "SonstigeStruktur",
                        "description": "Sonstige Struktur der Geländemorphologie",
                    },
                },
                "typename": "SO_KlassifizGelaendemorphologie",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    detailArtDerFestlegung: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte detailliertere Klassifikation der Geländestruktur",
            json_schema_extra={
                "typename": "SO_DetailKlassifizGelaendemorphologie",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="Informelle Bezeichnung der Struktur",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    nummer: Annotated[
        str | None,
        Field(
            description="Amtliche Bezeichnung / Kennziffer der Struktur",
            json_schema_extra={
                "typename": "CharacterString",
                "stereotype": "BasicType",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class SOGrenze(SOLinienobjekt):
    """
    Grenze einer Verwaltungseinheit oder sonstige Grenze in raumbezogenen Plänen.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal[
            "1000",
            "1100",
            "1200",
            "1250",
            "1300",
            "1400",
            "1450",
            "1500",
            "1510",
            "1550",
            "1600",
            "2000",
            "2100",
            "9999",
        ]
        | None,
        Field(
            description="Typ der Grenze",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Bundesgrenze", "description": "Bundesgrenze"},
                    "1100": {
                        "name": "Landesgrenze",
                        "description": "Grenze eines Bundeslandes",
                    },
                    "1200": {
                        "name": "Regierungsbezirksgrenze",
                        "description": "Grenze eines Regierungsbezirks",
                    },
                    "1250": {
                        "name": "Bezirksgrenze",
                        "description": "Grenze eines Bezirks.",
                    },
                    "1300": {
                        "name": "Kreisgrenze",
                        "description": "Grenze eines Kreises.",
                    },
                    "1400": {
                        "name": "Gemeindegrenze",
                        "description": "Grenze einer Gemeinde.",
                    },
                    "1450": {
                        "name": "Verbandsgemeindegrenze",
                        "description": "Grenze einer Verbandsgemeinde",
                    },
                    "1500": {
                        "name": "Samtgemeindegrenze",
                        "description": "Grenze einer Samtgemeinde",
                    },
                    "1510": {
                        "name": "Mitgliedsgemeindegrenze",
                        "description": "Mitgliedsgemeindegrenze",
                    },
                    "1550": {"name": "Amtsgrenze", "description": "Amtsgrenze"},
                    "1600": {
                        "name": "Stadtteilgrenze",
                        "description": "Stadtteilgrenze",
                    },
                    "2000": {
                        "name": "VorgeschlageneGrundstuecksgrenze",
                        "description": "Hinweis auf eine vorgeschlagene Grundstücksgrenze im BPlan.",
                    },
                    "2100": {
                        "name": "GrenzeBestehenderBebauungsplan",
                        "description": "Hinweis auf den Geltungsbereich eines bestehenden BPlan.",
                    },
                    "9999": {"name": "SonstGrenze", "description": "Sonstige Grenze"},
                },
                "typename": "XP_GrenzeTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
    sonstTyp: Annotated[
        AnyUrl | None,
        Field(
            description="Über eine Codeliste definierte weitere Grenztypen, wenn das Attribut typ den Wert 9999 hat.",
            json_schema_extra={
                "typename": "SO_SonstGrenzeTypen",
                "stereotype": "Codelist",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPBodenschutz(RPFreiraum):
    """
    Maßnahmen, die zum Schutz von Böden und Bodenfunktionen (auch vorsorglich) unter dem Aspekt des Natur- und Umweltschutzes getroffen werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000", "4000", "9999"] | None,
        Field(
            description="Klassifikation von Bodenschutztypen.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "BeseitigungErheblicherBodenbelastung",
                        "description": "Beseitigung von erheblicher Bodenbelastung.",
                    },
                    "2000": {
                        "name": "SicherungSanierungAltlasten",
                        "description": "Sicherung und/oder Sanierung von Altlasten.",
                    },
                    "3000": {
                        "name": "Erosionsschutz",
                        "description": "Erosionsschutz.",
                    },
                    "4000": {
                        "name": "Torferhalt",
                        "description": "Bodenschutz zum Torferhalt dient dem Erhalt von vorhandenen Torfkörpern als natürlichen Speicher von Kohlenstoffen, als Beitrag zum Klimaschutz.",
                    },
                    "9999": {
                        "name": "SonstigerBodenschutz",
                        "description": "Sonstiger Bodenschutz.",
                    },
                },
                "typename": "RP_BodenschutzTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPErholung(RPFreiraum):
    """
    Freizeit, Erholung und Tourismus.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typErholung: Annotated[
        list[
            Literal[
                "1000",
                "2000",
                "2001",
                "3000",
                "3001",
                "4000",
                "5000",
                "5001",
                "6000",
                "7000",
                "9999",
            ]
        ]
        | None,
        Field(
            description="Klassifikation von Erholungstypen.",
            json_schema_extra={
                "typename": "RP_ErholungTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Erholung", "description": "Erholung."},
                    "2000": {
                        "name": "RuhigeErholungInNaturUndLandschaft",
                        "description": "Ruhige Erholung in Natur und Landschaft.",
                    },
                    "2001": {
                        "name": "LandschaftsbezogeneErholung",
                        "description": "Landschaftsbezogene Erholung",
                    },
                    "3000": {
                        "name": "ErholungMitStarkerInanspruchnahmeDurchBevoelkerung",
                        "description": "Erholung mit starker Inanspruchnahme durch die Bevölkerung.",
                    },
                    "3001": {
                        "name": "InfrastrukturelleErholung",
                        "description": "Infrastrukturelle Erholung",
                    },
                    "4000": {
                        "name": "Erholungswald",
                        "description": 'Erholungswald sind Waldgebiete, oft im Umfeld von Ballungszentren, die hauptsächlich der Erholung der Bevölkerung dienen (gegenüber forstwirtschaftlicher Nutzung oder Naturschutz). Nach § 13 Bundeswaldgesetz (1) kann Wald "zu Erholungswald erklärt werden, wenn es das Wohl der Allgemeinheit erfordert, Waldflächen für Zwecke der Erholung zu schützen, zu pflegen oder zu gestalten".',
                    },
                    "5000": {
                        "name": "Freizeitanlage",
                        "description": "Freizeitanlage.",
                    },
                    "5001": {
                        "name": "Ferieneinrichtung",
                        "description": "Ferieneinrichtung",
                    },
                    "6000": {
                        "name": "ErholungslandschaftAlpen",
                        "description": "Erholungslandschaft in den Alpen.",
                    },
                    "7000": {
                        "name": "Kureinrichtung",
                        "description": "Kureinrichtung.",
                    },
                    "9999": {
                        "name": "SonstigeErholung",
                        "description": "Sonstige Erholung.",
                    },
                },
            },
        ),
    ] = None
    typTourismus: Annotated[
        list[Literal["1000", "2000", "9999"]] | None,
        Field(
            description="Klassifikation von Tourismustypen.",
            json_schema_extra={
                "typename": "RP_TourismusTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..*",
                "enumDescription": {
                    "1000": {"name": "Tourismus", "description": "Tourismus."},
                    "2000": {
                        "name": "Kuestenraum",
                        "description": "Tourismus im Küstenraum.",
                    },
                    "9999": {
                        "name": "SonstigerTourismus",
                        "description": "Sonstiger Tourismus.",
                    },
                },
            },
        ),
    ] = None
    besondererTyp: Annotated[
        Literal["1000", "2000", "3000"] | None,
        Field(
            description="Klassifikation von besonderen Typen für Tourismus und/oder Erholung.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {
                        "name": "Entwicklungsgebiet",
                        "description": "Entwicklungsgebiet.",
                    },
                    "2000": {"name": "Kernbereich", "description": "Kernbereich."},
                    "3000": {
                        "name": "BesondereEntwicklungsaufgabe",
                        "description": "Besondere Entwicklungsaufgabe von Tourismus und/oder Erholung.",
                    },
                },
                "typename": "RP_BesondereTourismusErholungTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPErneuerbareEnergie(RPFreiraum):
    """
    Erneuerbare Energie inklusive Windenergienutzung.
    Erneuerbare Energien sind Energiequellen, die keine endlichen Rohstoffe verbrauchen, sondern natürliche, sich erneuernde Kreisläufe anzapfen (Sonne, Wind, Wasserkraft, Bioenergie). Meist werden auch Gezeiten, die Meeresströmung und die Erdwärme dazugezählt.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal["1000", "2000", "3000", "4000", "5000", "9999"] | None,
        Field(
            description="Klassifikation von Typen Erneuerbarer Energie.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Windenergie", "description": "Windenergie."},
                    "2000": {"name": "Solarenergie", "description": "Solarenergie."},
                    "3000": {"name": "Geothermie", "description": "Geothermie."},
                    "4000": {"name": "Biomasse", "description": "Biomasse."},
                    "5000": {"name": "Wasserkraft", "description": "Wasserkraft"},
                    "9999": {
                        "name": "SonstigeErneuerbareEnergie",
                        "description": "Sonstige Erneuerbare Energie.",
                    },
                },
                "typename": "RP_ErneuerbareEnergieTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None


class RPForstwirtschaft(RPFreiraum):
    """
    Forstwirtschaft ist die zielgerichtete Bewirtschaftung von Wäldern.
    Die natürlichen Abläufe in den Waldökosystemen werden dabei so gestaltet und gesteuert, dass sie einen möglichst großen Beitrag zur Erfüllung von Leistungen erbringen, die von den Waldeigentümern und der Gesellschaft gewünscht werden.
    """

    abstract: ClassVar[bool] = False
    namespace: ClassVar[str] = "http://www.xplanung.de/xplangml/5/4"
    typ: Annotated[
        Literal[
            "1000",
            "1001",
            "1002",
            "2000",
            "2001",
            "2002",
            "3000",
            "3001",
            "4000",
            "9999",
        ]
        | None,
        Field(
            description="Klassifikation von Forstwirtschaftstypen und Wäldern.",
            json_schema_extra={
                "enumDescription": {
                    "1000": {"name": "Wald", "description": "Wald."},
                    "1001": {
                        "name": "Bannwald",
                        "description": 'Bannwald.\r\nNach §32 (2) Baden-Württemberg "ein sich selbst überlassenes Waldreservat. Pflegemaßnahmen sind nicht erlaubt; anfallendes Holz darf nicht entnommen werden. [...] Fußwege sind zulässig."\r\nNach $11 (1) BayWaldG Bayern " Wald, der auf Grund seiner Lage und seiner flächenmäßigen Ausdehnung vor allem in Verdichtungsräumen und waldarmen Bereichen unersetzlich ist, und deshalb in seiner Flächensubstanz erhalten werden muss und welchem eine außergewöhnliche Bedeutung für das Klima, den Wasserhaushalt oder die Luftreinigung zukommt.\r\nNach §13 (2) ForstG Hessen ein Wald, der "in seiner Flächensubstanz in besonderem Maße schützenswert ist".\r\nIn anderen Ländern ist ein Bannwald ggf. abweichend definiert.',
                    },
                    "1002": {
                        "name": "Schonwald",
                        "description": 'Schonwald.\r\nNach §32 (3) Baden-Württemberg "ein Waldreservat, in dem eine bestimmte Waldgesellschaft mit ihren Tier- und Pflanzenarten, ein bestimmter Bestandsaufbau oder ein bestimmter Waldbiotop zu erhalten, zu entwickeln oder zu erneuern ist. Die Forstbehörde legt PFlegemaßnahmen mti Zustimmung des Waldbesitzers fest." In anderen Ländern ist ein Schonwald ggf. abweichend definiert.',
                    },
                    "2000": {"name": "Waldmehrung", "description": "Waldmehrung."},
                    "2001": {
                        "name": "WaldmehrungErholung",
                        "description": "Waldmehrung für Erholung.",
                    },
                    "2002": {
                        "name": "VergroesserungDesWaldanteils",
                        "description": "Vergrößerung des Waldanteils.",
                    },
                    "3000": {"name": "Waldschutz", "description": "Waldschutz."},
                    "3001": {
                        "name": "BesondereSchutzfunktionDesWaldes",
                        "description": "Besondere Schutzfunktion des Waldes.",
                    },
                    "4000": {
                        "name": "VonAufforstungFreizuhalten",
                        "description": "Von Aufforstung freizuhaltendes Gebiet.",
                    },
                    "9999": {
                        "name": "SonstigeForstwirtschaft",
                        "description": "Sonstige Forstwirtschaft.",
                    },
                },
                "typename": "RP_ForstwirtschaftTypen",
                "stereotype": "Enumeration",
                "multiplicity": "0..1",
            },
        ),
    ] = None
