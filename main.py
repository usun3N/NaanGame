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
        self.click_protect = True

    def update(self, screen: pg.Surface):
        mouse_pos = pg.mouse.get_pos()
        left, middle, right = pg.mouse.get_pressed()
        
        if self.click_protect:
            if not (left or middle or right):
                self.click_protect = False
        if not self.click_protect:
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
        self.controll_manager = ControllManager()

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
    def setup(self):
        self.buttons = {}
        self.buttons["back"] = Button("Back", (600, 500), (100, 50), (100, 100, 100))
        self.buttons["start"] = Button("Start", (100, 200), (100, 50), (100, 100, 100))
    def process(self):
        screen = self.main.screen
        screen.fill((255, 255, 255))
        text = Tools.text_surface("Character Select", 100, (0, 0, 0))
        for button in self.buttons.values():
            button.update(screen)
        screen.blit(text, (50, 50))

    def event(self, event_list):
        if self.buttons["back"].get_clicked_once():
            self.main.change_scene(MainMenu(self.main))
        if self.buttons["start"].get_clicked_once():
            self.main.change_scene(Ingame(self.main))

class Ingame(Scene):
    def setup(self):
        self.player = Player()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.items = []

    def process(self):
        screen = self.main.screen
        screen.fill((255, 255, 255))
        text = Tools.text_surface(f"{self.player.stamina}", 30, (0, 0, 0))
        screen.blit(text, (50, 50))
        text = Tools.text_surface(f"{self.player.stamina_cooldown}", 30, (0, 0, 0))
        screen.blit(text, (50, 100))
        self.player.update()
        self.player.draw(screen)
    
    def event(self, event_list: list[pg.event.Event]):
        actions = self.main.controll_manager.update(event_list)
        speed = 2
        if actions["dash"] > 0 and self.player.stamina > 0:
            speed = 7
            self.player.decrease_stamina(1)
        if actions["move_left"] > 0:
            self.player.move((-speed, 0))
        if actions["move_right"] > 0:
            self.player.move((speed, 0))
        if actions["move_up"] > 0:
            self.player.move((0, -speed))
        if actions["move_down"] > 0:
            self.player.move((0, speed))
        if actions["pause"] > 0:
            self.overlays.append(PauseMenu(self))
            actions["pause"] = 0


class Player(pg.sprite.Sprite):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.hp = 100
        self.max_hp = 100
        self.stamina = 50
        self.max_stamina = 50
        self.stamina_cooldown = 0
        self.stamina_decreasing = False
        self.stamina_regen = False
        self.image = pg.image.load("discord.png")
        self.rect = self.image.get_rect()

    def decrease_stamina(self, amount: int):
        if self.stamina - amount < 0:
            self.stamina = 0
        else:
            self.stamina -= amount
        self.stamina_cooldown += 1
        self.stamina_decreasing = True
    
    def increase_stamina(self, amount: int):
        if self.stamina + amount > self.max_stamina:
            self.stamina = self.max_stamina
        else:
            self.stamina += amount

    def move(self, direction: tuple[int, int]):
        vx, vy = direction
        self.x += vx
        self.y += vy
    
    def update(self):
        if self.stamina_cooldown > 0:
            if not self.stamina_decreasing:
                self.stamina_cooldown -= 1
        else:
            self.stamina_regen = True
        if self.stamina_regen:
            self.increase_stamina(1)
        self.stamina_decreasing = False

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, (self.x, self.y))
        

        

class Enemy(pg.sprite.Sprite):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.hp = 20
    
class ControllManager:
    def __init__(self):
        self.key_map = {
            "move_left": pg.K_a,
            "move_right": pg.K_d,
            "move_up": pg.K_w,
            "move_down": pg.K_s,
            "dash": pg.K_LSHIFT,
            "pause": pg.K_p
        }
        self.key_hold = {
            "move_left": 0,
            "move_right": 0,
            "move_up": 0,
            "move_down": 0,
            "dash": 0,
            "pause": 0
        }

    def set_key(self, key, action):
        self.key_map[action] = key

    def update(self, events: list[pg.event.Event]):
        actions = []
        for event in events:
            if event.type == pg.KEYDOWN:
                for action, key in self.key_map.items():
                    if event.key == key:
                        self.key_hold[action] += 1
            if event.type == pg.KEYUP:
                for action, key in self.key_map.items():
                    if event.key == key:
                        self.key_hold[action] = 0
        return self.key_hold

                

if __name__ == "__main__":
    main = Main()
    main.run()
    pg.quit()