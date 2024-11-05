
with scaling_factor as (
    SELECT LEAST(
                $resolution_x / ($xmax - $xmin),
                $resolution_y / ($ymax - $ymin)
    ) as scaling_factor
),
bike_linestrings as (
    select
        feature_id,
        geometry
    from read_parquet($fname)
    where
    -- there are a lot of ways to tah bike paths
    -- https://wiki.openstreetmap.org/wiki/Bicycle
        (
            tags['highway'] = ['cycleway']
            OR tags['cycleway'] = ['track']
            )
    AND ST_GeometryType(geometry) = 'LINESTRING'
),
bike_vertices as (
    select
        feature_id,
        unnest(st_dump(st_points(geometry))).geom as p,
        unnest(st_dump(st_points(geometry))).path[1] as seq
    from bike_linestrings
),
pixel_vertices as (
    select
        feature_id,
        round((st_x(v.p) - $xmin) * scaling_factor.scaling_factor)::integer as X,
        round(($ymax - st_y(v.p)) * scaling_factor.scaling_factor)::integer as Y
    from bike_vertices v
    join scaling_factor on true
    order by feature_id, v.seq
)
SELECT
    feature_id,
    array_agg(struct_pack(X := X, Y := Y)) as P
from pixel_vertices
where X >= 0 and y >= 0 and x <= $resolution_x and y <= $resolution_y
group by feature_id
