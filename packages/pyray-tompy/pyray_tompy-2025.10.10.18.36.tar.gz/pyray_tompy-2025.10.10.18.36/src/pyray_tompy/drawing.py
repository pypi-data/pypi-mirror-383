import pyray as pr

from iterable_tompy.exceptions import EmptyIterableError
from iterable_tompy.head import head
from vector_tompy.line2 import Line2
from vector_tompy.vector2 import Vector2


def vector2_to_vector3(point: Vector2, y: float = 0.0) -> pr.Vector3:
    vector3: pr.Vector3 = pr.Vector3(float(point.x), y, float(point.y))
    return vector3


def pr_draw_concave_polygon(points: list[pr.Vector3], color: pr.Color, is_ordered: bool = True) -> None:
    if not is_ordered:
        # TODO: Order points anti-clockwise based on centroid point
        #       derive centroid from points list
        #       find normal vector or up vector from centroid point
        #       imagine sweeping cylinder around normal vector at centroid
        #       sort points list based on rotation angle in cylinder
        pass

    try:
        start = head(points)
        for point0, point1 in zip(points[1:-1], points[2:]):
            pr.draw_triangle_3d(start, point0, point1, color)
    except EmptyIterableError:
        pass


def draw_segment_with_ends(segment: Line2,
                           segment_color: pr.Color,
                           cube_size: tuple[float, float, float],
                           point_color: pr.Color
                           ) -> None:

    pr.draw_cube((segment.point0.x, 0.001, segment.point0.y),
                 cube_size[0], cube_size[1], cube_size[2],
                 point_color)
    pr.draw_cube((segment.point1.x, 0.001, segment.point1.y),
                 cube_size[0], cube_size[1], cube_size[2],
                 point_color)
    pr.draw_line_3d((segment.point0.x, 0.001, segment.point0.y),
                    (segment.point1.x, 0.001, segment.point1.y),
                    segment_color)
