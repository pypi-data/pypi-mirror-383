"""Provide a public API for the internal implementation of the geometry plotting command-line interface."""

import argparse

import matplotlib.pyplot
import numpy

from turbo_turtle._abaqus_python.turbo_turtle_abaqus import _mixed_utilities, parsers, vertices

_exclude_from_namespace = set(globals().keys())


def _get_parser() -> argparse.ArgumentParser:
    """Return a partial parser for the geometry-xyplot subcommand options appended to the geometry subcommand options.

    :return: parser
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--no-markers", action="store_true", help="Exclude vertex markers and only plot lines (default: %(default)s)"
    )
    parser.add_argument(
        "--annotate",
        action="store_true",
        help="Annotate the vertex coordinates with their index from the source CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--scale",
        action="store_true",
        help="Change the plot aspect ratio to use the same scale for the X and Y axes (default: %(default)s)",
    )

    return parser


def geometry_xyplot(
    coordinates_list: list,
    unit_conversion: float = parsers.geometry_xyplot_defaults["unit_conversion"],  # type: ignore[assignment]
    euclidean_distance: float = parsers.geometry_xyplot_defaults["euclidean_distance"],  # type: ignore[assignment]
    y_offset: float = parsers.geometry_xyplot_defaults["y_offset"],  # type: ignore[assignment]
    rtol: float | None = parsers.geometry_defaults["rtol"],  # type: ignore[assignment]
    atol: float | None = parsers.geometry_defaults["atol"],  # type: ignore[assignment]
    no_markers: bool = parsers.geometry_xyplot_defaults["no_markers"],  # type: ignore[assignment]
    annotate: bool = parsers.geometry_xyplot_defaults["annotate"],  # type: ignore[assignment]
    scale: bool = parsers.geometry_xyplot_defaults["scale"],  # type: ignore[assignment]
) -> matplotlib.pyplot.Figure:
    """Return a matplotlib figure with the coordinates plotted consistently with geometry/geometry-xyplot subcommands.

    :param coordinates_list: List of 2D numpy arrays of (X, Y) coordinates
    :param unit_conversion: multiplication factor applies to all coordinates
    :param euclidean_distance: if the distance between two coordinates is greater than this, draw a straight line.
        Distance should be provided in units *after* the unit conversion
    :param y_offset: vertical offset along the global Y-axis. Offset should be provided in units *after* the unit
        conversion.
    :param rtol: relative tolerance for vertical/horizontal line checks
    :param atol: absolute tolerance for vertical/horizontal line checks

    :param no_markers: Exclude vertex markers and only plot lines.
    :param annotate: Annotate the vertex coordinates with their index from the source CSV file.
    :param scale: Change the plot aspect ratio to use the same scale for the X and Y axes.

    :returns: matplotlib figure
    """
    if no_markers:
        line_kwargs = {}
        spline_kwargs = {}
    else:
        line_kwargs = {"marker": "o"}
        spline_kwargs = {"marker": "+"}

    figure = matplotlib.pyplot.figure()
    colors: numpy.ndarray | list[str]
    if len(coordinates_list) > 1:
        colors = matplotlib.colormaps["rainbow"](numpy.linspace(0, 1, len(coordinates_list)))
    else:
        colors = ["black"]
    for coordinates, color in zip(coordinates_list, colors, strict=True):
        transformed_coordinates = vertices.scale_and_offset_coordinates(coordinates, unit_conversion, y_offset)
        lines, splines = vertices.lines_and_splines(transformed_coordinates, euclidean_distance, rtol=rtol, atol=atol)
        for line in lines:
            array = numpy.array(line)
            matplotlib.pyplot.plot(array[:, 0], array[:, 1], color=color, markerfacecolor="none", **line_kwargs)  # type: ignore[arg-type]
        for spline in splines:
            array = numpy.array(spline)
            matplotlib.pyplot.plot(array[:, 0], array[:, 1], color=color, linestyle="dashed", **spline_kwargs)  # type: ignore[arg-type]
        if annotate:
            for index, coordinate in enumerate(transformed_coordinates):
                matplotlib.pyplot.annotate(str(index), coordinate, color=color)

    if scale:
        figure.axes[0].set_aspect("equal", adjustable="box")

    return figure


def _main(
    input_file: list,
    output_file: str,
    part_name: list[str | None] = parsers.geometry_xyplot_defaults["part_name"],  # type: ignore[assignment]
    unit_conversion: float = parsers.geometry_xyplot_defaults["unit_conversion"],  # type: ignore[assignment]
    euclidean_distance: float = parsers.geometry_xyplot_defaults["euclidean_distance"],  # type: ignore[assignment]
    delimiter: str = parsers.geometry_xyplot_defaults["delimiter"],  # type: ignore[assignment]
    header_lines: int = parsers.geometry_xyplot_defaults["header_lines"],  # type: ignore[assignment]
    y_offset: float = parsers.geometry_xyplot_defaults["y_offset"],  # type: ignore[assignment]
    rtol: float | None = parsers.geometry_defaults["rtol"],  # type: ignore[assignment]
    atol: float | None = parsers.geometry_defaults["atol"],  # type: ignore[assignment]
    no_markers: bool = parsers.geometry_xyplot_defaults["no_markers"],  # type: ignore[assignment]
    annotate: bool = parsers.geometry_xyplot_defaults["annotate"],  # type: ignore[assignment]
    scale: bool = parsers.geometry_xyplot_defaults["scale"],  # type: ignore[assignment]
) -> None:
    """Plotter for :meth:`turbo_turtle._abaqus_python.turbo_turtle_abaqus.vertices.lines_and_splines` division of
    coordinates into lines and splines.

    See the :meth:`turbo_turtle._abaqus_python.turbo_turtle_abaqus.parsers.geometry_parser`,
    :meth:`turbo_turtle._abaqus_python.turbo_turtle_abaqus.geometry.main`, or
    :meth:`turbo_turtle._cubit_python.geometry` interfaces for a description of the input arguments.

    :param input_file: input text file(s) with coordinates to draw
    :param output_file: Abaqus CAE database to save the part(s)
    :param part_name: name(s) of the part(s) being created
    :param unit_conversion: multiplication factor applies to all coordinates
    :param euclidean_distance: if the distance between two coordinates is greater than this, draw a straight line.
        Distance should be provided in units *after* the unit conversion
    :param delimiter: character to use as a delimiter when reading the input file
    :param header_lines: number of lines in the header to skip when reading the input file
    :param y_offset: vertical offset along the global Y-axis. Offset should be provided in units *after* the unit
        conversion.
    :param rtol: relative tolerance for vertical/horizontal line checks
    :param atol: absolute tolerance for vertical/horizontal line checks

    :param no_markers: Exclude vertex markers and only plot lines.
    :param annotate: Annotate the vertex coordinates with their index from the source CSV file.
    :param scale: Change the plot aspect ratio to use the same scale for the X and Y axes.

    :returns: writes ``{output_file}`` matplotlib image
    """  # noqa: D205
    part_name = _mixed_utilities.validate_part_name_or_exit(input_file, part_name)
    coordinates_list = [
        _mixed_utilities.return_genfromtxt_or_exit(
            file_name, delimiter, header_lines, expected_dimensions=2, expected_columns=2
        )
        for file_name in input_file
    ]
    figure = geometry_xyplot(
        coordinates_list,
        unit_conversion=unit_conversion,
        euclidean_distance=euclidean_distance,
        y_offset=y_offset,
        rtol=rtol,
        atol=atol,
        no_markers=no_markers,
        annotate=annotate,
        scale=scale,
    )

    figure.savefig(output_file)


_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
