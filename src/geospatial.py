import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import libpysal as lps
from shapely import vectorized
import folium
import libpysal as lps
from matplotlib.colors import TwoSlopeNorm, Normalize
from scipy.stats import gaussian_kde
from esda.getisord import G_Local
from shapely.geometry import Point, Polygon


def load_uk_boundary(FILE_LOCATION, SOURCE_CRS):
    UK_BOUNDARY_FILEPATH = FILE_LOCATION
    countries_gdf = gpd.read_file(UK_BOUNDARY_FILEPATH).to_crs(SOURCE_CRS)
    return countries_gdf.union_all()


def validate_within_uk_land_boundary(gdf, land_boundary):
    """Drops points that fall outside land_boundary."""
    within_land = gdf.geometry.within(land_boundary)
    n_outside = (~within_land).sum()
    if n_outside > 0:
        print(f"Dropping {n_outside} point(s) falling outside land_boundary.")
    return gdf[within_land].reset_index(drop=True)


def make_grid(land_boundary, cell_size, crs):
    """
    Create a square grid covering the bounding box of land_boundary,
    then keep only cells that actually intersect UK land — so the
    resulting grid follows the coastline instead of forming a solid
    rectangle.
    """
    xmin, ymin, xmax, ymax = land_boundary.bounds
    cols = np.arange(xmin, xmax + cell_size, cell_size)
    rows = np.arange(ymin, ymax + cell_size, cell_size)

    polygons = []
    for x in cols[:-1]:
        for y in rows[:-1]:
            polygons.append(
                Polygon(
                    [
                        (x, y),
                        (x + cell_size, y),
                        (x + cell_size, y + cell_size),
                        (x, y + cell_size),
                    ]
                )
            )

    full_grid = gpd.GeoDataFrame({"geometry": polygons}, crs=crs)

    # Keep only cells that actually touch land — this is what produces
    # the jagged coastline shape instead of a solid rectangle.
    land_mask = full_grid.intersects(land_boundary)
    return full_grid[land_mask].reset_index(drop=True)


def classify(z, p):
    if p > 0.05:
        return "Not significant"
    if z > 0:
        if p <= 0.01:
            return "Hot spot (99%)"
        elif p <= 0.05:
            return "Hot spot (95%)"
    else:
        if p <= 0.01:
            return "Cold spot (99%)"
        elif p <= 0.05:
            return "Cold spot (95%)"
    return "Not significant"


category_colors = {
    "Hot spot (99%)": "#67000d",
    "Hot spot (95%)": "#fb6a4a",
    "Not significant": "#d1cfcf",
    "Cold spot (95%)": "#6baed6",
    "Cold spot (99%)": "#08306b",
}


def run_gi_star_hotspot(
    grid,
    value_col,
    title,
    clip=8,
    k=8,
    significant_only=False,
    ax=None,
    show=True,
    savepath=None,
):
    sub = grid[grid[value_col] > 0].reset_index(drop=True)

    w = lps.weights.KNN.from_dataframe(sub, k=k)
    w.transform = "r"

    y = sub[value_col].values
    g_local = G_Local(y, w, star=True, permutations=999)

    sub["Gi_star"] = g_local.Zs
    sub["p_value"] = g_local.p_sim
    sub["hotspot_class"] = [
        classify(z, p) for z, p in zip(sub["Gi_star"], sub["p_value"])
    ]
    sub["color"] = sub["hotspot_class"].map(category_colors)

    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(1, 1, figsize=(5, 16))

    if significant_only:
        non_sig = sub[sub["p_value"] > 0.05]
        sig = sub[sub["p_value"] <= 0.05]

        n_sig = len(sig)
        print(
            f"[{title}] {n_sig}/{len(sub)} cells statistically significant (p<=0.05)."
        )
        print(sig["hotspot_class"].value_counts().to_string())

        if not non_sig.empty:
            non_sig.plot(ax=ax, color="#d1cfcf", alpha=0.4, edgecolor="none")

        # Plot by fixed category color (not continuous Gi_star) so weak-
        # magnitude but statistically significant cells are still clearly
        # visible, rather than fading into the background under a
        # continuous colormap.
        if not sig.empty:
            sig.plot(ax=ax, color=sig["color"], edgecolor="none")

            # Manual legend, since color= (not column=) skips the
            # automatic colorbar/legend that column= would normally add.
            handles = [
                plt.Line2D(
                    [0],
                    [0],
                    marker="s",
                    color="w",
                    label=label,
                    markerfacecolor=color,
                    markersize=10,
                )
                for label, color in category_colors.items()
                if label in sig["hotspot_class"].unique()
            ]
            ax.legend(handles=handles, loc="lower left", fontsize=8, frameon=True)
    else:
        norm = TwoSlopeNorm(vmin=-clip, vcenter=0, vmax=clip)
        sub.plot(
            column="Gi_star",
            cmap="RdBu_r",
            norm=norm,
            legend=True,
            ax=ax,
            edgecolor="none",
            legend_kwds={"label": "Gi* z-score", "shrink": 0.6},
        )

    ax.set_title(title)
    ax.set_axis_off()

    if own_fig:
        plt.tight_layout()
        if savepath:
            plt.savefig(savepath, dpi=200)
        if show:
            plt.show()

    return sub


# Getis-Ordis Gi* Accident Hotspots (Interactive)

# ── City reference points ─────────────────────────────────────────────────
UK_CITIES = {
    "London": (51.5074, -0.1278),
    "Birmingham": (52.4862, -1.8904),
    "Manchester": (53.4808, -2.2426),
    "Leeds": (53.8008, -1.5491),
    "Liverpool": (53.4084, -2.9916),
    "Sheffield": (53.3811, -1.4701),
    "Bristol": (51.4545, -2.5879),
    "Newcastle": (54.9783, -1.6178),
    "Nottingham": (52.9548, -1.1581),
    "Leicester": (52.6369, -1.1398),
}


def _haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km, used for nearest-city matching."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def find_top_hotspot_cities(
    sub_wgs84, cities=UK_CITIES, top_n=5, max_dist_km=40, sig_only=True
):
    """
    Identifies the top_n strongest hotspot cells (highest Gi_star) and
    labels each with its nearest city, provided that city is within
    max_dist_km. Cells with no city close enough are skipped (rather than
    mislabeling a rural cluster with a distant city name).
    """
    candidates = sub_wgs84.copy()
    if sig_only:
        candidates = candidates[candidates["p_value"] <= 0.05]
        candidates = candidates[candidates["hotspot_class"].str.startswith("Hot spot")]

    if candidates.empty:
        print("No statistically significant hot spots found — skipping city labeling.")
        return pd.DataFrame(
            columns=["city", "lat", "lon", "Gi_star", "p_value", "dist_km"]
        )

    candidates = candidates.sort_values("Gi_star", ascending=False)

    cent = candidates.geometry.centroid
    candidates = candidates.assign(_lat=cent.y, _lon=cent.x)

    city_names = list(cities.keys())
    city_lats = np.array([v[0] for v in cities.values()])
    city_lons = np.array([v[1] for v in cities.values()])

    results = []
    seen_cities = set()

    for _, row in candidates.iterrows():
        dists = _haversine_km(row["_lat"], row["_lon"], city_lats, city_lons)
        nearest_idx = int(np.argmin(dists))
        nearest_city = city_names[nearest_idx]
        nearest_dist = dists[nearest_idx]

        if nearest_dist > max_dist_km:
            continue
        if nearest_city in seen_cities:
            continue

        results.append(
            {
                "city": nearest_city,
                "lat": cities[nearest_city][0],
                "lon": cities[nearest_city][1],
                "Gi_star": row["Gi_star"],
                "p_value": row["p_value"],
                "dist_km": round(nearest_dist, 1),
            }
        )
        seen_cities.add(nearest_city)

        if len(results) >= top_n:
            break

    return pd.DataFrame(results)


# def plot_hotspot_folium(
#     sub, value_col, title, cities=UK_CITIES, zoom_start=6, top_n=5, max_dist_km=40
# ):
#     sub_wgs84 = sub.to_crs(epsg=4326)

#     center_lat = sub_wgs84.geometry.centroid.y.mean()
#     center_lon = sub_wgs84.geometry.centroid.x.mean()

#     m = folium.Map(
#         location=[center_lat, center_lon],
#         zoom_start=zoom_start,
#         tiles="OpenStreetMap"
#         # tiles="CartoDB positron",
#     )

#     folium.GeoJson(
#         sub_wgs84,
#         name=title,
#         style_function=lambda feat: {
#             "fillColor": feat["properties"]["color"],
#             "color": feat["properties"]["color"],
#             "weight": 0,
#             "fillOpacity": 0.75,
#         },
#         tooltip=folium.GeoJsonTooltip(
#             fields=[value_col, "Gi_star", "p_value", "hotspot_class"],
#             aliases=[
#                 value_col.replace("_", " ").title(),
#                 "Gi* z-score",
#                 "p-value",
#                 "Classification",
#             ],
#             localize=True,
#         ),
#     ).add_to(m)

#     top_cities = find_top_hotspot_cities(
#         sub_wgs84, cities=cities, top_n=top_n, max_dist_km=max_dist_km
#     )

#     city_layer = folium.FeatureGroup(name="Top hotspot cities")
#     for rank, row in enumerate(top_cities.itertuples(index=False), start=1):
#         folium.CircleMarker(
#             location=[row.lat, row.lon],
#             radius=6,
#             color="#000000",
#             fill=True,
#             fill_color="#ffffff",
#             fill_opacity=1.0,
#             weight=1.5,
#             tooltip=(
#                 f"#{rank} {row.city} — Gi* z={row.Gi_star:.2f}, "
#                 f"p={row.p_value:.3f} (~{row.dist_km} km from hotspot)"
#             ),
#         ).add_to(city_layer)
#         folium.map.Marker(
#             [row.lat, row.lon],
#             icon=folium.DivIcon(
#                 html=f'<div style="font-size:12px;font-weight:700;color:#000;'
#                 f"text-shadow:1px 1px 2px #fff,-1px -1px 2px #fff;"
#                 f'transform:translate(9px,-7px);">#{rank} {row.city}</div>'
#             ),
#         ).add_to(city_layer)
#     city_layer.add_to(m)

#     folium.LayerControl(collapsed=False).add_to(m)

#     if top_cities.empty:
#         print(
#             f"[{title}] No cities matched within {max_dist_km} km of a significant hotspot."
#         )
#     else:
#         print(
#             f"[{title}] Top hotspot cities:\n{top_cities[['city', 'Gi_star', 'p_value', 'dist_km']]}"
#         )

#     return m


def plot_hotspot_folium(
    sub, value_col, title, cities=UK_CITIES, zoom_start=6, top_n=5, max_dist_km=40
):
    sub_wgs84 = sub.to_crs(epsg=4326)

    center_lat = sub_wgs84.geometry.centroid.y.mean()
    center_lon = sub_wgs84.geometry.centroid.x.mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles=None,
    )

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri World Street Map",
        control=False,
    ).add_to(m)

    folium.GeoJson(
        sub_wgs84,
        name=title,
        style_function=lambda feat: {
            "fillColor": feat["properties"]["color"],
            "color": feat["properties"]["color"],
            "weight": 0,
            "fillOpacity": 0.75,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[value_col, "Gi_star", "p_value", "hotspot_class"],
            aliases=[
                value_col.replace("_", " ").title(),
                "Gi* z-score",
                "p-value",
                "Classification",
            ],
            localize=True,
        ),
    ).add_to(m)

    top_cities = find_top_hotspot_cities(
        sub_wgs84, cities=cities, top_n=top_n, max_dist_km=max_dist_km
    )

    city_layer = folium.FeatureGroup(name="Top hotspot cities")
    for rank, row in enumerate(top_cities.itertuples(index=False), start=1):
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=6,
            color="#000000",
            fill=True,
            fill_color="#ffffff",
            fill_opacity=1.0,
            weight=1.5,
            tooltip=(
                f"#{rank} {row.city} — Gi* z={row.Gi_star:.2f}, "
                f"p={row.p_value:.3f} (~{row.dist_km} km from hotspot)"
            ),
        ).add_to(city_layer)
        folium.map.Marker(
            [row.lat, row.lon],
            icon=folium.DivIcon(
                html=f'<div style="font-size:12px;font-weight:700;color:#000;'
                f"text-shadow:1px 1px 2px #fff,-1px -1px 2px #fff;"
                f'transform:translate(9px,-7px);">#{rank} {row.city}</div>'
            ),
        ).add_to(city_layer)
    city_layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    if top_cities.empty:
        print(
            f"[{title}] No cities matched within {max_dist_km} km of a significant hotspot."
        )
    else:
        print(
            f"[{title}] Top hotspot cities:\n{top_cities[['city', 'Gi_star', 'p_value', 'dist_km']]}"
        )

    return m

def clip_density_to_uk_boundary(xx, yy, density, boundary_geom):
    """
    Sets density to NaN for raster cells whose center falls outside
    boundary_geom (e.g. UK_LAND_BOUNDARY), so the KDE surface doesn't
    imply data exists in sea/outside the UK extent.
    """
    mask = vectorized.contains(boundary_geom, xx, yy)
    return np.where(mask, density, np.nan)


def estimate_accident_density(
    points_gdf, grid_bounds, grid_size=300, bw_method=None, weights=None
):
    """
    Fits a 2D Gaussian KDE on point geometries (projected CRS assumed,
    e.g. British National Grid) and evaluates it on a regular raster
    covering grid_bounds.

    Returns: (xx, yy, density) — meshgrid coordinates and density values,
             density reshaped to (grid_size, grid_size)
    """
    valid_geom = points_gdf[points_gdf.geometry.notna() & ~points_gdf.geometry.is_empty]

    x = valid_geom.geometry.x.to_numpy()
    y = valid_geom.geometry.y.to_numpy()

    finite_mask = np.isfinite(x) & np.isfinite(y)
    n_dropped = len(points_gdf) - finite_mask.sum()
    if n_dropped > 0:
        print(
            f"[estimate_accident_density] Dropping {n_dropped} point(s) with missing/invalid coordinates."
        )

    x = x[finite_mask]
    y = y[finite_mask]

    if len(x) < 2:
        raise ValueError(f"Need at least 2 valid points for KDE, got {len(x)}.")

    xy = np.vstack([x, y])
    kde = gaussian_kde(xy, bw_method=bw_method, weights=weights)

    minx, miny, maxx, maxy = grid_bounds
    xx, yy = np.mgrid[
        minx : maxx : complex(grid_size), miny : maxy : complex(grid_size)
    ]
    positions = np.vstack([xx.ravel(), yy.ravel()])

    density = kde(positions).reshape(xx.shape)
    return xx, yy, density


def plot_accident_density_map(
    xx,
    yy,
    density,
    boundary_geom,
    title,
    cmap="inferno",
    vmax=None,
    crs=None,
    ax=None,
    show=True,
    savepath=None,
):
    """
    Plots a pre-computed KDE density surface, clipped to boundary_geom,
    with the boundary outline drawn on top for geographic reference.

    Takes pre-computed (xx, yy, density) rather than raw points, so the
    expensive KDE evaluation happens exactly once per dataset — the
    caller computes density (e.g. via estimate_accident_density) and can
    reuse it both for a shared vmax calculation and for plotting.

    crs is passed explicitly rather than read from a global `grid`
    variable, so this function has no implicit dependency on notebook
    state outside its own arguments.

    If vmax is provided, the color scale is fixed to that value instead
    of auto-scaling to this panel's own max — pass a shared vmax across
    multiple calls to keep color intensity directly comparable.
    """
    density = clip_density_to_uk_boundary(xx, yy, density, boundary_geom)

    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(1, 1, figsize=(5, 16))

    scale_max = vmax if vmax is not None else np.nanmax(density)
    norm = Normalize(vmin=0, vmax=scale_max)

    im = ax.pcolormesh(xx, yy, density, cmap=cmap, norm=norm, shading="auto")
    plt.colorbar(im, ax=ax, shrink=0.6, label="Density")

    # Boundary overlay for geographic context
    boundary_gdf = gpd.GeoSeries([boundary_geom], crs=crs)
    boundary_gdf.boundary.plot(ax=ax, color="#ffffff", linewidth=0.5, alpha=0.6)

    ax.set_title(title)
    ax.set_axis_off()
    ax.set_aspect("equal")

    if own_fig:
        plt.tight_layout()
        if savepath:
            plt.savefig(savepath, dpi=200)
        if show:
            plt.show()

    return density


# Junction Analysis
# def filter_to_true_junctions(
#     junctions, form_col="formOfRoadNode", junction_forms=("Junction", "Roundabout")
# ):
#     """
#     Filters road nodes down to genuine junctions/intersections, excluding
#     simple road-end or pass-through nodes. Adjust junction_forms based on
#     the actual values printed from junctions[form_col].value_counts().
#     """
#     if form_col not in junctions.columns:
#         print(f"'{form_col}' not found — using all nodes as junctions (unfiltered).")
#         return junctions

#     filtered = junctions[junctions[form_col].isin(junction_forms)]
#     print(
#         f"Filtered {len(junctions)} nodes down to {len(filtered)} junctions ({junction_forms})."
#     )
#     return filtered


# def compute_junction_density_per_cell(grid, junctions):
#     """
#     Spatially joins junction points to grid cells and counts junctions
#     per cell — a proxy for road network complexity independent of total
#     road length.
#     """
#     joined = gpd.sjoin(junctions, grid, how="left", predicate="within")
#     counts = joined.groupby("index_right").size()

#     grid = grid.copy()
#     grid["junction_count"] = 0
#     grid.loc[counts.index, "junction_count"] = counts.values
#     grid["junction_count"] = grid["junction_count"].astype(np.float64)

#     grid["junctions_per_km"] = np.nan
#     valid_road = grid["road_length_m"] >= 100  # same threshold used for accident rate
#     grid.loc[valid_road, "junctions_per_km"] = grid.loc[
#         valid_road, "junction_count"
#     ] / (grid.loc[valid_road, "road_length_m"] / 1000)

#     return grid


# def compute_accidents_near_junctions(gdf, junctions, buffer_m=20):
#     """
#     Flags accidents that fall within buffer_m of a junction node — a
#     direct measure of junction-related accident involvement, distinct
#     from cell-level aggregation. Useful for asking "what fraction of
#     accidents in this area happen at/near junctions specifically" rather
#     than inferring it indirectly from cell-level density correlations.
#     """
#     junction_union = junctions.geometry.union_all()
#     junction_buffer = junction_union.buffer(buffer_m)

#     gdf = gdf.copy()
#     gdf["near_junction"] = gdf.geometry.within(junction_buffer)

#     pct = gdf["near_junction"].mean() * 100
#     print(
#         f"{gdf['near_junction'].sum()}/{len(gdf)} accidents ({pct:.1f}%) occur within {buffer_m}m of a junction."
#     )

#     return gdf
