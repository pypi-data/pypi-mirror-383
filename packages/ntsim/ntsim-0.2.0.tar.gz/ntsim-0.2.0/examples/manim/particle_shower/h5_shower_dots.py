from turtle import pos
from manimlib import *
from manimlib.mobject.types.image_mobject import ImageMobject

import numpy as np
from scipy.spatial.transform import Rotation as R

import h5py
import pandas as pd
import argparse

class Particle(Line):
    def __init__(self, start_point, end_point, color, **kwargs):
        super().__init__(start=start_point, end=end_point, color=color, **kwargs)

class ParticleShower(ThreeDScene):
    def construct(self):
        self.setup_background()
        self.setup_earth()
        self.setup_particle()

    def setup_background(self):
        self.background = ImageMobject("South_field.jpg")
        self.background.set_height(FRAME_HEIGHT*1.8)
        self.background.set_width(FRAME_WIDTH*1.8)
        self.add(self.background)

    def setup_earth(self):
        real_earth_radius_km = 6371
        desired_radius_km = 3
        sphere = Sphere(radius=desired_radius_km).rotate(350 * DEGREES)
        self.scale_factor = desired_radius_km / real_earth_radius_km
        self.scale_factor = round(self.scale_factor, 5)
        
        day_texture = "Whole_world1.jpeg"
        night_texture = "Whole_world2.jpeg"
        self.earth = TexturedSurface(sphere, day_texture, night_texture)
        self.earth.shift([0,-2,0])
        self.earth.rotate(angle=np.pi*1.62, axis=RIGHT)
        self.earth.mesh = SurfaceMesh(self.earth)
        self.earth.mesh.set_stroke(BLUE, 1, opacity=0.5)

        self.play(
            Rotate(self.earth, axis=UP, angle=2 * np.pi, run_time=11),
            self.camera.frame.animate.move_to([0, 1, 0]), run_time=8
        )
        self.play(
            ShowCreation(self.earth.mesh, lag_ratio=0.01, run_time=2),
            self.camera.frame.animate.scale(0.8).move_to([0, 2.1, 0]), run_time=2
        )
        self.add(self.earth, self.earth.mesh)

    def setup_particle(self):
        self.shower_start = [0, self.scale_factor * 5, 0]
        self.start_point = [0, 0, 0]
        self.height_ground = 2.5

        particle = Line([4, 30, 4], self.shower_start, color=WHITE, stroke_width=0.2)
        particle_ground = Line([4, 20, 4], self.start_point, color=WHITE, stroke_width=1)
        self.add(particle)
        self.play(ShowCreation(particle), run_time=1)
        self.play(self.camera.frame.animate.move_to([0, -0.7, 0]), run_time=2)
        self.play(
            FadeOut(self.earth), FadeOut(self.earth.mesh), FadeOut(particle), FadeOut(self.background),self.camera.frame.animate.scale(0.4).move_to(self.shower_start),
            run_time=2
        )
        self.play(self.camera.frame.animate.to_default_state())

        self.camera.frame.shift([0, -self.height_ground, 0])
        background = ImageMobject("tunka.jpeg")
        background.set_height(FRAME_HEIGHT)
        background.set_width(FRAME_WIDTH)
        background.shift([0, -self.height_ground, 0])
        self.add(background, particle_ground)
        self.play(ShowCreation(particle_ground), run_time=4)

        with open("conf.txt", "r") as f:
            for line in f:
                line = line.strip()
                parts = line.split(',')

        hdf5_path = parts[0]
        event_names = parts[1:]
        self.visualize_event(hdf5_path, event_names)

    def visualize_event(self, hdf5_path, event_names):
        with h5py.File(hdf5_path, 'r') as f:
            for event_name in event_names:
                count = 0
                data = f.get(f'{event_name}/tracks/g4_tracks')
                result = data[()]
                df = pd.DataFrame(result)
                df.sort_values('t_ns', inplace=True)

                max_particles = 10000  # Set your maximum number of particles here
                num_intervals = 50
                height_ground = 2.5
                max_ns = df['t_ns'].max()
                inter_size = max_ns // num_intervals
                inter = [(i * inter_size, (i + 1) * inter_size) for i in range(num_intervals)]
                print(inter)

                scale_ground = height_ground / 5000
                uid_start_points = {}

                for start_time, end_time in inter:
                    interval_particles = VGroup()
                    print(start_time, ' ', end_time)
                    interval_data = df.loc[start_time:end_time]
                    print(interval_data)
                    uids = interval_data['uid'].values
                    pdgids = interval_data['pdgid'].values
                    x_m = interval_data['x_m'].values
                    y_m = interval_data['y_m'].values
                    z_m = interval_data['z_m'].values
                    t_ns = interval_data['t_ns'].values

                    end_points = np.array([x_m * -scale_ground * 3.5, y_m * scale_ground * 3.5, ((z_m * scale_ground) - self.height_ground)*0.8]).T

                    for i in range(len(uids)):

                        #if i % 4 == 0:
                        #    continue

                        uid = uids[i]
                        pdgid = pdgids[i]
                        uid_start_points[uid] = end_points[i]

                        if ((pdgid == 2212) or (pdgid == 11)):
                            color = Color(BLUE)
                        elif pdgid == -11:
                            color = Color(RED)
                        else:
                            color = Color(YELLOW)
                        
                        dot = Dot(end_points[i], color=color, radius=0.005)
                        count += 1
                        interval_particles.add(dot)

                    self.play(ShowCreation(interval_particles))
                    print(count)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manim Particle Shower Animation')
    parser.add_argument('--max_particles', type=int, default=10000, help='Maximum number of particles')
    parser.add_argument('--ns_in_intervals', type=int, default=20000, help='Number of nanoseconds in each interval')
    parser.add_argument('--num_intervals', type=int, default=100, help='Number of intervals')
    args = parser.parse_args()

    use_opengl_renderer = False
    disable_caching = False

    if use_opengl_renderer:
        from manim.opengl import OpenGLRenderer
        config.renderer = OpenGLRenderer()

    if disable_caching:
        config.cache_animation_data = False