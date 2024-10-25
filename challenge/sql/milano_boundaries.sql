with
scaling_factor as (
    SELECT LEAST(
                $resolution_x / ($xmax - $xmin),
                $resolution_y / ($ymax - $ymin)
    ) as scaling_factor
),
milano as (select st_points(geometry) as mul
                from read_parquet($fname)
                where tags['admin_level'] = [8]
    and tags['name'] = ['Milano']
    and ST_GeometryType(geometry) = 'POLYGON'
),
milano_vertices as (
    select
        unnest(st_dump(mul)).geom as p,
        unnest(st_dump(mul)).path[1] as seq
    from milano
)


select
    round((st_x(v.p) - $xmin) * scaling_factor.scaling_factor)::integer as X,
    round(($ymax - st_y(v.p)) * scaling_factor.scaling_factor)::integer as Y
from milano_vertices v
join scaling_factor on true
order by v.seq
