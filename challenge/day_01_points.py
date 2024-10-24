import polars as pl
from PIL import Image, ImageDraw

from challenge.helpers.database import get_connection, run_ddb_query
from challenge.helpers.extents import ExtentDegrees

# The area around Milan, Italy, plus some margin
AREA = ExtentDegrees(45.131680, 45.840281, 8.640747, 9.766846)

RESOLUTION = 7000


def get_points() -> pl.DataFrame:
    con = get_connection()
    points = run_ddb_query(
        "day_01.sql",
        con,
        params=dict(
            resolution=RESOLUTION,
            xmin=AREA.lonmin,
            xmax=AREA.lonmax,
            ymin=AREA.latmin,
            ymax=AREA.latmax,
        ),
    ).pl()
    con.close()
    return points


def main() -> None:
    im = Image.new("RGB", (RESOLUTION, RESOLUTION), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    points_gray = get_points()
    max_value = points_gray.select(pl.max("density"))
    points_gray = points_gray.with_columns(
        pl.col("density") * 255 // max_value,  # type: ignore
    )
    for x, y, v in points_gray.iter_rows():
        draw.point((x, y), fill=(v, v, v))
    im.show()


if __name__ == "__main__":
    main()
