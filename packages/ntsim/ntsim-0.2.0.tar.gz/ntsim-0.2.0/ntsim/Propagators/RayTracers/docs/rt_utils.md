### `flatten_bb_nodes(node)`

This function takes a tree of bounding box nodes and flattens it into two lists: one containing the bounding boxes and the other containing the relationships between them.

#### Parameters:
- `node`: The root node of the bounding box tree.

#### Returns:
- `bbs`: A list of bounding boxes.
- `relationships`: A list of relationships between the bounding boxes, where each relationship is represented as a tuple containing the index and UID of the parent node, along with a list of tuples representing the index and UID of its children.

#### Example:
```python
root = BoundingBoxNode(0, [0, 0, 0], [2, 2, 2])
child1 = BoundingBoxNode(1, [1, 1, 1], [1, 1, 1])
child2 = BoundingBoxNode(2, [-1, -1, -1], [1, 1, 1])
root.add_child(child1)
root.add_child(child2)

flattened_bbs, relations = flatten_bb_nodes(root)
```

### `check_crossing(point1, point2, bb)`

This function checks whether a line segment between two points crosses a given bounding box.

#### Parameters:
- `point1`: The first point of the line segment.
- `point2`: The second point of the line segment.
- `bb`: The bounding box to check against.

#### Returns:
- `True` if the line segment crosses the bounding box, `False` otherwise.

### `check_inside(point, bb)`

This function checks whether a given point is inside a bounding box.

#### Parameters:
- `point`: A 3D point represented as a tuple or list of (x, y, z).
- `bb`: Bounding box represented as a tuple or list of (x_min, x_max, y_min, y_max, z_min, z_max).

#### Returns:
- `True` if the point is inside the bounding box, `False` otherwise.

### Additional Resources:

- Dedicated examples can be found in the `examples/RayTracer/` directory.
- Unit tests are available in the `unittests/RayTracing/` directory.

#### Example Files:
- `unittests/RayTracing/test_check_crossing.py`
- `unittests/RayTracing/test_check_inside.py`
- `unittests/RayTracing/test_flatten_bb_nodes.py`
- `examples/RayTracer/RayTracer.py`
- `examples/RayTracer/example_flatten_bb_nodes.py`
