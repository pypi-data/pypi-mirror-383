"""Python 3 module that imports cubit.

Which requires that Cubit's bin directory is found on PYTHONPATH, either directly by the end user or from a successful
:meth:`turbo_turtle._utilities.find_cubit_bin` call and internal ``sys.path`` modification. This module does *not*
perform ``sys.path`` manipulation, so the importing/calling module/script *must* verify that Cubit will import correctly
first.
"""

import pathlib
import typing

import numpy

from turbo_turtle import _utilities
from turbo_turtle._abaqus_python.turbo_turtle_abaqus import _mixed_utilities, parsers, vertices

cubit = _utilities.import_cubit()


def cubit_command_or_exception(command: str) -> bool:
    """Thin wrapper around ``cubit.cmd`` to raise an exception when returning False.

    Cubit returns True/False on ``cubit.cmd("")`` calls, but does not raise an exception. This method will raise a
    RuntimeError when the command returns False.

    :param command: Cubit APREPRO command to execute
    """
    success = cubit.cmd(command)
    if not success:
        raise RuntimeError(f"Command '{command}' returned an error. Please see the Cubit log for details.")
    return success


def geometry(
    input_file: typing.Sequence[str | pathlib.Path],
    output_file: str | pathlib.Path,
    planar: bool = parsers.geometry_defaults["planar"],  # type: ignore[assignment]
    part_name: str = parsers.geometry_defaults["part_name"],  # type: ignore[assignment]
    unit_conversion: float = parsers.geometry_defaults["unit_conversion"],  # type: ignore[assignment]
    euclidean_distance: float = parsers.geometry_defaults["euclidean_distance"],  # type: ignore[assignment]
    delimiter: str = parsers.geometry_defaults["delimiter"],  # type: ignore[assignment]
    header_lines: int = parsers.geometry_defaults["header_lines"],  # type: ignore[assignment]
    revolution_angle: float = parsers.geometry_defaults["revolution_angle"],  # type: ignore[assignment]
    y_offset: float = parsers.geometry_defaults["y_offset"],  # type: ignore[assignment]
    rtol: float = parsers.geometry_defaults["rtol"],  # type: ignore[assignment]
    atol: float = parsers.geometry_defaults["atol"],  # type: ignore[assignment]
) -> None:
    """Create 2D planar, 2D axisymmetric, or 3D revolved geometry from an array of XY coordinates.

    Note that 2D axisymmetric sketches and sketches for 3D bodies of revolution about the global Y-axis must lie
    entirely on the positive-X side of the global Y-axis.

    This function can create multiple sheet bodies or volumes in the same Cubit ``*.cub`` file. If no part (body/volume)
    names are provided, the body/volume will be named after the input file base name.

    :param str input_file: input text file(s) with coordinates to draw
    :param str output_file: Cubit ``*.cub`` database to save the part(s)
    :param bool planar: switch to indicate that 2D model dimensionality is planar, not axisymmetric
    :param list part_name: name(s) of the part(s) being created
    :param float unit_conversion: multiplication factor applies to all coordinates
    :param float euclidean_distance: if the distance between two coordinates is greater than this, draw a straight line.
        Distance should be provided in units *after* the unit conversion
    :param str delimiter: character to use as a delimiter when reading the input file
    :param int header_lines: number of lines in the header to skip when reading the input file
    :param float revolution_angle: angle of solid revolution for ``3D`` geometries. Ignore when planar is True.
    :param float y_offset: vertical offset along the global Y-axis. Offset should be provided in units *after* the unit
        conversion.
    :param float rtol: relative tolerance for vertical/horizontal line checks
    :param float atol: absolute tolerance for vertical/horizontal line checks

    :returns: writes ``{output_file}.cub``
    """
    # TODO: Figure out how to log the Cubit operations without printing to console
    # TODO: Figure out how to get a better log of the non-APREPRO actions
    cubit.init(["cubit", "-nojournal"])
    part_name = _mixed_utilities.validate_part_name(input_file, part_name)
    part_name = _mixed_utilities.cubit_part_names(part_name)
    output_file = pathlib.Path(output_file).with_suffix(".cub")
    surfaces = []
    for file_name, _new_part in zip(input_file, part_name, strict=True):
        coordinates = _mixed_utilities.return_genfromtxt(
            file_name, delimiter, header_lines, expected_dimensions=2, expected_columns=2
        )
        coordinates = vertices.scale_and_offset_coordinates(coordinates, unit_conversion, y_offset)
        lines, splines = vertices.lines_and_splines(coordinates, euclidean_distance, rtol=rtol, atol=atol)
        surfaces.append(_draw_surface(lines, splines))

    for surface, new_part in zip(surfaces, part_name, strict=True):
        _rename_and_sweep(surface, new_part, planar=planar, revolution_angle=revolution_angle)

    cubit_command_or_exception(f"save as '{output_file}' overwrite")


# Cannot use Cubit object type annotations because Cubit may not be importable at build/runtime
def _draw_surface(  # noqa: ANN202
    lines: list[tuple[tuple[float, float], tuple[float, float]]] | list[numpy.ndarray],
    splines: list[typing.Sequence[tuple[float, float]]] | list[numpy.ndarray],
):
    """Given ordered lists of line/spline coordinates, create a Cubit surface object.

    :param lines: list of [2, 2] shaped arrays of (x, y) coordinates defining a line segment
    :param splines: list of [N, 2] shaped arrays of (x, y) coordinates defining a spline

    :returns: Cubit surface defined by the lines and splines input
    :rtype: cubit.Surface
    """
    curves = []
    for first, second in lines:
        point1 = (*tuple(first), 0.0)
        point2 = (*tuple(second), 0.0)
        curves.append(create_curve_from_coordinates(point1, point2))
    for spline in splines:
        zero_column = numpy.zeros([len(spline), 1])
        spline_3d = numpy.append(spline, zero_column, axis=1)
        curves.append(create_spline_from_coordinates(spline_3d))
    return cubit.create_surface(curves)


# Cannot use Cubit object type annotations because Cubit may not be importable at build/runtime
def create_curve_from_coordinates(  # noqa: ANN202
    point1: tuple[float, float, float], point2: tuple[float, float, float]
):
    """Create a curve from 2 three-dimensional coordinates.

    :param tuple point1: First set of coordinates (x1, y1, z1)
    :param tuple point2: Second set of coordinates (x2, y2, z2)

    :returns: Cubit curve object defining a line segment
    :rtype: cubit.Curve
    """
    vertex1 = cubit.create_vertex(*tuple(point1))
    vertex2 = cubit.create_vertex(*tuple(point2))
    return cubit.create_curve(vertex1, vertex2)


# Cannot use Cubit object type annotations because Cubit may not be importable at build/runtime
def create_spline_from_coordinates(  # noqa: ANN202
    coordinates: typing.Sequence[tuple[float, float, float]] | numpy.ndarray,
):
    """Create a spline from a list of coordinates.

    :param coordinates: [N, 3] array of coordinates (x, y, z)

    :returns: Cubit curve object defining a spline
    :rtype: cubit.Curve
    """
    coordinates = numpy.array(coordinates)
    minimum = 2
    if coordinates.shape[0] < minimum:
        raise RuntimeError(f"Requires at least {minimum} coordinates to create a spline")

    points = [cubit.create_vertex(*tuple(point)) for point in coordinates]
    vertex_ids = [point.id() for point in points]
    vertex_ids_text = _utilities.character_delimited_list(vertex_ids)
    # TODO: Find a suitable Cubit Python function for creating splines that returns the curve object
    cubit_command_or_exception(f"create curve spline vertex {vertex_ids_text} delete")
    curve = points[0].curves()[0]
    return curve


# Cannot use Cubit object type annotations because Cubit may not be importable at build/runtime
def create_arc_from_coordinates(  # noqa: ANN202
    center: tuple[float, float, float] | numpy.ndarray,
    point1: tuple[float, float, float] | numpy.ndarray,
    point2: tuple[float, float, float] | numpy.ndarray,
):
    """Create a circular arc cubit.Curve object from center and points on the curve.

    :param center: tuple of floats (X, Y, Z) location for the center of the circle arc
    :param point1: tuple of floats (X, Y, Z) location for the first point on the arc
    :param point2: tuple of floats (X, Y, Z) location for the second point on the arc

    :returns: cubit curve object
    :rtype: curbit.Curve
    """
    center_vertex = cubit.create_vertex(*tuple(center))

    # Cubit creates arcs with anticlockwise rotation. Order vertices with most negative Y axis coordinate first.
    if point1[1] < point2[1]:
        vertex1 = cubit.create_vertex(*tuple(point1))
        vertex2 = cubit.create_vertex(*tuple(point2))
    else:
        vertex1 = cubit.create_vertex(*tuple(point2))
        vertex2 = cubit.create_vertex(*tuple(point1))

    # TODO: Find a suitable Cubit Python function for creating arcs that returns the curve object
    command = f"create curve arc center vertex {center_vertex.id()} {vertex1.id()} {vertex2.id()} normal 0 0 1"
    cubit_command_or_exception(command)
    curve = vertex1.curves()[0]
    cubit_command_or_exception(f"delete vertex {center_vertex.id()}")
    return curve


# Cannot use Cubit object type annotations because Cubit may not be importable at build/runtime
def create_surface_from_coordinates(  # noqa: ANN202
    coordinates: typing.Sequence[tuple[float, float, float]] | numpy.ndarray,
):
    """Create a surface from an [N, 3] array of coordinates.

    Each row of the array represents a coordinate in 3D space. Must have at least 3 rows or a RuntimeError is raised.
    Coordinates are connected in pairs to create curves. First and last coordinate connected for final curve. Curves
    must defind a closed perimeter to generate a surface.

    :param coordinates: [N, 3] array of 3D coordinates where N > 2.

    :returns: Cubit surface object
    :rtype: cubit.surface
    """
    coordinates = numpy.array(coordinates)
    if coordinates.shape[0] < 3:
        raise RuntimeError("Requires at least 3 coordinates to create a surface")
    curves = []
    last = numpy.array([coordinates[-1]])
    coordinates_shift = numpy.append(last, coordinates[0:-1], axis=0)
    for point1, point2 in zip(coordinates, coordinates_shift, strict=True):
        curves.append(create_curve_from_coordinates(point1, point2))
    return cubit.create_surface(curves)


def _surface_numbers(surfaces: typing.Sequence | numpy.ndarray) -> list[int]:
    """Return a list of surface IDs from the provided list of surface objects.

    :param surfaces: list of Cubit surface objects

    :returns: list of surface IDs
    """
    return [surface.surfaces()[0].id() for surface in surfaces]


def _surface_centroids(surfaces: list) -> list[numpy.ndarray]:
    """Return a list of 3D surface centroids from the provided list of surface objects.

    :param surfaces: list of Cubit surface objects

    :returns: list of surface centroids
    """
    surface_ids = _surface_numbers(surfaces)
    surface_centroids = [numpy.array(cubit.get_surface_centroid(_id)) for _id in surface_ids]
    return surface_centroids


def _surfaces_for_volumes(volumes: list) -> list:
    """Return a flat list of surface objects for a list of volumes.

    :param volumes: list of Cubit volume objects

    :returns: list of Cubit surface objects
    :rtype: list of cubit.Surface
    """
    surfaces = []
    for volume in volumes:
        surfaces.extend(volume.surfaces())
    return surfaces


def _surfaces_by_vector(
    surfaces: list,
    principal_vector: numpy.ndarray,
    center: tuple[float, float, float] | numpy.ndarray = (0.0, 0.0, 0.0),
) -> numpy.ndarray:
    """Return a flat list of Cubit surface objects that meet the requirement of a positive dot product between a given
    vector and the vector between two points: a user provided center point and a surface object centroid.

    :param surfaces: list of Cubit surface objects
    :param principal_vector: Local principal axis vector defined in global coordinates
    :param center: center location of the geometry

    :returns: numpy.array of Cubit surface objects
    """  # noqa: D205
    center = numpy.array(center)
    surface_centroids = _surface_centroids(surfaces)
    direction_vectors = [numpy.subtract(centroid, center) for centroid in surface_centroids]

    vector_dot = numpy.array(
        ([numpy.dot(direction_vector, principal_vector) for direction_vector in direction_vectors])
    )
    # Account for numerical errors in significant digits
    vector_dot[numpy.isclose(vector_dot, 0.0)] = 0.0
    return numpy.array(surfaces)[numpy.where(vector_dot > 0.0)]


# Cannot use Cubit object type annotations because Cubit may not be importable at build/runtime
def _create_volume_from_surfaces(surfaces: typing.Sequence | numpy.ndarray, keep: bool = True):  # noqa: ANN202
    """Create a volume from the provided surfaces. Surfaces must create a closed volume.

    :param surfaces: List of Cubit surface objects
    :param keep: Keep the original surface objects/sheet bodies

    :returns: Cubit volume object
    :rtype: cubit.Volume
    """
    volumes_before = cubit.get_entities("volume")
    surface_numbers = _surface_numbers(surfaces)
    surface_string = _utilities.character_delimited_list(surface_numbers)
    command = f"create volume surface {surface_string} heal"
    if keep:
        command = f"{command} keep"
    # TODO: Recover volume object directly when creation is possible with Cubit Python API
    cubit_command_or_exception(command)
    volumes_after = cubit.get_entities("volume")
    volume_id = list(set(volumes_after) - set(volumes_before))
    volume_id = volume_id[0]
    return cubit.volume(volume_id)


# Cannot use Cubit object type annotations because Cubit may not be importable at build/runtime
def _rename_and_sweep(  # noqa: ANN202
    surface,  # noqa: ANN001
    part_name: str,
    center: tuple[float, float, float] | numpy.ndarray = (0.0, 0.0, 0.0),
    planar: bool = parsers.geometry_defaults["planar"],  # type: ignore[assignment]
    revolution_angle: float = parsers.geometry_defaults["revolution_angle"],  # type: ignore[assignment]
):
    """Recover body or volume from body surface, sweep part if required, and rename body/volume by part name.

    Hyphens are replaced by underscores to make the ACIS engine happy.

    :param cubit.Surface surface: Cubit surface object to rename and conditionally sweep
    :param part_name: name of the part being created
    :param planar: switch to indicate that 2D model dimensionality is planar, not axisymmetric
    :param revolution_angle: angle of solid revolution for ``3D`` geometries. Ignore when planar is True.

    :returns: Cubit volume object
    :rtype: cubit.Volume
    """
    center = numpy.array(center)
    center_string = _utilities.character_delimited_list(center)
    revolution_axis = numpy.array([0.0, 1.0, 0.0])
    revolution_string = _utilities.character_delimited_list(revolution_axis)
    surface_number = _surface_numbers([surface])[0]
    part_name = part_name.replace("-", "_")
    if planar:
        return_object = surface.volumes()[0]
    elif numpy.isclose(revolution_angle, 0.0):
        return_object = surface.volumes()[0]
    else:
        cubit_command_or_exception(
            f"sweep surface {surface_number} axis {center_string} {revolution_string} angle {revolution_angle} merge"
        )
        return_object = surface.volumes()[0]
        volume_id = return_object.id()
        cubit_command_or_exception(f"regularize volume {volume_id}")

    return_object.set_entity_name(part_name)
    return return_object


def _get_volumes_from_name(names: list[str]) -> list:
    """Return all volume objects with a prefix from the ``names`` list.

    :param names: Name(s) prefix to search for with ``cubit.get_all_ids_from_name``

    :returns: list of Cubit volumes with name prefix
    :rtype: list of cubit.Volume objects
    """
    if isinstance(names, str):
        names = [names]
    parts = []
    for name in names:
        parts.extend([cubit.volume(number) for number in cubit.get_all_ids_from_name("volume", name)])
    if len(parts) < 1:
        raise RuntimeError(f"Could not find any volumes with prefix '{name}'")
    return parts


def cylinder(
    inner_radius: float,
    outer_radius: float,
    height: float,
    output_file: str | pathlib.Path,
    part_name: str = parsers.cylinder_defaults["part_name"],  # type: ignore[assignment]
    revolution_angle: float = parsers.geometry_defaults["revolution_angle"],  # type: ignore[assignment]
    y_offset: float = parsers.cylinder_defaults["y_offset"],  # type: ignore[assignment]
) -> None:
    """Accept dimensions of a right circular cylinder and generate an axisymmetric revolved geometry.

    Centroid of cylinder is located on the global coordinate origin by default.

    :param inner_radius: Radius of the hollow center
    :param outer_radius: Outer radius of the cylinder
    :param height: Height of the cylinder
    :param output_file: Cubit ``*.cub`` database to save the part(s)
    :param part_name: name(s) of the part(s) being created
    :param revolution_angle: angle of solid revolution for ``3D`` geometries
    :param y_offset: vertical offset along the global Y-axis
    """
    cubit.init(["cubit", "-nojournal"])
    part_name = _mixed_utilities.cubit_part_names(part_name)
    output_file = pathlib.Path(output_file).with_suffix(".cub")

    lines = vertices.cylinder_lines(inner_radius, outer_radius, height, y_offset=y_offset)
    surface = _draw_surface(lines, [])
    _rename_and_sweep(surface, part_name, revolution_angle=revolution_angle)

    cubit_command_or_exception(f"save as '{output_file}' overwrite")


def sphere(
    inner_radius: float,
    outer_radius: float,
    output_file: str | pathlib.Path,
    input_file: str | pathlib.Path | None = parsers.sphere_defaults["input_file"],  # type: ignore[assignment]
    quadrant: typing.Literal["upper", "lower", "both"] = parsers.sphere_defaults["quadrant"],  # type: ignore[assignment]
    revolution_angle: float = parsers.sphere_defaults["revolution_angle"],  # type: ignore[assignment]
    y_offset: float = parsers.sphere_defaults["y_offset"],  # type: ignore[assignment]
    part_name: str = parsers.sphere_defaults["part_name"],  # type: ignore[assignment]
) -> None:
    """Create a sphere geometry with file I/O handling.

    :param inner_radius: inner radius (size of hollow)
    :param outer_radius: outer radius (size of sphere)
    :param output_file: output file name. Will be stripped of the extension and ``.cub`` will be used.
    :param input_file: input file name. Will be stripped of the extension and ``.cub`` will be used.
    :param quadrant: quadrant of XY plane for the sketch: upper (I), lower (IV), both
    :param revolution_angle: angle of rotation 0.-360.0 degrees. Provide 0 for a 2D axisymmetric model.
    :param y_offset: vertical offset along the global Y-axis
    :param part_name: name of the part to be created in the Abaqus model
    """
    cubit.init(["cubit", "-nojournal"])

    # Preserve the (X, Y) center implementation, but use the simpler y-offset interface
    center = (0.0, y_offset)

    part_name = _mixed_utilities.cubit_part_names(part_name)
    output_file = pathlib.Path(output_file).with_suffix(".cub")
    if input_file is not None:
        input_file = pathlib.Path(input_file).with_suffix(".cub")
        # Avoid modifying the contents or timestamp on the input file.
        # Required to get conditional re-builds with a build system such as GNU Make, CMake, or SCons
        with _utilities.NamedTemporaryFileCopy(input_file, suffix=".cub", dir=".") as copy_file:
            # TODO: look for a Cubit Python interface proper open/close/save command(s)
            cubit_command_or_exception(f"open '{copy_file.name}'")
            _sphere(
                inner_radius,
                outer_radius,
                quadrant=quadrant,
                revolution_angle=revolution_angle,
                center=center,
                part_name=part_name,
            )
            cubit_command_or_exception(f"save as '{output_file}' overwrite")

    else:
        _sphere(
            inner_radius,
            outer_radius,
            quadrant=quadrant,
            revolution_angle=revolution_angle,
            center=center,
            part_name=part_name,
        )
        cubit_command_or_exception(f"save as '{output_file}' overwrite")


def _sphere(
    inner_radius: float,
    outer_radius: float,
    quadrant: typing.Literal["upper", "lower", "both"] = parsers.sphere_defaults["quadrant"],  # type: ignore[assignment]
    revolution_angle: float = parsers.sphere_defaults["revolution_angle"],  # type: ignore[assignment]
    center: tuple[float, float] = parsers.sphere_defaults["center"],  # type: ignore[assignment]
    part_name: str = parsers.sphere_defaults["part_name"],  # type: ignore[assignment]
) -> None:
    """Create a sphere geometry without file I/O.

    :param inner_radius: inner radius (size of hollow)
    :param outer_radius: outer radius (size of sphere)
    :param quadrant: quadrant of XY plane for the sketch: upper (I), lower (IV), both
    :param revolution_angle: angle of rotation 0.-360.0 degrees. Provide 0 for a 2D axisymmetric model.
    :param center: tuple of floats (X, Y) location for the center of the sphere
    :param part_name: name of the part to be created in the Abaqus model
    """
    # TODO: consolidate pure Python 3 logic in a common module for both Gmsh and Cubit
    # https://re-git.lanl.gov/aea/python-projects/turbo-turtle/-/boards
    arc_points = vertices.sphere(center, inner_radius, outer_radius, quadrant)
    inner_point1 = arc_points[0]
    inner_point2 = arc_points[1]
    outer_point1 = arc_points[2]
    outer_point2 = arc_points[3]

    center_3d = numpy.append(center, [0.0])
    curves = []
    if numpy.allclose(inner_point1, center) and numpy.allclose(inner_point2, center):
        inner_point1 = center
        inner_point2 = center
    else:
        curves.append(create_arc_from_coordinates(center_3d, inner_point1, inner_point2))
    curves.append(create_arc_from_coordinates(center_3d, outer_point1, outer_point2))
    curves.append(create_curve_from_coordinates(inner_point1, outer_point1))
    curves.append(create_curve_from_coordinates(inner_point2, outer_point2))
    surface = cubit.create_surface(curves)

    _rename_and_sweep(surface, part_name, revolution_angle=revolution_angle, center=center_3d)


def imprint_and_merge(names: list[str]) -> None:
    """Imprint and merge all volume objects with a prefix from the ``names`` list.

    :param names: Name(s) prefix to search for with ``cubit.get_all_ids_from_name``
    """
    parts = _get_volumes_from_name(names)
    part_ids = [part.id() for part in parts]
    part_string = _utilities.character_delimited_list(part_ids)

    cubit_command_or_exception(f"imprint volume {part_string}")
    cubit_command_or_exception(f"merge volume {part_string}")


def webcut_local_coordinate_primary_planes(
    center: tuple[float, float, float] | numpy.ndarray,
    xvector: tuple[float, float, float] | numpy.ndarray,
    zvector: tuple[float, float, float] | numpy.ndarray,
    names: list[str],
) -> list:
    """Webcut all volumes with a prefix in the ``names`` list on the local coordinate system primary planes.

    :param center: center location of the geometry
    :param xvector: Local x-axis vector defined in global coordinates
    :param zvector: Local z-axis vector defined in global coordinates
    :param names: Volume name prefix(es) to search for with ``cubit.get_all_ids_from_name``

    :returns: list of Cubit volumes with name prefix(es)
    :rtype: list of cubit.Volume objects
    """
    center = numpy.array(center)
    xvector = numpy.array(xvector)
    zvector = numpy.array(zvector)
    yvector = numpy.cross(zvector, xvector)
    # Create local coordinate system primary planes
    surface_coordinates = [
        numpy.array([center, center + xvector, center + yvector]),
        numpy.array([center, center + yvector, center + zvector]),
        numpy.array([center, center + zvector, center + xvector]),
    ]
    primary_surfaces = [create_surface_from_coordinates(coordinates) for coordinates in surface_coordinates]
    primary_surface_numbers = _surface_numbers(primary_surfaces)
    primary_surface_string = _utilities.character_delimited_list(primary_surface_numbers)

    # Webcut with local coordinate system primary planes
    for number in primary_surface_numbers:
        parts = _get_volumes_from_name(names)
        part_ids = [part.id() for part in parts]
        part_string = _utilities.character_delimited_list(part_ids)
        cubit_command_or_exception(f"webcut volume {part_string} with plane from surface {number}")

    # Clean up primary surfaces
    cubit_command_or_exception(f"delete surface {primary_surface_string}")

    return _get_volumes_from_name(names)


def create_pyramid_volumes(
    center: tuple[float, float, float] | numpy.ndarray,
    xvector: tuple[float, float, float] | numpy.ndarray,
    zvector: tuple[float, float, float] | numpy.ndarray,
    size: float,
) -> list:
    """Return the six (6) four-sided pyramid volumes defined by a cube's center point and six outer faces.

    :param list center: center location of the geometry
    :param list xvector: Local x-axis vector defined in global coordinates
    :param list zvector: Local z-axis vector defined in global coordinates
    :param float size: Half-length of the cube diagonals (length of the pyramid tip to corner)

    :returns: list of Cubit volumes
    :rtype: list of cubit.Volume objects
    """
    center = numpy.array(center)
    xvector = numpy.array(xvector)
    zvector = numpy.array(zvector)
    yvector = numpy.cross(zvector, xvector)

    # Create 6 4-sided pyramidal bodies defining the partitioning intersections
    surface_coordinates = vertices.pyramid_surfaces(center, xvector, zvector, size)
    pyramid_surfaces = [create_surface_from_coordinates(coordinates) for coordinates in surface_coordinates]

    # Identify surfaces for individual pyramid volumes based on location relative to local coordinate system
    pyramid_volume_surfaces = [
        _surfaces_by_vector(pyramid_surfaces, yvector, center),  # +Y
        _surfaces_by_vector(pyramid_surfaces, -yvector, center),  # -Y
        _surfaces_by_vector(pyramid_surfaces, xvector, center),  # +X
        _surfaces_by_vector(pyramid_surfaces, -xvector, center),  # -X
        _surfaces_by_vector(pyramid_surfaces, zvector, center),  # +Z
        _surfaces_by_vector(pyramid_surfaces, -zvector, center),  # -Z
    ]
    pyramid_volumes = [_create_volume_from_surfaces(surface_list) for surface_list in pyramid_volume_surfaces]

    # Remove pyramidal construction surfaces
    surface_numbers = _surface_numbers(pyramid_surfaces)
    surface_string = _utilities.character_delimited_list(surface_numbers)
    cubit_command_or_exception(f"delete surface {surface_string}")
    # TODO: ^^ Move pyramid volume creation to a dedicated function ^^

    return pyramid_volumes


def create_pyramid_partitions(
    center: tuple[float, float, float] | numpy.ndarray,
    xvector: tuple[float, float, float] | numpy.ndarray,
    zvector: tuple[float, float, float] | numpy.ndarray,
    size: float,
    names: list[str],
) -> list:
    """Partition all volumes with a prefix in the ``names`` list with the size pyramids defined by a cube.

    :param center: center location of the geometry
    :param xvector: Local x-axis vector defined in global coordinates
    :param zvector: Local z-axis vector defined in global coordinates
    :param size: Half-length of the cube diagonals (length of the pyramid tip to corner)
    :param names: Volume name prefix(es) to search for with ``cubit.get_all_ids_from_name``

    :returns: list of Cubit volumes
    :rtype: list of cubit.Volume objects
    """
    # Create pyramid partitioning (intersecting) volumes
    pyramid_volumes = create_pyramid_volumes(center, xvector, zvector, size)
    pyramid_volume_numbers = [pyramid.id() for pyramid in pyramid_volumes]
    pyramid_volume_string = _utilities.character_delimited_list(pyramid_volume_numbers)

    # Create pyramidal intersections/partitions
    parts = _get_volumes_from_name(names)
    for volume in pyramid_volumes:
        volume_id = volume.id()
        for part in parts:
            cubit_command_or_exception(f"intersect volume {volume_id} with volume {part.id()} keep")
    for part in parts:
        cubit_command_or_exception(f"delete volume {part.id()}")

    # Clean up pyramid volumes
    cubit_command_or_exception(f"delete volume {pyramid_volume_string}")

    return _get_volumes_from_name(names)


def partition(
    input_file: str | pathlib.Path,
    output_file: str | pathlib.Path = parsers.partition_defaults["output_file"],  # type: ignore[assignment]
    center: tuple[float, float, float] | numpy.ndarray = parsers.partition_defaults["center"],  # type: ignore[assignment]
    xvector: tuple[float, float, float] | numpy.ndarray = parsers.partition_defaults["xvector"],  # type: ignore[assignment]
    zvector: tuple[float, float, float] | numpy.ndarray = parsers.partition_defaults["zvector"],  # type: ignore[assignment]
    part_name: list[str] = parsers.partition_defaults["part_name"],  # type: ignore[assignment]
    big_number: float = parsers.partition_defaults["big_number"],  # type: ignore[assignment]
) -> None:
    """Partition Cubit files with pyramidal body intersections defined by a cube's center and vertices and with local
    coordinate planes.

    :param input_file: Cubit ``*.cub`` file to open that already contains parts/volumes to be meshed
    :param output_file: Cubit ``*.cub`` file to write
    :param center: center location of the geometry
    :param xvector: Local x-axis vector defined in global coordinates
    :param zvector: Local z-axis vector defined in global coordinates
    :param part_name: part/volume name prefixes
    :param big_number: Number larger than the outer radius of the part to partition.
    """  # noqa: D205
    cubit.init(["cubit", "-nojournal"])
    part_name = _mixed_utilities.cubit_part_names(part_name)

    if output_file is None:
        output_file = input_file
    input_file = pathlib.Path(input_file).with_suffix(".cub")
    output_file = pathlib.Path(output_file).with_suffix(".cub")
    with _utilities.NamedTemporaryFileCopy(input_file, suffix=".cub", dir=".") as copy_file:
        cubit_command_or_exception(f"open '{copy_file.name}'")
        _partition(center, xvector, zvector, part_name, big_number)
        cubit_command_or_exception(f"save as '{output_file}' overwrite")


def _partition(
    center: tuple[float, float, float] | numpy.ndarray = parsers.partition_defaults["center"],  # type: ignore[assignment]
    xvector: tuple[float, float, float] | numpy.ndarray = parsers.partition_defaults["xvector"],  # type: ignore[assignment]
    zvector: tuple[float, float, float] | numpy.ndarray = parsers.partition_defaults["zvector"],  # type: ignore[assignment]
    part_name: list[str] = parsers.partition_defaults["part_name"],  # type: ignore[assignment]
    big_number: float = parsers.partition_defaults["big_number"],  # type: ignore[assignment]
) -> None:
    """Partition Cubit files with pyramidal body intersections defined by a cube's center and vertices and with local
    coordinate planes.

    :param center: center location of the geometry
    :param xvector: Local x-axis vector defined in global coordinates
    :param zvector: Local z-axis vector defined in global coordinates
    :param part_name: part/volume name prefixes
    :param big_number: Number larger than the outer radius of the part to partition.
    """  # noqa: D205
    center = numpy.array(center)
    xvector = numpy.array(xvector)
    zvector = numpy.array(zvector)

    # Create pyramidal intersections/partitions
    create_pyramid_partitions(center, xvector, zvector, big_number, part_name)

    # Webcut with local coordinate system primary planes
    webcut_local_coordinate_primary_planes(center, xvector, zvector, part_name)

    # Imprint and merge
    for current_part_name in part_name:
        imprint_and_merge([current_part_name])


def _set_from_mask(feature: str, name_mask: typing.Sequence[tuple[str, str | int]]) -> None:
    """Create named features, with associated node and sidesets, by feature ID.

    :param feature: Cubit feature name
    :param name_mask: Feature set tuples (name, ID string)
    """
    feature = feature.lower()

    for name, mask in name_mask:
        cubit_command_or_exception(f'{feature} {mask} name "{name}"')

        nodeset_id = cubit.get_next_nodeset_id()
        cubit_command_or_exception(f"nodeset {nodeset_id} ADD {feature} {mask}")
        cubit_command_or_exception(f'nodeset {nodeset_id} name "{name}"')

        if feature not in ("vertex", "node"):
            sideset_id = cubit.get_next_sideset_id()
            cubit_command_or_exception(f"sideset {sideset_id} ADD {feature} {mask}")
            cubit_command_or_exception(f'sideset {sideset_id} name "{name}"')


def _feature_seeds(feature: str, name_number: typing.Sequence[tuple[str, str | int | float]]) -> None:
    """Create mesh seeds on features by name.

    If the number is an integer, seed by interval. If the number is a float, seed by size

    :param feature: Cubit feature name
    :param name_number: Feature seed tuples (name, number)
    """
    names, numbers = zip(*name_number, strict=True)
    float_numbers = [float(number) for number in numbers]
    positive_numbers = [number > 0.0 for number in float_numbers]
    if not all(positive_numbers):
        raise ValueError("Feature seeds must be positive numbers")
    for name, number in zip(names, float_numbers, strict=True):
        feature_ids = _utilities.character_delimited_list(cubit.get_all_ids_from_name(feature, name))
        if number.is_integer():
            cubit_command_or_exception(f"{feature} {feature_ids} interval {int(number)}")
        else:
            cubit_command_or_exception(f"{feature} {feature_ids} size {number}")


def _sets(
    face_sets: typing.Sequence[tuple[str, str | int]] | None = parsers.sets_defaults["face_sets"],  # type: ignore[assignment]
    edge_sets: typing.Sequence[tuple[str, str | int]] | None = parsers.sets_defaults["edge_sets"],  # type: ignore[assignment]
    vertex_sets: typing.Sequence[tuple[str, str | int]] | None = parsers.sets_defaults["vertex_sets"],  # type: ignore[assignment]
) -> None:
    """Create named features, with associated node and sidesets, by feature ID.

    :param face_sets: Face set tuples (name, mask)
    :param edge_sets: Edge set tuples (name, mask)
    :param vertex_sets: Vertex set tuples (name, mask)
    """
    if face_sets is not None:
        _set_from_mask("surface", face_sets)

    if edge_sets is not None:
        _set_from_mask("curve", edge_sets)

    if vertex_sets is not None:
        _set_from_mask("vertex", vertex_sets)


def sets(
    input_file: str | pathlib.Path,
    output_file: str | pathlib.Path | None = parsers.sets_defaults["output_file"],
    part_name: str | None = parsers.sets_defaults["part_name"],
    face_sets: typing.Sequence[tuple[str, str | int]] | None = parsers.sets_defaults["face_sets"],  # type: ignore[assignment]
    edge_sets: typing.Sequence[tuple[str, str | int]] | None = parsers.sets_defaults["edge_sets"],  # type: ignore[assignment]
    vertex_sets: typing.Sequence[tuple[str, str | int]] | None = parsers.sets_defaults["vertex_sets"],  # type: ignore[assignment]
) -> None:
    """Create Cubit sidesets and nodesets from feature numbers.

    :param input_file: Cubit ``*.cub`` file to open that already contains parts/volumes to be meshed
    :param output_file: Cubit ``*.cub`` file to write
    :param part_name: part/volume name prefix
    :param face_sets: Face set tuples (name, mask)
    :param edge_sets: Edge set tuples (name, mask)
    :param vertex_sets: Vertex set tuples (name, mask)
    """
    cubit.init(["cubit", "-nojournal"])
    part_name = _mixed_utilities.cubit_part_names(part_name)

    if not any([face_sets, edge_sets, vertex_sets]):
        raise RuntimeError("Must specify at least one of: face_sets, edge_sets, vertex_sets")

    if output_file is None:
        output_file = input_file
    input_file = pathlib.Path(input_file).with_suffix(".cub")
    output_file = pathlib.Path(output_file).with_suffix(".cub")
    with _utilities.NamedTemporaryFileCopy(input_file, suffix=".cub", dir=".") as copy_file:
        cubit_command_or_exception(f"open '{copy_file.name}'")
        _sets(face_sets, edge_sets, vertex_sets)
        cubit_command_or_exception(f"save as '{output_file}' overwrite")


def mesh(
    input_file: str | pathlib.Path,
    element_type: str,
    output_file: str | pathlib.Path | None = parsers.mesh_defaults["output_file"],  # type: ignore[assignment]
    part_name: str | None = parsers.mesh_defaults["part_name"],  # type: ignore[assignment]
    global_seed: float = parsers.mesh_defaults["global_seed"],  # type: ignore[assignment]
    edge_seeds: typing.Sequence[tuple[str, str | int | float]] | None = parsers.mesh_defaults["edge_seeds"],  # type: ignore[assignment]
) -> None:
    """Mesh Cubit volumes and sheet bodies by part/volume name.

    :param input_file: Cubit ``*.cub`` file to open that already contains parts/volumes to be meshed
    :param element_type: Cubit scheme "trimesh" or "tetmesh". Else ignored.
    :param output_file: Cubit ``*.cub`` file to write
    :param part_name: part/volume name prefix
    :param global_seed: The global mesh seed size
    :param edge_seeds: Edge seed tuples (name, number)
    """
    cubit.init(["cubit", "-nojournal"])
    part_name = _mixed_utilities.cubit_part_names(part_name)

    if output_file is None:
        output_file = input_file
    input_file = pathlib.Path(input_file).with_suffix(".cub")
    output_file = pathlib.Path(output_file).with_suffix(".cub")
    with _utilities.NamedTemporaryFileCopy(input_file, suffix=".cub", dir=".") as copy_file:
        cubit_command_or_exception(f"open '{copy_file.name}'")
        _mesh(element_type, part_name, global_seed, edge_seeds)
        cubit_command_or_exception(f"save as '{output_file}' overwrite")


def _mesh_sheet_body(
    # Cannot use Cubit object type annotations because Cubit may not be importable at build/runtime
    volume,  # noqa: ANN001
    global_seed: float,
    element_type: str | None = None,
) -> None:
    """Mesh a volume that is a sheet body.

    Assumes ``cubit.is_sheet_body(volume.id())`` is ``True``.

    :param cubit.Volume volume: Cubit volume to mesh as a sheet body
    :param global_seed: Seed size, e.g. ``cubit.cmd(surface {} size {global_seed}``
    :param element_type: Cubit meshing scheme. Accepts 'trimesh' or is ignored.
    """
    # TODO: Process multiple sheet bodies with a single Cubit command set
    # https://re-git.lanl.gov/aea/python-projects/turbo-turtle/-/issues/80
    surface_objects = volume.surfaces()
    surfaces = [surface.id() for surface in surface_objects]
    surface_string = _utilities.character_delimited_list(surfaces)
    if element_type == "trimesh":
        cubit_command_or_exception(f"surface {surface_string} scheme {element_type}")
    cubit_command_or_exception(f"surface {surface_string} size {global_seed}")
    for surface in surface_objects:
        surface.mesh()


def _mesh_volume(
    # Cannot use Cubit object type annotations because Cubit may not be importable at build/runtime
    volume,  # noqa: ANN001
    global_seed: float,
    element_type: str | None = None,
) -> None:
    """Mesh a volume.

    :param cubit.Volume volume: Cubit volume to mesh
    :param global_seed: Seed size, e.g. ``cubit.cmd(volume {} size {global_seed}``
    :param element_type: Cubit meshing scheme. Accepts 'tetmesh' or is ignored.
    """
    # TODO: Process multiple volumes with a single Cubit command set
    # https://re-git.lanl.gov/aea/python-projects/turbo-turtle/-/issues/80
    volume_id = volume.id()
    if element_type == "tetmesh":
        cubit_command_or_exception(f"volume {volume_id} scheme {element_type}")
    cubit_command_or_exception(f"volume {volume_id} size {global_seed}")
    volume.mesh()


def _mesh_multiple_volumes(volumes: list, global_seed: float, element_type: str | None = None) -> None:
    """Mesh ``cubit.Volume`` objects as volumes or sheet bodies.

    :param volumes: list of Cubit volume objects to mesh
    """
    # TODO: Process all sheet bodies and all volumes with a single Cubit command set
    # https://re-git.lanl.gov/aea/python-projects/turbo-turtle/-/issues/80
    for volume in volumes:
        volume_id = volume.id()
        if cubit.is_sheet_body(volume_id):
            _mesh_sheet_body(volume, global_seed, element_type=element_type)
        else:
            _mesh_volume(volume, global_seed, element_type=element_type)


def _mesh(
    element_type: str,
    part_name: str,
    global_seed: float,
    edge_seeds: typing.Sequence[tuple[str, str | int | float]] | None,
) -> None:
    """Mesh Cubit volumes and sheet bodies by part/volume name.

    :param element_type: Cubit scheme "trimesh" or "tetmesh". Else ignored.
    :param part_name: part/volume name prefix
    :param global_seed: The global mesh seed size
    :param edge_seeds: Edge seed tuples (name, number)
    """
    parts = _get_volumes_from_name([part_name])
    element_type = element_type.lower()
    # TODO: Cubit can support more than just edge seeds
    # https://re-git.lanl.gov/aea/python-projects/turbo-turtle/-/issues/174
    if edge_seeds is not None:
        _feature_seeds("curve", edge_seeds)
    _mesh_multiple_volumes(parts, global_seed, element_type=element_type)


def merge(input_file: typing.Sequence[str | pathlib.Path], output_file: str | pathlib.Path) -> None:
    """Merge Cubit ``*.cub`` files with forced unique block IDs and save to output file.

    :param input_file: List of Cubit ``*.cub`` file(s) to merge
    :param output_file: Cubit ``*.cub`` file to write
    """
    cubit.init(["cubit", "-nojournal"])
    input_file = [pathlib.Path(path).with_suffix(".cub") for path in input_file]
    output_file = pathlib.Path(output_file).with_suffix(".cub")
    for path in input_file:
        cubit_command_or_exception(f"import cubit '{path}' unique_genesis_ids")
    cubit_command_or_exception(f"save as '{output_file}' overwrite")


def export(
    input_file: str | pathlib.Path,
    part_name: list[str] = parsers.export_defaults["part_name"],  # type: ignore[assignment]
    element_type: list[str | None] = parsers.export_defaults["element_type"],  # type: ignore[assignment]
    destination: str | pathlib.Path = parsers.export_defaults["destination"],  # type: ignore[assignment]
    output_type: typing.Literal["abaqus", "genesis", "genesis-normal", "genesis-hdf5"] = parsers.export_defaults[  # type: ignore[assignment]
        "output_type"
    ],
) -> None:
    """Open a Cubit ``*.cub`` file and export ``part_name`` prefixed volumes as ``part_name``.inp.

    :param input_file: Cubit ``*.cub`` file to open that already contains meshed parts/volumes
    :param part_name: list of part/volume name prefix to export
    :param element_type: list of element types, one per part name or one global replacement for every part name
    :param destination: write output orphan mesh files to this output directory
    :param output_type: String identifying genesis output type: abaqus, genesis (large format), genesis-normal,
        genesis-hdf5
    """
    cubit.init(["cubit", "-nojournal"])
    part_name = _mixed_utilities.cubit_part_names(part_name)
    element_type = _mixed_utilities.validate_element_type(length_part_name=len(part_name), element_type=element_type)
    input_file = pathlib.Path(input_file).with_suffix(".cub")
    destination = pathlib.Path(destination)

    cubit_command_or_exception(f"open '{input_file}'")

    if output_type == "abaqus":
        _export_abaqus_list(part_name, element_type, destination)
    elif output_type.lower().startswith("genesis"):
        output_file = destination / input_file.with_suffix(".g").name
        _export_genesis(output_file, part_name, element_type, output_type)
    else:
        raise RuntimeError(f"Uknown output type request '{output_type}'")


def _create_new_block(volumes: list) -> int:
    """Create a new block for all volumes in list.

    Sheet bodies are added to block as surfaces. Volumes are added as volumes.

    :param volumes: list of Cubit volume objects

    :returns: new block ID
    """
    new_block_id = cubit.get_next_block_id()
    volume_ids = [volume.id() for volume in volumes]
    volume_string = _utilities.character_delimited_list(volume_ids)
    if any(cubit.is_sheet_body(volume_id) for volume_id in volume_ids):
        surfaces = _surface_numbers(_surfaces_for_volumes(volumes))
        surface_string = _utilities.character_delimited_list(surfaces)
        cubit_command_or_exception(f"block {new_block_id} add surface {surface_string}")
    else:
        cubit_command_or_exception(f"block {new_block_id} add volume {volume_string}")
    return new_block_id


def _create_volume_name_block(name: str) -> int:
    """Create a new block with all volumes prefixed by name.

    :param name: Name for new block and prefix for volume search

    :returns: New block ID
    """
    volumes = _get_volumes_from_name([name])
    new_block_id = _create_new_block(volumes)
    cubit_command_or_exception(f"block {new_block_id} name '{name}'")
    return new_block_id


def _set_genesis_output_type(output_type: typing.Literal["genesis", "genesis-normal", "genesis-hdf5"]) -> None:
    """Set Cubit exodus/genesis output type.

    :param output_type: String identifying genesis output type: genesis (large format), genesis-normal, genesis-hdf5
    """
    if output_type.lower() == "genesis":
        cubit_command_or_exception("set large exodus file on")
    elif output_type.lower() == "genesis-normal":
        cubit_command_or_exception("set large exodus file off")
    elif output_type.lower() == "genesis-hdf5":
        cubit_command_or_exception("set exodus netcdf4 on")
    else:
        raise RuntimeError("Unknown genesis output type '{output_type}'")


def _export_genesis(
    output_file: pathlib.Path,
    part_name: list[str],
    element_type: list[str | None],
    output_type: typing.Literal["genesis", "genesis-normal", "genesis-hdf5"] = "genesis",
) -> None:
    """Export all volumes with part name prefix to the output file.

    Always creates new blocks named after the part/volume prefix.

    :param output_file: Genesis file to write
    :param part_name: list of part/volume names to create as blocks from all volumes with a matching prefix
    :param element_type: list of element type strings
    :param output_type: String identifying genesis output type: genesis (large format), genesis-normal, genesis-hdf5
    """
    block_ids = []
    for name, element in zip(part_name, element_type, strict=True):
        block_ids.append(_create_volume_name_block(name))
        if element is not None:
            cubit_command_or_exception(f"block {block_ids[-1]} element type {element}")
    _set_genesis_output_type(output_type)
    block_string = _utilities.character_delimited_list(block_ids)
    cubit_command_or_exception(f"export mesh '{output_file}' block {block_string} overwrite")


def _export_abaqus_list(part_name: list[str], element_type: list[str | None], destination: pathlib.Path) -> None:
    """Export one Abaqus orphan mesh per part in the destination directory.

    :param part_name: list of part/volume names to create as blocks from all volumes with a matching prefix
    :param element_type: List of element type strings
    :param destination: Parent directory for orphan mesh files
    """
    for name, element in zip(part_name, element_type, strict=True):
        output_file = destination / name
        output_file = output_file.with_suffix(".inp")
        _export_abaqus(output_file, name)
        if element is not None:
            _mixed_utilities.substitute_element_type(output_file, element)


def _export_abaqus(output_file: pathlib.Path, part_name: str) -> None:
    """Create a part-named block, add all volumes/surfaces with name prefix, export an Abaqus orphan mesh file.

    :param output_file: Abaqus file to write
    :param part_name: part/volume name to create as blocks from all volumes with a matching prefix
    """
    new_block_id = _create_volume_name_block(part_name)
    cubit_command_or_exception(f"export abaqus '{output_file}' block {new_block_id} partial overwrite")


def image(
    input_file: str | pathlib.Path,
    output_file: str | pathlib.Path,
    cubit_command: str,
    x_angle: float = parsers.image_defaults["x_angle"],  # type: ignore[assignment]
    y_angle: float = parsers.image_defaults["y_angle"],  # type: ignore[assignment]
    z_angle: float = parsers.image_defaults["z_angle"],  # type: ignore[assignment]
    image_size: tuple[int, int] = parsers.image_defaults["image_size"],  # type: ignore[assignment]
) -> None:
    """Open a Cubit ``*.cub`` file and save an image.

    Uses the Cubit APREPRO `hardcopy`_ command, which accepts jpg, gif, bmp, pnm, tiff, and eps file extensions. This
    command only works in batch mode from Cubit APREPRO journal files, so an ``input_file``.jou is created for
    execution.

    :param str input_file: Cubit ``*.cub`` file to open that already contains parts/volumes to be meshed
    :param str output_file: Screenshot file to write
    :param float x_angle: Rotation about 'world' X-axis in degrees
    :param float y_angle: Rotation about 'world' Y-axis in degrees
    :param float z_angle: Rotation about 'world' Z-axis in degrees
    :param tuple image_size: Image size in pixels (width, height)
    """
    input_file = pathlib.Path(input_file).with_suffix(".cub")
    output_file = pathlib.Path(output_file)
    output_type = output_file.suffix.strip(".")

    journal_path = output_file.with_suffix(".jou")
    with journal_path.open("w") as journal_file:
        journal_file.write(f"open '{input_file}'\n")
        journal_file.write(f"graphics windowsize {image_size[0]} {image_size[1]}\n")
        journal_file.write(f"rotate {x_angle} about world x\n")
        journal_file.write(f"rotate {y_angle} about world y\n")
        journal_file.write(f"rotate {z_angle} about world z\n")
        journal_file.write(f"hardcopy '{output_file}' {output_type}\n")

    command = f"{cubit_command} -batch {journal_path}"
    _utilities.run_command(command)
