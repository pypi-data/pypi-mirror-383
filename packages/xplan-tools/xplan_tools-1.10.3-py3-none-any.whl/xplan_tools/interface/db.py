"""Module containing the class for extracting plans from and writing to databases."""

# import json
import logging
from pathlib import Path
from typing import Iterable, Literal

from alembic import command, config, script
from alembic.runtime import migration
from geoalchemy2 import load_spatialite_gpkg
from geoalchemy2.admin.dialects.sqlite import load_spatialite_driver
from sqlalchemy import DDL, Column, Engine, create_engine, inspect, text
from sqlalchemy.engine import URL, make_url

# from sqlalchemy.dialects.sqlite.base import SQLiteCompiler
from sqlalchemy.event import listen, listens_for, remove

# from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

# from sqlalchemy.sql.expression import BindParameter
from xplan_tools.model import model_factory
from xplan_tools.model.base import BaseCollection, BaseFeature
from xplan_tools.model.orm import Base, Feature, Geometry
from xplan_tools.util import check_schema_accessibility

# from xplan_tools.util import linearize_geom
from .base import BaseRepository

logger = logging.getLogger(__name__)


class DBRepository(BaseRepository):
    """Repository class for loading from and writing to databases."""

    def __init__(
        self,
        datasource: str = "",
        version: str | None = None,
        data_type: Literal["xplan", "xtrasse", "plu"] = "xplan",
        schema: str | None = None,
        srid: int = 25832,
        with_views: bool = False,
    ) -> None:
        """Initializes the DB Repository.

        During initialization, a connection is established and the existence of required tables is tested.
        If an alembic revision is found, automatic migration is executed for PostgreSQL DBs.
        For other DBs, an Exception is raised if the revision does not correspond to the current model.
        If no revision and tables are found, they are automatically created.

        Args:
            datasource: A connection string which will be transformed to a URL instance.
            version: If no explicit version is provided it is read from the respective table column.
            data_type: Specification of either xplan, xtrasse or INSPIRE plu.
            schema: Schema name for DB repository. If not specified, the default schema is used. Only for PostgreSQL.
            srid: the EPSG code for spatial data
            with_views: whether to create geometrytype-specific views (postgres only)
        """
        self.datasource: URL = make_url(datasource)
        self.content = None
        self.version = version
        self.schema = schema
        self.dialect = self.datasource.get_dialect().name
        self.Session = sessionmaker(bind=self._engine)
        # self.session = self.Session()
        self.data_type = data_type
        self.srid = srid
        self.with_views = with_views

        alembic_cfg = config.Config()
        alembic_cfg.set_main_option("script_location", "xplan_tools:model:migrations")
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            datasource.replace("gpkg:", "sqlite:").replace(
                "postgresql:", "postgresql+psycopg:"
            ),
        )
        alembic_url = make_url(alembic_cfg.get_main_option("sqlalchemy.url"))
        if self.schema and self.dialect == "postgresql":
            alembic_cfg.set_main_option("custom_schema", self.schema)
        current_version = script.ScriptDirectory.from_config(alembic_cfg).get_heads()
        alembic_engine = create_engine(alembic_url)
        # test for tables and revision
        with alembic_engine.connect() as conn:
            context = migration.MigrationContext.configure(
                conn,
            )
            db_version = context.get_current_heads()
            inspector = inspect(conn)
            tables = inspector.get_table_names(schema=self.schema)
        is_coretable = {"coretable", "refs"}.issubset(set(tables))
        is_current_version = set(db_version) == set(current_version)

        # handle schema upgrade or table creation
        if db_version:
            if not is_current_version:
                if self.dialect == "postgresql":
                    logger.info("Running database migrations")
                    command.upgrade(alembic_cfg, "head")
                else:
                    e = RuntimeError(
                        f"Incompatible database revision and automatic migration not implemented for {self.dialect}"
                    )
                    e.add_note(
                        "please set up a new database with the current version of this library"
                    )
                    raise e
            else:
                logger.info("Database is at current revision")
        else:
            if is_coretable:
                e = RuntimeError("Coretable with no revision found in database")
                e.add_note(
                    "it is likely that the database was set up with an older version of this library which didn't use revisions yet"
                )
                e.add_note(
                    "please set up a new database or add a revision corresponding to the current model manually"
                )
                raise e
            else:
                # create tables if it's a fresh DB and set it to current revision
                logger.info("Creating new database schema")
                self.create_tables(self.srid, self.with_views)
                command.stamp(alembic_cfg, "head")

    @property
    def _engine(self) -> Engine:
        if self.dialect == "geopackage":
            engine = create_engine(self.datasource)
            listen(engine, "connect", load_spatialite_gpkg)
            return engine
        elif self.dialect == "sqlite":
            engine = create_engine(self.datasource)
            listen(
                engine,
                "connect",
                load_spatialite_driver,
            )
            return engine
        else:
            engine = create_engine(
                self.datasource.set(drivername="postgresql+psycopg"), echo=False
            )
            if self.schema:
                check_schema_accessibility(engine, self.schema)

            return engine

    # see https://docs.sqlalchemy.org/en/20/faq/sqlexpressions.html#rendering-bound-parameters-inline
    # @compiles(BindParameter)
    # def _render_literal_bindparam(
    #     element: BindParameter, compiler, dump_to_file=False, **kw
    # ):
    #     if not dump_to_file:
    #         return compiler.visit_bindparam(element, **kw)
    #     if (
    #         isinstance(compiler, SQLiteCompiler)
    #         and "geometry" in str(element.type)
    #         and element.value is not None
    #     ):
    #         return repr(linearize_geom(element.value))
    #     elif isinstance(element.value, dict):
    #         return repr(json.dumps(element.value))
    #     else:
    #         return repr(str(element.value))

    def get_plan_by_id(self, id: str) -> BaseCollection:
        logger.debug(f"retrieving plan with id {id}")
        with self.Session() as session:
            stmt = text(
                "SELECT srs_id FROM gpkg_geometry_columns WHERE table_name='coretable'"
                if self.dialect == "geopackage"
                else "SELECT srid FROM geometry_columns WHERE f_table_name='coretable'"
            )
            srid = session.execute(stmt).scalar_one()

            feature = session.get(Feature, id)
            if not feature:
                raise ValueError(f"no feature found with id {id}")
            elif "Plan" not in feature.featuretype:
                raise ValueError(f"{feature.featuretype} is not a plan object")
            else:
                self.version = "2.0" if self.data_type == "xtrasse" else feature.version
                collection = {
                    id: model_factory(
                        feature.featuretype, self.version, feature.appschema
                    ).model_validate(feature)
                }
                for ref in feature.refs:
                    collection[ref.feature_inv.id] = model_factory(
                        ref.feature_inv.featuretype, self.version, feature.appschema
                    ).model_validate(ref.feature_inv)
                    if ref.rel == "bereich":
                        for obj in ref.feature_inv.refs:
                            collection[obj.feature_inv.id] = model_factory(
                                obj.feature_inv.featuretype,
                                self.version,
                                feature.appschema,
                            ).model_validate(obj.feature_inv)
                for ref_inv in feature.refs_inv:
                    collection[ref_inv.feature.id] = model_factory(
                        ref_inv.feature.featuretype, self.version, feature.appschema
                    ).model_validate(ref_inv.feature)
                return BaseCollection(features=collection, srid=srid)

    def get(self, id: str) -> BaseFeature:
        logger.debug(f"retrieving feature with id {id}")
        with self.Session() as session:
            feature = session.get(Feature, id)
            if not feature:
                raise ValueError(f"no feature found with id {id}")
            else:
                return model_factory(
                    feature.featuretype, feature.version, feature.appschema
                ).model_validate(feature)

    def save(self, feature: BaseFeature) -> None:
        logger.debug(f"saving feature with id {id}")
        with self.Session() as session:
            feature = feature.model_dump_coretable()
            if session.get(Feature, feature.id):
                raise ValueError(f"feature with id {feature.id} already exists")
            session.merge(feature)
            session.commit()

    def delete_plan_by_id(self, id: str) -> BaseFeature:
        logger.debug(f"deleting plan with id {id}")
        with self.Session() as session:
            feature = session.get(Feature, id)
            if not feature:
                raise ValueError(f"no feature found with id {id}")
            elif "Plan" not in feature.featuretype:
                raise ValueError(f"{feature.featuretype} is not a plan object")
            else:
                for ref in feature.refs:
                    if ref.rel == "bereich":
                        for bereich_ref in ref.feature_inv.refs:
                            session.delete(bereich_ref.feature_inv)
                    session.delete(ref.feature_inv)
                for ref_inv in feature.refs_inv:
                    session.delete(ref_inv.feature)
                session.delete(feature)
                session.commit()
                return model_factory(
                    feature.featuretype, feature.version, feature.appschema
                ).model_validate(feature)

    def delete(self, id: str) -> BaseFeature:
        logger.debug(f"deleting feature with id {id}")
        with self.Session() as session:
            feature = session.get(Feature, id)
            if not feature:
                raise ValueError(f"no feature found with id {id}")
            else:
                session.delete(feature)
                session.commit()
                return model_factory(
                    feature.featuretype, feature.version, feature.appschema
                ).model_validate(feature)

    def save_all(
        self, features: BaseCollection | Iterable[BaseFeature], **kwargs
    ) -> None:
        logger.debug("saving collection")
        with self.Session() as session:
            for feature in (
                features.get_features()
                if isinstance(features, BaseCollection)
                else features
            ):
                feature = feature.model_dump_coretable()
                if session.get(Feature, feature.id):
                    raise ValueError(f"feature with id {feature.id} already exists")
                session.merge(feature)
            session.commit()

    def update_all(
        self, features: BaseCollection | Iterable[BaseFeature], **kwargs
    ) -> None:
        logger.debug("updating collection")
        with self.Session() as session:
            for feature in (
                features.get_features()
                if isinstance(features, BaseCollection)
                else features
            ):
                feature = feature.model_dump_coretable()
                session.merge(feature)
            session.commit()

    def update(self, id: str, feature: BaseFeature) -> BaseFeature:
        logger.debug(f"updating feature with id {id}")
        with self.Session() as session:
            db_feature = session.get(Feature, id)
            if db_feature:
                session.merge(feature.model_dump_coretable())
                session.commit()
                return feature
            else:
                raise ValueError(f"no feature found with id {id}")

    def patch(self, id: str, partial_update: dict) -> BaseFeature:
        logger.debug(f"patching feature with id {id}: {partial_update}")
        with self.Session() as session:
            db_feature = session.get(Feature, id)
            if db_feature:
                feature_dict = (
                    model_factory(
                        db_feature.featuretype, db_feature.version, db_feature.appschema
                    )
                    .model_validate(db_feature)
                    .model_dump()
                )
                feature = model_factory(
                    db_feature.featuretype, db_feature.version, db_feature.appschema
                ).model_validate(feature_dict | partial_update)
                session.merge(feature.model_dump_coretable())
                session.commit()
                return feature
            else:
                raise ValueError(f"no feature found with id {id}")

    def create_tables(self, srid: int, with_views: bool = False) -> None:
        """Creates coretable and related/spatial tables in the database.

        Args:
            srid: the EPSG code for spatial data
            with_views: whether to create geometrytype-specific views (postgres only)
        """

        @listens_for(Base.metadata, "before_create")
        def pre_creation(metadata, conn, **kw):
            if self.dialect == "sqlite":
                conn.execute(text("SELECT InitSpatialMetaData('EMPTY')"))
                conn.execute(text("SELECT InsertEpsgSrid(:srid)"), {"srid": srid})

        @listens_for(Base.metadata, "after_create")
        def post_creation(metadata, conn, **kw):
            coretable = self.schema + ".coretable" if self.schema else "coretable"
            stmt = (
                DDL(
                    "CREATE INDEX IF NOT EXISTS idx_coretable_geometry ON %(coretable)s USING GIST (geometry)",
                    {"coretable": coretable},
                )
                if self.dialect == "postgresql"
                else text("SELECT CreateSpatialIndex(:coretable, 'geometry')")
            )
            conn.execute(stmt, {"coretable": coretable})
            if self.dialect == "geopackage":
                conn.execute(
                    text(
                        """
                        INSERT INTO gpkg_extensions (table_name, extension_name, definition, scope)
                        VALUES
                            ('gpkg_data_columns', 'gpkg_schema', 'http://www.geopackage.org/spec/#extension_schema', 'read-write'),
                            ('gpkg_data_column_constraints', 'gpkg_schema', 'http://www.geopackage.org/spec/#extension_schema', 'read-write'),
                            ('gpkgext_relations', 'related_tables', 'http://www.opengis.net/doc/IS/gpkg-rte/1.0', 'read-write'),
                            ('refs', 'related_tables', 'http://www.opengis.net/doc/IS/gpkg-rte/1.0', 'read-write')
                        """
                    )
                )
                conn.execute(
                    text("""
                            INSERT INTO gpkgext_relations (base_table_name, base_primary_column, related_table_name, related_primary_column, relation_name, mapping_table_name)
                            VALUES
                                ('coretable', 'id', 'coretable', 'id', 'features', 'refs')
                            """)
                )
                conn.execute(
                    text("""
                            INSERT INTO gpkg_data_columns (table_name, column_name, mime_type)
                            VALUES
                                ('coretable', 'properties', 'application/json')
                            """)
                )
            if with_views:
                if self.dialect != "postgresql":
                    logger.warning(
                        f"Creating views not yet supported for {self.dialect}, skipping"
                    )
                else:
                    conn.execute(
                        DDL(
                            """
                                create or replace view %(schema)s.coretable_points as
                                select pk, id, featuretype, properties, ST_Multi(geometry)::geometry(MultiPoint, %(srid)s) as geometry, appschema, version
                                from %(schema)s.coretable
                                where geometry_type = 'point'
                                """,
                            {"srid": srid, "schema": self.schema or "public"},
                        )
                    )
                    conn.execute(
                        DDL(
                            """
                                create or replace view %(schema)s.coretable_lines as
                                select pk, id, featuretype, properties, ST_Multi(ST_ForceCurve(geometry))::geometry(MultiCurve, %(srid)s) as geometry, appschema, version
                                from %(schema)s.coretable
                                where geometry_type = 'line'
                                """,
                            {"srid": srid, "schema": self.schema or "public"},
                        )
                    )
                    conn.execute(
                        DDL(
                            """
                                create or replace view %(schema)s.coretable_polygons as
                                select pk, id, featuretype, properties, ST_Multi(ST_ForceCurve(geometry))::geometry(MultiSurface, %(srid)s) as geometry, appschema, version
                                from %(schema)s.coretable
                                where geometry_type = 'polygon'
                                """,
                            {"srid": srid, "schema": self.schema or "public"},
                        )
                    )
                    conn.execute(
                        DDL(
                            """
                                create or replace view %(schema)s.coretable_nogeoms as
                                select pk, id, featuretype, properties, geometry, appschema, version
                                from %(schema)s.coretable
                                where geometry_type = 'nogeom'
                                """,
                            {"schema": self.schema or "public"},
                        ),
                    )

        logger.debug(f"creating tables with srid {srid}")
        tables = Base.metadata.sorted_tables
        if not self.dialect == "geopackage":
            tables.pop(1)
        tables[0].append_column(
            Column("geometry", Geometry(srid=srid, spatial_index=False), nullable=True),
            replace_existing=True,
        )

        if self.schema and self.dialect.startswith("postgresql"):
            for table in Base.metadata.tables.values():
                table.schema = self.schema

        try:
            Base.metadata.create_all(self._engine, tables)
            remove(Base.metadata, "before_create", pre_creation)
            remove(Base.metadata, "after_create", post_creation)

        except Exception as e:
            if self.dialect in ["sqlite", "geopackage"]:
                file = self._engine.url.database
                Path(file).unlink(missing_ok=True)
            raise e

    def delete_tables(self) -> None:
        """Deletes coretable and related/spatial tables from the database."""
        logger.debug("deleting tables")
        if self.schema and self.dialect.startswith("postgresql"):
            for table in Base.metadata.tables.values():
                table.schema = self.schema
        Base.metadata.drop_all(self._engine)
