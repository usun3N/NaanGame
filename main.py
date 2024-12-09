import pygame as pg

pg.init()
pg.mixer.init()

WIDTH, HEIGHT = 800, 600

class Tools:
    def text_surface(text: str, size: int, color: tuple[int, int, int]) -> pg.Surface:
        font = pg.font.Font(None, size)
        return font.render(text, True, color)
    

class Main:
    def __init__(self):
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.running = True
        self.scene = MainMenu(self)

    def run(self):
        while self.running:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.running = False
                    break
            self.scene.update(events)
            self.clock.tick(60)
            pg.display.flip()
            

class Scene:
    def __init__(self, main: Main):
        self.main = main
        self.event_block = True
        self.overlays = []

    def update(self, events: list[pg.event.Event]):
        self.process()
        for overlay in self.overlays:
            overlay_surface =overlay.update()
            self.main.screen.blit(overlay_surface, (0, 0))

        for overlay in reversed(self.overlays):
            event_block = overlay.event(events)
            if event_block:
                break
        else:
            self.event(events)

    def process(self):
        pass

    def event(self, event_list: list):
        pass


class Overlay:
    def __init__(self, root_scene: Scene):
        self.root_scene = root_scene
        self.event_block = True
    
    def update(self) -> pg.Surface:
        """
        オーバーレイの更新メソッド
        Returns:
            pg.Surface: オーバーレイのSurface
        """

    def event(self, event_list) -> bool: # Trueで以降のイベントをブロック
        pass

    def close(self):
        self.root_scene.overlays.remove(self)


class MainMenu(Scene):
    def process(self):
        screen = self.main.screen
        screen.fill((255, 255, 255))
        screen.blit(Tools.text_surface("Main Menu", 100, (0, 0, 0)), (100, 100))
    
    def event(self, event_list: list[pg.event.Event]):
        for event in event_list:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.overlays.append(PauseMenu(self))
                if event.key == pg.K_a:
                    print("aaa")

class PauseMenu(Overlay):
    def update(self):
        screen = pg.Surface((WIDTH, HEIGHT))
        bg = pg.Surface((WIDTH, HEIGHT))
        bg.fill((0, 0, 0))
        bg.set_alpha(128)
        screen.blit(bg, (0, 0))

        text = Tools.text_surface("Pause Menu", 100, (255, 255, 255))
        screen.blit(text, (100, 100))
        return bg
    
    def event(self, event_list):
        for event in event_list:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.close()
                if event.key == pg.K_a:
                    print("overlay")
        return self.event_block


if __name__ == "__main__":
    main = Main()
    main.run()
    pg.quit()