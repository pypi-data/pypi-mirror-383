import abc
from typing import List, Dict, Any
from argparse import Namespace
import numpy as np
from ntsim.Telescopes.Base.BoundingBoxNode import BoundingBoxNode
from ntsim.SensitiveDetectors.Base.BaseSensitiveDetector import BaseSensitiveDetector
from ntsim.Base.BaseConfig import BaseConfig

class BaseTelescope(BaseConfig):
    def __init__(self, name: str):
        self._name = name
        self._world = None
        self._sensitive_detector_blueprint = None
        self._sensitive_detectors = []
        
        self.logger.info("Initialized Telescope")

    def build(self, detector_blueprint: BaseSensitiveDetector) -> bool:
        """Build the telescope."""

        # Build the bounding boxes for the telescope
        self.add_bounding_boxes()

        # Provide the blueprint of the sensitive detector to the telescope
        self.sensitive_detector_blueprint = detector_blueprint

        # Place the sensitive detectors
        self.place_sensitive_detectors()
        # Make a single array collecting detectors from all leafs
        self.collect_all_sensitive_detectors()

    def get_effects_options(self):
        if len(self._sensitive_detectors) == 0:
            raise ValueError("_sensitive_detectors has not been initialized!")

        # Determine the  length of opts for dtype
        opts_shape = self._sensitive_detectors[0].effects_options.shape

        dtype = [('uid', 'i8'), ('opts', 'f8', opts_shape)]
        effects_options = np.zeros(len(self._sensitive_detectors), dtype=dtype)

        for i, det in enumerate(self._sensitive_detectors):
            effects_options[i] = (det.uid, det.effects_options)

        return effects_options

    @property
    def world(self):
        if self._world is None:
            raise ValueError("World has not been initialized!")
        return self._world

    @world.setter
    def world(self, value):
        self._world = value

    @property
    def sensitive_detector_blueprint(self):
        if self._sensitive_detector_blueprint is None:
            raise ValueError("Sensitive detector has not been initialized!")
        return self._sensitive_detector_blueprint

    @sensitive_detector_blueprint.setter
    def sensitive_detector_blueprint(self, detector: BaseSensitiveDetector):
        self._sensitive_detector_blueprint = detector

    @property
    def sensitive_detectors(self):
        if self._sensitive_detectors is []:
            raise ValueError("Sensitive detectors empty!")
        return self._sensitive_detectors

    @sensitive_detectors.setter
    def sensitive_detectors(self, detectors):
        self._sensitive_detectors = detectors

    @abc.abstractmethod
    def add_bounding_boxes(self) -> bool:
        """Add bounding boxes nodes."""
        pass

    @abc.abstractmethod
    def place_sensitive_detectors(self) -> bool:
        """Place sensitive detectors at centers of their bounding boxes."""
        pass

    def collect_all_sensitive_detectors(self):
        all_detectors = []

        def _traverse_and_collect(node):
            nonlocal all_detectors
            if len(node.children) == 0:  # If the node is a leaf
                if len(node._sensitive_detectors) == 0:
                    raise ValueError(f"No sensitive detectors found for leaf node with UID {node.uid}")
                all_detectors.extend(node._sensitive_detectors)
            else:
                for child in node.children:
                    _traverse_and_collect(child)

        _traverse_and_collect(self._world)
        self._sensitive_detectors = all_detectors

    def flatten_nodes(self):
        bbox_dtype = [
            ('bbs', 'f8', (6,)),
            ('parent', 'i4'),
            ('box_uid', 'i4'),
            ('depth', 'i4'),
            ('label', 'S20')
        ]
        detector_dtype = [
            ('detector_uid', 'i4'),
            ('parent_box_uid', 'i4'),
            ('depth', 'i4'),
            ('position', 'f8', (3,)),
            ('direction', 'f8', (3,)),
            ('radius', 'f8')
        ]

        bbox_array = np.empty(0, dtype=bbox_dtype)
        detector_array = np.empty(0, dtype=detector_dtype)
        def _traverse_node(node, depth, parent_uid):
            # assign depth to the curent node
            node._depth = depth
            nonlocal bbox_array, detector_array
            new_bbox_entry = np.array([(node.quantities, parent_uid, node.uid, depth, node.label)], dtype=bbox_dtype)
            bbox_array = np.concatenate([bbox_array, new_bbox_entry])
            for det in node._sensitive_detectors:
                new_detector_entry = np.array([(det.uid, node.uid, depth, det.position, det.photocathode_unit_vector, det.radius)], dtype=detector_dtype)
                detector_array = np.concatenate([detector_array, new_detector_entry])

            for child in node.children:
                _traverse_node(child, depth + 1, node.uid)

        _traverse_node(self._world, 0, -1)  # Assign world's parent_uid to -1
        return bbox_array, detector_array

    def boxes_at_depth(self, bbox_array, target_depth):
        return bbox_array[bbox_array['depth'] <= target_depth]

    def detectors_at_depth(self, bbox_array, detector_array, target_depth):
        propagated_detectors_list = []  # List to keep track of added detectors

        for det in detector_array:
            current_depth = det['depth']
            current_box_uid = det['parent_box_uid']

            while current_depth >= target_depth:
                # Break if parent_box_uid is not valid or if we reached the target depth
                if current_box_uid == -1 or current_depth == target_depth:
                    break

                # Find the parent of the current box
                parent_box_uid = bbox_array[bbox_array['box_uid'] == current_box_uid]['parent'][0]

                # Update current_box_uid and current_depth for the next iteration
                current_box_uid = parent_box_uid
                current_depth -= 1

            if current_depth == target_depth:
                propagated_detectors_list.append(
                    (det['detector_uid'], current_box_uid, current_depth, det['position'], det['direction'], det['radius'])
                )

        # Define the dtype for the np.array
        detector_dtype = [
            ('detector_uid', 'i4'),
            ('parent_box_uid', 'i4'),
            ('depth', 'i4'),
            ('position', 'f8', (3,)),
            ('direction', 'f8', (3,)),
            ('radius', 'f8')
        ]

        propagated_detectors = np.array(propagated_detectors_list, dtype=detector_dtype)
        return propagated_detectors

    def get_detectors_for_box(self, propagated_detectors, target_box_uid):
        filtered_detectors = propagated_detectors[propagated_detectors['parent_box_uid'] == target_box_uid]
        return filtered_detectors['detector_uid']

    def sensitive_detectors_info(self):
        self._sensitive_detector_blueprint.print_instance_count()
