
import os
import pygame
import time
import sys

# Inicialização
pygame.init()
pygame.mixer.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Temple of Shadows")
clock = pygame.time.Clock()
FPS = 60

# Caminhos
ASSETS_DIR = os.path.join("assets")
IMG_DIR = os.path.join(ASSETS_DIR, "img")
SOUND_DIR = os.path.join(ASSETS_DIR, "sound")

# Música
MENU_MUSIC = os.path.join(SOUND_DIR, "bamboo-forest-level.wav")
GAME_MUSIC = os.path.join(SOUND_DIR, "royalty-free-rock-n-roll.wav")

def play_music(path, loop=-1):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(loop)



# Fonte
font = pygame.font.SysFont("Arial", 32)



# Carregar imagem de fundo
background = pygame.image.load(os.path.join(IMG_DIR, "background 1.jpg")).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Carregar imagem do player
player_idle = pygame.image.load(os.path.join(IMG_DIR, "player", "idle.jpg")).convert_alpha()
player_img = pygame.transform.scale(player_idle, (50, 50))



# --- CLASSES ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False

    def update(self, keys):
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -5
        if keys[pygame.K_RIGHT]:
            dx = 5
        self.rect.x += dx

        # Gravidade
        self.vel_y += 1
        if self.vel_y > 15:
            self.vel_y = 15
        self.rect.y += self.vel_y

        # Chão
        if self.rect.bottom >= HEIGHT - 20:
            self.rect.bottom = HEIGHT - 20
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.vel_y = -20


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range=200):
        super().__init__()
        # Carregar sprites do inimigo
        self.images = [
            pygame.image.load(os.path.join(IMG_DIR, "enemy", "walk1.png")).convert_alpha(),
            pygame.image.load(os.path.join(IMG_DIR, "enemy", "walk2.png")).convert_alpha()
        ]
        self.images = [pygame.transform.scale(img, (60, 60)) for img in self.images]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.start_x = x
        self.move_range = move_range
        self.speed = 2
        self.animation_timer = 0

    def update(self, keys=None):
        # Movimento
        self.rect.x += self.speed
        if abs(self.rect.x - self.start_x) > self.move_range:
            self.speed *= -1

        # Animação
        self.animation_timer += 1
        if self.animation_timer >= 20:
            self.animation_timer = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]




# --- ESTADOS ---
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
WIN = "win"

def draw_text(text, size, x, y, color=(255,255,255)):
    font_tmp = pygame.font.SysFont("Arial", size, bold=True)
    surface = font_tmp.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)

# --- FUNÇÕES DE TELA ---
def menu():
    play_music(MENU_MUSIC)
    selection = 1
    while True:
        screen.blit(background, (0, 0))
        draw_text("TEMPLE OF SHADOWS", 50, WIDTH//2, HEIGHT//4, (255, 255, 0))
        draw_text("Select Level:", 36, WIDTH//2, HEIGHT//2 - 60)

        color1 = (0, 255, 0) if selection == 1 else (255, 255, 255)
        color2 = (0, 255, 0) if selection == 2 else (255, 255, 255)

        draw_text("Level 1"  , 32, WIDTH//2, HEIGHT//2, color1)
        draw_text("Level 2"  , 32, WIDTH//2, HEIGHT//2 + 40, color2)

        draw_text("Press ENTER to Start | ESC to Quit", 24, WIDTH//2, HEIGHT - 80)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selection = 1
                if event.key == pygame.K_DOWN:
                    selection = 2
                if event.key == pygame.K_RETURN:
                    return PLAYING, selection
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

def game(level):
    play_music(GAME_MUSIC)
    if level == 1:
        player = Player(100, HEIGHT - 150)
        enemy1 = Enemy(300, HEIGHT - 80, 125)
        enemy2 = Enemy(500, HEIGHT - 80, 150)
        time_limit = 30
    else:  # Level 2
        player = Player(100, HEIGHT - 150)
        enemy1 = Enemy(300, HEIGHT - 80, 125)
        enemy2 = Enemy(500, HEIGHT - 80, 150)
        enemy3 = Enemy(650, HEIGHT - 80, 165)
        time_limit = 30

    all_sprites = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()

    if level == 1:
        all_sprites.add(enemy1,enemy2)
        enemies.add(enemy1, enemy2)
    else:
        all_sprites.add(enemy1, enemy2, enemy3)
        enemies.add(enemy1, enemy2, enemy3)

    start_time = time.time()

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.jump()

        all_sprites.update(keys)

        # Colisões
        if pygame.sprite.spritecollide(player, enemies,dokill=False):
            return GAME_OVER, level, time.time() - start_time


        # Tempo limite
        elapsed = time.time() - start_time
        if elapsed > time_limit:
            return WIN, level, elapsed

        # Desenhar cronometro
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        draw_text(f"Time: {elapsed:.2f}s / {time_limit}", 24, 120, 30, (255,255,255))
        pygame.display.flip()

def game_over_screen():
    play_music(MENU_MUSIC)
    while True:
        screen.blit(background, (0, 0))
        draw_text("GAME OVER", 50, WIDTH//2, HEIGHT//3, (255, 0, 0))
        draw_text("Press ENTER to Return to Menu", 32, WIDTH//2, HEIGHT//2, (255, 255, 255))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return MENU

def win_screen(level, time_spent):
    play_music(MENU_MUSIC)
    while True:
        screen.blit(background, (0, 0))
        draw_text("YOU WIN!", 50, WIDTH//2, HEIGHT//3, (0, 255, 0))
        draw_text("Press ENTER to Return to Menu", 32, WIDTH//2, HEIGHT//2 + 50, (255, 255, 255))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return MENU

# --- LOOP PRINCIPAL ---
state = MENU
level = 1
while True:
    if state == MENU:
        state,level = menu()
    elif state == PLAYING:
        state, level, elapsed = game(level)
        if state == GAME_OVER:
            state = game_over_screen()
        elif state == WIN:
            state = win_screen(level, elapsed)
