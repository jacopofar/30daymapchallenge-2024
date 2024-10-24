from dataclasses import dataclass

from pyproj import Transformer

TRAN_4326_TO_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857")


@dataclass
class ExtentDegrees:
    """Bounding box in WGS84 degrees. Aka EPSG:4326"""

    latmin: float
    latmax: float
    lonmin: float
    lonmax: float

    # mypy does not support typing.Self it seems
    def enlarged(self, factor: float) -> "ExtentDegrees":
        """Calculate an extent enlarged in all directions.

        The factor is RELATIVE, 0 means no change, 1.0 means 100% larger,
        -0.5 means 50% smaller

        Parameters
        ----------
        factor : float
            How much to enlarge, e.g. 0.1 means 10% more
        """
        lat_mid = (self.latmax + self.latmin) / 2
        lat_radius = abs(self.latmax - self.latmin) / 2 * (1 + factor)
        lon_mid = (self.lonmax + self.lonmin) / 2
        lon_radius = abs(self.lonmax - self.lonmin) / 2 * (1 + factor)
        return ExtentDegrees(
            latmin=min(lat_mid - lat_radius, lat_mid + lat_radius),
            latmax=max(lat_mid - lat_radius, lat_mid + lat_radius),
            lonmin=min(lon_mid - lon_radius, lon_mid + lon_radius),
            lonmax=max(lon_mid - lon_radius, lon_mid + lon_radius),
        )

    def as_e7_dict(self) -> dict[str, int]:
        return dict(
            latmin=int(self.latmin * 10**7),
            latmax=int(self.latmax * 10**7),
            lonmin=int(self.lonmin * 10**7),
            lonmax=int(self.lonmax * 10**7),
        )

    def as_epsg3857(self) -> tuple[float, float, float, float]:
        """Convert the extent to a tuple in EPSG 3857.

        The order is the same required by PostGIS st_makeenvelope
        that is: lonmin, latmin, lonmax, latmax
        """
        lonmin, latmin = TRAN_4326_TO_3857.transform(self.latmin, self.lonmin)
        lonmax, latmax = TRAN_4326_TO_3857.transform(self.latmax, self.lonmax)
        return (lonmin, latmin, lonmax, latmax)


def coord_to_pixel(
    lat: float, lon: float, height: float, width: float, extent: ExtentDegrees
) -> tuple[float, float]:
    """Convert lat/lon coordinate to a pixel coordinate for a given area.

    NOTE: this assumes the extent is very small, enough to not introduce errors
    due to curvature. For this project is usually no bigger than a city.
    """
    x = (lon - extent.lonmin) * width / (extent.lonmax - extent.lonmin)
    y = (lat - extent.latmin) * height / (extent.latmax - extent.latmin)

    return x, y
