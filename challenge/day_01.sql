with pixels as (
    select (st_x(geometry) - $xmin) * $resolution / ($xmax - $xmin) as X,
        ($ymax - st_y(geometry)) * $resolution / ($ymax - $ymin) as Y
    from read_parquet('nord-ovest-20241022_nofilter_compact.parquet') s
    where ST_GeometryType(geometry) = 'POINT'
)
select x::integer AS X,
    y::integer AS Y,
    count(*) AS density
from pixels
group by 1,2
