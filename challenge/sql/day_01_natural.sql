
with scaling_factor as (
    SELECT LEAST(
                $resolution_x / ($xmax - $xmin),
                $resolution_y / ($ymax - $ymin)
    ) as scaling_factor
),
pixels as (
    select (st_x(geometry) - $xmin) * scaling_factor.scaling_factor as X,
        ($ymax - st_y(geometry)) * scaling_factor.scaling_factor as Y
    from read_parquet($fname) s
    join scaling_factor on true
    where
        ST_GeometryType(geometry) = 'POINT'
        AND tags['natural'] <> []
)
select x::integer AS X,
    y::integer AS Y,
    count(*) AS density
from pixels
group by 1, 2
