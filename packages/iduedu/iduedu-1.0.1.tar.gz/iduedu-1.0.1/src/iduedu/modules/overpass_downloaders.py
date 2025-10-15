import datetime as dt
import math
import time
from collections import defaultdict
from typing import Literal

import geopandas as gpd
import pandas as pd
import requests
from shapely import LineString, MultiPolygon, Polygon, unary_union
from shapely.ops import polygonize

from iduedu import config

logger = config.logger

import threading
from email.utils import parsedate_to_datetime
from time import monotonic


class RateLimiter:
    def __init__(self, min_interval: float):
        self.min_interval = float(min_interval)
        self._next_ts = 0.0
        self._cv = threading.Condition()

    def wait(self):
        start = monotonic()
        with self._cv:
            while True:
                now = monotonic()
                if now >= self._next_ts:
                    # фиксированное расписание слотов
                    self._next_ts = max(self._next_ts, now) + self.min_interval
                    slept = monotonic() - start
                    # logger.info(f"GRANT; slept={slept:.3f}s; next_slot_in={self._next_ts - now:.3f}s")
                    self._cv.notify_all()
                    return
                to_sleep = self._next_ts - now
                # logger.info(f"SLEEP for {to_sleep:.3f}s (next_ts={self._next_ts:.3f})")
                self._cv.wait(timeout=to_sleep)


OVERPASS_MIN_INTERVAL = config.overpass_min_interval
OVERPASS_RL = RateLimiter(OVERPASS_MIN_INTERVAL)


def _overpass_http(
    method: Literal["GET", "POST"], url: str, *, params=None, data=None, timeout=None
) -> requests.Response:
    OVERPASS_RL.wait()

    headers = {"User-Agent": config.user_agent}
    proxies = config.proxies
    verify = config.verify_ssl
    req_timeout = timeout or config.timeout

    if method == "GET":
        return requests.get(url, params=params, timeout=req_timeout, headers=headers, proxies=proxies, verify=verify)
    else:
        return requests.post(url, data=data, timeout=req_timeout, headers=headers, proxies=proxies, verify=verify)


class RequestError(RuntimeError):
    """
    Basic error for eny requests problems
    """

    def __init__(self, message, status_code=None, reason=None, response_text=None, response_content=None):
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason
        self.response_text = response_text
        self.response_content = response_content

    def __str__(self):
        if self.status_code == 400:
            return (
                f"{super().__str__()} (status: {self.status_code}, reason: {self.reason}). "
                f"Make sure provided polygon is in CRS 4326."
            )
        return f"{super().__str__()} (status: {self.status_code}, reason: {self.reason})."


def _get_overpass_pause(
    base_endpoint: str,
    recursion_pause: float = 5,
) -> float:
    url = base_endpoint[: -len("/interpreter")] + "/status"
    try:
        response = _overpass_http("GET", url, timeout=config.timeout)
        response_text = response.text
    except requests.RequestException as e:
        raise RequestError(f"Unable to reach {url}, {e}") from e

    try:
        status = response_text.split("\n")[4]
        status_first_part = status.split(" ")[0]
    except (AttributeError, IndexError, ValueError):
        raise RequestError(f"Unable to parse {url} response: {response_text}")

    try:
        _ = int(status_first_part)  # number of available slots
        pause: float = 0
    except ValueError:
        if status_first_part == "Slot":
            utc_time_str = status.split(" ")[3]
            pattern = "%Y-%m-%dT%H:%M:%SZ,"
            utc_time = dt.datetime.strptime(utc_time_str, pattern).replace(tzinfo=dt.timezone.utc)
            utc_now = dt.datetime.now(tz=dt.timezone.utc)
            seconds = int(math.ceil((utc_time - utc_now).total_seconds()))
            pause = max(seconds, 1)
        elif status_first_part == "Currently":
            time.sleep(recursion_pause)
            pause = _get_overpass_pause(base_endpoint, recursion_pause=recursion_pause)
        else:
            raise RequestError(f"Unrecognized server status: {status!r}")
    return pause


def _overpass_request(
    method: Literal["GET", "POST"],
    overpass_url: str,
    params: dict | None = None,
    data: dict | None = None,
    timeout: float | None = None,
    *,
    max_retries: int | None = None,
    backoff_base: float | None = None,
) -> requests.Response:

    if max_retries is None:
        max_retries = config.overpass_max_retries
    if backoff_base is None:
        backoff_base = config.overpass_backoff_base

    retryable_statuses = set(config.overpass_retry_statuses)

    last_err_text = None
    for attempt in range(max_retries + 1):
        try:
            pause = _get_overpass_pause(overpass_url)
        except RequestError as e:
            pause = 0
            logger.debug(f"Overpass /status check failed: {e}")

        if pause > 0:
            logger.warning(f"Waiting {pause} seconds for available Overpass API slot")
            time.sleep(pause)

        try:
            resp = _overpass_http(method, overpass_url, params=params, data=data, timeout=timeout or config.timeout)
        except requests.RequestException as e:
            last_err_text = str(e)
            if attempt < max_retries:
                sleep_s = min(60, backoff_base**attempt)
                logger.warning(f"Network error, retrying in {sleep_s} (attempt {attempt + 1}/{max_retries})")
                time.sleep(sleep_s)
                continue
            raise RequestError(f"Request error: {e}") from e

        if resp.status_code == 200:
            return resp

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_s = int(retry_after)
                except ValueError:
                    try:
                        ra_dt = parsedate_to_datetime(retry_after)
                        wait_s = max(1, int((ra_dt - dt.datetime.now(tz=ra_dt.tzinfo)).total_seconds()))
                    except Exception:
                        wait_s = 5
                wait_s = max(wait_s, 1)
                logger.debug(f"HTTP 429: honoring Retry-After={wait_s}")
                time.sleep(wait_s)
            else:
                try:
                    pause = _get_overpass_pause(overpass_url)
                except RequestError:
                    pause = 0
                wait_s = max(1, pause or int(backoff_base**attempt))
                logger.debug(f"HTTP 429: waiting {wait_s} seconds before retry")
                time.sleep(wait_s)

            if attempt < max_retries:
                continue

        if resp.status_code in retryable_statuses:
            if attempt < max_retries:
                wait_s = min(60, backoff_base**attempt)
                logger.warning(f"HTTP {resp.status_code}: retrying in {wait_s}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_s)
                continue
        last_err_text = resp.text
        break

    raise RequestError(
        message=f"Request failed with status code {resp.status_code}, reason: {resp.reason}",
        status_code=resp.status_code,
        reason=resp.reason,
        response_text=last_err_text,
        response_content=resp.content,
    )


def get_boundary_by_osm_id(osm_id) -> MultiPolygon | Polygon:
    overpass_query = f"""
                [out:json];
                        (
                            relation({osm_id});
                        );
                out geom;
                """
    logger.debug(f"Downloading territory bounds with osm_id <{osm_id}> ...")
    resp = _overpass_request(
        method="GET",
        overpass_url=config.overpass_url,
        params={"data": overpass_query},
    )
    json_result = resp.json()
    geoms = []
    for element in json_result["elements"]:
        geometries_inners = []
        geometries_outers = []
        for member in element["members"]:
            if "geometry" in member:
                if member["role"] == "outer":
                    geometries_outers.append(
                        LineString([(coords["lon"], coords["lat"]) for coords in member["geometry"]])
                    )
                if member["role"] == "inner":
                    geometries_inners.append(
                        LineString([(coords["lon"], coords["lat"]) for coords in member["geometry"]])
                    )
        outer_poly = unary_union(list(polygonize(geometries_outers)))
        inner_poly = unary_union(list(polygonize(geometries_inners)))
        geoms.append(outer_poly.difference(inner_poly))
    return unary_union(geoms)


def get_4326_boundary(
    *, osm_id: int | None = None, territory: Polygon | MultiPolygon | gpd.GeoDataFrame | None = None
) -> Polygon:
    """
    Normalize a territory boundary to a single EPSG:4326 Polygon.

    Accepts either an `osm_id` (relation id) to fetch the boundary from OSM, a direct
    `Polygon`/`MultiPolygon`, or a `GeoDataFrame`. Returns a single `Polygon` in lon/lat.
    For `MultiPolygon`, the function returns its **convex hull** as a Polygon.

    Parameters:
        osm_id (int | None): OSM relation id. If provided, boundary is fetched via Overpass.
        territory (Polygon | MultiPolygon | gpd.GeoDataFrame | None): Existing boundary geometry
            or a GeoDataFrame containing it. If GeoDataFrame is given, it is reprojected to 4326
            and unioned (`.union_all()`).

    Returns:
        (shapely.Polygon): Boundary polygon in EPSG:4326.

    Notes:
        - Input `Polygon` is returned as-is (assumed already in EPSG:4326 by caller).
        - For `MultiPolygon`, a **convex hull** is returned (may slightly expand the area and
          fill gaps between parts).
        - For `GeoDataFrame`, the geometry is first reprojected to 4326 and dissolved via
          `.union_all()`; the result is then normalized to a `Polygon` (convex hull if needed).

    Examples:
        >>> get_4326_boundary(osm_id=1114252)             # fetch by OSM id
        >>> get_4326_boundary(territory=poly4326)         # keep polygon
        >>> get_4326_boundary(territory=multi_poly_4326)  # convex hull of multipart
        >>> get_4326_boundary(territory=territory_gdf)    # GDF -> to_crs(4326) -> union_all -> Polygon
    """
    if osm_id:
        territory = get_boundary_by_osm_id(osm_id)

    if isinstance(territory, Polygon):
        return territory

    if isinstance(territory, MultiPolygon):
        return Polygon(territory.convex_hull)

    if isinstance(territory, gpd.GeoDataFrame):
        return get_4326_boundary(territory=territory.to_crs(4326).union_all())

    raise ValueError("Either osm_id or polygon must be specified")


def _poly_to_overpass(poly: Polygon) -> str:
    return " ".join(f"{y} {x}" for x, y in poly.exterior.coords[:-1])


def get_routes_by_poly(polygon: Polygon, public_transport_type: str) -> pd.DataFrame:
    if public_transport_type == "subway":
        return get_subway_routes_by_poly(polygon)
    polygon_coords = _poly_to_overpass(polygon)
    overpass_query = f"""
        [out:json][timeout:{config.timeout}];
                (
                    relation(poly:\"{polygon_coords}\")[ 'route' = '{public_transport_type}' ];
                );
        out geom;
        """
    logger.debug(f"Downloading routes from OSM with type <{public_transport_type}> ...")
    resp = _overpass_request(
        method="POST",
        overpass_url=config.overpass_url,
        data={"data": overpass_query},
    )
    json_result = resp.json()["elements"]
    data = pd.DataFrame(json_result)
    data["transport_type"] = public_transport_type
    return data


def get_subway_routes_by_poly(polygon: Polygon) -> pd.DataFrame:
    polygon_coords = _poly_to_overpass(polygon)
    overpass_query = f"""
        [out:json][timeout:500];
            rel(poly:"{polygon_coords}")["route"="subway"]->.routes;
            node(r.routes)-> .route_nodes;
            rel(bn.route_nodes)->.stop_areas;
            rel(br.stop_areas)["public_transport"="stop_area_group"]["type"="public_transport"]->.groups;
            nwr(r.stop_areas)["public_transport"="station"]->.stations;
            .stop_areas     out geom qt;
            .groups         out body qt;
            .stations       out tags qt;
        """

    logger.debug(f"Downloading subway routes data from OSM ...")
    resp = _overpass_request(
        method="POST",
        overpass_url=config.overpass_url,
        data={"data": overpass_query},
    )
    json_result = resp.json()["elements"]
    if len(json_result) == 0:
        return pd.DataFrame()

    for e in json_result:
        tags = e.get("tags") or {}
        etype = e.get("type")

        e["is_stop_area"] = etype == "relation" and tags.get("public_transport") == "stop_area"
        e["is_stop_area_group"] = (
            etype == "relation"
            and tags.get("public_transport") == "stop_area_group"
            and tags.get("type") == "public_transport"
        )
        e["is_station"] = tags.get("public_transport") == "station"

    data = pd.DataFrame(json_result)
    data["transport_type"] = "subway"
    return data


def get_network_by_filters(polygon: Polygon, way_filter: str) -> pd.DataFrame:
    polygon_coords = _poly_to_overpass(polygon)
    overpass_query = f"""
        [out:json][timeout:{config.timeout}];
            (way{way_filter}(poly:\"{polygon_coords}\"););
        out geom;
        """
    logger.debug(f"Downloading network from OSM with filters <{way_filter}> ...")
    resp = _overpass_request(
        method="POST",
        overpass_url=config.overpass_url,
        data={"data": overpass_query},
    )

    json_result = resp.json()["elements"]
    return pd.DataFrame(json_result)


def fetch_member_tags(members_missing, chunk_size=2000):
    """
    members_missing: iterable of dicts  {'type': 'node|way|relation', 'ref': int}
    :returns {("node", 123): {tags...}, ("way", 456): {tags...}, ...}
    """
    ids = defaultdict(list)
    for m in members_missing:
        t = m["type"]
        ids[t].append(int(m["ref"]))

    for k in list(ids.keys()):
        ids[k] = sorted(set(ids[k]))

    result = {}

    def _build_query(sub_ids: dict) -> str:
        parts = []
        if sub_ids.get("node"):
            parts.append(f'node(id:{",".join(map(str, sub_ids["node"]))});')
        if sub_ids.get("way"):
            parts.append(f'way(id:{",".join(map(str, sub_ids["way"]))});')
        if sub_ids.get("relation"):
            parts.append(f'rel(id:{",".join(map(str, sub_ids["relation"]))});')
        body = "\n".join(parts)
        return f"[out:json][timeout:{config.timeout}];\n(\n{body}\n);\nout tags center qt;"

    def _yield_chunks(type_key):
        arr = ids.get(type_key, [])
        for i in range(0, len(arr), chunk_size):
            yield {type_key: arr[i : i + chunk_size]}

    chunks = []
    for tk in ("node", "way", "relation"):
        chunks.extend(_yield_chunks(tk))

    for sub in chunks:
        q = _build_query(sub)
        resp = _overpass_request(method="POST", overpass_url=config.overpass_url, data={"data": q})
        els = resp.json().get("elements", [])
        for e in els:
            key = (e["type"], int(e["id"]))
            result[key] = e.get("tags", {}) or {}
            if e["type"] != "node":
                if "center" in e:
                    result[key]["__center__"] = (e["center"]["lon"], e["center"]["lat"])

    return result
