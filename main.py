import pygame as pg

pg.init()
pg.mixer.init()

WIDTH, HEIGHT = 800, 600

class Tools:
    def text_surface(text: str, size: int, color: tuple[int, int, int]) -> pg.Surface:
        font = pg.font.Font(None, size)
        return font.render(text, True, color)

    def shift_color(color: tuple[int, int, int], shift: int) -> tuple[int, int, int]:
        color = [i + shift if i + shift <= 255 else 255 for i in color]
        return color

    
class Clickable:
    def __init__(self, coordinate: tuple[int, int], size: tuple[int, int]) -> None:
        self.x, self.y = coordinate
        self.width, self.height = size
        self.hover = 0
        self.left = 0
        self.middle = 0
        self.right = 0

    def update(self, screen: pg.Surface):
        mouse_pos = pg.mouse.get_pos()
        left, middle, right = pg.mouse.get_pressed()
        if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
            self.left += left
            self.middle += middle
            self.right += right
            self.hover += 1
        else:
            self.hover = 0
        if not left: self.left = 0
        if not middle: self.middle = 0
        if not right: self.right = 0
        self.render(screen)
    
    def render(self, screen: pg.Surface):
        pass
    
    def get_hover(self) -> bool:
        return self.hover > 0

    def get_clicked(self, button: int=0) -> tuple[bool, bool, bool]:
        res = (self.left != 0, self.middle != 0, self.right != 0)
        return res[button]
    
    def get_hold(self, frame: int, button: int=0) -> tuple[bool, bool, bool]:
        res = (self.left > frame, self.middle > frame, self.right > frame)
        return res[button]
    
    def get_clicked_once(self, button: int=0) -> tuple[bool, bool, bool]:
        res = (self.left == 1, self.middle == 1, self.right == 1)
        return res[button]

        



    
class Button(Clickable):
    def __init__(self, text: str, coordinate: tuple[int, int], size: tuple[int, int], color: tuple[int, int, int]) -> None:
        super().__init__(coordinate, size)
        self.text = text
        self.x, self.y = coordinate
        self.width, self.height = size
        self.color = color
        self.text_surface = Tools.text_surface(self.text, 30, (0, 0, 0))
    
    def render(self, screen:pg.Surface):
        surface = pg.Surface((self.width, self.height))
        if self.get_hover():
            color = Tools.shift_color(self.color, 50)
        else:
            color = self.color
        surface.fill(color)
        surface.blit(self.text_surface, (self.width / 2 - self.text_surface.get_width() / 2, self.height / 2 - self.text_surface.get_height() / 2))
        screen.blit(surface, (self.x, self.y))
    

class Main:
    def __init__(self):
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.running = True
        self.scene = None
        self.change_scene(MainMenu(self))

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
    
    def change_scene(self, scene):
        self.scene = scene
            

class Scene:
    def __init__(self, main: Main):
        self.main = main
        self.event_block = True
        self.overlays = []
        self.setup()
    
    def setup(self):
        pass

    def update(self, events: list[pg.event.Event]):
        self.process()
        for overlay in self.overlays:
            overlay_surface = overlay.process()
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
        self.setup()
    
    def setup(self):
        pass
    
    def proecss(self) -> pg.Surface:
        pass

    def event(self, event_list) -> bool: # Trueで以降のイベントをブロック
        pass

    def close(self):
        self.root_scene.overlays.remove(self)


class MainMenu(Scene):
    def setup(self):
        self.buttons = {}
        self.buttons["start"] = Button("Start", (100, 200), (100, 50),(100, 100, 100))
        self.buttons["settings"] = Button("Settings", (100, 300), (100, 50),(100, 100, 100))
        self.buttons["exit"] = Button("Exit", (100, 400), (100, 50),(100, 100, 100))

    def process(self):
        screen = self.main.screen
        screen.fill((255, 255, 255))
        screen.blit(Tools.text_surface("Main Menu", 100, (0, 0, 0)), (100, 100))
        for button in self.buttons.values():
            button.update(screen)
    
    def event(self, event_list: list[pg.event.Event]):
        if self.buttons["start"].get_clicked_once():
            self.main.change_scene(CharacterSelect(self.main))
        if self.buttons["settings"].get_clicked_once():
            self.overlays.append(SettingMenu(self))
        if self.buttons["exit"].get_clicked_once():
            self.main.running = False
        for event in event_list:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.overlays.append(PauseMenu(self))
                if event.key == pg.K_a:
                    print("aaa")

class PauseMenu(Overlay):
    def process(self):
        screen = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        screen.fill((0, 0, 0, 200))

        text = Tools.text_surface("Pause Menu", 100, (255, 255, 255))
        screen.blit(text, (50, 50))
        return screen
    
    def event(self, event_list):
        for event in event_list:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.close()
                if event.key == pg.K_a:
                    print("overlay")
        return self.event_block

class SettingMenu(Overlay):
    def setup(self):
        self.buttons = {}
        self.buttons["back"] = Button("Back", (600, 500), (100, 50), (100, 100, 100))
        self.buttons["pause"] = Button("Pause", (100, 200), (100, 50), (100, 100, 100))

    def process(self):
        screen = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        screen.fill((0, 0, 0, 200))

        text = Tools.text_surface("Settings", 100, (255, 255, 255))
        screen.blit(text, (50, 50))
        for button in self.buttons.values():
            button.update(screen)
        return screen
    
    def event(self, event_list):
        if self.buttons["back"].get_clicked_once():
            self.close()
        return self.event_block

class CharacterSelect(Scene):
    def process(self):
        screen = pg.Surface((WIDTH, HEIGHT))
        screen.fill((255, 255, 255))


if __name__ == "__main__":
    main = Main()
    main.run()
    pg.quit()