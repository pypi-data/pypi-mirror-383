import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import shapely
import Geometry3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go


def plot_building(
    vertices,
    surfaces,
    surf_to_show="all",
    show_vertices=True,
    title="",
    real_scale=True,
):
    vertices = np.array(vertices)
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(projection="3d")
    vertices_to_plot = []
    for surf_name, surf_vert in surfaces.items():
        if surf_name in surf_to_show or surf_to_show == "all":
            xyz_surf = vertices[surf_vert]
            poly = Poly3DCollection([xyz_surf], alpha=0.1, linewidths=1, edgecolors="k")
            ax.add_collection3d(poly)
            vertices_to_plot += surf_vert
    # Add vertices with idx as text and dots
    # for idx_v in range(len(vertices)):
    if show_vertices:
        # Use a colormap to generate unique colors for each vertex
        unique_vertices = sorted(list(set(vertices_to_plot)))
        colors = (["b", "r", "g", "c", "m", "y", "k"] * 20)[: len(unique_vertices)]
        vertex_colors = {v_idx: c for v_idx, c in zip(unique_vertices, colors)}

        for idx_v in unique_vertices:
            vert = vertices[idx_v]
            color = vertex_colors[idx_v]
            ax.text(*vert, " " + str(idx_v), color=color, fontsize=10)
            ax.scatter(*vert, color=[color], s=20)  # Add a small dot
    # Set axes limits
    xyz_min = np.min(vertices, axis=0)
    if real_scale:
        xyz_max = [np.max(vertices)] * 3
    else:
        xyz_max = np.max(vertices, axis=0)
    ax.set_xlim3d(xyz_min[0], xyz_max[0])
    ax.set_ylim3d(xyz_min[1], xyz_max[1])
    ax.set_zlim3d(xyz_min[2], xyz_max[2])
    # Remove ticks labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    plt.title(title)
    plt.show()
    return


def visualize_geometry(vertices, surfaces, debug_mode=False):
    """
    Visualizes the building geometry.

    If debug_mode is True, it launches a Dash app for interactive inspection.
    If debug_mode is False, it returns a Plotly figure for use in other apps like Streamlit.
    """

    if debug_mode:
        color_zone = False
        list_surfaces = True
    else:
        color_zone = True
        list_surfaces = False

    def create_geometry_figure(
        vertices, surfaces, highlight=None, camera=None, color_zone=False
    ):
        """Create a 3D figure of the geometry with optional surface highlighting."""

        fig = go.Figure()

        if color_zone:
            zones = sorted(list(set([name.split("-")[0] for name in surfaces.keys()])))
            colors = [
                "tab:orange",
                "tab:blue",
                "tab:green",
                "tab:red",
                "tab:purple",
                "tab:brown",
            ]
            colors = matplotlib.colors.ListedColormap(colors)
            zone_color_map = {zone: colors(i) for i, zone in enumerate(zones)}

            for name, inds in surfaces.items():
                x = [vertices[i][0] for i in inds]
                y = [vertices[i][1] for i in inds]
                z = [vertices[i][2] for i in inds]
                zone = name.split("-")[0]
                color = zone_color_map.get(zone, (0, 0, 1, 1))
                color_str = f"rgba({color[0]*255}, {color[1]*255}, {color[2]*255}, 0.9)"

                fig.add_trace(
                    go.Mesh3d(
                        x=x,
                        y=y,
                        z=z,
                        i=list(range(1, len(inds) - 1)),
                        j=list(range(2, len(inds))),
                        k=[0] * (len(inds) - 2),
                        color=color_str,
                        opacity=0.5,
                        hoverinfo="text",
                        text=f"Surface: {name}",
                        name=name,
                    )
                )
        else:
            for name, inds in surfaces.items():
                x = [vertices[i][0] for i in inds] + [vertices[inds[0]][0]]
                y = [vertices[i][1] for i in inds] + [vertices[inds[0]][1]]
                z = [vertices[i][2] for i in inds] + [vertices[inds[0]][2]]
                color = "yellow" if name == highlight else "blue"
                fig.add_trace(
                    go.Scatter3d(
                        x=x,
                        y=y,
                        z=z,
                        mode="lines",
                        name=name,
                        line=dict(width=8 if name == highlight else 3, color=color),
                        hoverinfo="text",
                        text=f"Surface: {name}",
                    )
                )

        if highlight and highlight in surfaces:
            highlight_inds = surfaces[highlight]
            if len(highlight_inds) >= 1:
                v1 = vertices[highlight_inds[0]]
                fig.add_trace(
                    go.Scatter3d(
                        x=[v1[0]],
                        y=[v1[1]],
                        z=[v1[2]],
                        mode="markers",
                        marker=dict(color="green", size=10),
                        name="First Vertex",
                    )
                )
            if len(highlight_inds) >= 2:
                v2 = vertices[highlight_inds[1]]
                fig.add_trace(
                    go.Scatter3d(
                        x=[v2[0]],
                        y=[v2[1]],
                        z=[v2[2]],
                        mode="markers",
                        marker=dict(color="red", size=10),
                        name="Second Vertex",
                    )
                )

        current_camera = camera if camera else dict(eye=dict(x=1.5, y=-2, z=1))

        fig.update_layout(
            scene=dict(
                xaxis=dict(showbackground=True),
                yaxis=dict(showbackground=True),
                zaxis=dict(showbackground=True),
                camera=current_camera,
                annotations=get_facade_annotations(vertices),
            ),
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=600,
        )
        return fig

    def get_facade_annotations(vertices):
        """Generate annotations for the facades."""
        xyz_min = np.min(vertices, axis=0)
        xyz_max = np.max(vertices, axis=0)
        x_mid = (xyz_min[0] + xyz_max[0]) / 2
        y_mid = (xyz_min[1] + xyz_max[1]) / 2
        z_mid = (xyz_min[2] + xyz_max[2]) / 2
        offset = 2  # Offset to place labels outside the building

        annotations = [
            # Front annotation (min y)
            dict(
                showarrow=False,
                x=x_mid,
                y=xyz_min[1] - offset,
                z=z_mid,
                text="Front",
                xanchor="center",
                yanchor="middle",
                font=dict(color="black", size=14),
            ),
            # Back annotation (max y)
            dict(
                showarrow=False,
                x=x_mid,
                y=xyz_max[1] + offset,
                z=z_mid,
                text="Back",
                xanchor="center",
                yanchor="middle",
                font=dict(color="black", size=14),
            ),
            # Left annotation (min x)
            dict(
                showarrow=False,
                x=xyz_min[0] - offset,
                y=y_mid,
                z=z_mid,
                text="Left",
                xanchor="center",
                yanchor="middle",
                font=dict(color="black", size=14),
            ),
            # Right annotation (max x)
            dict(
                showarrow=False,
                x=xyz_max[0] + offset,
                y=y_mid,
                z=z_mid,
                text="Right",
                xanchor="center",
                yanchor="middle",
                font=dict(color="black", size=14),
            ),
        ]
        return annotations

    if not debug_mode:
        return create_geometry_figure(vertices, surfaces, color_zone=color_zone)

    # --- Debug mode: Launch Dash app ---
    app = dash.Dash(__name__)

    main_layout = [
        html.Div(
            [
                dcc.Graph(
                    id="geometry-viewer",
                    figure=create_geometry_figure(
                        vertices, surfaces, color_zone=color_zone
                    ),
                ),
            ],
            style={
                "width": "70%" if list_surfaces else "100%",
                "display": "inline-block",
            },
        ),
    ]

    if list_surfaces:
        main_layout.append(
            html.Div(
                [
                    html.H3("Surfaces", style={"color": "white"}),
                    dcc.RadioItems(
                        id="surface-selector",
                        options=[
                            {"label": name, "value": name} for name in surfaces.keys()
                        ],
                        value=None,
                        labelStyle={"display": "block", "cursor": "pointer"},
                        style={"color": "white"},  # ✅ make text white
                    ),
                ],
                style={
                    "width": "25%",
                    "display": "inline-block",
                    "verticalAlign": "top",
                    "backgroundColor": "black",
                },
            ),
        )

    app.layout = html.Div(main_layout)

    if list_surfaces:

        @app.callback(
            Output("geometry-viewer", "figure"),
            [Input("surface-selector", "value")],
            [dash.dependencies.State("geometry-viewer", "relayoutData")],
        )
        def highlight_surface(selected, relayoutData):
            camera = None
            if relayoutData and "scene.camera" in relayoutData:
                camera = relayoutData["scene.camera"]
            return create_geometry_figure(
                vertices,
                surfaces,
                highlight=selected,
                camera=camera,
                color_zone=color_zone,
            )

    app.run(debug=True)


def check_for_naked_edges(surfaces):
    """
    Raise an error if there are naked edges in the geometry.
    A naked edge is an edge that is present in only one surface.

    Inputs
    ------
    surfaces : dict
        Dictionary mapping surface names to a list with the index of their vertices.
    """
    edge_counts = {}
    for surf_name, surf_vert in surfaces.items():
        for i1, i2 in zip(surf_vert, surf_vert[1:] + [surf_vert[0]]):
            edge = tuple(sorted([i1, i2]))
            if edge in edge_counts:
                edge_counts[edge] += 1
            else:
                edge_counts[edge] = 1
    naked_edges = [edge for edge, count in edge_counts.items() if count == 1]
    if len(naked_edges) > 0:
        raise ValueError(f"Naked edges found in the geometry: {naked_edges}")
    return


def ConvexPolygon(points):
    """
    Create a ConvexPolygon object from a list of points.
    Unlike the ConvexPolygon_old class fron Geometry3D, this function doesn't require
    the first 3 points to be non-collinear. This is achieved by testing all circular
    permutations of the points.

    Inputs
    ------
    points : array-like of shape (n_points, 3)
        Array of shape (n_vertices, 3) representing the points (x, y, z) of the surface.

    Returns
    -------
    poly : Geometry3D.ConvexPolygon
    """
    # Try all circular permutations of the points when creating the polygon
    # This is because ConvexPolygon requires the first 3 points to be non-collinear,
    # which may not be the case sometimes (e.g. for "EastWall_2F").
    n_points = len(points)
    for i in range(n_points):
        points_perm = np.roll(points, i, axis=0)
        try:
            poly = Geometry3D.ConvexPolygon([Geometry3D.Point(p) for p in points_perm])
            return poly
        except ZeroDivisionError:
            continue
    raise ValueError(
        f"Could not create a ConvexPolygon from the given points: {points}"
    )
    return


def make_box(
    dimensions: list, origin: list, zone: str, frac_shared_side_walls: float, label=""
):
    lx, ly, lz = dimensions
    vertices = [
        [0, 0, 0],
        [lx, 0, 0],
        [lx, ly * frac_shared_side_walls, 0],
        [lx, ly, 0],
        [0, ly, 0],
        [0, ly * frac_shared_side_walls, 0],
        [0, 0, lz],
        [lx, 0, lz],
        [lx, ly * frac_shared_side_walls, lz],
        [lx, ly, lz],
        [0, ly, lz],
        [0, ly * frac_shared_side_walls, lz],
    ]
    vertices = np.array(vertices) + np.array(origin)
    surfaces = {
        "Floor": [0, 1, 2, 3, 4, 5][::-1],
        "Roof": [6, 7, 8, 9, 10, 11],
        "FrontWall": [0, 1, 7, 6],
        "BackWall": [3, 4, 10, 9],
        "SharedRightWall": [1, 2, 8, 7],
        "RightWall": [2, 3, 9, 8],
        "LeftWall": [4, 5, 11, 10],
        "SharedLeftWall": [5, 0, 6, 11],
    }
    if label != "":
        surfaces = {f"{zone}-{surf}_{label}": idxs for surf, idxs in surfaces.items()}
    else:
        surfaces = {f"{zone}-{surf}": idxs for surf, idxs in surfaces.items()}
    vertices, surfaces = fix_duplicate_vertices(vertices, surfaces)
    return vertices, surfaces


def make_slanted_roof(
    dimensions: list[float],
    orientation: str,
    origin: list[float],
    zone: str,
    frac_shared_side_walls: float,
):
    assert dimensions[2] > 0
    assert orientation in ["left", "right", "front", "back"]
    lx, ly, lz = dimensions
    alpha = frac_shared_side_walls
    vertices = [[0, 0, 0], [lx, 0, 0], [lx, ly, 0], [0, ly, 0]]
    surfaces = {}
    if orientation == "front":
        vertices += [
            [0, ly, lz],  # 4
            [lx, ly, lz],  # 5
            [0, ly * alpha**0.5, lz * alpha**0.5],
            [0, ly * alpha**0.5, 0],  # 7
            [lx, ly * alpha**0.5, lz * alpha**0.5],
            [lx, ly * alpha**0.5, 0],  # 9
        ]
        surfaces["Floor"] = [0, 7, 3, 2, 9, 1]
        surfaces["Roof"] = [0, 1, 8, 5, 4, 6]
        surfaces["SharedRightWall"] = [1, 9, 8]
        surfaces["RightWall"] = [9, 2, 5, 8]
        surfaces["BackWall"] = [2, 3, 4, 5]
        surfaces["SharedLeftWall"] = [7, 0, 6]
        surfaces["LeftWall"] = [3, 7, 6, 4]
    elif orientation == "back":
        vertices += [
            [0, 0, lz],
            [lx, 0, lz],
            [0, ly * (1 - alpha**0.5), lz * alpha**0.5],  # 6
            [0, ly * (1 - alpha**0.5), 0],  # 7
            [lx, ly * (1 - alpha**0.5), lz * alpha**0.5],  # 8
            [lx, ly * (1 - alpha**0.5), 0],  # 9
        ]
        surfaces["Floor"] = [0, 7, 3, 2, 9, 1]
        surfaces["Roof"] = [2, 3, 6, 4, 5, 8]
        surfaces["SharedRightWall"] = [2, 8, 9]
        surfaces["RightWall"] = [1, 9, 8, 5]
        surfaces["FrontWall"] = [0, 1, 5, 4]
        surfaces["SharedLeftWall"] = [3, 7, 6]
        surfaces["LeftWall"] = [7, 0, 4, 6]
    elif orientation == "left":
        vertices += [
            [lx, 0, lz],
            [lx, ly, lz],
            [lx, ly * alpha, lz],
            [lx, ly * alpha, 0],
        ]
        surfaces["Floor"] = [0, 3, 2, 7, 1]
        surfaces["Roof"] = [3, 0, 4, 6, 5]
        surfaces["SharedRightWall"] = [1, 7, 6, 4]
        surfaces["RightWall"] = [7, 2, 5, 6]
        surfaces["FrontWall"] = [0, 1, 4]
        surfaces["BackWall"] = [2, 3, 5]
    else:
        vertices += [
            [0, 0, lz],
            [0, ly, lz],
            [0, ly * alpha, lz],
            [0, ly * alpha, 0],
        ]
        surfaces["Floor"] = [0, 7, 3, 2, 1]
        surfaces["Roof"] = [1, 2, 5, 6, 4]
        surfaces["SharedLeftWall"] = [7, 0, 4, 6]
        surfaces["LeftWall"] = [3, 7, 6, 5]
        surfaces["FrontWall"] = [0, 1, 4]
        surfaces["BackWall"] = [2, 3, 5]

    # Translate vertices based on origin
    vertices = np.array(vertices) + np.array(origin)
    surfaces = {f"{zone}-{surf}": idxs for surf, idxs in surfaces.items()}
    vertices, surfaces = fix_duplicate_vertices(vertices, surfaces)
    return vertices, surfaces


def make_pitched_roof(
    dimensions: list[float],
    orientation: str,
    origin: list[float],
    zone: str,
    shared_side_walls: bool,
    dormer_params: dict = {},
):
    lx, ly, lz = dimensions
    assert lz > 0
    assert orientation in ["left-right", "front-back"]
    vertices = [[0, 0, 0], [lx, 0, 0], [lx, ly, 0], [0, ly, 0]]
    if orientation == "left-right":
        vertices += [[lx / 2, 0, lz], [lx / 2, ly, lz]]
        surfaces = {
            "Floor": [0, 3, 2, 1],
            "LeftRoof": [3, 0, 4, 5],
            "RightRoof": [1, 2, 5, 4],
            "FrontWall": [0, 1, 4],
            "BackWall": [2, 3, 5],
        }
    elif orientation == "front-back":
        vertices += [[0, ly / 2, lz], [lx, ly / 2, lz]]
        surfaces = {
            "Floor": [0, 3, 2, 1],
            "FrontRoof": [0, 1, 5, 4],
            "BackRoof": [2, 3, 4, 5],
            "SharedLeftWall" if shared_side_walls else "LeftWall": [3, 0, 4],
            "SharedRightWall" if shared_side_walls else "RightWall": [1, 2, 5],
        }
    # Add dormers
    for loc, params in dormer_params.items():
        assert loc in orientation
        add_dormer(
            vertices,
            surfaces,
            roof_surf_name=loc.capitalize() + "Roof",
            dormer_width=params["width"],
            dormer_height=params["height"],
        )

    # Translate vertices based on origin
    vertices = np.array(vertices) + np.array(origin)
    surfaces = {f"{zone}-{surf}": idxs for surf, idxs in surfaces.items()}
    vertices, surfaces = fix_duplicate_vertices(vertices, surfaces)
    return vertices, surfaces


def add_dormer(
    vertices,
    surfaces,
    roof_surf_name: str,
    dormer_width: float,
    dormer_height: float,
):
    # Get roof info
    roof_vert_idx = surfaces.pop(roof_surf_name)
    roof_verts = np.array(vertices)[roof_vert_idx]
    lx, ly, lz = np.max(roof_verts, axis=0) - np.min(roof_verts, axis=0)
    x_mid, y_mid, z_mid = np.mean(roof_verts, axis=0)
    ori = next(x for x in ["Front", "Back", "Left", "Right"] if x in roof_surf_name)
    # Add new vertices
    N = len(vertices)
    if ori in ["Front", "Back"]:
        dlx, dlz = dormer_width, dormer_height
        assert dlx < lx and dlz < lz
        dly = ly * dlz / lz
        s = 1 if ori == "Front" else -1
        new_vert_1 = [
            [x_mid - dlx / 2, y_mid - s * dly / 2, z_mid - dlz / 2],  # N
            [x_mid - dlx / 2, y_mid - s * dly / 2, z_mid + dlz / 2],  # N + 1
            [x_mid - dlx / 2, y_mid + s * dly / 2, z_mid + dlz / 2],  # N + 2
        ]
        new_vert_2 = [
            [x_mid + dlx / 2, y_mid - s * dly / 2, z_mid - dlz / 2],  # N + 3
            [x_mid + dlx / 2, y_mid - s * dly / 2, z_mid + dlz / 2],  # N + 4
            [x_mid + dlx / 2, y_mid + s * dly / 2, z_mid + dlz / 2],  # N +5
        ]
    else:  # Left or Right
        dly, dlz = dormer_width, dormer_height
        assert dly < ly and dlz < lz
        dlx = lx * dlz / lz
        s = 1 if ori == "Left" else -1
        new_vert_1 = [
            [x_mid - s * dlx / 2, y_mid + dly / 2, z_mid - dlz / 2],  # N
            [x_mid - s * dlx / 2, y_mid + dly / 2, z_mid + dlz / 2],  # N + 1
            [x_mid + s * dlx / 2, y_mid + dly / 2, z_mid + dlz / 2],  # N + 2
        ]
        new_vert_2 = [
            [x_mid - s * dlx / 2, y_mid - dly / 2, z_mid - dlz / 2],  # N + 3
            [x_mid - s * dlx / 2, y_mid - dly / 2, z_mid + dlz / 2],  # N + 4
            [x_mid + s * dlx / 2, y_mid - dly / 2, z_mid + dlz / 2],  # N + 5
        ]
    vertices += (
        new_vert_1 + new_vert_2 if ori in ["Front", "Left"] else new_vert_2 + new_vert_1
    )
    # Add surfaces for dormer and decompose original roof into 4 parts
    v1, v2, v3, v4 = roof_vert_idx
    new_surfaces = {
        f"{ori}Dormer_Wall1": [N, N + 3, N + 4, N + 1],
        f"{ori}Dormer_Roof": [N + 1, N + 4, N + 5, N + 2],
        f"{ori}Dormer_Wall2": [N, N + 1, N + 2],
        f"{ori}Dormer_Wall3": [N + 3, N + 5, N + 4],
        f"{roof_surf_name}_1": [v1, v2, N + 3, N],
        f"{roof_surf_name}_2": [v2, v3, N + 5, N + 3],
        f"{roof_surf_name}_3": [N + 2, N + 5, v3, v4],
        f"{roof_surf_name}_4": [v1, N, N + 2, v4],
    }
    surfaces.update(new_surfaces)
    return


def make_gambrel_roof(
    dimensions: list[float],
    fraction_flat: float,
    orientation: str,
    origin: list[float],
    zone: str,
    shared_side_walls: bool,
):
    assert dimensions[2] > 0
    assert fraction_flat > 0
    assert orientation in ["left-right", "front-back"]
    lx, ly, lz = dimensions
    vertices = [[0, 0, 0], [lx, 0, 0], [lx, ly, 0], [0, ly, 0]]
    surfaces = {}
    if orientation == "left-right":
        vertices += [
            [lx / 2 * (1 - fraction_flat), 0, lz],
            [lx / 2 * (1 - fraction_flat), ly, lz],
            [lx / 2 * (1 + fraction_flat), 0, lz],
            [lx / 2 * (1 + fraction_flat), ly, lz],
        ]
        surfaces["Floor"] = [0, 3, 2, 1]
        surfaces["LeftRoof"] = [3, 0, 4, 5]
        surfaces["TopRoof"] = [4, 6, 7, 5]
        surfaces["RightRoof"] = [1, 2, 7, 6]
        surfaces["FrontWall"] = [0, 1, 6, 4]
        surfaces["BackWall"] = [2, 3, 5, 7]
    else:
        vertices += [
            [0, ly / 2 * (1 - fraction_flat), lz],  # 4
            [lx, ly / 2 * (1 - fraction_flat), lz],  # 5
            [0, ly / 2 * (1 + fraction_flat), lz],  # 6
            [lx, ly / 2 * (1 + fraction_flat), lz],  # 7
        ]
        surfaces["Floor"] = [0, 3, 2, 1]
        surfaces["FrontRoof"] = [0, 1, 5, 4]
        surfaces["TopRoof"] = [4, 5, 7, 6]
        surfaces["BackRoof"] = [2, 3, 6, 7]
        surfaces["SharedLeftWall" if shared_side_walls else "LeftWall"] = [3, 0, 4, 6]
        surfaces["SharedRightWall" if shared_side_walls else "RightWall"] = [1, 2, 7, 5]

    # Translate vertices based on origin
    vertices = np.array(vertices) + np.array(origin)
    surfaces = {f"{zone}-{surf}": idxs for surf, idxs in surfaces.items()}
    vertices, surfaces = fix_duplicate_vertices(vertices, surfaces)
    return vertices, surfaces


def merge_objects(objects: list[tuple], connected_zones: dict[tuple, bool]):
    """
    Merges several geometric objects into a single object.

    Each object is a tuple (vertices, surfaces). The function concatenates
    their vertices and surfaces, then removes duplicate vertices.

    Args:
        objects (list[tuple]): A list of objects to merge, where each object is a
        tuple (vertices, surfaces).

    Returns:
        tuple: A tuple (merged_vertices, merged_surfaces) for the combined object.
    """
    # Concatenate vertices
    concatenated_vertices = np.vstack([vertices for vertices, _ in objects])
    # Concatenate surfaces
    all_surfaces = objects[0][1].copy()
    offset = len(objects[0][0])
    for vertices, surfaces in objects[1:]:
        # Update indices for the second object's surfaces and handle name clashes
        for surf_name, surf_indices in surfaces.items():
            if surf_name in all_surfaces:
                raise ValueError(f"Duplicate surface: {surf_name}")
            all_surfaces[surf_name] = [idx + offset for idx in surf_indices]
        offset += len(vertices)

    # Use fix_duplicate_vertices to remove duplicates and update indices
    vertices, surfaces = fix_duplicate_vertices(concatenated_vertices, all_surfaces)

    # Process connected zones by merging or separating them
    vert_to_insert = {}
    for (zone1, zone2), merge in connected_zones.items():
        surf_name_small, surf_name_large = find_overlapping_surfaces(
            vertices, surfaces, zone1, zone2
        )
        vert_to_insert.update(
            find_overlapping_segments(
                vertices, surfaces, surf_name_small, surf_name_large
            )
        )
        fix_overlapping_surfaces(
            surfaces, surf_name_small, surf_name_large, merge, zone2
        )
    fix_overlapping_segments(surfaces, vert_to_insert)

    # Reorder surfaces alphabetically
    surfaces = dict(sorted(surfaces.items()))
    # Offset vertices to start from zero
    vertices -= np.min(vertices, axis=0)
    return vertices, surfaces


def fix_duplicate_vertices(vertices, surfaces):
    """
    Removes duplicate vertices and updates surface indices accordingly.
    Also removes duplicate vertices within each surface definition.

    Args:
        vertices (np.ndarray): Array of vertices, shape (N, 3).
        surfaces (dict): Dictionary mapping surface names to lists of vertex indices.

    Returns:
        tuple: A tuple (new_vertices, new_surfaces) with duplicates removed.
    """
    # Round to handle floating point inaccuracies
    rounded_vertices = np.round(vertices, decimals=5)

    # Find unique vertices and the mapping from old to new indices
    unique_vertices, inverse_indices = np.unique(
        rounded_vertices, axis=0, return_inverse=True
    )

    new_surfaces = {}
    for surf_name, surf_indices in surfaces.items():
        # Map old indices to new indices
        new_indices = [inverse_indices[idx] for idx in surf_indices]

        # Remove duplicate vertices within the surface definition
        # while preserving order
        unique_in_surface = []
        seen = set()
        for idx in new_indices:
            if idx not in seen:
                unique_in_surface.append(idx)
                seen.add(idx)

        new_surfaces[surf_name] = unique_in_surface
    # Remove surfaces that have less than 3 vertices
    new_surfaces = {k: v for k, v in new_surfaces.items() if len(v) >= 3}
    return unique_vertices, new_surfaces


def find_overlapping_surfaces(vertices, surfaces, zone1, zone2):
    """
    Find the two surfaces, find the other surface that is it overlapping with.
    Raise an error if no such surface could be found.
    """
    overlapping_surfaces = []
    for surf_name1 in surfaces:
        poly1 = ConvexPolygon(vertices[surfaces[surf_name1]])
        for surf_name2 in surfaces:
            if surf_name1.split("-")[0] == zone1 and surf_name2.split("-")[0] == zone2:
                poly2 = ConvexPolygon(vertices[surfaces[surf_name2]])
                # Check that one surface is included in the other with Geometry3D
                intersection = poly1.intersection(poly2)
                area1, area2 = poly1.area(), poly2.area()
                try:
                    area_intersection = intersection.area()
                except AttributeError:  # Intersection is not a polygon
                    continue
                if abs(area_intersection - area2) < 1e-6:  # poly2 in poly1
                    overlapping_surfaces.append((surf_name2, surf_name1))
                elif abs(area_intersection - area1) < 1e-6:  # poly1 in poly2
                    overlapping_surfaces.append((surf_name1, surf_name2))
    if overlapping_surfaces == []:
        raise ValueError(
            f"Couldn't find surface shared between zones {zone1} and {zone2}"
        )
    if len(overlapping_surfaces) > 1:
        raise ValueError(
            f"Multiple overlapping surfaces found between zones {zone1} and {zone2}: {overlapping_surfaces}"
        )
    return overlapping_surfaces[0]


def find_overlapping_segments(vertices, surfaces, surf1, surf2):
    """
    Find the two surfaces, find the other surface that is it overlapping with.
    Raise an error if no such surface could be found.
    """
    vert_to_insert = {}
    L1_vert = surfaces[surf1] + [surfaces[surf1][0]]
    L2_vert = surfaces[surf2] + [surfaces[surf2][0]]
    for idx_11, idx_12 in zip(L1_vert[:-1], L1_vert[1:]):
        seg1 = Geometry3D.Segment(
            Geometry3D.Point(vertices[idx_11]), Geometry3D.Point(vertices[idx_12])
        )
        set1 = set([idx_11, idx_12])
        for idx_21, idx_22 in zip(L2_vert[:-1], L2_vert[1:]):
            seg2 = Geometry3D.Segment(
                Geometry3D.Point(vertices[idx_21]), Geometry3D.Point(vertices[idx_22])
            )
            set2 = set([idx_21, idx_22])
            if set1 == set2:
                continue  # Same segment
            intersection = seg1.intersection(seg2)
            if type(intersection) is Geometry3D.Segment:
                if seg1.length() < seg2.length():
                    vert_to_insert[(idx_21, idx_22)] = list(set1 - set2)[0]
                else:
                    vert_to_insert[(idx_11, idx_12)] = list(set2 - set1)[0]
    return vert_to_insert


def fix_overlapping_surfaces(
    surfaces, surf_name_small, surf_name_large, merge: bool, new_zone=None
):
    """
    Given a small surface included in a large one, modifies the surfaces dict
    to merge them or not.
    """
    surf_small = surfaces.pop(surf_name_small)
    surf_large = surfaces.pop(surf_name_large)
    small_zone = surf_name_small.split("-")[0]
    large_zone = surf_name_large.split("-")[0]
    shared_vertices = set(surf_small) & set(surf_large)
    assert len(shared_vertices) in [2, 4]
    if len(shared_vertices) == 4 == len(surf_small):  # The two surfaces are identical
        if merge:
            update_zone_names(surfaces, [small_zone, large_zone], new_zone)
        else:
            surfaces[surf_name_small] = surf_small
            surfaces[surf_name_large] = surf_large
        return surfaces
    else:  # Split large surface in two parts
        D = {}
        for vert in shared_vertices:
            i_vert = surf_small.index(vert)
            i_prev, i_next = (i_vert - 1) % len(surf_small), (i_vert + 1) % len(
                surf_small
            )
            vert_prev, vert_next = surf_small[i_prev], surf_small[i_next]
            if vert_prev in shared_vertices:  # Use next
                D[vert] = vert_next
            elif vert_next in shared_vertices:  # Use prev
                D[vert] = vert_prev
            else:  # Raise error
                raise ValueError(
                    f"Shared vertex {vert} in surfaces {surf_name_small} and {surf_name_large} has both neighbours also shared. Cannot determine replacement."
                )
        # Then, surf_large_excl is easily obtained by replacing these vertices
        surf_large_excl = [D.get(vert, vert) for vert in surf_large]
        # Update surface dict
        if merge:
            surfaces[surf_name_large.replace(large_zone, new_zone)] = surf_large_excl
            update_zone_names(surfaces, [small_zone, large_zone], new_zone)
        else:
            surfaces[surf_name_small] = surf_small
            if (cpt := surf_name_large.split("_")[-1]).isdigit():
                surf_base_name_large = "_".join(surf_name_large.split("_")[:-1])
                surfaces[surf_name_large] = surf_small[::-1]
                surfaces[f"{surf_base_name_large}_{int(cpt) + 1}"] = surf_large_excl
            else:
                surfaces[f"{surf_name_large}_1"] = surf_small[::-1]
                surfaces[f"{surf_name_large}_2"] = surf_large_excl
    return


def update_zone_names(surfaces, old_zones, new_zone):
    """
    Given a list of old zone names, modifies the surfaces dict
    to update these zones to a new zone name.
    """
    for surf_name in surfaces.copy():
        surf_zone = surf_name.split("-")[0]
        if surf_zone in old_zones and surf_zone != new_zone:
            new_surf_name = f"{new_zone}-{surf_zone}_{surf_name.split('-')[1]}"
            surfaces[new_surf_name] = surfaces.pop(surf_name)
    return


def fix_overlapping_segments(surfaces, vert_to_insert):
    """
    Given a dict of segments to insert vertices into, modifies the surfaces dict
    to insert these vertices.
    """
    for (idx1, idx2), vert_idx_to_insert in vert_to_insert.items():
        for surf_name in surfaces.copy():
            L_vert = surfaces[surf_name] + [surfaces[surf_name][0]]
            for seg in zip(L_vert[:-1], L_vert[1:]):
                if set(seg) == set([idx1, idx2]):
                    idx_of_insert = L_vert.index(seg[0]) + 1
                    L_vert.insert(idx_of_insert, vert_idx_to_insert)
                    surfaces[surf_name] = L_vert[:-1]
    return


def make_house_geometry(
    n_floors: int,
    floor_dimensions: list[float],
    frac_shared_side_walls: float,
    roof_type: str,
    roof_orientation: str,
    roof_height: float,
    dormer_params: dict = {},
    extension_params: dict = {},
):
    """
    Creates the geometry of the terraced house.
    The house always has 3 or 4 zones, with one zone on the 0th floor (living room),
    two zones on the 1st floor (bedrooms), and one zones for the 2nd floor
    (attic or extra bedroom).

    Parameters
    ----------

    n_floors: int
        The number of floors of the house. Should be 2 or 3.
    floor_dimensions: list
        The floor dimensions (in meters) = [width, length, height].
        The width (resp. length) corresponds to the length of the front/back
        (resp. left/right) walls.
    frac_shared_side_walls: float,
        The fraction of side walls (left/right) which are shared with another terraced
        house, and thus modelled as adiabatic.
    roof_type: str
        The roof type = "pitched", "slanted", or "gambrel".
    roof_orientation: str
        The roof orientation = "front-back" or "left right for pitched and gambrel roof.
        For slanted roofs, supported values are "front", "back", "left" or "right".
    roof_height: float
        The roof height in meters.
    """

    assert n_floors in [2, 3]
    assert roof_type in ["pitched", "slanted", "gambrel"]
    if roof_type == "slanted":
        assert roof_orientation in ["front", "back", "left", "right"]
    else:
        assert roof_orientation in ["left-right", "front-back"]
        assert roof_height > 0
    lx, ly, lz = floor_dimensions
    # Add 0th and 1st floors
    objects = [
        make_box(
            dimensions=floor_dimensions,
            origin=[0, 0, 0],
            zone="0F",
            frac_shared_side_walls=frac_shared_side_walls,
        ),
        make_box(
            dimensions=[lx, ly / 2, lz],
            origin=[0, 0, lz],
            zone="1F_Front",
            frac_shared_side_walls=frac_shared_side_walls,
        ),
        make_box(
            dimensions=[lx, ly / 2, lz],
            origin=[0, ly / 2, lz],
            zone="1F_Back",
            frac_shared_side_walls=frac_shared_side_walls,
        ),
    ]
    connected_zones = {
        ("1F_Front", "0F"): False,
        ("1F_Back", "0F"): False,
    }
    if n_floors == 2 and roof_height == 0:
        pass
    elif n_floors == 2 and roof_height > 0:
        assert roof_type == "slanted"
        offset_front_roof = roof_height / 2 if roof_orientation == "back" else 0
        offset_back_roof = roof_height / 2 if roof_orientation == "front" else 0
        obj_roof_front = make_slanted_roof(
            dimensions=[
                lx,
                ly / 2,
                roof_height / (2 if roof_orientation in ["front", "back"] else 1),
            ],
            orientation=roof_orientation,
            origin=[0, 0, 2 * lz + offset_front_roof],
            zone="FrontRoof",
            frac_shared_side_walls=frac_shared_side_walls,
        )
        obj_roof_back = make_slanted_roof(
            dimensions=[
                lx,
                ly / 2,
                roof_height / (2 if roof_orientation in ["front", "back"] else 1),
            ],
            orientation=roof_orientation,
            origin=[0, ly / 2, 2 * lz + offset_back_roof],
            zone="BackRoof",
            frac_shared_side_walls=frac_shared_side_walls,
        )
        objects += [obj_roof_front, obj_roof_back]
        if roof_orientation in ["front", "back"]:
            ori = roof_orientation.capitalize()
            opp_ori = "Back" if roof_orientation == "front" else "Front"
            objects.append(
                make_box(
                    dimensions=[lx, ly / 2, roof_height / 2],
                    origin=[0, ly / 2 if ori == "Front" else 0, 2 * lz],
                    zone=f"{opp_ori}RoofBox",
                    frac_shared_side_walls=frac_shared_side_walls,
                )
            )
            connected_zones[(f"{ori}Roof", f"1F_{ori}")] = True
            connected_zones[(f"{opp_ori}RoofBox", f"1F_{opp_ori}")] = True
            connected_zones[(f"{opp_ori}Roof", f"1F_{opp_ori}")] = True
        else:
            connected_zones[("FrontRoof", "1F_Front")] = True
            connected_zones[("BackRoof", "1F_Back")] = True
    elif roof_type == "pitched":  # 3 floors with pitched roof
        obj_roof = make_pitched_roof(
            dimensions=[lx, ly, roof_height],
            orientation=roof_orientation,
            origin=[0, 0, 2 * lz],
            zone="2F",
            shared_side_walls=frac_shared_side_walls == 1,
            dormer_params=dormer_params,
        )
        objects.append(obj_roof)
        connected_zones[("2F", "1F_Front")] = False
        connected_zones[("2F", "1F_Back")] = False
    elif roof_type == "gambrel":  # 3 floors with gambrel roof
        obj_roof = make_gambrel_roof(
            dimensions=[lx, ly, roof_height],
            fraction_flat=0.4,
            orientation=roof_orientation,
            origin=[0, 0, 2 * lz],
            zone="2F",
            shared_side_walls=frac_shared_side_walls == 1,
        )
        objects.append(obj_roof)
        connected_zones[("2F", "1F_Front")] = False
        connected_zones[("2F", "1F_Back")] = False
    elif roof_type == "slanted":  # 3 floors with slanted roof
        # Add box for 2nd floor
        objects.append(
            make_box(
                dimensions=[lx, ly, lz],
                origin=[0, 0, 2 * lz],
                zone="2F",
                frac_shared_side_walls=frac_shared_side_walls,
            )
        )
        connected_zones[("2F", "1F_Front")] = False
        connected_zones[("2F", "1F_Back")] = False
        if roof_height > 0:  # Add slanted roof
            obj_roof = make_slanted_roof(
                dimensions=[lx, ly, roof_height],
                orientation=roof_orientation,
                origin=[0, 0, 3 * lz],
                zone="Roof",
                frac_shared_side_walls=frac_shared_side_walls,
            )
            objects.append(obj_roof)
            connected_zones[("Roof", "2F")] = True
    else:
        raise ValueError(f"Unsupported geometry")

    # Add extensions if specified
    for ext_loc, ext_params in extension_params.items():
        ext_loc = ext_loc.capitalize()
        ext_type = ext_params["type"]
        assert ext_type in ["box", "skidak"]
        assert ext_params["side"] in ["left", "right"]
        assert 0 < ext_params["width"] <= lx and 0 < ext_params["length"]
        ext_lx, ext_ly = ext_params["width"], ext_params["length"]
        offset_x = 0 if ext_params["side"] == "left" else lx - ext_lx
        offset_y = -ext_ly if ext_loc == "Front" else ly
        objects.append(
            make_box(
                dimensions=[ext_lx, ext_ly, lz],
                origin=[offset_x, offset_y, 0],
                zone=f"{ext_loc}Ext",
                frac_shared_side_walls=0,
            )
        )
        connected_zones[(f"{ext_loc}Ext", "0F")] = ext_params.get("merge", False)
        if ext_type == "skidak":
            assert ext_params.get("merge", False) == False
            objects.append(
                make_slanted_roof(
                    dimensions=[ext_lx, ext_ly, lz],
                    orientation=ext_loc.lower(),
                    origin=[offset_x, offset_y, lz],
                    zone=f"{ext_loc}Skidak",
                    frac_shared_side_walls=0,
                )
            )
            connected_zones[(f"{ext_loc}Skidak", f"1F_{ext_loc}")] = False
            connected_zones[(f"{ext_loc}Skidak", f"{ext_loc}Ext")] = True
    # Merge objects
    vertices, surfaces = merge_objects(objects, connected_zones)
    return vertices, surfaces


if __name__ == "__main__":
    vertices, surfaces = make_house_geometry(
        n_floors=3,
        floor_dimensions=[6, 8, 3],
        frac_shared_side_walls=0,
        roof_type="pitched",
        roof_orientation="front-back",
        roof_height=3,
        dormer_params={
            "front": {"width": 4, "height": 1.5},
            "back": {"width": 4, "height": 1.5},
        },
        extension_params={
            "front": {
                "type": "skidak",
                "width": 3,
                "length": 3,
                "side": "left",
                "merge": False,
            },
            "back": {
                "type": "box",
                "width": 3,
                "length": 2,
                "side": "right",
                "merge": True,
            },
        },
    )
    fig = visualize_geometry(vertices, surfaces, debug_mode=False)
    fig.show()
    check_for_naked_edges(surfaces)
    # TODO: code doesnt work when frac_shared_side_walls > 0
    # Need to update fix_overlapping_surfaces or make a function that cuts side walls
    # at the end (i.e. after merging), which may be easier
    # NOTE: skidak does not reach the roof when slanted and n_floors = 3. Is it fine?
    # plot_building(vertices, surfaces)
