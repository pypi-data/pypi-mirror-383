# port of David McClure's svg-to-wkt
import math
from svgpath2mpl import parse_path
from shapely.geometry import Polygon, LineString
from bs4 import BeautifulSoup

# The number of decimal places computed during curve interpolation when
# generating points for `<circle>` and `<ellipse>` elements.
PRECISION = 3

# The number of points computed during curve interpolation per unit of
# linear pixel length. For example, if a a path is 10px in length, and
# `DENSITY` is set to 2, the path will be rendered with 20 points.
DENSITY = 1

__version__ = "0.1.0"

def line(x1: float, y1: float, x2: float, y2: float) -> str:
    """
    Construct a WKT line from SVG start/end point coordinates.
    """
    return "LINESTRING({} {},{} {})".format(x1, y1, x2, y2)


def polyline(points: str) -> str:
    """
    Construct a WKT linestrimg from SVG `points` attribute value.
    """
    # "1,2 3,4 " => "1 2,3 4"
    pts = []
    for pt in points.strip().split(" "):
        pts.append(" ".join(pt.split(",")))

    return "LINESTRING({})".format(",".join(pts))


def polygon(points: str) -> str:
    """
    Construct a WKT polygon from SVG `points` attribute value.
    """
    # "1,2 3,4 " => "1 2,3 4"
    pts = []
    for pt in points.strip().split(" "):
        pts.append(" ".join(pt.split(",")))

    pts.append(pts[0])
    return "POLYGON(({}))".format(",".join(pts))


def rect(x: float, y: float, width: float, height: float) -> str:
    """
    Construct a WKT polygon from SVG rectangle origin and dimensions.
    """
    pts = []

    # No corner rounding
    pts.append("{} {}".format(x, -y))  # top left
    pts.append("{} {}".format(x + width, -y))  # top right
    pts.append("{} {}".format(x + width, -y - height))  # bottom right
    pts.append("{} {}".format(x, -y - height))  # bottom left
    pts.append("{} {}".format(x, -y))  # close

    return "POLYGON(({}))".format(",".join(pts))


def circle(cx: float, cy: float, r: float) -> str:
    """
    Construct a WKT polygon for a circle from origin and radius.
    """
    pts = []

    # Compute number of points.
    circumference = math.pi * 2 * r
    point_count = round(circumference * DENSITY)

    # Compute angle between points.
    interval_angle = 360 / point_count

    # Generate the circle
    for i in range(point_count):
        angle = (interval_angle * i) * (math.pi / 180)
        x = round(cx + r * math.cos(angle), PRECISION)
        y = round(cy + r * math.sin(angle), PRECISION)
        pts.append("{} {}".format(x, -y))

    # close
    pts.append(pts[0])

    return "POLYGON(({}))".format(",".join(pts))


def ellipse(cx: float, cy: float, rx: float, ry: float) -> str:
    """
    Construct a WKT polygon for an ellipse from origin and radii.
    """
    pts = []

    # Approximate the circumference.
    circumference = 2 * math.pi * math.sqrt((math.pow(rx, 2) + math.pow(ry, 2)) / 2)

    # Compute number of points and angle between points.
    point_count = round(circumference * DENSITY)
    interval_angle = 360 / point_count

    # Generate the ellipse.
    for i in range(point_count):
        angle = (interval_angle * i) * (math.pi / 180)
        x = round(cx + rx * math.cos(angle), PRECISION)
        y = round(cy + ry * math.sin(angle), PRECISION)
        pts.append("{} {}".format(x, -y))

    # close
    pts.append(pts[0])

    return "POLYGON(({}))".format(",".join(pts))


def path(d: str, as_line: bool = False) -> str:
    """
    Construct a WKT polygon from a SVG path string.

    The original code relies on SVG's getTotalLength
    and getPointAtLength which are only available in
    the browser so we'll be using svgpath2mpl and then
    feed the points to shapely.

    Y axis is reversed using numpy's dot([[1, 0], [0, -1]])
    since the 0,0 point for SVG is expected to be top left
    while the 0,0 point for WKT is expected to be bottom left.
    """
    mpl_path = parse_path(d)
    coords = mpl_path.to_polygons()
    if as_line:
        return LineString(coords[0].dot([[1, 0], [0, -1]])).wkt
    return Polygon(coords[0].dot([[1, 0], [0, -1]])).wkt


def convert(svg: str) -> str:
    """
    SVG => WKT

    NO verification is done here and it will happily
    crash upon malformed xml or missing attributes.
    """
    els = []
    svg = BeautifulSoup(svg, features="lxml")
    for el in svg.findAll("polygon"):
        els.append(polygon(el["points"]))
    for el in svg.findAll("polyline"):
        els.append(polyline(el["points"]))
    for el in svg.findAll("line"):
        els.append(
            line(
                float(el["x1"]),
                float(el["y1"]),
                float(el["x2"]),
                float(el["y1"]),
            )
        )
    for el in svg.findAll("rect"):
        els.append(
            rect(
                float(el["x"]),
                float(el["y"]),
                float(el["width"]),
                float(el["height"]),
            )
        )
    for el in svg.findAll("circle"):
        els.append(
            circle(
                float(el["cx"]),
                float(el["cy"]),
                float(el["r"]),
            )
        )
    for el in svg.findAll("ellipse"):
        els.append(
            ellipse(
                float(el["cx"]),
                float(el["cy"]),
                float(el["rx"]),
                float(el["ry"]),
            )
        )
    for el in svg.findAll("path"):
        els.append(path(el["d"]))

    val = "GEOMETRYCOLLECTION({})".format(",".join(els))
    return val

