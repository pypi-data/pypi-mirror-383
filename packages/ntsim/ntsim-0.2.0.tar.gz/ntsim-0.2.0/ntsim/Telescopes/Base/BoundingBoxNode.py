import numpy as np
from typing import Optional


class BoundingBoxNode:
    instances = {}

    def __init__(self, uid, center, dimensions, parent=None):
        if uid in self.instances:
            raise ValueError(f"UID {uid} is already in use.")
        self.uid = uid
        self.center = np.array(center)
        self.dimensions = np.array(dimensions)
        self.bounding_box = np.concatenate([self.center - self.dimensions / 2,
                                            self.center + self.dimensions / 2])
        self.children = []
        self.instances[uid] = self
        self._parent = parent
        self._depth = -1
        self._sensitive_detectors = []
        self.check_children_within_bounds()  # Sanity check

    @property
    def parent(self) -> 'Optional[BoundingBoxNode]':
        return self._parent

    @parent.setter
    def parent(self, value: 'Optional[BoundingBoxNode]'):
        self._parent = value

    def add_child(self, child, check_bounds=False):
        if child.uid not in self.instances:
            raise ValueError(f"Child with UID {child.uid} does not exist.")
        child._parent = self
        self.children.append(child)
        if check_bounds:
            self.check_children_within_bounds()  # Sanity check after adding a child

    def check_children_within_bounds(self):
        for child in self.children:
            if not np.all(self.bounding_box[:3] <= child.bounding_box[:3]) or \
               not np.all(self.bounding_box[3:] >= child.bounding_box[3:]):
                raise ValueError(f"Child with UID {child.uid} is not contained within parent with UID {self.uid}.")
            child.check_children_within_bounds()  # Recursively check grandchildren

    def find_node(self, uid):
        if self.uid == uid:
            return self
        for child in self.children:
            found = child.find_node(uid)
            if found is not None:
                return found
        return None

    def print(self, indent=0):
        center_str = ', '.join(f'{x:.2f}' for x in self.center)
        dimensions_str = ', '.join(f'{x:.2f}' for x in self.dimensions)
        bounding_box_str = ', '.join(f'{x:.2f}' for x in self.bounding_box)
        print('  ' * indent + f'UID: {self.uid}, Center: [{center_str}], Dimensions: [{dimensions_str}], Bounding Box: [{bounding_box_str}], Depth: {self._depth}')
        for child in self.children:
            child.print(indent + 1)


    def update_dimensions(self):
        if not self.children:
            return self.dimensions

        min_coords = np.min([child.bounding_box[:3] for child in self.children], axis=0)
        max_coords = np.max([child.bounding_box[3:] for child in self.children], axis=0)

        # Update the center
        self.center = (min_coords + max_coords) / 2

        # Update the dimensions
        self.dimensions = max_coords - min_coords

        # Update the bounding box
        self.bounding_box = np.concatenate([min_coords, max_coords])
