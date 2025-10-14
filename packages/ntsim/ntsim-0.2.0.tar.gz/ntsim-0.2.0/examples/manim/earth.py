from manimlib import *

class EarthScene(ThreeDScene):
    def construct(self):
        # Texture for the Earth
        day_texture = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Whole_world_-_land_and_oceans.jpg/1280px-Whole_world_-_land_and_oceans.jpg"

        # Create a sphere with the Earth texture
        earth = Sphere(radius=3)
        earth_surface = TexturedSurface(earth, day_texture)
        earth_surface.shift(IN)

        # Set perspective
        self.camera.frame.set_euler_angles(
            theta=-30 * DEGREES,
            phi=70 * DEGREES,
        )

        # Animate the Earth
        self.play(FadeIn(earth_surface))
        self.wait()

        # Add ambient rotation
        self.camera.frame.add_updater(lambda m, dt: m.increment_theta(-0.1 * dt))
        self.wait(0.5)
