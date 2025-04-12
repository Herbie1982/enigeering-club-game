import os
import random
import math
import time
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("assets/Sounds/Background.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Loops forever

pygame.display.set_caption("Fire Legends")

START_VEL = 7.5
FONT = pygame.font.SysFont("Arial", 18, bold=True)
WIDTH, HEIGHT = 1200, 700
FPS = 60
PLAYER_VEL = START_VEL
PLAYER_VEL_1 = START_VEL
PLAYER_VEL_2 = START_VEL
WHITE = (255, 255, 255)
TIME_UNFORMATTED = int(input("How long do you want the game to last (in seconds)? (INPUT NOTE: Input just the number, i.e '60'.) "))
TIME = TIME_UNFORMATTED * 1000  # Convert to milliseconds
TAG_COUNT = 0
TAG = input("Who starts as Tag? ")
while TAG != "p" and TAG != "p1" and TAG != "p2":
    TAG = input("Invalid. Please state 'p', 'p1', or 'p2'. Who starts as Tag? ")
last_switch_time = 0
start_time = 0
FIRE_COUNT = 0
NO_OF_PLAYERS = int(input("How many players? "))
while NO_OF_PLAYERS != 2 and NO_OF_PLAYERS != 3:
    NO_OF_PLAYERS = int(input("Invalid. Please state either 2 or 3. How may players? "))


window = pygame.display.set_mode((WIDTH, HEIGHT))
world_surface = pygame.Surface((WIDTH, HEIGHT))


def flip(sprites):
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

def lerp(a, b, t):
    return a + (b - a) * t

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def load_sprite_sheets_boss(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            # Double the width and height
            surface = pygame.Surface((width * 2, height * 2), pygame.SRCALPHA)
            rect = pygame.Rect(i * width, 0, width * 2, height * 2)  # Keep original rect
            
            # Blit and scale up manually instead of using scale2x
            temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            temp_surface.blit(sprite_sheet, (0, 0), rect)
            enlarged_surface = pygame.transform.scale(temp_surface, (width * 2, height * 2))
            
            sprites.append(enlarged_surface)

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = [pygame.transform.flip(s, True, False) for s in sprites]
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

import pygame
from os.path import join

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class HomingFireball(pygame.sprite.Sprite):
    """A fireball that homes in on the nearest player."""
    
    def __init__(self, x, y, target):
        super().__init__()
        self.image = pygame.image.load("assets/fireball.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect(center=(x, y))
        self.target = target  # The player it's chasing
        self.speed = 3
        self.lifetime = 180  # Fireball lasts 3 seconds

    def update(self):
        """Move toward the target player."""
        if self.target:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2) + 0.01

            self.rect.x += (dx / distance) * self.speed
            self.rect.y += (dy / distance) * self.speed

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class BasePlayer(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3
   
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0 
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.boss_distance = 0
        self.boss_height = 0
        self.life_count = 3
        self.fire_count = 0
        self.pushback = False

    def jump(self):
        self.y_vel = -self.GRAVITY * 7.7
        self.animation_count = 0
        self.jump_count +=1
        if self.jump_count == 1:
            self.fall_count = 0
        

    def move (self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
    
    def KO(self):
        self.rect.x = 1000
        self.rect.y = 1000
        self.x_vel = 0
        self.y_vel = 0
    
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
           self.direction = "left"
           self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
           self.direction = "right"
           self.animation_count = 0

    def loop(self, fps):

        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        
        self.update_sprite()

       
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
               sprite_sheet = "double_jump"
            elif self.y_vel > self.GRAVITY * 2:
                sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY // 2) % len(sprites)
        self.sprite = sprites[sprite_index]
        
        self.animation_count += 1  

        self.update()
    
    def update_fireball(self):
        sprite_sheet = "fireball"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY // 2) % len(sprites)
        self.sprite = sprites[sprite_index]
        
        self.animation_count += 1  

        self.update()

    def tag_check(self, tag_count, width, height):
        triangle_points = [(self.rect.x - 128,  - width/2), (self.rect.x - height - 64, self.rect.y + width/2), (self.rect.x - height - 10, self.rect.y - width/2)]
        if TAG_COUNT == 0:
            tag_rect =  pygame.draw.polygon(window, WHITE, triangle_points, 0)
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
    
    def find_boss(self, boss):
        self.boss_distance = self.rect.x - boss.rect.x
        self.boss_height = self.rect.y - boss.rect.y

    def switch_tag(self, tag):
        if tag == "p1":
            tag = "p"

class Player(BasePlayer):
    
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3
   
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0 
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        
        self.fire_count = 0

class Fireball(BasePlayer):
    
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    ANIMATION_DELAY = 3
   
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0 
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        triangle_points = [(x - height - 64, y - width/2), (x - height - 64, y + width/2), (x - height - 10, y - width/2)]
        self.fire_count = 0

class Player_1(BasePlayer):
    
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 3
   
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.tag_count = 0

class Player_2(BasePlayer):
    
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3
   
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0 
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        triangle_points = [(x - height - 64, y - width/2), (x - height - 64, y + width/2), (x - height - 10, y - width/2)]

    

class BOSS(pygame.sprite.Sprite):
    
    GRAVITY = 1
    SPRITES = load_sprite_sheets_boss("MainCharacters", "PinkMan", 48, 48, True)
    ANIMATION_DELAY = 3
    KICK = pygame.mixer.Sound("assets/Sounds/Kick_1.wav")
    HIT = pygame.mixer.Sound("assets/Sounds/Hit_1.wav")
    PUNCH = pygame.mixer.Sound("assets/Sounds/Punch_1.wav")
    HIT.set_volume(1)  # Optional volume control
    PUNCH.set_volume(1)  # Optional volume control
    KICK.set_volume(1)  # Optional volume control
    
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.target_player = None
        self.fireballs = pygame.sprite.Group()
        self.SPRITES["Fireball"] = load_sprite_sheets_boss("MainCharacters", "PinkMan", 32, 32, True)
        self.sound_hit = 0



        # Fireball cooldowns
        self.normal_fireball_cooldown = 120  # 2 seconds
        self.homing_fireball_cooldown = 3600  # 60 seconds
        self.last_homing_fireball_time = time.time()

    def find_nearest_player(self, players):
        #Find the closest player every 2.5 seconds.
        nearest_player = None
        min_distance = float("inf")

        for player in players:
            distance_x = abs(self.rect.x - player.rect.x)
            distance_y = abs(self.rect.y - player.rect.y)
            distance = (distance_x**2 + distance_y**2)**(1/2)
            if distance < min_distance:
                min_distance = distance
                nearest_player = player

        self.target_player = nearest_player

    def move_toward_player(self):
        #Move towards the nearest player.
        if self.target_player:
            if self.rect.x < self.target_player.rect.x:
                self.x_vel = 1
                self.direction = "right"
                for i in range(-5, 5):
                    if self.rect.x + i == self.target_player.rect.x:
                        if self.rect.y - 380 <= self.target_player.rect.y:
                            self.x_vel = 0
                            self.rect.y = self.target_player.rect.y
                        else:
                            self.x_vel = 0
            else:
                self.x_vel = -1
                self.direction = "left"
                for i in range(-5, 5):
                    if self.rect.x + i == self.target_player.rect.x:
                        if self.rect.y - 380 >= self.target_player.rect.y:
                            self.x_vel = 0
                            self.rect.y = self.target_player.rect.y

        self.rect.x += self.x_vel

    def jump_if_needed(self, walls):
        #Jump if near an obstacle.
        for wall in walls:
            if self.rect.colliderect(wall.rect) and self.y_vel >= 0:
                self.y_vel = -self.GRAVITY * 8  # Jump if hitting a wall

    def shoot_fireball(self):
        # Shoots fireballs: Normal every 2s, Homing every 60s.
        current_time = time.time()

        #Homing fireball (every 60 seconds)
        #if current_time - self.last_homing_fireball_time >= 60:
        #    if self.target_player:
         #       fireball_sprites = self.SPRITES["homing_fireball"]  # Use correct sprites
          #      fireball = HomingFireball(self.rect.centerx, self.rect.y + 10, self.target_player, fireball_sprites)
           #     self.fireballs.add(fireball)
            #    self.last_homing_fireball_time = current_time  # Reset homing cooldown

        # Normal fireball (every 2 seconds)
        #if self.normal_fireball_cooldown <= 0:
         #   fireball_sprites = self.SPRITES["fireball.png"]
          #  direction = "right" if self.direction == "right" else "left"
            #fireball = Fireball(self.rect.centerx, self.rect.y + 10, 32, 32)
           # self.fireballs.add(fireball)
            #self.normal_fireball_cooldown = 120  # Reset cooldown

       # self.normal_fireball_cooldown -= 1


    def loop(self, fps, players, walls):
        """Update AI behavior every frame."""
        self.y_vel += min(10, (self.fall_count / fps) * self.GRAVITY)
        self.rect.y += self.y_vel
        self.fall_count += 1

        # Check if boss has landed on the ground
        if self.rect.bottom >= HEIGHT - 100:  # Adjust 100 to your ground level
            self.rect.bottom = HEIGHT - 100  # Keep the boss above the ground
            self.landed()  # Reset fall physics

        for player in players:
            if player.pushback == True:
                if self.sound_hit == 1:
                    self.PUNCH.play()
                if self.sound_hit == 2:
                    self.HIT.play()
                    self.sound_hit = 0

        self.find_nearest_player(players)
        self.move_toward_player()
        self.jump_if_needed(walls)
        self.shoot_fireball()

        self.fireballs.update()
        self.update_sprite()

    def update_sprite(self):
        #Update the AI's animation based on movement.
        sprite_sheet = "idle"
        if self.y_vel < 0:
            sprite_sheet = "jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY // 2) % len(sprites)
        self.sprite = sprites[sprite_index]

        self.animation_count += 1
        self.update()
    
    def landed(self):
        """Reset jump and fall counters when the boss lands."""
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def update(self):
        """Update hitbox and mask."""
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        """Draw the boss and fireballs."""
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
        self.fireballs.draw(win)

        name_text = FONT.render("DODGY", True, (255, 0, 0))  # Red color
        name_rect = name_text.get_rect(center=(self.rect.centerx - offset_x, self.rect.top - 15 - offset_y))
        window.blit(name_text, name_rect)

class Boss(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets_boss("MainCharacters", "PinkMan", 48, 48, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, ):
        super().__init__
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0 
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.target_player = None
    
    def find_nearest_player(self, player, player_1, player_2):
        if player.boss_distance > 0 and player_1.boss_distance > 0 and player_2.boss_distance > 0:   
            if player.boss_distance > player_1.boss_distance and player.boss_distance > player_2.boss_distance:
                if player.boss_height <= player_1.boss_height and player.boss_height <= player_2.boss_height:
                    self.target_player = player


    
class Object(pygame.sprite.Sprite):
    
    def __init__(self, x, y, width, height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class Block(Object):

    def __init__(self, x, y, width, size):
        super().__init__(x, y, size, size)
        self.image.fill((0, 0, 0))
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.timer = pygame.time.get_ticks()
        self.animation_count = 0
        self.animation_name = "off"
        self.active = True  # Fire is active by default

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def disappear(self):
        global X, Y, FIRE_COUNT
        FIRE_COUNT = 1
        X = 1300
        Y = 900
        self.active = False
        self.timer = pygame.time.get_ticks()  # Store the time it disappeared
        self.rect.topleft = (X, Y)  # Move hitbox off-screen

    def reappear(self, player, player_1):
        global FIRE_COUNT
        FIRE_COUNT = 0
        
        block_size = 96
        
        self.active = True
        
        new_x = random.randint(0, 1)  # Pick a new X position
        
        if new_x == 0:
            self.rect.topleft = (player.rect.x, HEIGHT - block_size)  # Set new position
        
        if new_x == 1:
            self.rect.topleft = (player_1.rect.x, HEIGHT - block_size)  # Set new position
        

    def loop(self, player, player_1):
        if not self.active:
            self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)  # Fully transparent image
            return  # Skip further updates

    # Fire animation logic
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0
        
        
        
        if FIRE_COUNT == 1:
            if pygame.time.get_ticks() - self.timer > 20000:  # 20 seconds
                self.reappear(player, player_1)
                self.redraw
        
    def redraw(self, window):
        if self.active:
            window.blit(self.image, self.rect)    


class Tag():

    def __init__(self, player, player_1):
        super().__init__()
        self.x = player.rect.x
        self.y = player.rect.y
        self.x_1 = player_1.rect.x
        self.y_1 = player_1.rect.y 
         
        
    
    def draw(self, window, player, player_1, player_2, width, tag_count, offset_x, offset_y):
        tag_points = [(player.rect.x - width/4 - offset_x + 32,  player.rect.y - 37 - offset_y), 
                      (player.rect.x + width/4 - offset_x + 32,  player.rect.y - 37 - offset_y), (player.rect.x - offset_x + 32,  player.rect.y - 5 - offset_y)]
        tag_points_1 = [(player_1.rect.x - width/4 - offset_x + 32,  player_1.rect.y - 37 - offset_y), 
                      (player_1.rect.x + width/4 - offset_x + 32,  player_1.rect.y - 37 - offset_y), (player_1.rect.x - offset_x + 32,  player_1.rect.y - 5 - offset_y)]
        tag_points_2 = [(player_2.rect.x - width/4 - offset_x + 32,  player_2.rect.y - 37 - offset_y), 
                      (player_2.rect.x + width/4 - offset_x + 32,  player_2.rect.y - 37 - offset_y), (player_2.rect.x - offset_x + 32,  player_2.rect.y - 5 - offset_y)]
        if tag_count == "p":
            tag_p = True
            
            pygame.draw.polygon(window, WHITE, tag_points, 0)
            
        elif tag_count == "p1":
            tag_p = False
            
            pygame.draw.polygon(window, WHITE, tag_points_1, 0)
        
        elif tag_count == "p2":
            tag_p = False
            
            pygame.draw.polygon(window, WHITE, tag_points_2, 0)

class Portal(Object):
    SPRITES = pygame.image.load("Portal.png").convert_alpha()
    TELEPORT_SOUND = pygame.mixer.Sound("assets/Sounds/teleport.wav")
    TELEPORT_SOUND.set_volume(1)  # Optional volume control

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "portal")
        self.sprite = self.SPRITES
        self.cooldown_duration = 10 * 1000  # 10 seconds
        self.mask = pygame.mask.from_surface(self.sprite)
        self.rect = pygame.Rect(x, y, width, height)
        self.last_spawn_time = pygame.time.get_ticks()
        self.cooldown = 500  # 0.5 seconds
        self.active = True
        self.deactivated_time = 0
        self.start_x = x
        self.start_y = y
        self.angle = 0
        self.pulse_scale = 1.0
        self.pulse_direction = 1  # 1 = growing, -1 = shrinking

    def draw(self, window, x, y, offset_x, offset_y):
        if self.active:
            # 🌀 Apply rotation and scale
            rotated_image = pygame.transform.rotozoom(self.sprite, self.angle, self.pulse_scale)
            rotated_rect = rotated_image.get_rect(center=(x - offset_x + self.sprite.get_width() // 2,
                                                      y - offset_y + self.sprite.get_height() // 2))
            window.blit(rotated_image, rotated_rect.topleft)

    def spawn(self, window, x, y, offset_x, offset_y):
        current_time = pygame.time.get_ticks()

        if not self.active:
            if current_time - self.deactivated_time >= self.cooldown_duration:
                self.active = True

        if self.active:
            # 🔄 Rotate
            self.angle = (self.angle + 2) % 360

            # 💓 Pulse
            pulse_speed = 0.01
            self.pulse_scale += pulse_speed * self.pulse_direction
            if self.pulse_scale >= 1.1:
                self.pulse_direction = -1
            elif self.pulse_scale <= 0.9:
                self.pulse_direction = 1

            # ✅ Always draw when active
            self.draw(window, self.start_x, self.start_y, offset_x, offset_y)
            self.rect.x = x
            self.rect.y = y

    
    def deactivate(self):
        self.active = False
        self.deactivated_time = pygame.time.get_ticks()
        self.TELEPORT_SOUND.play()
            

    def update(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def loop(self):
        self.update()
        

        

class Trampoline(Object):
    ANIMATION_DELAY = 3
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Traps", "Trampoline", 32, 32, True)

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.image = load_sprite_sheets("Traps", "Trampoline", width, height, True)
        self.rect = pygame.Rect(x, y, width, height)
        self.hit_check = False
        self.direction = "left"
        self.mask = pygame.mask.from_surface(self.image["Idle_left"][0])
        self.animation_count = 1
        self.hit_count = 0

    def draw(self, window, offset_x, offset_y):
        window.blit((self.image["Idle_left"][0]), (self.rect.x - offset_x, self.rect.y - offset_y))
    
    def hit(self, players):
        for player in players:
            if self.rect.colliderect(player.rect):
                player.y_vel = -self.GRAVITY * 30  # Adjust the jump height as needed
                self.hit_check = True
                self.animation_count = 0
                player.jump_count = 0

        
    def loop(self, fps, players):
        
        if self.hit_check:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit_check = False
            self.hit_count = 0
        
        self.hit(players)
        self.update_sprite() 
    
    def update_sprite(self):
        sprite_sheet = "Idle"
        if self.hit_check:
            sprite_sheet = "Jump"

        sprite_sheet_name = f"{sprite_sheet}_{self.direction}"
        sprites = self.SPRITES[sprite_sheet_name]

        if len(sprites) == 0:
            return  # Avoid division/modulo by zero

        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]

        self.animation_count += 1

        # If jump animation is done, revert to idle
        if self.hit_check and self.animation_count // self.ANIMATION_DELAY >= len(sprites):
            self.hit_check = False
            self.animation_count = 0

        self.update()

    
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)


def tag_logic(player, player_1, player_2):
    global TAG
    global last_switch_time
    
    player.update_sprite()
    player_1.update_sprite()
    player_2.update_sprite()
    
    
    current_time = pygame.time.get_ticks()
    switch_cooldown = 500  # Cooldown time in milliseconds

    # Only switch tag if the current "tag" player is involved in the collision
    if TAG == "p" and pygame.sprite.collide_mask(player, player_1):
        if current_time - last_switch_time > switch_cooldown:
            TAG = "p1"
            last_switch_time = current_time  # Reset cooldown timer
    elif TAG == "p" and pygame.sprite.collide_mask(player, player_2):
        if current_time - last_switch_time > switch_cooldown:
            TAG = "p2"
            last_switch_time = current_time  # Reset cooldown timer
    elif TAG == "p1" and pygame.sprite.collide_mask(player_1, player_2):
        if current_time - last_switch_time > switch_cooldown:
            TAG = "p2"
            last_switch_time = current_time  # Reset cooldown timer
    elif TAG == "p1" and pygame.sprite.collide_mask(player_1, player):
        if current_time - last_switch_time > switch_cooldown:
            TAG = "p"
            last_switch_time = current_time  # Reset cooldown timer
    elif TAG == "p2" and pygame.sprite.collide_mask(player_1, player_2):
        if current_time - last_switch_time > switch_cooldown:
            TAG = "p1"
            last_switch_time = current_time  # Reset cooldown timer
    elif TAG == "p2" and pygame.sprite.collide_mask(player_2, player):
        if current_time - last_switch_time > switch_cooldown:
            TAG = "p"
            last_switch_time = current_time  # Reset cooldown timer

def wall_jump(player, walls):
    if pygame.sprite.collide_mask(player, walls):
        if player.y_vel > 0:
            player.y_vel = -()
        elif player.y_vel < 0:
            player.rect.top = walls.rect.bottom
            player.hit_head()
        if player.x_vel > 0:
            player.rect.right = walls.rect.left
        elif player.x_vel < 0:
            player.rect.left = walls.rect.right


def tag_logic_2player(player, player_1):
    global TAG
    global last_switch_time
    
    player.update_sprite()
    player_1.update_sprite()
    
    current_time = pygame.time.get_ticks()
    switch_cooldown = 500  # Cooldown time in milliseconds

    # Only switch tag if the current "tag" player is involved in the collision
    if TAG == "p" and pygame.sprite.collide_mask(player, player_1):
        if current_time - last_switch_time > switch_cooldown:
            TAG = "p1"
            last_switch_time = current_time  # Reset cooldown timer
    elif TAG == "p1" and pygame.sprite.collide_mask(player_1, player):
        if current_time - last_switch_time > switch_cooldown:
            TAG = "p"
            last_switch_time = current_time  # Reset cooldown timer



def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, player_1, player_2, boss, objects, offset_x, offset_y, tag_marker, tag, remaining_time, portal, portal_1):
    global NO_OF_PLAYERS
    for tile in background:
        window.blit(bg_image, tile)

    boss.fireballs.draw(window)

    for obj in objects:
        obj.draw(window, offset_x, offset_y)
    
    tag_marker.draw(window, player, player_1, player_2, 64, tag, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)
    player_1.draw(window, offset_x, offset_y)
    if NO_OF_PLAYERS == 3:
        player_2.draw(window, offset_x, offset_y)
    boss.draw(window, offset_x, offset_y)
    

    font = pygame.font.Font(None, 40)
    timer_text = font.render(f"Time Left: {remaining_time}s", True, (255, 255, 255))
    window.blit(timer_text, (WIDTH - 220, 20))
    portal.spawn(window, 96, HEIGHT - 128 - 32, offset_x, offset_y)
    portal_1.spawn(window, 96 * 2, HEIGHT - 480, offset_x, offset_y)
    

    pygame.display.update()

def respawn(players):
    for player in players:
        if player.rect.y < -2000 and player.rect.x > 100:
            player.rect.y = 50
            player.rect.x = 1100
            player.make_hit()
            player.life_count -= 1
            if player.life_count == 0:
                player.KO()
        if player.rect.y < -2000 and player.rect.x < 100:
            player.rect.y = 100
            player.rect.x = 50
            player.make_hit()
            player.life_count -= 1
            if player.life_count == 0:
                player.KO()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def pushback(player, boss):
     
    if pygame.sprite.collide_mask(player, boss):
        boss.sound_hit += 1
        player.pushback = True
        contact_point = player.rect.x
        contact_point_y = player.rect.y
        if player.direction == "left":
            if contact_point < player.rect.x + 500:
                player.x_vel = 50
            else:
                player.x_vel = 0
            if contact_point_y < player.rect.y + 100:
                player.y_vel = 10
            else:
                player.x_vel = 0
        if player.direction == "right":
            if contact_point > player.rect.x - 500:
                player.x_vel = -50
            else:
                player.x_vel = 0
            if contact_point_y > player.rect.y - 100:
                player.y_vel = -10
            else:
                player.x_vel = 0
    else:
        player.pushback = False

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
              
    player.move(-dx, 0)
    player.update()
    return collided_object
    
        
def handle_move(player, objects, boss):
    global PLAYER_VEL
    
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    boss_collision = pushback(player, boss)

    for obj in to_check:
        if obj and obj.name == "fire":
            obj.disappear()
            #player.make_hit()
 

def handle_move_1(player, objects, boss):

    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL_1 * 2)
    collide_right = collide(player, objects, PLAYER_VEL_1 * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL_1)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL_1)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    boss_collision = pushback(player, boss)

    for obj in to_check:
        if obj and obj.name == "fire":
            obj.disappear()  # Make fire disappear
            #player.make_hit()

def handle_move_2(player, objects, boss):

    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL_2 * 2)
    collide_right = collide(player, objects, PLAYER_VEL_2 * 2)

    if keys[pygame.K_j] and not collide_left:
        player.move_left(PLAYER_VEL_2)
    if keys[pygame.K_l] and not collide_right:
        player.move_right(PLAYER_VEL_2)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    boss_collision = pushback(player, boss)

    for obj in to_check:
        if obj and obj.name == "fire":
            obj.disappear()  # Make fire disappear
            #player.make_hit()

def handle_fireball_collisions(fireballs, players):
    """Check if fireballs hit any player and apply effects."""
    for fireball in fireballs:
        for player in players:
            if pygame.sprite.collide_mask(fireball, player):
                if isinstance(player, BOSS):  # Ignore boss collisions
                    continue
                print(f"{player} was hit by a fireball!")
                fireball.kill()  # Remove fireball
                #player.make_hit()  # Apply effect (e.g., slow down)

def handle_portal_collision(portal, twin_portal, players, offset_x, offset_y):
    for player in players:
        player.update_sprite()

        portal.update()
        twin_portal.update()

        if portal.active and pygame.sprite.collide_mask(player, portal):
            player.rect.x = twin_portal.rect.x
            player.rect.y = twin_portal.rect.y
            portal.deactivate()
            twin_portal.deactivate()
            player.jump()

        elif twin_portal.active and pygame.sprite.collide_mask(player, twin_portal):
            player.rect.x = portal.rect.x
            player.rect.y = portal.rect.y
            portal.deactivate()
            twin_portal.deactivate()
            player.jump()

        # Draw portals (only active ones are drawn)
        portal.draw(window, 96, HEIGHT - 128 - 32, offset_x, offset_y)
        twin_portal.draw(window, 96 * 2, HEIGHT - 480, offset_x, offset_y)



def main():
    global TAG
    global NO_OF_PLAYERS
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")  

    block_size = 96

    player = Player(100, 100, 50, 50)
    player_1 = Player_1(200, 100, 50, 50)
    if NO_OF_PLAYERS == 3:
        player_2 = Player_2(300, 100, 50, 50)
    boss = BOSS(600, HEIGHT - block_size, 100, 100)
    tag_marker = Tag(player, player_1)
    fire = Fire(196, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size, block_size) 
             for i in range(-WIDTH // block_size, WIDTH * 2  // block_size)]
    platform = [Block(192 + i * block_size, HEIGHT - (block_size * 4), block_size, block_size) 
             for i in range(0, 4)]
    platform_1 = [Block(-i * block_size, HEIGHT - (block_size * 6), block_size, block_size) 
             for i in range(2, 6)]
    platform_2 = [Block(192 + i * block_size, HEIGHT - (block_size * 8), block_size, block_size) 
             for i in range(5, 8)]
    platform_3 = [Block(192 + i * block_size, HEIGHT - (block_size * 8), block_size, block_size) 
             for i in range(10, 12)]
    
    wall_left = [Block(-(block_size * 5), HEIGHT - block_size * i, block_size, block_size) 
             for i in range(0, 100)]
    wall_right = [Block(WIDTH + (block_size * 2), HEIGHT - block_size * i, block_size, block_size) 
             for i in range(0, 100)]
    trampoline = Trampoline(1200 - block_size, HEIGHT - 152, 28, 28)

    objects = [*floor, *platform, *platform_1, *platform_2, *platform_3, Block(0, HEIGHT - block_size * 2, block_size, block_size), fire, *wall_left, *wall_right, trampoline]
    
    portal = Portal(96, HEIGHT - 128 - 32, 32, 32)
    portal_1 = Portal(96 * 2, HEIGHT - 480, 32, 32)
    
    
    start_time = pygame.time.get_ticks()
    timer_duration = TIME
    
    players = [player, player_1, player_2] if NO_OF_PLAYERS == 3 else [player, player_1]

    offset_x = 0
    offset_x_1 = 0
    offset_x_2 = 0
    offset_y = 0
    offset_y_1 = 0
    offset_y_2 = 0
    scroll_area_width = 200
    scroll_area_height = 96

    players_to_track = [player, player_1, player_2]  # adjust based on your code
    

    run = True
    while run:
        clock.tick(FPS)

        respawn([player, player_1, player_2])
        trampoline.loop(FPS, players)

        if NO_OF_PLAYERS == 2:
            boss.loop(FPS, [player, player_1], objects)
        elif NO_OF_PLAYERS == 3:
            boss.loop(FPS, [player, player_1, player_2], objects)
        
        for fireball in boss.fireballs:
            fireball.update_fireball() 

        if NO_OF_PLAYERS == 2:
            handle_fireball_collisions(boss.fireballs, [player, player_1])
        if NO_OF_PLAYERS == 3:
            handle_fireball_collisions(boss.fireballs, [player, player_1, player_2])
            handle_portal_collision(portal, portal_1, players, offset_x, offset_y)

        player.tag_check(TAG_COUNT, 32, 64)
        elapsed_time = pygame.time.get_ticks() - start_time
        remaining_time = max(0, (timer_duration - elapsed_time) // 1000)

        if remaining_time <= 0:
            print("Time's up! Game Over.")
            print (tag, "loses.")
            break
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_w and player_1.jump_count < 2:
                    player_1.jump()
                if event.key == pygame.K_i and player_2.jump_count < 2:
                    player_2.jump()
        fire.loop(player, player_1)  # Update fire state
        

        tag = TAG   
        
        if NO_OF_PLAYERS == 2:
            tag_logic_2player(player, player_1)
        elif NO_OF_PLAYERS == 3:
            tag_logic(player, player_1, player_2)
        
        portal.loop()
        portal_1.loop()
        player.loop(FPS)
        player_1.loop(FPS)
        if NO_OF_PLAYERS == 3:
            player_2.loop(FPS)
        
        handle_move(player, objects, boss)
        handle_move_1(player_1, objects, boss)
        if NO_OF_PLAYERS == 3:
            handle_move_2(player_2, objects, boss)
        
        
        if NO_OF_PLAYERS == 3:
            if player.rect.y < 700:
                draw(window, background, bg_image, player, player_1, player_2, boss, objects, offset_x, offset_y, tag_marker, tag, remaining_time, portal, portal_1)
                
            elif player.rect.y > 700 and player_1.rect.y < 700 and player_2.rect.y < 700:
                
                draw(window, background, bg_image, player, player_1, player_2, boss, objects, offset_x_1, offset_y_1, tag_marker, tag, remaining_time, portal, portal_1)
            elif player.rect.y > 700 and player_1.rect.y > 700 and player_2.rect.y < 700:
                
                draw(window, background, bg_image, player, player_1, player_2, boss, objects, offset_x_2, offset_y_2, tag_marker, tag, remaining_time, portal, portal_1)
                time.sleep(1)
                pygame.quit()
                quit()
        
        
        if NO_OF_PLAYERS == 3:
            if player.rect.y > 700:
            
                if TAG == "p":
                    if player_1.rect.y > player_2.rect.y:
                        TAG = "p2"
                    elif player_1.rect.y < player_2.rect.y:
                        TAG = "p1"
        
            if player_1.rect.y > 700:
            
                if TAG == "p1":
                    if player.rect.y > player_2.rect.y:
                        TAG = "p2"
                    elif player.rect.y < player_2.rect.y:
                        TAG = "p"
        
        
            if player_2.rect.y > 700:
            
                if TAG == "p2":
                    if player.rect.y > player_1.rect.y:
                        TAG = "p1"
                    elif player.rect.y < player_1.rect.y:
                        TAG = "p"


        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
        if ((player_1.rect.right - offset_x_1 >= WIDTH - scroll_area_width) and player_1.x_vel > 0) or (
            (player_1.rect.left - offset_x_1 <= scroll_area_width) and player_1.x_vel < 0):
            offset_x_1 += player_1.x_vel
        
        if NO_OF_PLAYERS == 3:
            if ((player_2.rect.right - offset_x_2 >= WIDTH - scroll_area_width) and player_2.x_vel > 0) or (
            (player_2.rect.left - offset_x_2 <= scroll_area_width) and player_2.x_vel < 0):
                offset_x_2 += player_2.x_vel
        
        if player.rect.bottom < HEIGHT - block_size:
            if ((player.rect.bottom - offset_y >= HEIGHT - scroll_area_height) and player.y_vel > 0) or (
            (player.rect.top - offset_y <= scroll_area_height) and player.y_vel < 0):
                offset_y += player.y_vel

    
    pygame.quit()
    quit()

if __name__ == "__main__":
    main()
