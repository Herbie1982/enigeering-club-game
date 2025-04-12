import os
import random
import math
import time
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer Advanced")

START_VEL = 6
WIDTH, HEIGHT = 1200, 700
FPS = 60
PLAYER_VEL = START_VEL
PLAYER_VEL_1 = START_VEL
PLAYER_VEL_2 = START_VEL
WHITE = (255, 255, 255)
TAG_COUNT = 0
TAG = input("Who starts as Tag? ")
while TAG != "p" and TAG != "p1" and TAG != "p2":
    TAG = input("Invalid. Please state 'p', 'p1', or 'p2'. Who starts as Tag? ")
last_switch_time = 0
FIRE_COUNT = 0
NO_OF_PLAYERS = int(input("How many players? "))
while NO_OF_PLAYERS != 2 and NO_OF_PLAYERS != 3:
    NO_OF_PLAYERS = int(input("Invalid. Please state either 2 or 3. How may players? "))


window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

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

def  get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3
    POTION_EFFECTS = [False, False, False, False, False, False] #makes room for 6 magic effects for each player; currently 1 magic effect is in use (curse, which attracts the boss)
   
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
        triangle_points = [(x - height - 64, y - width/2), (x - height - 64, y + width/2), (x - height - 10, y - width/2)]
        self.fire_count = 0

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
        global PLAYER_VEL
        current_time = pygame.time.get_ticks()
        fire_cooldown = 5000  # 5 seconds
        PLAYER_VEL = 10  # Reset velocity

        # If fire_count is None, set it to current time (first hit)
        if self.fire_count == 0:
            self.fire_count = current_time

        print(f"Current Time: {current_time}, Fire Count: {self.fire_count}")

        if current_time - self.fire_count > fire_cooldown:
            PLAYER_VEL = 6
            self.fire_count = current_time  # Reset cooldown
            print("Cooldown over - Velocity reduced to 6!")
        else:
            print("Cooldown active - Velocity remains 10!")

        

        
    
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

        self.y_vel += min(10, (self.fall_count / fps) * self.GRAVITY)
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

    def tag_check(self, tag_count, width, height):
        triangle_points = [(self.rect.x - 128,  - width/2), (self.rect.x - height - 64, self.rect.y + width/2), (self.rect.x - height - 10, self.rect.y - width/2)]
        if TAG_COUNT == 0:
            tag_rect =  pygame.draw.polygon(window, WHITE, triangle_points, 0)
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

    def switch_tag(self, tag):
        if tag == "p1":
            tag = "p"

class Player_1(pygame.sprite.Sprite):
    
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
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
        self.tag_count = 0
        

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
        current_time = pygame.time.get_ticks()
        fire_cooldown = 5000  # 5 seconds
        self.player_vel = 10
        
        if current_time - self.fire_count > fire_cooldown:
            self.player_vel = 6
            self.fire_count = current_time
    
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
        self.y_vel += min(20, (self.fall_count / fps) * self.GRAVITY)
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
    
    def tag_check(self, tag_count, width, height):
        triangle_points = [(self.rect.x - 128,  - width/2), (self.rect.x - height - 64, self.rect.y + width/2), (self.rect.x - height - 10, self.rect.y - width/2)]
        if TAG_COUNT == 1:
            tag_rect =  pygame.draw.polygon(window, WHITE, triangle_points, 0)
        
        

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

    def switch_tag(self, tag):
        if tag == "p":
            tag = "p1"

class Player_2(pygame.sprite.Sprite):
    
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
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
        triangle_points = [(x - height - 64, y - width/2), (x - height - 64, y + width/2), (x - height - 10, y - width/2)]

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
        current_time = pygame.time.get_ticks()
        fire_cooldown = 5000  # 5 seconds
        self.player_vel = 10
        
        if current_time - self.fire_count > fire_cooldown:
            self.player_vel = 6
            self.fire_count = current_time
    
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

        self.y_vel += min(10, (self.fall_count / fps) * self.GRAVITY)
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

    def tag_check(self, tag_count, width, height):
        triangle_points = [(self.rect.x - 128,  - width/2), (self.rect.x - height - 64, self.rect.y + width/2), (self.rect.x - height - 10, self.rect.y - width/2)]
        if TAG_COUNT == 0:
            tag_rect =  pygame.draw.polygon(window, WHITE, triangle_points, 0)
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

    def switch_tag(self, tag):
        if tag == "p1":
            tag = "p"


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



def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, player_1, player_2, objects, offset_x, offset_y, tag_marker, tag, remaining_time):
    global NO_OF_PLAYERS
    for tile in background:
        window.blit(bg_image, tile)

    

    for obj in objects:
        obj.draw(window, offset_x, offset_y)
    
    tag_marker.draw(window, player, player_1, player_2, 64, tag, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)
    player_1.draw(window, offset_x, offset_y)
    player_2.draw(window, offset_x, offset_y)
    

    font = pygame.font.Font(None, 40)
    timer_text = font.render(f"Time Left: {remaining_time}s", True, (255, 255, 255))
    window.blit(timer_text, (WIDTH - 220, 20))

    pygame.display.update()


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

def handle_move(player, objects):
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

    for obj in to_check:
        if obj and obj.name == "fire":
            obj.disappear()
            #player.make_hit()
 

def handle_move_1(player, objects):

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

    for obj in to_check:
        if obj and obj.name == "fire":
            obj.disappear()  # Make fire disappear
            #player.make_hit()

def handle_move_2(player, objects):

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

    for obj in to_check:
        if obj and obj.name == "fire":
            obj.disappear()  # Make fire disappear
            #player.make_hit()




def main():
    global TAG
    global NO_OF_PLAYERS
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")  

    block_size = 96

    player = Player(100, 100, 50, 50)
    player_1 = Player_1(200, 100, 50, 50)
    player_2 = Player_2(300, 100, 50, 50)
    tag_marker = Tag(player, player_1)
    fire = Fire(196, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size, block_size) 
             for i in range(-WIDTH // block_size, WIDTH * 2  // block_size)]
    platform = [Block(192 + i * block_size, HEIGHT - (block_size * 4), block_size, block_size) 
             for i in range(0, 4)]
    platform_1 = [Block(-i * block_size, HEIGHT - (block_size * 6), block_size, block_size) 
             for i in range(2, 6)]
    objects = [*floor, *platform, *platform_1, Block(0, HEIGHT - block_size * 2, block_size, block_size), fire]
            
        
    
    start_time = pygame.time.get_ticks()
    timer_duration = 180000
    

    offset_x = 0
    offset_x_1 = 0
    offset_x_2 = 0
    offset_y = 0
    offset_y_1 = 0
    offset_y_2 = 0
    scroll_area_width = 200
    scroll_area_height = 96


    run = True
    while run:
        clock.tick(FPS)
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
        
        tag_logic(player, player_1, player_2)
        

        player.loop(FPS)
        player_1.loop(FPS)
        player_2.loop(FPS)
        
        handle_move(player, objects)
        handle_move_1(player_1, objects)
        handle_move_2(player_2, objects)
        
        
        if player.rect.y < 700:
            draw(window, background, bg_image, player, player_1, player_2, objects, offset_x, offset_y, tag_marker, tag, remaining_time)
        elif player.rect.y > 700 and player_1.rect.y < 700 and player_2.rect.y < 700:
            draw(window, background, bg_image, player, player_1, player_2, objects, offset_x_1, offset_y_1, tag_marker, tag, remaining_time)
        elif player.rect.y > 700 and player_1.rect.y > 700 and player_2.rect.y < 700:
            draw(window, background, bg_image, player, player_1, player_2, objects, offset_x_2, offset_y_2, tag_marker, tag, remaining_time)
            time.sleep(1)
            pygame.quit()
            quit()
        
        
        if player.rect.y > 700:
            
            if TAG == "p":
                if player_1.rect.y > player_2.rect.y:
                    TAG = "p2"
                if player_1.rect.y < player_2.rect.y:
                    TAG = "p1"
        
        if player_1.rect.y > 700:
            
            if TAG == "p1":
                if player.rect.y > player_2.rect.y:
                    TAG = "p2"
                if player.rect.y < player_2.rect.y:
                    TAG = "p"
        
        
        if player_2.rect.y > 700:
            
            if TAG == "p2":
                if player.rect.y > player_1.rect.y:
                    TAG = "p1"
                if player.rect.y < player_1.rect.y:
                    TAG = "p"


        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
        if ((player_1.rect.right - offset_x_1 >= WIDTH - scroll_area_width) and player_1.x_vel > 0) or (
            (player_1.rect.left - offset_x_1 <= scroll_area_width) and player_1.x_vel < 0):
            offset_x_1 += player_1.x_vel
        
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
    
