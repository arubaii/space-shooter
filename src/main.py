import pygame as pg 
import os 
from os.path import join
import random
from random import randint, uniform


# SPRITE CLASSES ______________________________________________________________________________________________________

class Player(pg.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        # Player attributes
        self.image = pg.image.load(ship_png).convert_alpha() 
        self.rect = self.image.get_frect(center=(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2))
        self.player_pos = pg.Vector2()
        self.player_speed = 800
        self.mask = pg.mask.from_surface(self.image)

        # Cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400        


    def update(self, dt):
        '''Creates WASD controls, and laser functionality'''

        keys = pg.key.get_pressed()
        self.player_pos.x = int(keys[pg.K_d]) - int(keys[pg.K_a])
        self.player_pos.y = int(keys[pg.K_s]) - int(keys[pg.K_w]) 
        # Normalizing our vector so that in a diagonal direction, we are not moving faster than the predetermined speed
        self.player_pos = self.player_pos.normalize() if self.player_pos else self.player_pos 
        self.rect.center += self.player_pos * self.player_speed * dt     

        key_press = pg.key.get_just_pressed()

        if key_press[pg.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            # Introducing delay after each laser shot
            self.can_shoot = False
            self.laser_shoot_time = pg.time.get_ticks()
            laser_sound.play()
        self.laser_timer()
    

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pg.time.get_ticks()
            # If enough time has passed since user has shot a laser, they may fire again
            if current_time - self.laser_shoot_time > self.cooldown_duration:
                self.can_shoot = True



class Star(pg.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        # Star attributes
        self.image = pg.image.load(star_png).convert_alpha()
        self.rect = self.image.get_frect(center=(randint(0,DISPLAY_WIDTH), 0))
        self.start_time = pg.time.get_ticks()
        self.lifetime = 3000
        self.direction = pg.Vector2(0, 1)
        self.speed = 1500
        

    def update(self,dt):
        self.rect.center += self.speed * self.direction * dt
        if pg.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        


class Laser(pg.sprite.Sprite):
    def __init__(self, laser_surf, pos ,groups):
        super().__init__(groups)
        # Laser attributes
        self.image = laser_surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.laser_speed = 800


    def update(self, dt):
        self.rect.centery -= self.laser_speed * dt
        if self.rect.bottom < 0:
            self.kill() # Kills laser once off screen



class Meteor(pg.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        # Meteor attributes
        self.original_image = meteor_surf
        self.image = self.original_image
        # We raise a power to the y-value to skew the distribution
        self.rect = self.image.get_frect(center=(randint(0,DISPLAY_WIDTH), DISPLAY_HEIGHT * (random.random() ** 10)))  
        self.start_time = pg.time.get_ticks()
        self.lifetime = 3000
        self.direction = pg.Vector2(uniform(-0.5,0.5), 1)
        self.speed = randint(400,500)
        self.rotation = 0
        self.rotate_speed = randint(100,500)


    def update(self,dt):
        self.rect.center += self.speed * self.direction * dt
        if pg.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        
        # Continuous rotation
        self.rotation += self.rotate_speed * dt
        self.image = pg.transform.rotozoom(self.original_image, self.rotation, 1)
        # Fixes weird behavior
        self.rect = self.image.get_frect(center = self.rect.center)


def collisions(player_health, player_score):
    '''All of the collision sprites, and collision logic is stored in this function'''

    # Checks if player is colliding with meteor
    collision_sprites = pg.sprite.spritecollide(player, meteor_sprites, True, pg.sprite.collide_mask) 

    if collision_sprites:
        # Ends game when colldiing with a meteor
        player_health -= 1
        if player_health == 0:
            running = False

    for laser in laser_sprites:
        # Checks if laser is colliding with meteor
        collided_sprites = pg.sprite.spritecollide(laser, meteor_sprites, dokill=True) 
        if collided_sprites:
            laser.kill()
            explosion_sound.play()
            player_score += 10
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)

    return player_health, player_score



class AnimatedExplosion(pg.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self, dt):
        '''
        When the 'AnimatedExplosion' class is called, we create a list of the frames (see 'explosion_images' variable) 
        with the self.image starting at 0. Then index over each frame with respect to delta time, 
        updating the self.image variable at each frame.
        '''

        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            # Kill animation once we hit the 20th frame
            self.kill()



class Button():
    def __init__(self, image, x, y, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pg.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_frect(center=(x,y))
        self.mask = pg.mask.from_surface(self.image)
        display.blit(self.image, self.rect)
        self.quit = quit
    

    def draw(self):
        mouse_pos = pg.mouse.get_pos()
        # Get mouse position relative to the button's positon
        relative_x, relative_y = mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y

        # Check if mouse is inside the button's rect AND over a visible pixel
        if self.rect.collidepoint(mouse_pos):
            if self.mask.get_at((relative_x, relative_y)): # Ensures mouse is over a non-transparent pixel
                if pg.mouse.get_just_pressed()[0] == 1:
                    start_sound.play()
                    pg.time.delay(750)
                    return False
   
        return True


# SETUP ____________________________________________________________________________________________________________________

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pg.init()
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
DEBUG = True
FPS = 120
display = pg.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT), flags=pg.SCALED,vsync=1)
title = pg.display.set_caption("Space Shooter")
clock = pg.Clock()

player_health = 5 
player_score = 0


# IMPORTS ____________________________________________________________________________________________________________________

# Images --------------

ship_png = join(BASE_PATH, "Assets", "images", "player.png")
star_png = join(BASE_PATH, "Assets", "images", "star.png")

meteor_png = join(BASE_PATH, "Assets", "images", "meteor.png")
laser_png = join(BASE_PATH, "Assets", "images", "laser.png")
start_png = join(BASE_PATH, "Assets", "images", "start_button.png")
quit_png = join(BASE_PATH, "Assets", "images", "quit_button.png")
font_ttf = join(BASE_PATH, "Assets", "images", "Oxanium-Bold.ttf")

ship_surf = pg.image.load(ship_png).convert_alpha()
pg.display.set_icon(ship_surf) # Window logo
meteor_surf = pg.image.load(meteor_png).convert_alpha() 
laser_surf = pg.image.load(laser_png).convert_alpha() 
start_surf = pg.image.load(start_png).convert_alpha()
quit_surf = pg.image.load(quit_png).convert_alpha()
explosion_frames = [ # Loads all 20 explosion images in a list comprehenshion
    pg.image.load(join(BASE_PATH, "Assets", "images", "explosion", f"{image}.png", )).convert_alpha() for image in range(21)
    ]

# Audio ----------------

laser_sound = pg.mixer.Sound(join(BASE_PATH, "Assets", 'audio', 'laser.wav'))
laser_sound.set_volume(0.15)
explosion_sound = pg.mixer.Sound(join(BASE_PATH, "Assets", 'audio', 'explosion.wav'))
explosion_sound.set_volume(0.18)
music = pg.mixer.Sound(join(BASE_PATH, "Assets", 'audio', 'game_music.wav'))
start_sound = pg.mixer.Sound(join(BASE_PATH, "Assets", 'audio', 'start_sound.wav'))
start_sound.set_volume(0.20)


# TEXT ________________________________________________________________________________________________________________________

def font(font_size):
    text_font = pg.font.Font(font_ttf, size=font_size)
    return text_font

def fps_counter():
    fps = str(int(clock.get_fps()))
    fps_t = font(18).render(fps, antialias=True, color='red')
    display.blit(fps_t,(2,2)) 

def display_health(player_health, player_score) -> pg.Surface:
    player_health, player_score = collisions(player_health, player_score)
    health_text = font(50).render("HEALTH |", antialias=True, color='lightgray')
    health_value = font(50).render(f"{player_health}", True, (230, 0, 0))

    return health_text, health_value

def display_death():
    death_text = font(70).render("YOU LOST", antialias=True, color='red')
    display.blit(death_text, (DISPLAY_WIDTH / 2 - 145, DISPLAY_HEIGHT / 4 - 100))

def display_score(player_health, player_score): 
    player_health, player_score = collisions(player_health, player_score)
    # Different colors based on score
    if player_score < 10: 
        color = 'lightgrey'
    elif player_score < 20:
        color = 'lightyellow'
    elif player_score < 30:
        color = 'cyan'
    elif player_score < 50:
        color = 'lightgreen'
    else:
        color = 'red'
    score_surf = font(40).render(f"SCORE | {player_score}", True, color)
    score_rect = score_surf.get_frect(midbottom= (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 25))

    return score_surf, score_rect

def start_screen(player_dead):
    '''Display start screen and wait for user input to start the game'''

    waiting = True

    while waiting:
        music.stop()
        display.fill("lightgrey")
        if player_dead:
            display_death()
        text = font(40).render("BY AHMAD", True, "Orange")
        display.blit(text, (DISPLAY_WIDTH - 215,DISPLAY_HEIGHT - 40))
        start_button = Button(start_surf, DISPLAY_WIDTH / 2 - 300, DISPLAY_HEIGHT / 2 + 25, 1)
        quit_button = Button(quit_surf, DISPLAY_WIDTH / 2 + 300, DISPLAY_HEIGHT / 2 - 9, 1)
        
        if start_button.draw() == False:

            waiting = False

        pg.display.flip()
        for event in pg.event.get():
            # Exit loop when user clicks X
            if event.type == pg.QUIT:
                pg.quit()
                exit()

            # Exit loop when user clicks 'Exit'   
            if quit_button.draw() == False:
                pg.time.delay(250) # Makes the quit less jarring
                pg.quit()
                exit() 
    return waiting

def play_music(music):
    music.set_volume(0.05)
    music.play()
    music.play(loops=-1) # Music plays indefinitely
        

# SPRITES INSTANCES ____________________________________________________________________________________________________________

# Calling star screen function before main game
player_dead = False
start_screen(player_dead)

all_sprites = pg.sprite.Group()         # The first Group call will always contain all sprites
meteor_sprites = pg.sprite.Group()
laser_sprites = pg.sprite.Group()
star_sprites = pg.sprite.Group()


player = Player(all_sprites)
star_event = pg.event.custom_type()
pg.time.set_timer(star_event, 15)       # Stars spawn ever 10 ms
meteor_event = pg.event.custom_type()
pg.time.set_timer(meteor_event, 250)    # Meteors spawn ever 250 ms

play_music(music)
running = True

# DISPLAY LOOP _________________________________________________________________________________________________________________
while running:
    # FPS limit, delta time is how long it takes for us to render one frame
    dt = clock.tick(FPS) / 1000 

    # Game loop
    for event in pg.event.get():
        # Exit loop when user clicks X
        if event.type == pg.QUIT:
            running = False
        if event.type == meteor_event:
            Meteor([all_sprites, meteor_sprites])
        if event.type == star_event:
            Star(star_sprites)

        if player_health == 0:
            player_dead = True
            waiting = start_screen(player_dead)
 
            if not waiting:
                # We reset the game if the user selects start again
                player_health = 5
                player_score = 0
                all_sprites.empty()
                meteor_sprites.empty()
                laser_sprites.empty()
                star_sprites.empty()

                player = Player(all_sprites)
                play_music(music)
                    
                    

    # Update
    all_sprites.update(dt)
    star_sprites.update(dt)
    player_health, player_score = collisions(player_health, player_score)

    # Game draw
    display.fill("#0A0A23")         # First background
    star_sprites.draw(display)      # Then stars
    all_sprites.draw(display)       # Then meteors

    score_surf, score_rect = display_score(player_health, player_score)
    display.blit(score_surf, score_rect)

    health_text, health_value = display_health(player_health, player_score)
    display.blit(health_text, (0, DISPLAY_HEIGHT - 55) )
    display.blit(health_value, (10 + health_text.get_width(), DISPLAY_HEIGHT - 55))
    # Draws a border around the score
    pg.draw.rect(display, 'lightgrey', score_rect.inflate(20,15).move(0,-7), 5, border_radius=5)

    fps_counter()
    pg.display.flip()


pg.quit()
