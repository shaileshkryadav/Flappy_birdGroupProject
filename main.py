import pygame
import random
import sys

# Configuration
WIDTH, HEIGHT = 500, 650
FPS = 60
GRAVITY = 0.45
FLAP_STRENGTH = -8.5
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQ_MS = 1500
GROUND_HEIGHT = 100
BIRD_X = 80

pygame.init()
pygame.mixer.init()
playSound= pygame.mixer.Sound("pew_pew-dknight556-1379997159.mp3")
gameOver = pygame.mixer.Sound("dun-dun-dun-sound-effect-brass_8nFBccR.mp3")
intoSound = pygame.mixer.Sound("spiderman-meme-song.mp3")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)

ADDPIPE = pygame.USEREVENT + 1
pygame.time.set_timer(ADDPIPE, PIPE_FREQ_MS)

#Load images
background_img = pygame.image.load("background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

bird_img = pygame.image.load("bird.png").convert_alpha()
bird_img = pygame.transform.scale(bird_img, (45, 40))

pipe_img = pygame.image.load("Pipes.png").convert_alpha()
pipe_img = pygame.transform.scale(pipe_img, (70, 500))
pipe_img_flipped = pygame.transform.flip(pipe_img, False, True)  # top pipe

def draw_text(surf, text, size, x, y, color=(255, 255, 255)):
    f = font if size >= 40 else small_font
    img = f.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    surf.blit(img, rect)

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = HEIGHT // 2
        self.vel = 0.0
        self.radius = 16
        self.image = bird_img
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.angle = 0

    def flap(self):
        self.vel = FLAP_STRENGTH

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        self.rect.center = (self.x, self.y)
        self.angle = max(-25, min(90, -self.vel * 3))

    def draw(self, surf):
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surf.blit(rotated, rect.topleft)

    def get_hitbox(self):
        shrink = 6   # reduce rectangle by 6px on each side
        hitbox = self.rect.inflate(-shrink, -shrink)
        return hitbox


class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 70
        self.gap_y = random.randint(120, HEIGHT - GROUND_HEIGHT - 120)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def offscreen(self):
        return self.x + self.width < -10

    def collides_with(self, bird_rect):
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y - PIPE_GAP // 2)
        bottom_rect = pygame.Rect(
            self.x,
            self.gap_y + PIPE_GAP // 2,
            self.width,
            HEIGHT - GROUND_HEIGHT - (self.gap_y + PIPE_GAP // 2)
        )

        top_rect.inflate_ip(-4, -4)
        bottom_rect.inflate_ip(-4, -4)

        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect)


    def draw(self, surf):
        # top pipe (flipped)
        top_height = self.gap_y - PIPE_GAP // 2
        surf.blit(pipe_img_flipped, (self.x, top_height - 500))
        # bottom pipe
        surf.blit(pipe_img, (self.x, self.gap_y + PIPE_GAP // 2))

def reset_game():
    bird = Bird()
    pipes = []
    score = 0
    game_over = False
    started = False
    return bird, pipes, score, game_over, started

def main():
    bird, pipes, score, game_over, started = reset_game()
    ground_x = 0
    intoSound.play()

    # Read high score
    try:
        with open("score.txt", "r") as file:
            line = file.readline().strip()
            HIGESTSCORE = int(line) if line.isdigit() else 0
    except FileNotFoundError:
        HIGESTSCORE = 0
        print("File doesn't exist!!")

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gameOver.stop()
                    intoSound.stop()
                    if not started:
                        started = True
                    if not game_over:
                        bird.flap()
                        playSound.play()
                    else:
                        bird, pipes, score, game_over, started = reset_game()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not started:
                    started = True
                if not game_over:
                    bird.flap()
                else:
                    bird, pipes, score, game_over, started = reset_game()

            if event.type == ADDPIPE and started and not game_over:
                pipes.append(Pipe(WIDTH + 20))

        if started and not game_over:
            bird.update()
            for pipe in pipes:
                pipe.update()
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                if pipe.collides_with(bird.get_hitbox()):
                    game_over = True
            pipes = [p for p in pipes if not p.offscreen()]

            if bird.y + bird.radius >= HEIGHT - GROUND_HEIGHT:
                bird.y = HEIGHT - GROUND_HEIGHT - bird.radius
                game_over = True

            if bird.y - bird.radius <= 0:
                bird.y = bird.radius
                bird.vel = 0

            ground_x = (ground_x - PIPE_SPEED) % WIDTH

        # Draw background
        screen.blit(background_img, (0, 0))
        for pipe in pipes:
            pipe.draw(screen)

        # Draw ground (rectangle instead of image)
        pygame.draw.rect(screen, (222, 184, 135), (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
        for i in range(0, WIDTH // 40 + 2):
            x = (i * 40 + ground_x) % (WIDTH + 40) - 40
            pygame.draw.rect(screen, (205, 133, 63), (x, HEIGHT - 40, 20, 40))

        bird.draw(screen)

        # HUD
        if not started:
            draw_text(screen, "Press SPACE or Click to Start", 28, WIDTH // 2, HEIGHT // 2, (255, 0, 0))
            draw_text(screen, "Flappy Bird", 28, WIDTH // 2, HEIGHT // 2 - 40,(255,0,0))
            draw_text(screen, f"Highest Score: {HIGESTSCORE}", 24, WIDTH // 2, HEIGHT // 2 - 80,(255,0,0))
        else:
            draw_text(screen, str(score), 48, WIDTH // 2, 50, (255, 0, 0))

        if game_over:
            gameOver.play()
            if score > HIGESTSCORE:
                HIGESTSCORE = score
                try:
                    with open("score.txt", "w") as file:
                        file.write(str(HIGESTSCORE))
                except Exception as e:
                    print("Error saving score:", e)

            draw_text(screen, "GAME OVER", 48, WIDTH // 2, HEIGHT // 2 - 30, (255, 50, 50))
            draw_text(screen, f"Score: {score}", 28, WIDTH // 2, HEIGHT // 2 + 10,(255,50,50))
            draw_text(screen, "Press SPACE or Click to Restart", 20, WIDTH // 2, HEIGHT // 2 + 60,(255,50,50))

        pygame.display.flip()

if __name__ == "__main__":
    main()
