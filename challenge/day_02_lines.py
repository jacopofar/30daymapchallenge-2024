import polars as pl
from duckdb import DuckDBPyConnection
from PIL import Image, ImageDraw

from challenge.helpers.database import get_connection, run_ddb_query
from challenge.helpers.extents import ExtentDegrees

# The area around Milan, Italy, plus some margin
AREA = ExtentDegrees(45.261680, 45.620281, 8.860747, 9.546846)

# Resolution of the resulting image
# if the ratio is not the same as the extent, there will be an unused margin
RESOLUTION_X = 3000
RESOLUTION_Y = 3000


def get_bike_paths(con: DuckDBPyConnection, params: object) -> pl.DataFrame:
    points = run_ddb_query(
        "day_02_bike_paths.sql",
        con,
        params=params,
    ).pl()
    return points


def get_milano_boundaries(
    con: DuckDBPyConnection, params: object
) -> list[tuple[int, int]]:
    boundaries = run_ddb_query(
        "milano_boundaries.sql",
        con,
        params=params,
    ).fetchall()
    assert isinstance(boundaries, list)
    return boundaries


def main(show: bool = True) -> Image.Image:
    con = get_connection()
    common_params = dict(
        resolution_x=RESOLUTION_X,
        resolution_y=RESOLUTION_Y,
        xmin=AREA.lonmin,
        xmax=AREA.lonmax,
        ymin=AREA.latmin,
        ymax=AREA.latmax,
        fname="nord-ovest-20241022_nofilter_compact.parquet",
    )
    im = Image.new("RGB", (RESOLUTION_X, RESOLUTION_Y), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    bike_segments = get_bike_paths(con, common_params)
    print(bike_segments)
    milano_border = get_milano_boundaries(con, common_params)
    con.close()
    for _f_id, points in bike_segments.iter_rows():
        for i in range(-1, len(points) - 1):
            draw.line(
                (
                    points[i]["X"],
                    points[i]["Y"],
                    points[i + 1]["X"],
                    points[i + 1]["Y"],
                ),
                fill=(0, 0, 0),
                width=1,
            )
    for i in range(-1, len(milano_border) - 1):
        draw.line(
            (milano_border[i], milano_border[i + 1]),
            fill=(255, 0, 0),
            width=1 + RESOLUTION_X // 1000,
        )
    if show:
        im.show()
    return im


if __name__ == "__main__":
    main()
