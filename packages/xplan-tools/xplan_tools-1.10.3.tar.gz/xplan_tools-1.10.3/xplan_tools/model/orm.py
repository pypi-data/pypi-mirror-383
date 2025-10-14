import json
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from geoalchemy2 import Geometry as GeometryBase
from geoalchemy2 import WKTElement
from geoalchemy2.admin.dialects.geopackage import register_gpkg_mapping
from geoalchemy2.admin.dialects.sqlite import register_sqlite_mapping
from sqlalchemy import (
    JSON,
    BigInteger,
    Computed,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import DropTable
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator

from xplan_tools.util import linearize_geom

register_sqlite_mapping({"ST_AsEWKT": "AsEWKT"})
register_gpkg_mapping({"ST_AsEWKT": "AsEWKT"})


@compiles(DropTable, "postgresql")
def compile_drop_table(element, compiler, **kwargs):
    """Appends DROP TABLE statements for postgres dialect with CASCADE to drop dependent views."""
    return f"{compiler.visit_drop_table(element)} CASCADE"


class Base(DeclarativeBase):
    pass


class Geometry(GeometryBase):
    from_text = "ST_GeomFromEWKT"
    as_binary = "ST_AsEWKT"
    ElementType = WKTElement
    cache_ok = True

    def bind_processor(self, dialect):
        def process(bindvalue):
            # Linearize Curve Geometries for compatibility
            if bindvalue is not None and dialect.name in ["geopackage", "sqlite"]:
                return linearize_geom(bindvalue)
            return bindvalue

        return process


class PGGeometry(TypeDecorator):
    impl = Geometry
    cache_ok = True

    def bind_expression(self, bindvalue):
        """Transform incoming geometries to the SRID of the DB."""
        return func.ST_Transform(
            bindvalue, func.Find_SRID("public", "coretable", "geometry"), type_=self
        )


class TextJSON(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect) -> Any:
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


class Feature(Base):
    __tablename__ = "coretable"
    pk: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger, "postgresql"),
        Identity(always=True),
        primary_key=True,
    )
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=False).with_variant(Text, "geopackage"),
        unique=True,
    )
    featuretype: Mapped[str] = mapped_column(
        String(50).with_variant(Text, "geopackage"), index=True
    )
    properties: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql").with_variant(TextJSON, "geopackage")
    )
    geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(spatial_index=False).with_variant(
            PGGeometry(spatial_index=False), "postgresql"
        )
    )
    geometry_type: Mapped[Optional[str]] = mapped_column(
        Text,
        Computed(
            """
            CASE WHEN
            GeometryType(geometry) LIKE '%POINT'
            THEN 'point'
            WHEN GeometryType(geometry) LIKE '%STRING' OR GeometryType(geometry) LIKE '%CURVE' OR GeometryType(geometry) = 'LINEARRING'
            THEN 'line'
            WHEN GeometryType(geometry) LIKE '%POLYGON' OR GeometryType(geometry) LIKE '%SURFACE'
            THEN 'polygon'
            ELSE 'nogeom'
            END
            """
        ),
        index=True,
    )
    appschema: Mapped[str] = mapped_column(
        String(10).with_variant(Text, "geopackage"), index=True
    )
    version: Mapped[str] = mapped_column(
        String(3).with_variant(Text, "geopackage"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )
    refs: Mapped[list["Refs"]] = relationship(
        back_populates="feature",
        cascade="all, delete-orphan",
        primaryjoin="Feature.id==Refs.base_id",
        lazy="selectin",
    )
    refs_inv: Mapped[list["Refs"]] = relationship(
        back_populates="feature_inv",
        cascade="all, delete-orphan",
        primaryjoin="Feature.id==Refs.related_id",
        lazy="selectin",
    )

    __mapper_args__ = {"primary_key": [id]}

    def __repr__(self) -> str:
        return f"Feature(id={self.id!r}, featuretype={self.featuretype!r}, properties={self.properties!r}, version={self.version!r}, refs={self.refs!r}, refs_inv={self.refs_inv!r})"


class Refs(Base):
    __tablename__ = "refs"
    pk: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger, "postgresql"),
        Identity(always=True),
        primary_key=True,
    )
    base_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "coretable.id", ondelete="CASCADE", deferrable=True, initially="DEFERRED"
        ),
        # primary_key=True,
    )
    related_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "coretable.id", ondelete="CASCADE", deferrable=True, initially="DEFERRED"
        ),
    )
    rel: Mapped[str] = mapped_column(String(50).with_variant(Text, "geopackage"))
    rel_inv: Mapped[Optional[str]] = mapped_column(
        String(50).with_variant(Text, "geopackage")
    )
    feature: Mapped["Feature"] = relationship(
        back_populates="refs",
        primaryjoin="Feature.id==Refs.base_id",
        viewonly=True,
    )
    feature_inv: Mapped["Feature"] = relationship(
        back_populates="refs_inv",
        primaryjoin="Feature.id==Refs.related_id",
        viewonly=True,
    )

    __mapper_args__ = {
        "primary_key": [base_id, related_id],
        "confirm_deleted_rows": False,
    }

    def __repr__(self) -> str:
        return f"Refs(base_id={self.base_id!r}, related_id={self.related_id!r}, rel={self.rel!r}, rel_inv={self.rel_inv!r})"


class GPKGEXT_Relations(Base):
    __tablename__ = "gpkgext_relations"
    id: Mapped[int] = mapped_column(
        Integer(),
        primary_key=True,
    )
    base_table_name: Mapped[str] = mapped_column(Text())
    base_primary_column: Mapped[str] = mapped_column(Text())
    related_table_name: Mapped[str] = mapped_column(Text())
    related_primary_column: Mapped[str] = mapped_column(Text())
    relation_name: Mapped[str] = mapped_column(Text())
    mapping_table_name: Mapped[str] = mapped_column(Text(), unique=True)
