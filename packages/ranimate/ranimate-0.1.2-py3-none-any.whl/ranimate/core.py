import json
import pygame
import cv2
import numpy as np
import os
import random
from typing import Optional, Dict, Any, List, Tuple

# ------------------ Meta kezelése ------------------
_meta: Dict[str, Any] = {}

def metafile(path: str):
    """Betölti a meta JSON fájlt (res, fps, format, concat_scenes stb.)."""
    global _meta
    with open(path, "r", encoding="utf-8") as f:
        _meta = json.load(f)

def get_meta(key: str, default=None):
    return _meta.get(key, default)

def _ensure_meta_defaults():
    """Belül használt alapértékek biztosítása."""
    if "res" not in _meta:
        _meta["res"] = [800, 600]
    if "fps" not in _meta:
        _meta["fps"] = 60
    if "format" not in _meta:
        _meta["format"] = "mp4"
    if "concat_scenes" not in _meta:
        _meta["concat_scenes"] = False
    # Normalizálás
    _meta["res"] = [int(_meta["res"][0]), int(_meta["res"][1])]
    _meta["fps"] = int(_meta["fps"])

def parse_pos(pos, screen_w: int, screen_h: int) -> Tuple[int,int]:
    """Pozíció feldolgozása: 'center,center' a felbontás közepét jelenti."""
    if isinstance(pos, str):
        s = pos.strip().lower()
        if s == "center,center" or s == "center":
            return screen_w // 2, screen_h // 2
        parts = pos.split(",")
        if len(parts) == 2:
            px = parts[0].strip()
            py = parts[1].strip()
            x = screen_w // 2 if px == "center" else int(px)
            y = screen_h // 2 if py == "center" else int(py)
            return x, y
        raise ValueError(f"Invalid pos string: {pos}")
    elif isinstance(pos, (tuple, list)) and len(pos) == 2:
        return int(pos[0]), int(pos[1])
    else:
        raise ValueError(f"Invalid pos: {pos}")

# ------------------ Element osztályok ------------------
class Element:
    def __init__(self, name: str, **kwargs):
        # name: a megjelenítendő szöveg (Text esetén)
        self.name: str = name
        # props: pos, size, color, opacity, stb.
        self.props: Dict[str, Any] = kwargs.copy()
        # animációk: Animate objektumok listája
        self.animations: List["Animate"] = []

    def update_props(self, **kwargs):
        self.props.update(kwargs)

class Text(Element):
    def __init__(self, text: str, font: str = "Arial", **kwargs):
        super().__init__(text, **kwargs)
        self.font: str = font

# ------------------ Transform osztály ------------------
class Transform:
    def __init__(self, element: Element, from_props: Optional[Dict[str,Any]] = None, to_props: Optional[Dict[str,Any]] = None):
        self.element = element
        # ha nincs megadva from_props, használjuk az elem aktuális props-ait
        self.from_props = from_props.copy() if from_props else element.props.copy()
        self.to_props = to_props.copy() if to_props else {}

    def apply(self, t: float, screen_w: int, screen_h: int):
        """Alkalmazza a lineáris interpolációt 0..1 t-vel a target elem props-aira."""
        # clamp t
        if t < 0: t = 0.0
        if t > 1: t = 1.0
        for key, end_val in self.to_props.items():
            start_val = self.from_props.get(key, self.element.props.get(key))
            if key == "pos":
                x0, y0 = parse_pos(start_val, screen_w, screen_h)
                x1, y1 = parse_pos(end_val, screen_w, screen_h)
                x = int(x0 + (x1 - x0) * t)
                y = int(y0 + (y1 - y0) * t)
                self.element.props[key] = f"{x},{y}"
            elif key == "size":
                start_num = int(start_val)
                end_num = int(end_val)
                self.element.props[key] = int(start_num + (end_num - start_num) * t)
            elif key == "opacity":
                # opacity expects 0..1
                sv = float(start_val)
                ev = float(end_val)
                self.element.props[key] = float(sv + (ev - sv) * t)
            else:
                # általános numerikus interpoláció (ha kell)
                try:
                    sv = float(start_val)
                    ev = float(end_val)
                    self.element.props[key] = sv + (ev - sv) * t
                except Exception:
                    # ha nem numerikus, írjuk felül a végét amikor t==1
                    if t >= 1.0:
                        self.element.props[key] = end_val

# ------------------ Animate osztály ------------------
class Animate:
    def __init__(self, element: Element, animation: str, duration: float = 1.0,
                 transform: Optional[Transform] = None, loop: bool = False, pingpong: bool = False):
        """
        animation: 'fade-in', 'fade-out', 'path', 'opacity', stb. (a transform és opacity kombinálható)
        duration: másodpercben
        transform: ha megadott, az apply()-ját hívjuk
        loop: ismételje (folyamatos)
        pingpong: oda-vissza
        """
        self.element = element
        self.animation = animation
        self.duration = float(duration)
        self.transform = transform
        self.loop = bool(loop)
        self.pingpong = bool(pingpong)
        # Animációkat regisztráljuk az elemen
        element.animations.append(self)

    def progress_t(self, frame_idx: int, fps: int) -> float:
        """Számolja az 0..1 t értéket az adott frameIdx-re és fps-re figyelembe véve loop/pingpong."""
        if self.duration <= 0:
            return 1.0
        raw = frame_idx / (self.duration * fps)
        if self.loop:
            # maradék része 0..1
            t = raw % 1.0
        else:
            t = min(raw, 1.0)
        if self.pingpong:
            # pingpong: 0..1..0 periodikus
            period = raw % 2.0
            if period <= 1.0:
                t = period
            else:
                t = 2.0 - period
        return max(0.0, min(1.0, t))

# ------------------ ParticleEmitter osztály ------------------
class ParticleEmitter:
    def __init__(self, pos: Tuple[int,int], color: str = "white", count: int = 50,
                 speed: float = 2.0, lifetime: float = 1.0, size: int = 3, spread: float = 1.0, loop: bool = False):
        """
        pos: kezdő pozíció (x,y)
        color: pygame színné konvertálható string
        count: egyszerre kibocsátott részecskék száma (emitkor)
        speed: sebesség skála
        lifetime: másodpercben
        size: pixel sugár
        spread: mennyire szóródnak a sebességek
        loop: ha True, minden frame emitol új részecskéket
        """
        self.pos = np.array(pos, dtype=float)
        self.color = color
        self.count = int(count)
        self.speed = float(speed)
        self.lifetime = float(lifetime)
        self.size = int(size)
        self.spread = float(spread)
        self.loop = bool(loop)
        self._particles: List[Dict[str, Any]] = []

    def emit_once(self):
        for _ in range(self.count):
            angle = random.uniform(0, 2*np.pi)
            speed = random.uniform(0.2, 1.0) * self.speed
            vx = np.cos(angle) * speed + random.uniform(-self.spread, self.spread)
            vy = np.sin(angle) * speed + random.uniform(-self.spread, self.spread)
            self._particles.append({
                "pos": np.array(self.pos, dtype=float),
                "vel": np.array([vx, vy], dtype=float),
                "age": 0.0,
                "life": self.lifetime
            })

    def emit_continuous(self):
        # folyamatos, kis adagokban
        for _ in range(max(1, int(self.count/5))):
            angle = random.uniform(-0.5, 0.5) + (-np.pi/2)  # inkább felfelé
            speed = random.uniform(0.2, 1.0) * self.speed
            vx = np.cos(angle) * speed + random.uniform(-self.spread, self.spread)
            vy = np.sin(angle) * speed + random.uniform(-self.spread, self.spread)
            self._particles.append({
                "pos": np.array(self.pos, dtype=float),
                "vel": np.array([vx, vy], dtype=float),
                "age": 0.0,
                "life": self.lifetime
            })

    def update(self, dt: float):
        alive = []
        for p in self._particles:
            p["pos"] += p["vel"] * dt
            # egyszerű gravitáció lefelé
            p["vel"][1] += 9.81 * 0.02 * dt
            p["age"] += dt
            if p["age"] < p["life"]:
                alive.append(p)
        self._particles = alive

    def render(self, surface):
        color = pygame.Color(self.color)
        for p in self._particles:
            pos_int = (int(p["pos"][0]), int(p["pos"][1]))
            pygame.draw.circle(surface, color, pos_int, self.size)

# ------------------ wait segéd ------------------
_wait_queue: List[float] = []
def wait(duration: float):
    _wait_queue.append(float(duration))

# ------------------ Scene osztály ------------------
class Scene:
    def __init__(self, duration: float = 5.0, name: str = "scene"):
        _ensure_meta_defaults()
        self.duration = float(duration)
        self.name = name
        self.elements: List[Element] = []
        self.frames: List[np.ndarray] = []
        self.screen_w = int(get_meta("res")[0])
        self.screen_h = int(get_meta("res")[1])
        self.fps = int(get_meta("fps", 60))
        self.render_path = "./render"
        os.makedirs(self.render_path, exist_ok=True)
        self.emitters: List[ParticleEmitter] = []

    def add(self, element: Element):
        self.elements.append(element)

    def add_emitter(self, emitter: ParticleEmitter):
        self.emitters.append(emitter)

    def _get_font(self, elem: Element, size: int):
        font_name = getattr(elem, "font", "Arial")
        # TTF fájl esetén ./fonts mappában keresünk
        if isinstance(font_name, str) and font_name.lower().endswith(".ttf"):
            font_path = os.path.join("./fonts", font_name)
            if os.path.isfile(font_path):
                return pygame.font.Font(font_path, size)
            else:
                # fallback
                print(f"[Warning] Font file not found: {font_path}. Using default system font.")
                return pygame.font.SysFont("Arial", size)
        else:
            return pygame.font.SysFont(font_name, size)

    def _render_frame(self, frame_idx: int, wait_remaining_frames: int, wait_queue: List[float]) -> Tuple[np.ndarray,int,List[float]]:
        """Visszaad egy BGR numpy frame-et és a frissített wait értékeket."""
        # Biztonsági inicializálás pygame/pygame.font-ra
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        surface = pygame.Surface((self.screen_w, self.screen_h), flags=0)
        surface.fill((0,0,0))

        # Várakozás kezelése
        if wait_remaining_frames > 0:
            wait_remaining_frames -= 1
        elif wait_queue:
            wait_duration = wait_queue.pop(0)
            wait_remaining_frames = int(wait_duration * self.fps) - 1

        # Particle rendszerek: emit + update + render
        dt = 1.0 / max(1, self.fps)
        for emitter in self.emitters:
            if emitter.loop:
                emitter.emit_continuous()
            else:
                # ha nincs részecske, egyszer kilövünk (vagy ha count nagy, egyszerre)
                if len(emitter._particles) == 0:
                    emitter.emit_once()
            emitter.update(dt)
            emitter.render(surface)

        # Elemenként frissítjük a props-okat az animációk alapján
        for elem in self.elements:
            # Alapértékek
            # ha nincs pos, default "0,0"
            base_pos = elem.props.get("pos", "0,0")
            base_size = int(elem.props.get("size", 40))
            base_color = elem.props.get("color", "white")
            base_opacity = float(elem.props.get("opacity", 1.0))

            # összegzők (ha több animáció van, a transformokat egymás után alkalmazzuk)
            current_opacity = base_opacity

            for anim in elem.animations:
                # t számítása a scene frame-hez képest
                t = anim.progress_t(frame_idx, self.fps)
                # ha van transform, alkalmazzuk
                if anim.transform:
                    anim.transform.apply(t, self.screen_w, self.screen_h)
                # animáció típus-specifikus hatás
                if anim.animation == "fade-in":
                    current_opacity = min(current_opacity, float(t))  # 0..1
                elif anim.animation == "fade-out":
                    current_opacity = min(current_opacity, float(1.0 - t))
                elif anim.animation == "opacity":
                    # ha a transform kezeli az opacity-t, az már beíródott elem.props['opacity']
                    current_opacity = float(elem.props.get("opacity", current_opacity))
                # egyéb anim típusok az alkalmazott transform-on keresztül működnek (pl. path)

            # végleges props a rajzoláshoz
            elem_opacity_float = max(0.0, min(1.0, float(elem.props.get("opacity", current_opacity))))
            elem_size = int(elem.props.get("size", base_size))
            elem_color = elem.props.get("color", base_color)
            x, y = parse_pos(elem.props.get("pos", base_pos), self.screen_w, self.screen_h)

            # render szöveg
            font = self._get_font(elem, elem_size)
            color = pygame.Color(elem_color)
            text_surface = font.render(elem.name, True, color)
            # beállítjuk az alfa csatornát: Pygame 1.9+ esetén set_alpha működik
            alpha_val = int(elem_opacity_float * 255)
            # Hozzunk létre egy felületet, ami RGBA és beállítjuk az alpha-t
            if text_surface.get_flags() & pygame.SRCALPHA:
                # ha már van alpha csatorna, set_alpha még működik
                text_surface.set_alpha(alpha_val)
                blit_surf = text_surface
            else:
                blit_surf = text_surface.copy()
                blit_surf.set_alpha(alpha_val)

            rect = blit_surf.get_rect(center=(x, y))
            surface.blit(blit_surf, rect)

        # Pygame surface -> numpy (RGB) -> OpenCV BGR
        arr = pygame.surfarray.array3d(surface).transpose([1,0,2])
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        return bgr, wait_remaining_frames, wait_queue

    def play(self):
        """Rendereli a scene-t külön fájlba (self.name.mp4)."""
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
        for f in self.frames:
            out.write(f)
        out.release()
        print(f"Scene rendered: {out_file}")

# ------------------ Project osztály ------------------
class Project:
    def __init__(self, name: str = "project"):
        _ensure_meta_defaults()
        self.name = name
        self.scenes: List[Scene] = []

    def add_scene(self, scene: Scene):
        self.scenes.append(scene)

    def render_all(self):
        """Rendereli a Project összes Scene-jét.
           Ha a meta 'concat_scenes' True, akkor egyetlen fájlba fűzi össze az összes frame-et.
        """
        _ensure_meta_defaults()
        concat = bool(_meta.get("concat_scenes", False))
        if not self.scenes:
            print("No scenes to render.")
            return

        pygame.init()
        if concat:
            all_frames: List[np.ndarray] = []
            screen_w = int(get_meta("res")[0])
            screen_h = int(get_meta("res")[1])
            fps = int(get_meta("fps", 60))
            for scene in self.scenes:
                total_frames = int(scene.duration * fps)
                frame_idx = 0
                wait_queue = _wait_queue.copy()
                wait_remaining_frames = 0
                while frame_idx < total_frames:
                    frame, wait_remaining_frames, wait_queue = scene._render_frame(frame_idx, wait_remaining_frames, wait_queue)
                    all_frames.append(frame)
                    frame_idx += 1

            out_file = os.path.join("./render", f"{self.name}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_file, fourcc, fps, (screen_w, screen_h))
            for f in all_frames:
                out.write(f)
            out.release()
            print(f"All scenes rendered into {out_file}")
        else:
            for scene in self.scenes:
                scene.play()
        pygame.quit()
