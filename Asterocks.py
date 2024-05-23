import pygame
import random
import numpy as np
import cmath

from pygame.locals import (
        RLEACCEL,
        K_UP,
        K_DOWN,
        K_LEFT,
        K_RIGHT,
        K_ESCAPE,
        K_SPACE,
        KEYDOWN,
        KEYUP,
        QUIT,
        MOUSEBUTTONUP,
        MOUSEBUTTONDOWN,
        )
######################
# Inicjalizacja
######################

## Gra
pygame.init()

## Muzyka
pygame.mixer.init()

######################
# Konfiguracja
######################

## Pliki
ship = "ship1.png"
ship_flame = "ship1_flame.png"

with open('high_scores.txt', 'r') as file:
    info = file.read().rstrip('\n')
    info = list(info.split('\n'))

## Ekran
WIDTH, HEIGHT = 900, 500
bg = pygame.image.load("nebulawetstars.png")
bg = pygame.transform.scale(bg, [900, 500])

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Asterocks")
pygame.display.flip()

## Obrazy
player_icon = pygame.image.load(ship).convert()
player_icon = pygame.transform.scale(player_icon, (27, 27))
player_icon.set_colorkey((255, 255, 255), RLEACCEL)

arrowkey = pygame.image.load("arrow.png").convert()
arrowkey = pygame.transform.scale(arrowkey, (30, 30))

spacebar = pygame.image.load("spacebar.png").convert()
spacebar = pygame.transform.scale(spacebar, (100, 30))

ship1 = pygame.image.load("ship1.png").convert()
ship1 = pygame.transform.scale(ship1, (70, 70))
ship1.set_colorkey((255, 255, 255), RLEACCEL)

ship2 = pygame.image.load("ship2.png").convert()
ship2 = pygame.transform.scale(ship2, (68, 68))
ship2.set_colorkey((255, 255, 255), RLEACCEL)

ship3 = pygame.image.load("ship3.png").convert()
ship3 = pygame.transform.scale(ship3, (69, 69))
ship3.set_colorkey((255, 255, 255), RLEACCEL)

xchosen = 580
ychosen = 170

## Dźwięki

explotion_sound = pygame.mixer.Sound("explosion.wav")
rock_sound = pygame.mixer.Sound("boom3.wav")
shot_sound = pygame.mixer.Sound("laser4.wav")
engine_sound = pygame.mixer.Sound("engine_takeoff.wav")
click_sound = pygame.mixer.Sound("click_sound_1.mp3")

######################
# Funckje pomocnicze
######################

def explotion(x, y, size):
    """Funkcja wyświetlająca animacje explozji gracza"""
    i = 0
    start = pygame.time.get_ticks()
    while i < 6:
        expl = pygame.image.load(f"explosion{i+1}.png").convert()
        expl = pygame.transform.scale(expl, [size, size])
        expl.set_colorkey((0, 0, 0), RLEACCEL)
        screen.blit(expl, [x, y])
        draw_text(f"Score: {score}", 5, HEIGHT-50, 30, screen)
        draw_lives(10, 10, player.hearts)
        pygame.display.flip()
        if pygame.time.get_ticks() - start > 75*(i+1):
            i += 1

def draw_text(text, x, y, size, surf ,color=(255, 255, 255)):
    """Funckaj rysująca tekst na ekran"""
    font = pygame.font.Font("Pixel.ttf", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surf.blit(text_surface, text_rect)

def draw_lives(x, y, lives):
    """Funckja rysująca życia na ekran"""
    for i in range(lives):
        img_rect = player_icon.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        screen.blit(player_icon, img_rect)

def set_ship(name):
    """Funkcja ustawiająca odpowiedni statek jako gracza"""
    global ship, ship_flame, player_icon
    ship = f"{name}.png"
    ship_flame = f"{name}_flame.png"
    player_icon = pygame.image.load(ship).convert()
    player_icon = pygame.transform.scale(player_icon, (27, 27))
    player_icon.set_colorkey((255, 255, 255), RLEACCEL)

def chosen(x, y):
    """Funkcja ustalająca gdzie pojawi się strzałka pokazująca na wybrany przez gracza statek"""
    global xchosen, ychosen
    xchosen = x
    ychosen = y

def scoreboard(score):
    """Funkcja podmieniająca nowy wynik"""
    scores = []
    i = 1
    for item in info:
        scr = item.replace(f'{i}. ', '')
        scr = eval(scr)
        scores.append(scr)
        i += 1
    scores.append(score)
    new_scores = sorted(scores, reverse=True)
    new_scores = new_scores[:10]
    places = ''
    for j in range(len(new_scores)):
        place = f'{j+1}. {new_scores[j]}\n'
        places += place
    return places

def update_scoreboard(score):
    """Funkcja wstawiająca nowy wynik do pliku i zmiennej globalnej"""
    board = scoreboard(score)
    with open('high_scores.txt', 'w') as file:
        file.write(board)
    global info
    with open('high_scores.txt', 'r') as file:
        info = file.read().rstrip('\n')
        info = list(info.split('\n'))

######################
# Klasy
######################
class Player(pygame.sprite.Sprite):
    """Klasa gracza"""
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load(ship).convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.copysurf = pygame.image.load(ship).convert()
        self.copysurf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rect.inflate_ip(-10, -10)
        self.rect.centerx = WIDTH/2
        self.rect.top = 200
        self.xvel = 0
        self.yvel = 0
        self.xratio = 0
        self.yratio = 1
        self.inv_time = pygame.time.get_ticks()
        self.collision = False
        self.hearts = 3

    def rotate(self, angle):
        """Metoda odpowiadająca za obrót gracza"""
        x = self.xratio
        y = self.yratio
        self.xratio = x * np.cos(angle * np.pi/180) - y * np.sin(angle * np.pi/180)
        self.yratio = x * np.sin(angle * np.pi/180) + y * np.cos(angle * np.pi/180)

    def update(self):
        """Metoda odpowiadająca za uaktualnienie pozycji i stanu gracza"""
        self.rect.move_ip((self.xvel, self.yvel))

        # Topologiczna powierzchnia "donuta"
        self.rect.left = self.rect.left % (WIDTH+20)
        self.rect.right = self.rect.right % (WIDTH+20)
        self.rect.top = self. rect.top % (HEIGHT+20)
        self.rect.bottom = self.rect.bottom % (HEIGHT+20)

        for i in range(8):
            if self.collision and pygame.time.get_ticks() - self.inv_time > (i+1)*300:
                if i % 2 == 1:
                    if accelerate:
                        self.surf = pygame.image.load(ship_flame).convert()
                        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
                        self.copysurf = pygame.image.load(ship_flame).convert()
                        self.copysurf.set_colorkey((255, 255, 255), RLEACCEL)
                        self.surf = pygame.transform.rotate(self.copysurf, angle)
                    else:
                        self.surf = pygame.image.load(ship).convert()
                        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
                        self.copysurf = pygame.image.load(ship).convert()
                        self.copysurf.set_colorkey((255, 255, 255), RLEACCEL)
                        self.surf = pygame.transform.rotate(self.copysurf, angle)
                    if i == 7:
                        self.collision = False
                else:
                    self.surf = pygame.Surface((25, 25))
                    self.surf.fill((0, 0, 0))
                    self.surf.set_colorkey((0, 0, 0))
                    self.copysurf = pygame.Surface((25, 25))
                    self.copysurf.fill((0, 0, 0))
                    self.copysurf.set_colorkey((0, 0, 0))


    def shoot(self, angle):
        """Metoda odpowiadająca za strzelanie pociskami"""
        bullet = Bullet(self.rect.centerx, self.rect.centery, angle)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def invincibility_frames(self):
        """Metoda odpowiadająca za zrobienie garcza niezniszczalnym na jakiś czas"""
        self.collision = True
        self.rect.centerx = WIDTH/2
        self.rect.top = 200
        self.xvel = 0
        self.yvel = 0
        self.xratio = 0
        self.yratio = 1
        self.inv_time = pygame.time.get_ticks()


class Bullet(pygame.sprite.Sprite):
    """Klasa pocisków"""
    def __init__(self, x, y, angle):
        super(Bullet, self).__init__()
        self.surf = pygame.image.load("laserBullet.png").convert()
        self.surf = pygame.transform.rotate(self.surf, -angle)
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.xvel = 10 * np.sin(angle * np.pi/180)
        self.yvel = -10 * np.cos(angle * np.pi/180)

    def update(self):
        """Metoda odpowiadająca za uaktulnienie pozycji pociskó"""
        self.rect.x += self.xvel
        self.rect.y += self.yvel

        if self.rect.left > WIDTH or self.rect.left < 0 or self.rect.top < 0 or self.rect.top > HEIGHT:
            self.kill()

class Rock(pygame.sprite.Sprite):
    """Klasas asteroid"""
    def __init__(self, x, y, angle):
        super(Rock, self).__init__()
        self.surf = pygame.image.load("asteroid.png").convert()
        self.surf = pygame.transform.rotate(self.surf, random.randint(1, 360))
        self.size = random.randint(50, 100)
        self.surf = pygame.transform.scale(self.surf, [self.size, self.size])
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rect.inflate_ip(-np.sqrt(self.size), -np.sqrt(self.size))
        self.rect.centerx = x
        self.rect.centery = y
        self.xvel = random.randint(2, 6) * np.sin(angle * np.pi/180)
        self.yvel = -random.randint(2, 6) * np.cos(angle * np.pi/180)
        self.time = pygame.time.get_ticks()
        self.exploded = False

    def update(self):
        """Metoda odpowiadająca za uaktulanienie pozycji i stanu asteroid"""
        self.rect.x += self.xvel
        self.rect.y += self.yvel

        if self.rect.left > WIDTH + 300 or self.rect.left < -300 or self.rect.top < -300 or self.rect.top > HEIGHT + 300:
            self.kill()

        for i in range(6):
            if self.exploded and pygame.time.get_ticks() - self.time > i * 75:
                self.surf = pygame.image.load(f"explosion{i+1}.png").convert()
                self.surf = pygame.transform.scale(self.surf, [self.size, self.size])
                self.surf.set_colorkey((0, 0, 0), RLEACCEL)
                if i == 5:
                    self.kill()

    def explotion(self):
        """Metoda odpowiadająca za eksplozje asteroidy"""
        self.exploded = True
        self.time = pygame.time.get_ticks()
        self.xvel = 0
        self.yvel = 0

class Button(pygame.sprite.Sprite):
    """Klasa przycisków"""
    def __init__(self, x, y):
        super(Button, self).__init__()
        self.surf = pygame.image.load("Button.png").convert()
        self.rect = self.surf.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        """Metoda odpowiadająca za zmiane stanu przycisków"""
        self.surf = pygame.transform.scale(self.surf, [249, 47])
        self.rect.topleft = (self.rect.topleft[0] - 2, self.rect.topleft[1] - 2)

## Własny event

ADDROCK = pygame.USEREVENT + 1
pygame.time.set_timer(ADDROCK, 700)

######################
# Pętla zdarzeń
######################

## Zegar
clock = pygame.time.Clock()

## Zmienne globalne potrzebne do pętli zdarzeń
running = True
menu = True
play = False
high = False
opt = False
inst = False
about = False
game_over = False
menu_music = True
play_music = False
play2_music = False

while running:

    if menu_music:
        pygame.mixer.music.stop()
        pygame.mixer.music.load("MalreDeszik_-_Blowdy_Life.mp3")
        pygame.mixer.music.play(loops=-1)

    # Ekran menu
    if menu:

        menu_music = False

        play_btn = Button(320, 200)
        screen.blit(bg, [0, 0])
        screen.blit(play_btn.surf, play_btn.rect)
        draw_text("PLAY", 400, 197, 30, screen)

        high_btn = Button(320, 255)
        screen.blit(high_btn.surf, high_btn.rect)
        draw_text("HIGH SCORES", 338, 252, 30, screen)

        opt_btn = Button(320, 310)
        screen.blit(opt_btn.surf, opt_btn.rect)
        draw_text("OPTIONS", 370, 307, 30, screen)

        inst_btn = Button(320, 365)
        screen.blit(inst_btn.surf, inst_btn.rect)
        draw_text("INSTRUCTION", 335, 362, 30, screen)

        about_btn = Button(320, 420)
        screen.blit(about_btn.surf, about_btn.rect)
        draw_text("ABOUT", 390, 417, 30, screen)

        exit_btn = Button(620, 420)
        screen.blit(exit_btn.surf, exit_btn.rect)
        draw_text("EXIT", 710, 417, 30, screen)

        draw_text("ASTEROCKS", 190, 30, 80, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if pos[0] >= 265 and pos[0] <= 600 and pos[1] >= 200 and pos[1] <= 243:
                        click_sound.play()

                        player = Player()

                        all_sprites = pygame.sprite.Group()
                        all_sprites.add(player)

                        bullets = pygame.sprite.Group()
                        rocks = pygame.sprite.Group()

                        score_time = pygame.time.get_ticks()
                        rockx, rocky = 0, 0
                        shoot_time = pygame.time.get_ticks()
                        score = 0
                        single = 0
                        angle = 0
                        new_best = False
                        rotate_left = False
                        rotate_right = False
                        accelerate = False
                        menu = False
                        play = True
                        high = False
                        play_music = True
                        pygame.mouse.set_visible(False)
                    if pos[0] >= 320 and pos[0] <= 565 and pos[1] >= 255 and pos[1] <= 298:
                        click_sound.play()
                        menu = False
                        high = True
                        play = False
                    if pos[0] >= 320 and pos[0] <= 565 and pos[1] >= 310 and pos[1] <= 353:
                        click_sound.play()
                        menu = False
                        opt = True
                    if pos[0] >= 320 and pos[0] <= 565 and pos[1] >= 365 and pos[1] <= 408:
                        click_sound.play()
                        menu = False
                        inst = True
                    if pos[0] >= 320 and pos[0] <= 565 and pos[1] >= 420 and pos[1] <= 463:
                        click_sound.play()
                        menu = False
                        about = True
                    if pos[0] >= 620 and pos[0] <= 865 and pos[1] >= 420 and pos[1] <= 463:
                        click_sound.play()
                        running = False

        pos = pygame.mouse.get_pos()
        if pos[0] >= 320 and pos[0] <= 565 and pos[1] >= 200 and pos[1] <= 243:
            play_btn.update()
            screen.blit(play_btn.surf, play_btn.rect)
            draw_text("PLAY", 398, 195, 32, screen)
        if pos[0] >= 320 and pos[0] <= 565 and pos[1] >= 255 and pos[1] <= 298:
            high_btn.update()
            screen.blit(high_btn.surf, high_btn.rect)
            draw_text("HIGH SCORES", 335, 250, 32, screen)
        if pos[0] >= 320 and pos[0] <= 565 and pos[1] >= 310 and pos[1] <= 353:
            opt_btn.update()
            screen.blit(opt_btn.surf, opt_btn.rect)
            draw_text("OPTIONS", 368, 305, 32, screen)
        if pos[0] >= 320 and pos[0] <= 565 and pos[1] >= 365 and pos[1] <= 408:
            inst_btn.update()
            screen.blit(inst_btn.surf, inst_btn.rect)
            draw_text("INSTRUCTION", 332, 360, 32, screen)
        if pos[0] >= 320 and pos[0] <= 565 and pos[1] >= 420 and pos[1] <= 463:
            about_btn.update()
            screen.blit(about_btn.surf, about_btn.rect)
            draw_text("ABOUT", 388, 415, 32, screen)
        if pos[0] >= 620 and pos[0] <= 865 and pos[1] >= 420 and pos[1] <= 463:
            exit_btn.update()
            screen.blit(exit_btn.surf, exit_btn.rect)
            draw_text("EXIT", 708, 415, 32, screen)

        pygame.display.flip()

    if play_music:
        pygame.mixer.music.stop()
        pygame.mixer.music.load("MalreDeszik_-_Neuronal_House.mp3")
        pygame.mixer.music.play(loops=-1)

    # Ekran about
    if about:
        screen.blit(bg, [0, 0])
        draw_text("ABOUT", 330, 40, 70, screen)

        draw_text("My name is Aleksander Rzyhak. I'm a student at Wroclaw University of Science and Technology.", 60, 200, 16, screen)
        draw_text("This game was HEAVILY inspired by 1979 arcade game called 'Asteroids'.", 150, 240, 16, screen)
        draw_text("All graphics and sounds used have been taken from page opengameart.com.", 140, 270, 16, screen)
        draw_text("Music by MalreDeszik (c) copyright 2021 Licensed under a Creative Commons Attribution Noncommercial  (3.0) license.",
                  58, 305, 13, screen)
        draw_text("http://dig.ccmixter.org/files/MalreDeszik/64476", 280, 330, 13, screen)

        back_btn = Button(40, 420)
        screen.blit(back_btn.surf, back_btn.rect)
        draw_text("BACK", 120, 417, 30, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
                        click_sound.play()
                        menu = True
                        about = False

        pos = pygame.mouse.get_pos()
        if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
            back_btn.update()
            screen.blit(back_btn.surf, back_btn.rect)
            draw_text("BACK", 118, 415, 32, screen)

        pygame.display.flip()

    # Ekran instrucji
    if inst:
        screen.blit(bg, [0, 0])
        draw_text("INSTRUCTION", 200, 40, 70, screen)

        screen.blit(arrowkey, [500, 200])
        draw_text("^", 506, 199, 30, screen, color=(0, 0, 0))
        draw_text("- accelerate", 540, 200, 20, screen)

        screen.blit(arrowkey, [500, 250])
        draw_text(">", 510, 245, 25, screen, color=(0, 0, 0))
        draw_text("- rotate clockwise", 540, 250, 20, screen)

        screen.blit(arrowkey, [500, 300])
        draw_text("<", 509, 295, 25, screen, color=(0, 0, 0))
        draw_text("- rotate counterclockwise", 540, 300, 20, screen)

        screen.blit(spacebar, [430, 350])
        draw_text("space", 448, 345, 22, screen, color=(0, 0, 0))
        draw_text("- shoot", 540, 350, 20, screen)

        back_btn = Button(40, 420)
        screen.blit(back_btn.surf, back_btn.rect)
        draw_text("BACK", 120, 417, 30, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
                        click_sound.play()
                        menu = True
                        inst = False

        pos = pygame.mouse.get_pos()
        if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
            back_btn.update()
            screen.blit(back_btn.surf, back_btn.rect)
            draw_text("BACK", 118, 415, 32, screen)

        pygame.display.flip()

    # Ekran opcji
    if opt:

        screen.blit(bg, [0, 0])
        draw_text("OPTIONS", 306, 40, 65, screen)

        draw_text("<", xchosen, ychosen, 40, screen)

        ship1_btn = Button(180, 184)
        screen.blit(ship1_btn.surf, ship1_btn.rect)
        draw_text("Venus IV", 236, 182, 30, screen)
        screen.blit(ship1, [500, 170])

        ship2_btn = Button(180, 254)
        screen.blit(ship2_btn.surf, ship2_btn.rect)
        draw_text("Saturn III", 233, 252, 30, screen)
        screen.blit(ship2, [502, 240])

        ship3_btn = Button(180, 324)
        screen.blit(ship3_btn.surf, ship3_btn.rect)
        draw_text("Urania IX", 233, 322, 30, screen)
        screen.blit(ship3, [502, 310])

        back_btn = Button(40, 420)
        screen.blit(back_btn.surf, back_btn.rect)
        draw_text("BACK", 120, 417, 30, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
                        click_sound.play()
                        menu = True
                        opt = False
                    if pos[0] >= 180 and pos[0] <= 425 and pos[1] >= 184 and pos[1] <= 227:
                        click_sound.play()
                        set_ship("ship1")
                        chosen(580, 170)
                    if pos[0] >= 180 and pos[0] <= 425 and pos[1] >= 254 and pos[1] <= 297:
                        click_sound.play()
                        set_ship("ship2")
                        chosen(580, 243)
                    if pos[0] >= 180 and pos[0] <= 425 and pos[1] >= 324 and pos[1] <= 367:
                        click_sound.play()
                        set_ship("ship3")
                        chosen(580, 312)

        pos = pygame.mouse.get_pos()
        if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
            back_btn.update()
            screen.blit(back_btn.surf, back_btn.rect)
            draw_text("BACK", 118, 415, 32, screen)
        if pos[0] >= 180 and pos[0] <= 425 and pos[1] >= 184 and pos[1] <= 227:
            ship1_btn.update()
            screen.blit(ship1_btn.surf, ship1_btn.rect)
            draw_text("Venus IV", 231, 180, 32, screen)
        if pos[0] >= 180 and pos[0] <= 425 and pos[1] >= 254 and pos[1] <= 297:
            ship2_btn.update()
            screen.blit(ship2_btn.surf, ship2_btn.rect)
            draw_text("Saturn III", 231, 252, 32, screen)
        if pos[0] >= 180 and pos[0] <= 425 and pos[1] >= 324 and pos[1] <= 367:
            ship3_btn.update()
            screen.blit(ship3_btn.surf, ship3_btn.rect)
            draw_text("Urania IX", 231, 322, 32, screen)

        pygame.display.flip()

    # Ekran z najlepszymi wynikami
    if high:

        screen.blit(bg, [0, 0])
        draw_text("HIGH SCORES", 240, 30, 65, screen)

        for i in range(len(info)):
            draw_text(f"{info[i]}", 430, 130+28*i, 20, screen)

        back_btn = Button(40, 420)
        screen.blit(back_btn.surf, back_btn.rect)
        draw_text("BACK", 120, 417, 30, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
                        click_sound.play()
                        menu = True
                        high = False

        pos = pygame.mouse.get_pos()
        if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
            back_btn.update()
            screen.blit(back_btn.surf, back_btn.rect)
            draw_text("BACK", 118, 415, 32, screen)

        pygame.display.flip()

    # Ekran game over
    if game_over:

        menu_music = False

        screen.blit(bg, [0, 0])
        draw_text("GAME OVER", 245, 30, 65, screen)

        if new_best:
            draw_text("New high score!!!", 290, 140, 35, screen)

        draw_text("Score: ", 380-9*len(str(score)), 220, 30, screen)
        draw_text(f"{score}", 490-9*len(str(score)), 220, 30, screen)

        back_btn = Button(40, 420)
        screen.blit(back_btn.surf, back_btn.rect)
        draw_text("MENU", 120, 417, 30, screen)

        play_btn = Button(315, 300)
        screen.blit(play_btn.surf, play_btn.rect)
        draw_text("PLAY AGAIN", 340, 297, 30, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
                        click_sound.play()
                        menu = True
                        game_over = False
                    if pos[0] >= 320 and pos[0] <= 564 and pos[1] >= 300 and pos[1] <= 343:
                        click_sound.play()
                        player = Player()

                        all_sprites = pygame.sprite.Group()
                        all_sprites.add(player)

                        bullets = pygame.sprite.Group()
                        rocks = pygame.sprite.Group()

                        score_time = pygame.time.get_ticks()
                        rockx, rocky = 0, 0
                        shoot_time = pygame.time.get_ticks()
                        score = 0
                        single = 0
                        angle = 0
                        new_best = False
                        rotate_left = False
                        rotate_right = False
                        accelerate = False
                        game_over = False
                        play = True
                        play2_music = True
                        pygame.mouse.set_visible(False)

        pos = pygame.mouse.get_pos()
        if pos[0] >= 40 and pos[0] <= 284 and pos[1] >= 420 and pos[1] <= 463:
            back_btn.update()
            screen.blit(back_btn.surf, back_btn.rect)
            draw_text("MENU", 118, 415, 32, screen)
        if pos[0] >= 320 and pos[0] <= 564 and pos[1] >= 300 and pos[1] <= 343:
            play_btn.update()
            screen.blit(play_btn.surf, play_btn.rect)
            draw_text("PLAY AGAIN", 338, 295, 32, screen)

        pygame.display.flip()

    if play2_music:
        pygame.mixer.music.stop()
        pygame.mixer.music.load("MalreDeszik_-_Neuronal_House.mp3")
        pygame.mixer.music.play(loops=-1)

    # Ekran gry
    if play:

        play2_music = False
        play_music = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_LEFT:
                    rotate_left = True
                elif event.key == K_RIGHT:
                    rotate_right = True
                elif event.key == K_UP:
                    engine_sound.play()
                    accelerate = True
                elif event.key == K_SPACE and pygame.time.get_ticks() - shoot_time > 200:
                    shot_sound.play()
                    player.shoot(-angle)
                    shoot_time = pygame.time.get_ticks()
            elif event.type == pygame.KEYUP:
                if event.key == K_LEFT:
                    rotate_left = False
                elif event.key == K_RIGHT:
                    rotate_right = False
                elif event.key == K_UP:
                    engine_sound.stop()
                    accelerate = False
            elif event.type == ADDROCK:
                rock_angle = 0
                side = random.choice([1, 2, 3, 4])
                if side == 1:
                    x = -random.randint(50, 100)
                    y = HEIGHT/2 + random.randint(-100, 100)
                    rock_angle = 90 + random.randint(-30, 30)
                if side == 2:
                    x = WIDTH/2 + random.randint(-200, 200)
                    y = -random.randint(50, 100)
                    rock_angle = 180 + random.randint(-30, 30)
                if side == 3:
                    x = WIDTH + random.randint(50, 100)
                    y = HEIGHT/2 + random.randint(-100, 100)
                    rock_angle = 270 + random.randint(-30, 30)
                if side == 4:
                    x = WIDTH/2 + random.randint(-200, 200)
                    y = HEIGHT + random.randint(50, 100)
                    rock_angle = random.randint(-30, 30)
                rock = Rock(x, y, rock_angle)
                rocks.add(rock)
                all_sprites.add(rock)

        player.surf = pygame.image.load(ship).convert()
        player.copysurf = pygame.image.load(ship).convert()
        player.surf = pygame.transform.rotate(player.copysurf, angle)
        player.surf.set_colorkey((255, 255, 255), RLEACCEL)
        player.copysurf.set_colorkey((255, 255, 255), RLEACCEL)
        if rotate_left:
            player.rotate(-4)
            angle += 4
            player.surf = pygame.transform.rotate(player.copysurf, angle)
        if rotate_right:
            player.rotate(4)
            angle -= 4
            player.surf = pygame.transform.rotate(player.copysurf, angle)
        if accelerate:
            player.xvel -= player.xratio * 0.5
            player.yvel -= player.yratio * 0.5
            player.surf = pygame.image.load(ship_flame).convert()
            player.copysurf = pygame.image.load(ship_flame).convert()
            player.surf = pygame.transform.rotate(player.copysurf, angle)
            player.surf.set_colorkey((255, 255, 255), RLEACCEL)
            player.copysurf.set_colorkey((255, 255, 255), RLEACCEL)

        player.update()
        bullets.update()
        rocks.update()

        screen.blit(bg, [0, 0])
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        hits = pygame.sprite.spritecollide(player, rocks, False)
        for rock in hits:
            if not player.collision and not rock.exploded:
                explotion_sound.play()
                explotion(player.rect.left, player.rect.top, 50)
                player.invincibility_frames()
                angle = 0
                player.hearts -= 1

        hits = pygame.sprite.groupcollide(rocks, bullets, False, True)
        for rock in hits:
            if not rock.exploded:
                xvel, yvel = rock.xvel, rock.yvel
                rock_sound.play()
                rock.explotion()
                score += 100 - rock.size + 5*int(np.sqrt(xvel**2 + yvel**2))
                single = 100 - rock.size + 5*int(np.sqrt(xvel**2 + yvel**2))
                rockx, rocky = rock.rect.left, rock.rect.top
                score_time = pygame.time.get_ticks()
        draw_text(f'Score: {score}', 5, HEIGHT-50, 30, screen)

        draw_lives(10, 10, player.hearts)

        if pygame.time.get_ticks() - score_time < 300 and single != 0:
            draw_text(f'+{single}', rockx, rocky, 20, screen)

        pygame.display.flip()

        if player.hearts == 0:
            engine_sound.stop()
            update_scoreboard(score)
            game_over = True
            if score == eval(info[0][3:]):
                new_best = True
            play = False
            pygame.mouse.set_visible(True)
            menu_music = True

    clock.tick(30)

pygame.quit()