from compas_pb import pb_dump_bts
from compas_pb import pb_load_bts


def test_serialize_frame():
    from compas.geometry import Frame

    frame = Frame([1, 2, 3], [4, 5, 6], [7, 8, 9])

    bts = pb_dump_bts(frame)
    new_frame = pb_load_bts(bts)

    assert isinstance(new_frame, Frame)
    assert new_frame.point == frame.point
    assert new_frame.xaxis == frame.xaxis
    assert new_frame.yaxis == frame.yaxis


def test_serialize_point():
    from compas.geometry import Point

    point = Point(1, 2, 3)

    bts = pb_dump_bts(point)
    new_point = pb_load_bts(bts)

    assert isinstance(new_point, Point)
    assert new_point.x == point.x
    assert new_point.y == point.y
    assert new_point.z == point.z


def test_serialize_vector():
    from compas.geometry import Vector

    vector = Vector(1, 2, 3)

    bts = pb_dump_bts(vector)
    new_vector = pb_load_bts(bts)

    assert isinstance(new_vector, Vector)
    assert new_vector.x == vector.x
    assert new_vector.y == vector.y
    assert new_vector.z == vector.z


def test_serialize_line():
    from compas.geometry import Line, Point

    line = Line(Point(1, 2, 3), Point(4, 5, 6))

    bts = pb_dump_bts(line)
    new_line = pb_load_bts(bts)

    assert isinstance(new_line, Line)
    assert new_line.start == line.start
    assert new_line.end == line.end


def test_serialize_nested_data():
    from compas.geometry import Point, Vector, Frame

    nested_data = {
        "point": Point(1.0, 2.0, 3.0),
        "line": [Point(1.0, 2.0, 3.0), Point(4.0, 5.0, 6.0)],
        "list of Object": [Point(4.0, 5.0, 6.0), [Vector(7.0, 8.0, 9.0), Point(10.0, 11.0, 12.0)]],
        "frame": Frame(Point(1.0, 2.0, 3.0), Vector(4.0, 5.0, 6.0), Vector(7.0, 8.0, 9.0)),
        "list of primitive": ["I am String", [0.0, 0.5, 1.5], True, 5, 10],
    }

    bts = pb_dump_bts(nested_data)
    new_data = pb_load_bts(bts)

    assert isinstance(new_data["point"], Point)
    assert isinstance(new_data["line"], list) and all(isinstance(pt, Point) for pt in new_data["line"])
    assert isinstance(new_data["list of Object"], list)
    assert isinstance(new_data["frame"], Frame)
    assert isinstance(new_data["list of primitive"], list)
    assert new_data["point"] == nested_data["point"]
    assert new_data["line"] == nested_data["line"]
    assert new_data["list of Object"] == nested_data["list of Object"]
    assert new_data["frame"].point == nested_data["frame"].point
    assert new_data["frame"].xaxis == nested_data["frame"].xaxis
    assert new_data["frame"].yaxis == nested_data["frame"].yaxis


def test_serialize_plane():
    from compas.geometry import Plane, Point, Vector

    plane = Plane(Point(1, 2, 3), Vector(0, 0, 1))

    bts = pb_dump_bts(plane)
    new_plane = pb_load_bts(bts)

    assert isinstance(new_plane, Plane)
    assert new_plane.point == plane.point
    assert new_plane.normal == plane.normal


def test_serialize_polygon():
    from compas.geometry import Polygon

    polygon = Polygon([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])

    bts = pb_dump_bts(polygon)
    new_polygon = pb_load_bts(bts)

    assert isinstance(new_polygon, Polygon)
    assert len(new_polygon.points) == len(polygon.points)
    for orig_pt, new_pt in zip(polygon.points, new_polygon.points):
        assert orig_pt == new_pt


def test_serialize_box():
    from compas.geometry import Box

    box = Box.from_width_height_depth(2, 3, 4)

    bts = pb_dump_bts(box)
    new_box = pb_load_bts(bts)

    assert isinstance(new_box, Box)
    assert new_box.xsize == box.xsize
    assert new_box.ysize == box.ysize
    assert new_box.zsize == box.zsize
    assert new_box.frame.point == box.frame.point


def test_serialize_arc():
    import math
    from compas.geometry import Frame, Circle, Arc
    from compas.tolerance import TOL

    frame = Frame.worldXY()
    circle = Circle(frame=frame, radius=2.0)
    arc = Arc.from_circle(circle, 0, math.pi / 2)  # quarter circle

    bts = pb_dump_bts(arc)
    new_arc = pb_load_bts(bts)

    assert isinstance(new_arc, Arc)
    assert TOL.is_close(new_arc.start_angle, arc.start_angle)
    assert TOL.is_close(new_arc.end_angle, arc.end_angle)
    assert TOL.is_close(new_arc.circle.radius, arc.circle.radius)


def test_serialize_sphere():
    from compas.geometry import Sphere, Frame
    from compas.tolerance import TOL

    sphere = Sphere(radius=2.0, frame=Frame.worldXY())

    bts = pb_dump_bts(sphere)
    new_sphere = pb_load_bts(bts)

    assert isinstance(new_sphere, Sphere)
    assert TOL.is_close(new_sphere.radius, sphere.radius)
    assert new_sphere.frame.point == sphere.frame.point


def test_serialize_cylinder():
    from compas.geometry import Cylinder, Frame
    from compas.tolerance import TOL

    cylinder = Cylinder(radius=1.5, height=3.0, frame=Frame.worldXY())

    bts = pb_dump_bts(cylinder)
    new_cylinder = pb_load_bts(bts)

    assert isinstance(new_cylinder, Cylinder)
    assert TOL.is_close(new_cylinder.radius, cylinder.radius)
    assert TOL.is_close(new_cylinder.height, cylinder.height)
    assert new_cylinder.frame.point == cylinder.frame.point


def test_serialize_cone():
    from compas.geometry import Cone, Frame
    from compas.tolerance import TOL

    cone = Cone(radius=1.0, height=2.5, frame=Frame.worldXY())

    bts = pb_dump_bts(cone)
    new_cone = pb_load_bts(bts)

    assert isinstance(new_cone, Cone)
    assert TOL.is_close(new_cone.radius, cone.radius)
    assert TOL.is_close(new_cone.height, cone.height)
    assert new_cone.frame.point == cone.frame.point


def test_serialize_torus():
    from compas.geometry import Torus, Frame
    from compas.tolerance import TOL

    torus = Torus(radius_axis=2.0, radius_pipe=0.5, frame=Frame.worldXY())

    bts = pb_dump_bts(torus)
    new_torus = pb_load_bts(bts)

    assert isinstance(new_torus, Torus)
    assert TOL.is_close(new_torus.radius_axis, torus.radius_axis)
    assert TOL.is_close(new_torus.radius_pipe, torus.radius_pipe)
    assert new_torus.frame.point == torus.frame.point


def test_serialize_ellipse():
    from compas.geometry import Ellipse, Frame
    from compas.tolerance import TOL

    ellipse = Ellipse(major=3.0, minor=1.5, frame=Frame.worldXY())

    bts = pb_dump_bts(ellipse)
    new_ellipse = pb_load_bts(bts)

    assert isinstance(new_ellipse, Ellipse)
    assert TOL.is_close(new_ellipse.major, ellipse.major)
    assert TOL.is_close(new_ellipse.minor, ellipse.minor)
    assert new_ellipse.frame.point == ellipse.frame.point


def test_serialize_polyline():
    from compas.geometry import Polyline

    points = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1]]
    polyline = Polyline(points)

    bts = pb_dump_bts(polyline)
    new_polyline = pb_load_bts(bts)

    assert isinstance(new_polyline, Polyline)
    assert len(new_polyline.points) == len(polyline.points)
    for orig_pt, new_pt in zip(polyline.points, new_polyline.points):
        assert orig_pt == new_pt


def test_serialize_pointcloud():
    from compas.geometry import Pointcloud, Point

    points = [Point(i, j, 0) for i in range(3) for j in range(3)]
    pointcloud = Pointcloud(points)

    bts = pb_dump_bts(pointcloud)
    new_pointcloud = pb_load_bts(bts)

    assert isinstance(new_pointcloud, Pointcloud)
    assert len(new_pointcloud.points) == len(pointcloud.points)
    for orig_pt, new_pt in zip(pointcloud.points, new_pointcloud.points):
        assert orig_pt == new_pt


def test_serialize_transformation():
    from compas.geometry import Transformation, Frame

    transformation = Transformation.from_frame_to_frame(Frame.worldXY(), Frame([1, 2, 3], [1, 0, 0], [0, 1, 0]))

    bts = pb_dump_bts(transformation)
    new_transformation = pb_load_bts(bts)

    assert isinstance(new_transformation, Transformation)
    # Compare matrices element by element with tolerance
    for i in range(4):
        for j in range(4):
            assert abs(new_transformation.matrix[i][j] - transformation.matrix[i][j]) < 1e-6


def test_serialize_translation():
    from compas.geometry import Translation

    translation = Translation.from_vector([1.5, 2.5, 3.5])

    bts = pb_dump_bts(translation)
    new_translation = pb_load_bts(bts)

    assert isinstance(new_translation, Translation)
    assert new_translation.translation_vector == translation.translation_vector


def test_serialize_rotation():
    from compas.geometry import Rotation
    import math

    rotation = Rotation.from_axis_and_angle([0, 0, 1], math.pi / 4)

    bts = pb_dump_bts(rotation)
    new_rotation = pb_load_bts(bts)

    assert isinstance(new_rotation, Rotation)
    # Compare axis and angle with tolerance
    orig_axis_angle = rotation.axis_and_angle
    new_axis_angle = new_rotation.axis_and_angle

    assert abs(orig_axis_angle[0].x - new_axis_angle[0].x) < 1e-6
    assert abs(orig_axis_angle[0].y - new_axis_angle[0].y) < 1e-6
    assert abs(orig_axis_angle[0].z - new_axis_angle[0].z) < 1e-6
    assert abs(orig_axis_angle[1] - new_axis_angle[1]) < 1e-6
