import pygame as pg
import json

pg.init()
pg.mixer.init()

WIDTH, HEIGHT = 800, 600

class Tools:
    def text_surface(text: str, size: int, color: tuple[int, int, int]) -> pg.Surface:
        font = pg.font.Font(None, size)
        return font.render(text, True, color)

    def shift_color(color: tuple[int, int, int], shift: int) -> tuple[int, int, int]:
        color = [i + shift if i + shift <= 255 else 255 for i in color]
        color = [i + shift if i + shift >= 0 else 0 for i in color]
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

    def run(self):
        while self.running:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.running = False
                    break
            cm.update(events)
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
    
    def process(self) -> pg.Surface:
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
    def setup(self):
        self.buttons = {}
        self.buttons["back"] = Button("Back", (600, 500), (100, 50), (100, 100, 100))

    def process(self):
        screen = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        screen.fill((0, 0, 0, 200))

        text = Tools.text_surface("Pause Menu", 100, (255, 255, 255))
        screen.blit(text, (50, 50))
        for button in self.buttons.values():
            button.update(screen)
        return screen
    
    def event(self, event_list):
        if cm.get_key_pressing_once("pause"):
            self.close()
        if self.buttons["back"].get_clicked_once():
            self.close()
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
        self.buttons["control"] = Button("Control", (100, 200), (100, 50), (100, 100, 100))

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
        if self.buttons["control"].get_clicked_once():
            self.root_scene.overlays.append(ControlMenu(self.root_scene))
        return self.event_block
class ControlMenu(Overlay):
    def setup(self):
        self.buttons = {}
        self.buttons["back"] = Button("Back", (600, 500), (100, 50), (100, 100, 100))

    def process(self):
        screen = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        screen.fill((0, 0, 0, 200))

        text = Tools.text_surface("Control", 100, (255, 255, 255))
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
        self.buttons["start"] = Button("Start", (100, 500), (100, 50), (100, 100, 100))
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
        self.player = UPlayer()
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.images = {}
        self.items = []
        self.overlays.append(IngameOverlay(self))

    def process(self):
        screen = self.main.screen
        screen.fill((255, 255, 255))
        self.player.update()
        self.player.draw(screen)
    
    def event(self, event_list: list[pg.event.Event]):
        speed = 2
        if cm.get_key_pressing("dash") and self.player.can_dash:
            speed = 7
            self.player.decrease_stamina(1)
        if cm.get_key_pressing("move_left"):
            self.player.move((-speed, 0))
        if cm.get_key_pressing("move_right"):
            self.player.move((speed, 0))
        if cm.get_key_pressing("move_up"):
            self.player.move((0, -speed))
        if cm.get_key_pressing("move_down"):
            self.player.move((0, speed))
        if cm.get_key_pressing_once("pause"):
            self.overlays.append(PauseMenu(self))

class IngameOverlay(Overlay):
    def setup(self):
        self.event_block = False
        self.ui = {}
        self.ui["hp_bar"] = Bar((0, 0), (400, 30), self.root_scene.player.max_hp, self.root_scene.player.hp, (255, 0, 0), True)
        self.ui["stamina_bar"] = Bar((0, 30), (400, 30), self.root_scene.player.max_stamina, self.root_scene.player.stamina, (0, 0, 255), True)
        
    def process(self) -> pg.Surface:
        surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        self.ui["hp_bar"].value = self.root_scene.player.hp
        self.ui["stamina_bar"].value = self.root_scene.player.stamina
        for ui in self.ui.values():
            ui.update(surface)
        return surface

class Bar:
    def __init__(self, coordinate: tuple[int, int], size: tuple[int, int], max_value, value, color, show_value=True):
        self.x, self.y = coordinate
        self.width, self.height = size
        self.color = color
        self.max_value = max_value
        self.value = value
        self.show_value = show_value
        self.ghost = self.value
        self.ghost_max_countdown = 60
        self.ghost_countdown = self.ghost_max_countdown
        self.decrease_rate = 0.5

    def update(self, screen: pg.Surface):
        if self.value > self.max_value:
            self.value = self.max_value
        if self.value < 0:
            self.value = 0
        if self.value < self.ghost:
            self.ghost_countdown -= 1
            if self.ghost_countdown <= 0:
                self.ghost -= self.decrease_rate
        else:
            self.ghost_countdown = self.ghost_max_countdown
            self.ghost = self.value
        self.render(screen)

    def render(self, screen: pg.Surface):
        bar_surface = pg.Surface((self.width, self.height))
        bar_surface.fill(Tools.shift_color(self.color, -100))
        per = self.value / self.max_value
        per_ghost = self.ghost / self.max_value
        pg.draw.rect(bar_surface, Tools.shift_color(self.color, -50), (0, 0, self.width * per_ghost, self.height))
        pg.draw.rect(bar_surface, self.color, (0, 0, self.width * per, self.height))
        if self.show_value:
            text = Tools.text_surface(f"{self.value}/{self.max_value}", 30, (255, 255, 255))
            bar_surface.blit(text, (self.width / 2 - text.get_width() / 2, self.height / 2 - text.get_height() / 2))
        screen.blit(bar_surface, (self.x, self.y))


class Player(pg.sprite.Sprite):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.max_hp = 100
        self.hp = self.max_hp
        self.max_stamina = 150
        self.stamina = self.max_stamina
        self.stamina_cooldown = 0
        self.can_dash = True
        self.animations = {}
        self.surface = pg.Surface((32, 32))
        self.rect = self.surface.get_rect()
        self.status = "idle"
        self.direction = "right" #right or left
        self.tick = 0

    def decrease_stamina(self, amount: int):
        if self.stamina - amount < 0:
            self.stamina = 0
        else:
            self.stamina -= amount
        self.stamina_cooldown = 60
    
    def increase_stamina(self, amount: int):
        if self.stamina + amount > self.max_stamina:
            self.stamina = self.max_stamina
        else:
            self.stamina += amount
    
    def decrease_hp(self, amount: int):
        if self.hp - amount < 0:
            self.hp = 0
        else:
            self.hp -= amount
    
    def increase_hp(self, amount: int):
        if self.hp + amount > self.max_hp:
            self.hp = self.max_hp
        else:
            self.hp += amount
    
    def move(self, direction: tuple[int, int]):
        vx, vy = direction
        if vx > 0:
            self.direction = "right"
        elif vx < 0:
            self.direction = "left"
        self.x += vx
        self.y += vy
    
    def update(self):
        if self.stamina == self.max_stamina:
            self.can_dash = True
        elif self.stamina == 0:
            self.can_dash = False

        if self.stamina_cooldown > 0:
            self.stamina_cooldown -= 1
        else:
            self.increase_stamina(1)
        self.tick += 1

    def draw(self, screen: pg.Surface):
        surface = self.animations[self.status].get_surface()
        if self.direction == "left":
            surface = pg.transform.flip(surface, True, False)
        screen.blit(surface, (self.x, self.y))
            
            

class UPlayer(Player):
    def __init__(self):
        super().__init__()
        self.animations = {
            "idle" : am.get_animation("U_idle_animation"),
            "walk" : am.get_animation("U_idle_animation")
        }



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
            "pause": pg.K_p,
            "skill1": pg.K_q,
            "skill2": pg.K_e,
            "skill3": pg.K_SPACE
        }
        self.key_pressing = {}
        for action in self.key_map.keys():
            self.key_pressing[action] = False

        self.key_hold_tick = {}
        for action in self.key_map.keys():
            self.key_hold_tick[action] = 0


    def set_key(self, key, action):
        self.key_map[action] = key

    def update(self, events: list[pg.event.Event]):
        for event in events:
            if event.type == pg.KEYDOWN:
                for action, key in self.key_map.items():
                    if event.key == key:
                        self.key_pressing[action] = True
            if event.type == pg.KEYUP:
                for action, key in self.key_map.items():
                    if event.key == key:
                        self.key_pressing[action] = False
        for action in self.key_map.keys():
            if self.key_pressing[action]:
                self.key_hold_tick[action] += 1
            else:
                self.key_hold_tick[action] = 0
    
    def get_key_pressing(self, action):
        if action in self.key_pressing.keys():
            return self.key_pressing[action]
        
    def get_key_pressing_once(self, action):
        if action in self.key_hold_tick.keys():
            if self.key_pressing[action] and self.key_hold_tick[action] == 1:
                self.key_hold_tick[action] += 1
                return True

    
    def get_key_hold_tick(self, action):
        if action in self.key_hold_tick.keys():
            return self.key_hold_tick[action]

class Image_:
    def __init__(self, name: str, path: str) -> None:
        self.image = None
        self.path = "./assets/" + path
        self.name = name

    def load(self):
        self.image = pg.image.load(self.path).convert_alpha()
    
    def unload(self):
        self.image = None

    def get_surface(self) -> pg.Surface:
        if self.image is None:
            self.load()
        return self.image
        

class Animation:
    def __init__(self, name:str, frames:list[Image_], interval:int) -> None:
        self.name = name
        self.frames = frames
        self.length = len(frames)
        self.interval = interval
        self.now_frame = 0
        self.tick = 0
    
    def reset(self):
        self.now_frame = 0
        self.tick = 0

    def get_surface(self) -> pg.Surface:
        if self.tick % self.interval == 0:
            self.now_frame += 1
            if self.now_frame >= self.length:
                self.now_frame = 0
            self.tick = 0
        return self.frames[self.now_frame].get_surface()

class ImageManager:
    def __init__(self) -> None:
        self.images = {}
        self.load("./images.json")
    def load(self, file_path):
        with open(file_path) as f:
            data_list = json.load(f)
            for data in data_list:
                name, path = data["name"], data["path"]
                self.images[name] = Image_(name, path)

    def get_image(self, name:str):
        return self.images[name]

class AnimationManager:
    def __init__(self, image_manager: ImageManager) -> None:
        self.animations = {}
        self.image_manager = image_manager
        self.load("./animations.json")

    def load(self, file_path):
        with open(file_path) as f:
            data_list = json.load(f)
            for data in data_list:
                name, frames, interval = data["name"], data["frames"], data["interval"]
                self.animations[name] = Animation(name, [self.image_manager.get_image(i) for i in frames], interval)
    
    def get_animation(self, name:str):
        return self.animations[name]

cm = ControllManager()
im = ImageManager()
am = AnimationManager(im)

if __name__ == "__main__":
    main = Main()
    main.run()
    pg.quit()