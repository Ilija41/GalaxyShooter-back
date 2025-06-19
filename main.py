import pygame
import os
import threading
import asyncio
import websocket as ws_server  

def start_ws():
    try:
        asyncio.run(ws_server.main())
    except OSError as e:
        if hasattr(e, 'errno') and e.errno == 10048:
            print("⚠️ WS server je već pokrenut na portu 8765, nastavljam...")
        else:
            raise

ws_thread = threading.Thread(target=start_ws, daemon=True)
ws_thread.start()

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("First Game!")

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255,   0,   0)
YELLOW = (255, 255,   0)

BORDER = pygame.Rect(WIDTH//2 - 5, 0, 10, HEIGHT)

HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)

FPS         = 60
VEL         = 5
BULLET_VEL  = 7
MAX_BULLETS = 3
SP_W, SP_H  = 55, 40

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT    = pygame.USEREVENT + 2

Y_IMAGE = pygame.transform.rotate(
    pygame.transform.scale(
        pygame.image.load(os.path.join('Assets','spaceship_yellow.png')),
        (SP_W, SP_H)
    ), 90
)
R_IMAGE = pygame.transform.rotate(
    pygame.transform.scale(
        pygame.image.load(os.path.join('Assets','spaceship_red.png')),
        (SP_W, SP_H)
    ), 270
)
SPACE = pygame.transform.scale(
    pygame.image.load(os.path.join('Assets','space.png')),
    (WIDTH, HEIGHT)
)

def draw_window(red, yellow, r_bullets, y_bullets, r_hp, y_hp):
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)
    r_text = HEALTH_FONT.render(f"Health: {r_hp}", 1, WHITE)
    y_text = HEALTH_FONT.render(f"Health: {y_hp}", 1, WHITE)
    WIN.blit(r_text, (WIDTH - r_text.get_width() - 10, 10))
    WIN.blit(y_text, (10, 10))
    WIN.blit(Y_IMAGE, (yellow.x, yellow.y))
    WIN.blit(R_IMAGE, (red.x, red.y))
    for b in r_bullets: pygame.draw.rect(WIN, RED, b)
    for b in y_bullets: pygame.draw.rect(WIN, YELLOW, b)
    pygame.display.update()

def apply_commands(rect, cmd):
    if cmd["LEFT"] and rect.x - VEL > (0 if rect == yellow else BORDER.x + BORDER.width):
        rect.x -= VEL
    if cmd["RIGHT"] and rect.x + VEL + rect.width < (BORDER.x if rect == yellow else WIDTH):
        rect.x += VEL
    if cmd["UP"] and rect.y - VEL > 0:
        rect.y -= VEL
    if cmd["DOWN"] and rect.y + VEL + rect.height < HEIGHT - 15:
        rect.y += VEL

def handle_bullets(y_bullets, r_bullets, yellow, red):
    for b in y_bullets[:]:
        b.x += BULLET_VEL
        if red.colliderect(b):
            pygame.event.post(pygame.event.Event(RED_HIT))
            y_bullets.remove(b)
        elif b.x > WIDTH:
            y_bullets.remove(b)
    for b in r_bullets[:]:
        b.x -= BULLET_VEL
        if yellow.colliderect(b):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            r_bullets.remove(b)
        elif b.x < 0:
            r_bullets.remove(b)

def draw_winner(text):
    render = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(render, ((WIDTH - render.get_width())//2, (HEIGHT - render.get_height())//2))
    pygame.display.update()
    pygame.time.delay(5000)

def main():
    global yellow, red
    red    = pygame.Rect(700, 300, SP_W, SP_H)
    yellow = pygame.Rect(100, 300, SP_W, SP_H)
    r_bullets, y_bullets = [], []
    r_hp, y_hp = 10, 10

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
                pygame.quit()
            if e.type == RED_HIT:
                r_hp -= 1
            if e.type == YELLOW_HIT:
                y_hp -= 1

        if r_hp <= 0:
            draw_winner("Yellow Wins!")
            break
        if y_hp <= 0:
            draw_winner("Red Wins!")
            break

        apply_commands(yellow, ws_server.commands["yellow"])
        apply_commands(red,    ws_server.commands["red"])

        if ws_server.commands["yellow"]["FIRE"]:
            print("🎯 DEBUG: FIRE == True")

        if ws_server.commands["yellow"]["FIRE"] and len(y_bullets) < MAX_BULLETS:
            print("🟢 DEBUG: spawnujem yellow bullet")
            y_bullets.append(pygame.Rect(
                yellow.x + yellow.width,
                yellow.y + yellow.height//2 - 2,
                10, 5
            ))
            ws_server.commands["yellow"]["FIRE"] = False

        if ws_server.commands["red"]["FIRE"] and len(r_bullets) < MAX_BULLETS:
            print("🟢 DEBUG: spawnujem red bullet")
            r_bullets.append(pygame.Rect(
                red.x,
                red.y + red.height//2 - 2,
                10, 5
            ))
            ws_server.commands["red"]["FIRE"] = False

        handle_bullets(y_bullets, r_bullets, yellow, red)
        draw_window(red, yellow, r_bullets, y_bullets, r_hp, y_hp)

    pygame.quit()

if __name__ == "__main__":
    main()
