from manimlib import *
from manimlib.mobject.types.image_mobject import ImageMobject

import numpy as np
from scipy.spatial.transform import Rotation as R
import numpy as np

def uniform_random_vector_in_cone(axis, angle, size=1):
    # Generate random angles within the cone
    z = np.random.uniform(np.cos(angle), 1, size)
    phi = 2 * np.pi * np.random.uniform(0, 1, size)
    v1 = np.array([np.sqrt(1 - z**2) * np.cos(phi), np.sqrt(1 - z**2) * np.sin(phi), z]).T

    # Normalize the axis
    axis = axis / np.linalg.norm(axis)

    # Compute the rotation needed to align the z-axis with the given axis
    rot_axis = np.cross([0, 0, 1], axis)
    rot_angle = np.arccos(np.dot([0, 0, 1], axis))
    rot = R.from_rotvec(rot_angle * rot_axis)

    # Apply the rotation to the random vectors
    new_v = rot.apply(v1)

    return new_v


class ParticleShower(ThreeDScene):
    def construct(self):
#        axes = ThreeDAxes()  # Create 3D axes
#        self.add(axes)  # Add them to the scene
        # add night sky background
        background = ImageMobject("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/GOODS_South_field.jpg/2560px-GOODS_South_field.jpg")
#        attributes_and_methods = dir(background)

#        for item in attributes_and_methods:
#            print(item)
        background.set_height(FRAME_HEIGHT)
        background.set_width(FRAME_WIDTH)
        self.add(background)

        # Earth
        sphere = Sphere(radius=3)
        day_texture = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Whole_world_-_land_and_oceans.jpg/1280px-Whole_world_-_land_and_oceans.jpg"
        night_texture = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/The_earth_at_night.jpg/1280px-The_earth_at_night.jpg"
        earth = TexturedSurface(sphere, day_texture, night_texture)
        earth.shift([0,-2,0])
        # Rotating the Earth so that the North Pole faces upwards
        earth.rotate(PI/2, axis=RIGHT)
        earth.mesh = SurfaceMesh(earth)
        earth.mesh.set_stroke(BLUE, 1, opacity=0.5)

        def pseudo_interaction(start, direction, nparticles=5, cone_angle=np.deg2rad(20), max_track_length=1, generations=3):
            if generations == 0:
                return []

            generation_lines = VGroup()  # Group to hold the lines for this generation
            # List to hold all child lines from all iterations
            all_child_lines_list = []

            # Generate random vectors within the cone centered around the given direction
            directions = uniform_random_vector_in_cone(direction, cone_angle, nparticles)
            color = random_color()
            for new_direction in directions:
                track_length = np.random.uniform(0, max_track_length)
                end_point = start - track_length * new_direction
                line = Line(start, end_point)
                line.set_stroke(color=color, width=3)  # Set random color
                generation_lines.add(line)
                # Recursively call the function with the new end point and direction
                child_lines_list = pseudo_interaction(end_point, new_direction, nparticles, cone_angle, max_track_length, generations - 1)
                # Collect all child lines
                all_child_lines_list.extend(child_lines_list)

            # Add the child lines to the current generation's lines
            for child_lines in all_child_lines_list:
                generation_lines.add(child_lines)

            return [generation_lines]


        # Setting the shower starting point above a specific location
        shower_start = earth.get_top() + [0,1,0]  # Adjust as needed
        initial_direction = np.array([0, 1, 0])  # Direction pointing downward
        # Generate the shower lines
        shower_lines_list = pseudo_interaction(shower_start, initial_direction, generations=3)
        # Reverse the order of the generations
        shower_lines_list.reverse()

        # Adding Earth and shower to the scene
        self.add(earth, earth.mesh)

        self.play(FadeIn(earth), ShowCreation(earth.mesh, lag_ratio=0.01, run_time=3))

        # Play the animations in the correct order
        for shower_lines in shower_lines_list:
            self.play(ShowCreation(shower_lines), run_time=3)


        # Rotating to get a better view
#        self.move_camera(phi=30 * DEGREES, theta=70 * DEGREES)
#        self.begin_ambient_camera_rotation(rate=0.1)

#        self.wait(5)
