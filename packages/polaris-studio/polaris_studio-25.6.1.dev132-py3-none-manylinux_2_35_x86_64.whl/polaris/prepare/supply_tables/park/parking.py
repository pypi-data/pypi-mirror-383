# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import random
from pathlib import Path


from polaris.network.utils.srid import get_srid
from polaris.network.network import Network
from polaris.utils.database.db_utils import commit_and_close, has_table, read_and_close


def add_parking(supply_path: Path, tags, sample_rate):
    random.seed(42)
    net = Network.from_file(supply_path, False)
    geotool = net.geotools
    osm = net.osm
    with read_and_close(supply_path) as conn:
        max_park = conn.execute("Select coalesce(max(parking) + 1, 1) from Parking").fetchone()[0]
        srid = get_srid(conn=conn)

    model_area = geotool.model_area

    geometries, osm_parking, osm_parking_pricing_rule = [], [], []
    for tag in tags:
        gdf = osm.get_tag("parking", tag)
        for _, rec in gdf.iterrows():
            geo = rec.geo
            geometries.append(geo)
            if not model_area.contains(geo):
                continue
            if random.random() > sample_rate:
                continue
            links_found = geotool.get_link_for_point_by_mode(geo, ["AUTO"])
            link = links_found[0] if links_found else -1
            ofst = geotool.offset_for_point_on_link(link, geo) if link > 0 else 0
            walk_link = geotool.get_geo_item("walk_link", geo)
            walk_ofst = 0 if walk_link is None else geotool.offset_for_point_on_link(walk_link, geo)
            bike_link = geotool.get_geo_item("bike_link", geo)
            bike_ofst = 0 if bike_link is None else geotool.offset_for_point_on_link(bike_link, geo)

            zone = geotool.get_geo_item("zone", geo)
            osm_parking.append([max_park, link, zone, ofst, walk_link, walk_ofst, bike_link, bike_ofst, geo.wkb, srid])
            osm_parking_pricing_rule.append([max_park, max_park])
            max_park += 1

    parking_sql = """insert into Parking(parking, link, dir, zone, offset, setback, "type", space, walk_link, walk_offset, bike_link, bike_offset, num_escooters, close_time, geo)
                                 values (?, ?, 0, ?, ?, 0, 'OSM', 1, ?, ?, ?, ?, 0, 86400, GeomFromWKB(?, ?));"""

    parking_pricing_sql = """insert into Parking_Pricing("parking", "parking_rule", "entry_start", "entry_end", "price")
                            values(?, ?, 0, 86400, 0);"""

    parking_rule_sql = """Insert into Parking_Rule("parking_rule", "parking", "rule_type", "rule_priority", "min_cost", "min_duration", "max_duration")
                            values(?, ?, 3, 1, 0, 0, 86400);"""

    if len(osm_parking) > 0:
        with commit_and_close(supply_path, spatial=True) as conn:
            if not has_table(conn, "Parking_Rule") or not has_table(conn, "Parking_Pricing"):
                raise RuntimeError("Missing Parking_Rule or Parking_Pricing table, make sure to upgrade your model")

            conn.executemany(parking_sql, osm_parking)
            conn.executemany(parking_rule_sql, osm_parking_pricing_rule)
            conn.executemany(parking_pricing_sql, osm_parking_pricing_rule)

    net.close(False)
