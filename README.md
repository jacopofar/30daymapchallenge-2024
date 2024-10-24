# 30 Days Map Challenge - 2024 edition

This repository contains my own experiments with cartography and visualization
for the [#30DayMapChallenge](https://30daymapchallenge.com/).

For each day of November there's a theme, I will use mostly DuckDB + Python and
 focus mostly on the area of Milan, Italy.


# How to run

First, download the PBF file for your area, using for example the extracts from
 Geofabrik.

You can filter it down, so take the smallest file *containing* your area, in my
 case the whole north-west Italy in order to filter down to the area around
 Milan.

Use UV to install the dependencies and activate the corresponding virtualenv.

Now the command `quackosm` is available, run it:

```bash
quackosm  --geom-filter-bbox "8.640747,45.131680,9.766846,45.840281" nord-ovest-20241022.osm.pbf
```

in this case I used `--geom-filter-bbox` to filter only the area around Milan.
I used [bboxfinder](http://bboxfinder.com) to easily fetch the BBox limits.

It creates a file under the "files" folder, I moved it and renamed it to remove
 the hash from the name (not gonna need it).

Verify it with duckdb:

```SQL
import duckdb

con = duckdb.connect()
con.install_extension('spatial')
con.load_extension('spatial')

con.sql("""
select *, ST_AsGeoJSON(geometry)
from read_parquet('*_nofilter_compact.parquet')
            limit 4;
""").show()

con.sql("""
select ST_GeometryType(geometry), count(*)
from read_parquet('*_nofilter_compact.parquet')
group by 1;
""").show()

print(con.sql("""
select st_asgeojson(ST_Extent_Agg(geometry))
from read_parquet('*_nofilter_compact.parquet');
""").fetchone())

con.close()
```
