import json
import pygame
import cv2
import numpy as np
import os

# ------------------ Meta kezelése ------------------
_meta = {}

def metafile(path):
    global _meta
    with open(path, "r") as f:
        _meta = json.load(f)

def get_meta(key, default=None):
    return _meta.get(key, default)

def parse_pos(pos, screen_w, screen_h):
    """Pozíció feldolgozása: 'center,center' a felbontás közepét jelenti"""
    if isinstance(pos, str):
        if pos.lower() == "center,center":
            return screen_w // 2, screen_h // 2
        x, y = pos.split(",")
        return int(x), int(y)
    elif isinstance(pos, (tuple, list)) and len(pos) == 2:
        return int(pos[0]), int(pos[1])
    else:
        raise ValueError(f"Invalid pos: {pos}")

# ------------------ Element osztályok ------------------
class Element:
    def __init__(self, name, **kwargs):
        self.name = name
        self.props = kwargs
        self.animations = []

    def update_props(self, **kwargs):
        self.props.update(kwargs)

class Text(Element):
    def __init__(self, text, font="Arial", **kwargs):
        super().__init__(text, **kwargs)
        self.font = font

# ------------------ Transform osztály ------------------
class Transform:
    def __init__(self, element, from_props=None, to_props=None):
        self.element = element
        self.from_props = from_props or element.props.copy()
        self.to_props = to_props or {}

    def apply(self, t, screen_w, screen_h):
        """t: 0..1 interpoláció, frissíti az elemet"""
        for key, end_val in self.to_props.items():
            start_val = self.from_props.get(key, self.element.props.get(key))
            if key == "pos":
                x0, y0 = parse_pos(start_val, screen_w, screen_h)
                x1, y1 = parse_pos(end_val, screen_w, screen_h)
                x = int(x0 + (x1 - x0) * t)
                y = int(y0 + (y1 - y0) * t)
                self.element.props[key] = f"{x},{y}"
            elif key == "size":
                self.element.props[key] = int(start_val + (int(end_val) - int(start_val)) * t)

# ------------------ Animate osztály ------------------
class Animate:
    def __init__(self, element, animation, duration=1, transform=None):
        self.element = element
        self.animation = animation
        self.duration = duration
        self.transform = transform
        element.animations.append(self)

# ------------------ wait segéd ------------------
_wait_queue = []
def wait(duration):
    _wait_queue.append(duration)

# ------------------ Scene osztály ------------------
class Scene:
    def __init__(self, duration=5, name="scene"):
        self.duration = duration
        self.name = name
        self.elements = []
        self.frames = []
        self.screen_w = int(get_meta("res")[0])
        self.screen_h = int(get_meta("res")[1])
        self.fps = int(get_meta("fps", 60))
        self.render_path = "./render"
        os.makedirs(self.render_path, exist_ok=True)

    def add(self, element):
        self.elements.append(element)

    def _get_font(self, elem, size):
        font_name = getattr(elem, "font", "Arial")
        if font_name.lower().endswith(".ttf"):
            font_path = os.path.join("./fonts", font_name)
            if os.path.isfile(font_path):
                return pygame.font.Font(font_path, size)
            else:
                print(f"[Warning] Font file not found: {font_path}. Using default font.")
                return pygame.font.SysFont("Arial", size)
        else:
            return pygame.font.SysFont(font_name, size)

    def _render_frame(self, frame_idx, wait_remaining_frames, wait_queue):
        surface = pygame.Surface((self.screen_w, self.screen_h))
        surface.fill((0,0,0))

        # Várakozás kezelése
        if wait_remaining_frames > 0:
            wait_remaining_frames -= 1
        elif wait_queue:
            wait_duration = wait_queue.pop(0)
            wait_remaining_frames = int(wait_duration * self.fps) - 1

        for elem in self.elements:
            for anim in elem.animations:
                x, y = parse_pos(elem.props.get("pos", "0,0"), self.screen_w, self.screen_h)
                font_size = int(elem.props.get("size", 40))
                font = self._get_font(elem, font_size)
                color = pygame.Color(elem.props.get("color", "white"))

                if anim.animation == "fade-in":
                    anim_frame_count = int(anim.duration * self.fps)
                    alpha = int(255 * min(frame_idx / max(anim_frame_count,1), 1))
                    text_surface = font.render(elem.name, True, color)
                    text_surface.set_alpha(alpha)
                    rect = text_surface.get_rect(center=(x, y))
                    surface.blit(text_surface, rect)

                elif anim.animation == "fade-out":
                    anim_frame_count = int(anim.duration * self.fps)
                    alpha = int(255 * max(1 - frame_idx / max(anim_frame_count,1), 0))
                    text_surface = font.render(elem.name, True, color)
                    text_surface.set_alpha(alpha)
                    rect = text_surface.get_rect(center=(x, y))
                    surface.blit(text_surface, rect)

                elif anim.animation == "path" and anim.transform:
                    t = min(frame_idx / (anim.duration * self.fps), 1)
                    anim.transform.apply(t, self.screen_w, self.screen_h)
                    x, y = parse_pos(elem.props.get("pos", "0,0"), self.screen_w, self.screen_h)
                    font_size = int(elem.props.get("size", 40))
                    font = self._get_font(anim.element, font_size)
                    color = pygame.Color(elem.props.get("color", "white"))
                    text_surface = font.render(anim.element.name, True, color)
                    rect = text_surface.get_rect(center=(x, y))
                    surface.blit(text_surface, rect)

        frame = pygame.surfarray.array3d(surface).transpose([1,0,2])
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame, wait_remaining_frames, wait_queue

    def play(self):
        pygame.init()
        total_frames = int(self.duration * self.fps)
        frame_idx = 0
        wait_queue = _wait_queue.copy()
        wait_remaining_frames = 0
        self.frames = []

        while frame_idx < total_frames:
            frame, wait_remaining_frames, wait_queue = self._render_frame(frame_idx, wait_remaining_frames, wait_queue)
            self.frames.append(frame)
            frame_idx += 1

        out_file = os.path.join(self.render_path, f"{self.name}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(out_file, fourcc, self.fps, (self.screen_w, self.screen_h))
        for frame in self.frames:
            out.write(frame)
        out.release()
        pygame.quit()
        print(f"Video saved to {out_file}")

# ------------------ Project osztály ------------------
class Project:
    def __init__(self, name="project"):
        self.name = name
        self.scenes = []

    def add_scene(self, scene):
        self.scenes.append(scene)

    def render_all(self):
        concat_scenes = _meta.get("concat_scenes", False)
        if not self.scenes:
            print("No scenes to render.")
            return

        if concat_scenes:
            all_frames = []
            screen_w = int(get_meta("res")[0])
            screen_h = int(get_meta("res")[1])
            fps = int(get_meta("fps", 60))
            for scene in self.scenes:
                total_frames = int(scene.duration * fps)
                frame_idx = 0
                wait_queue = _wait_queue.copy()
                wait_remaining_frames = 0
                while frame_idx < total_frames:
                    frame, wait_remaining_frames, wait_queue = scene._render_frame(
                        frame_idx, wait_remaining_frames, wait_queue
                    )
                    all_frames.append(frame)
                    frame_idx += 1

            out_file = os.path.join("./render", f"{self.name}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_file, fourcc, fps, (screen_w, screen_h))
            for frame in all_frames:
                out.write(frame)
            out.release()
            print(f"All scenes rendered into {out_file}")

        else:
            for scene in self.scenes:
                scene.play()
