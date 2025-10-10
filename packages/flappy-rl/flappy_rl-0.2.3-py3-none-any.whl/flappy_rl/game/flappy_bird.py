import pygame
import random
import math
import os
try:
    import pkg_resources
    PKG_RESOURCES_AVAILABLE = True
except ImportError:
    PKG_RESOURCES_AVAILABLE = False

def get_asset_path(asset_name):
    """
    Gets the absolute path to an asset, handling both installed package
    and local script execution scenarios.
    """
    # If running as an installed package, use pkg_resources
    if PKG_RESOURCES_AVAILABLE and 'flappy_rl.egg-info' in str(os.path.abspath(__file__)):
        try:
            return pkg_resources.resource_filename('flappy_rl', f'assets/{asset_name}')
        except Exception:
            pass # Fallback to file-based path

    # If running from source (developer mode), use relative paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate from src/flappy_rl/game -> src/flappy_rl -> src -> root -> assets
    asset_dir = os.path.join(base_dir, '..', 'assets')
    return os.path.join(asset_dir, asset_name)

class FlappyBirdEnv:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1200, 600
        self.WIN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Flappy Bird RL")

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GOLD = (255, 215, 0)

        background_path = get_asset_path('image (1).png')
        bird_image_path = get_asset_path('futuristic-robotic-hummingbird_23-2151443897-Photoroom.png')

        self.BACKGROUND = pygame.image.load(background_path).convert()
        self.BACKGROUND = pygame.transform.scale(self.BACKGROUND, (self.WIDTH, self.HEIGHT))
        self.BIRD_IMAGE = pygame.image.load(bird_image_path).convert_alpha()
        self.BIRD_IMAGE = pygame.transform.scale(self.BIRD_IMAGE, (80, 50))

        self.glow_radius = 30
        self.GLOW_SURFACE = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.GLOW_SURFACE, (0, 255, 255, 100), (self.glow_radius, self.glow_radius), self.glow_radius)

        self.font = pygame.font.SysFont("helvetica", 30, bold=False)

        self.bird_x = 100
        self.GRAVITY = 0.3
        self.FLAP = -3
        self.PIPE_WIDTH = 100
        self.PIPE_GAP = 150
        self.pipe_speed = 5

        self.glow_alpha = 100
        self.glow_timer = 0

        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.bird_y = 300
        self.bird_vel = 0
        self.pipe_x = self.WIDTH
        self.pipe_height = random.randint(100, 400)
        self.score = 0
        self.glow_timer = 0
        return self._get_state()

    def step(self, action):
        if action == 1:
            self.bird_vel = self.FLAP

        self.bird_vel += self.GRAVITY
        self.bird_y += self.bird_vel

        self.pipe_x -= self.pipe_speed
        reward = 0
        if self.pipe_x < -self.PIPE_WIDTH:
            self.pipe_x = self.WIDTH
            self.pipe_height = random.randint(100, 400)
            self.score += 1
            reward = 20

        bird_rect = pygame.Rect(self.bird_x, self.bird_y, self.BIRD_IMAGE.get_width(), self.BIRD_IMAGE.get_height())
        pipe_top = pygame.Rect(self.pipe_x, 0, self.PIPE_WIDTH, self.pipe_height)
        pipe_bottom = pygame.Rect(self.pipe_x, self.pipe_height + self.PIPE_GAP, self.PIPE_WIDTH, self.HEIGHT)

        if self.bird_y > 550:
            done = True
            reward = -100
            print(f"Died: Hit bottom, bird_y = {self.bird_y}, vel = {self.bird_vel}")
        elif self.bird_y < 0:
            done = True
            reward = -100
            print(f"Died: Hit top, bird_y = {self.bird_y}, vel = {self.bird_vel}")
        elif bird_rect.colliderect(pipe_top):
            done = True
            reward = -100
            print(f"Died: Hit top pipe, bird_y = {self.bird_y}, vel = {self.bird_vel}")
        elif bird_rect.colliderect(pipe_bottom):
            done = True
            reward = -100
            print(f"Died: Hit bottom pipe, bird_y = {self.bird_y}, vel = {self.bird_vel}")
        else:
            done = False

        gap_center = self.pipe_height + self.PIPE_GAP / 2
        height_diff = abs(self.bird_y - gap_center)
        reward += max(0, 2 - height_diff / 50)

        state = self._get_state()
        return state, reward, done

    def render(self):
        self.glow_timer += 0.1
        self.glow_alpha = 100 + 50 * math.sin(self.glow_timer)
        glow_surface = self.GLOW_SURFACE.copy()
        glow_surface.set_alpha(int(self.glow_alpha))

        self.WIN.blit(self.BACKGROUND, (0, 0))
        self.WIN.blit(glow_surface, (self.bird_x + self.BIRD_IMAGE.get_width() // 2 - self.glow_radius, 
                                     self.bird_y + self.BIRD_IMAGE.get_height() // 2 - self.glow_radius))
        render_y = max(0, min(self.bird_y, self.HEIGHT - self.BIRD_IMAGE.get_height()))
        self.WIN.blit(self.BIRD_IMAGE, (self.bird_x, render_y))
        pygame.draw.rect(self.WIN, self.BLACK, (self.pipe_x, 0, self.PIPE_WIDTH, self.pipe_height))
        pygame.draw.rect(self.WIN, self.BLACK, (self.pipe_x, self.pipe_height + self.PIPE_GAP, self.PIPE_WIDTH, self.HEIGHT))

        # Display score at top corner
        score_text = self.font.render(f"Score: {self.score}", True, self.GOLD)
        self.WIN.blit(score_text, (10, 30))

        pygame.display.update()
        self.clock.tick(60)

    def _get_state(self):
        return [self.bird_y, self.pipe_x, self.pipe_height]

    def close(self):
        pygame.quit()

if __name__ == "__main__":
    env = FlappyBirdEnv()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                action = 1
            else:
                action = 0
        state, reward, done = env.step(action)
        env.render()
        if done:
            state = env.reset()
    env.close()