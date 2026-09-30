import math
import random
import pygame

WIDTH = 960
HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (80, 180, 100)
YELLOW = (235, 210, 70)
RED = (220, 70, 50)
BLUE = (70, 120, 220)
BROWN = (135, 95, 55)


def draw_grass(screen):
    screen.fill(GREEN)
    for y in range(0, HEIGHT, 30):
        pygame.draw.rect(screen, (90, 160, 90), (0, y, WIDTH, 15))


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (15, 15), 15)
        pygame.draw.rect(self.image, WHITE, (10, 10, 10, 10))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = 260

    def update(self, keys, dt):
        move_x = 0
        move_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1

        if move_x != 0 or move_y != 0:
            length = math.hypot(move_x, move_y)
            move_x /= length
            move_y /= length
            self.rect.x += move_x * self.speed * dt
            self.rect.y += move_y * self.speed * dt

        self.rect.x = clamp(self.rect.x, 0, WIDTH - self.rect.width)
        self.rect.y = clamp(self.rect.y, 0, HEIGHT - self.rect.height)


class Chicken(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, YELLOW, (2, 2, 18, 16))
        pygame.draw.circle(self.image, BLACK, (8, 9), 2)
        pygame.draw.circle(self.image, BLACK, (16, 9), 2)
        pygame.draw.arc(self.image, BLACK, (8, 12, 8, 5), 3.14, 6.28, 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.direction = random.uniform(0, math.tau)
        self.wander_timer = random.uniform(0.5, 2.5)
        self.bob = random.uniform(0, math.tau)

    def reset(self):
        self.rect.x = random.randint(20, WIDTH - 50)
        self.rect.y = random.randint(20, HEIGHT - 50)
        self.direction = random.uniform(0, math.tau)
        self.wander_timer = random.uniform(0.5, 2.5)

    def update(self, player, dt):
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = math.hypot(dx, dy)

        if distance < 200:
            angle = math.atan2(dy, dx) + math.pi
            self.direction = angle
            move_x = math.cos(self.direction) * self.speed * 1.5
            move_y = math.sin(self.direction) * self.speed * 1.5
        else:
            self.wander_timer -= dt
            if self.wander_timer <= 0:
                self.direction = random.uniform(0, math.tau)
                self.wander_timer = random.uniform(0.8, 2.0)
            move_x = math.cos(self.direction) * self.speed
            move_y = math.sin(self.direction) * self.speed

        new_x = self.rect.x + move_x * dt
        new_y = self.rect.y + move_y * dt

        if new_x < 0 or new_x > WIDTH - self.rect.width:
            self.direction = math.pi - self.direction
        if new_y < 0 or new_y > HEIGHT - self.rect.height:
            self.direction = -self.direction

        self.rect.x += move_x * dt
        self.rect.y += move_y * dt
        self.rect.x = clamp(self.rect.x, 0, WIDTH - self.rect.width)
        self.rect.y = clamp(self.rect.y, 0, HEIGHT - self.rect.height)


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chasing Chicken")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    chickens = pygame.sprite.Group()
    for _ in range(7):
        chicken = Chicken(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), random.uniform(45, 80))
        chickens.add(chicken)
        all_sprites.add(chicken)

    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)
    score = 0
    lives = 3
    time_left = 45.0
    state = "playing"

    while True:
        dt = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and state == "game_over":
                return

        if state == "playing":
            player.update(keys, dt)
            time_left -= dt

            if time_left <= 0:
                state = "game_over"

            for chicken in chickens:
                chicken.update(player, dt)

            collisions = pygame.sprite.spritecollide(player, chickens, False)
            if collisions:
                lives -= 1
                for chicken in collisions:
                    chicken.reset()
                if lives <= 0:
                    state = "game_over"

        draw_grass(screen)

        all_sprites.draw(screen)

        score_text = font.render(f"Score: {score}", True, BLACK)
        lives_text = font.render(f"Lives: {lives}", True, BLACK)
        time_text = font.render(f"Time: {max(0, int(time_left))}", True, BLACK)
        screen.blit(score_text, (20, 20))
        screen.blit(lives_text, (20, 55))
        screen.blit(time_text, (WIDTH - 120, 20))

        if state == "playing":
            for chicken in chickens:
                if chicken.rect.colliderect(player.rect):
                    score += 1
                    chicken.reset()

        if state == "game_over":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            final_text = big_font.render("Game Over", True, WHITE)
            screen.blit(
                final_text,
                (WIDTH // 2 - final_text.get_width() // 2, HEIGHT // 2 - 50),
            )

            result_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 + 20))

            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))

        pygame.display.flip()


if __name__ == "__main__":
    while True:
        run_game()
