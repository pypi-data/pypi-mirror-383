import sys
import runpy
import pygame
import ranimate as ra

def preview(script_path):
    """Futtatja a scriptet preview módban."""
    # Betöltjük a scriptet
    runpy.run_path(script_path, run_name="__main__")

    # Feltételezzük, hogy a script létrehoz egy Scene vagy Project objektumot 'scene' vagy 'project' néven
    try:
        from __main__ import scene
        s = scene
        print(f"[Preview] Running scene '{s.name}' in preview mode")
        _preview_scene(s)
    except ImportError:
        try:
            from __main__ import project
            p = project
            print(f"[Preview] Running project '{p.name}' in preview mode")
            for s in p.scenes:
                _preview_scene(s)
        except ImportError:
            print("No scene or project found in script for preview.")
            return

def _preview_scene(scene):
    """Megjelenít egy Scene-t Pygame ablakban valós időben."""
    pygame.init()
    screen = pygame.display.set_mode((scene.screen_w, scene.screen_h))
    pygame.display.set_caption(f"Preview: {scene.name}")
    clock = pygame.time.Clock()
    running = True
    frame_idx = 0
    total_frames = int(scene.duration * scene.fps)

    while running and frame_idx < total_frames:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        surface = pygame.Surface((scene.screen_w, scene.screen_h))
        surface.fill((0,0,0))
        # Rendereljük a frame-et _render_frame segítségével
        frame, _, _ = scene._render_frame(frame_idx, 0, [])
        # Átalakítás Pygame Surface-re
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pygame.surfarray.blit_array(surface, frame_rgb.transpose(1,0,2))
        screen.blit(surface, (0,0))
        pygame.display.flip()
        clock.tick(scene.fps)
        frame_idx += 1

    pygame.quit()

def render(script_path):
    """Futtatja a scriptet és rendereli a videót."""
    runpy.run_path(script_path, run_name="__main__")
    try:
        from __main__ import project
        project.render_all()
    except ImportError:
        try:
            from __main__ import scene
            scene.play()
        except ImportError:
            print("No scene or project found to render.")

def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: ranimate <preview|render> <script.py>")
        sys.exit(1)
    command = sys.argv[1]
    script = sys.argv[2]
    if command == "preview":
        preview(script)
    elif command == "render":
        render(script)
    else:
        print("Unknown command. Use 'preview' or 'render'.")
