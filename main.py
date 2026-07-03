import pygame
import button
import random
from enum import Enum

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 20
COLS = SCREEN_WIDTH // CELL_SIZE
ROWS = SCREEN_HEIGHT // CELL_SIZE
FPS = 60

# Define colors
TEXT_COL = (255, 255, 255)
SNAKE_COL = (0, 255, 0)
BG_COL = (52, 78, 91)

DIFFICULTY_DELAYS = {
    "easy": 160,
    "normal": 80,
    "hard": 40,
}

DIRECTIONS = {
    pygame.K_w: [0, -1],
    pygame.K_s: [0, 1],
    pygame.K_a: [-1, 0],
    pygame.K_d: [1, 0],
}

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake")

# Game variables
clock = pygame.time.Clock()
game_start = False
game_snake = None
global MOVE_DELAY
last_move_time = pygame.time.get_ticks()
screen_state = "main"
score = 0
highscore = 0

class GameState(Enum):
    """Enumeration of possible game states.
    
    Defines the different screens and states the game can be in.
    """
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"

class Assets:
    """Manages all game assets including fonts and images.
    
    This class loads and stores all graphical assets needed for the game,
    including button images for different difficulty levels and game screens,
    as well as the fruit sprite used in gameplay.
    
    Attributes:
        font (pygame.font.Font): The main font used for rendering text (Arial Black, size 40).
        easy_image (pygame.Surface): Button image for easy difficulty mode.
        normal_image (pygame.Surface): Button image for normal difficulty mode.
        hard_image (pygame.Surface): Button image for hard difficulty mode.
        start_image (pygame.Surface): Button image to start the game.
        retry_image (pygame.Surface): Button image to retry after game over.
        fruit_image (pygame.Surface): Scaled sprite for the fruit in the game.
    """

    def __init__(self):
        """Initialize and load all game assets from the images directory."""
        # Load images for buttons
        self.easy_image = pygame.image.load("images/button_easy.png").convert_alpha()
        self.normal_image = pygame.image.load("images/button_normal.png").convert_alpha()
        self.hard_image = pygame.image.load("images/button_hard.png").convert_alpha()
        self.start_image = pygame.image.load("images/button_start.png").convert_alpha()
        self.retry_image = pygame.image.load("images/button_retry.png").convert_alpha()

        fruit_image = pygame.image.load("images/fruit.png").convert_alpha()
        # Scale fruit to fit in one cell
        self.fruit_image = pygame.transform.scale(
            fruit_image,
            (CELL_SIZE, CELL_SIZE)
        )

class Snake:
    """Represents the snake in the game.

    The snake is composed of segments represented by a list of [x, y] coordinates.

    Attributes:
        snake (list): A list of [x, y] coordinates representing the snake's body segments.
        direction (list): The current direction of movement as [dx, dy].
        next_direction (list): The next direction to move in, set by player input.
    """
    
    def __init__(self):
        """Initialize the snake with default starting position and direction.
        
        The snake starts at position (10, 10) with a length of 3 segments,
        facing right (direction [1, 0]).
        """
        self.body = [
            [10, 10],
            [9, 10],
            [8, 10]
        ]
        self.direction = [1, 0]
        self.next_direction = [1, 0]

    @property
    def head(self):
        """Return the current position of the snake's head."""
        return self.body[0]

    def set_direction(self, new_dir: list):
        """Set the snake's next direction of movement.
        
        Prevents the snake from reversing into itself by checking if the new
        direction is not exactly opposite to the current direction.

        Args:
            new_dir (list): A list with the new direction [dx, dy].
        """
        reverse_dir = [
            -self.direction[0], 
            -self.direction[1]
        ]
        if new_dir != reverse_dir:
            self.next_direction = new_dir

    def check_next_move(self):
        """Check and validate the next move. Without moving the snake yet."""
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        next_move = [
            head_x + self.direction[0],
            head_y + self.direction[1]
        ]  

        return next_move
    
    def move(self, new_head: list, grow=True) -> None:
        """Move the snake by adding a new head position."""
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()
    
    @staticmethod
    def check_wall(pos: list) -> bool:
        """Check if the given position is outside the game boundaries.
        
        Args:
            pos (list): A list with the position [x, y] to check.
        """
        x, y = pos
        return (
            x < 0 or
            x >= COLS or
            y < 0 or
            y >= ROWS
        )

    def draw(self, screen):
        """Draw the snake on the game screen.
        
        Each segment of the snake is drawn as a rectangle on the grid.
        
        Args:
            screen (pygame.Surface): The game screen surface to draw the snake on.
        """
        BORDER_COL = (0, 100, 0)

        for x, y in self.body:

            rect = pygame.Rect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            pygame.draw.rect(
                screen,
                BORDER_COL,
                rect,
                border_radius=2
            )

            pygame.draw.rect(
                screen,
                SNAKE_COL,
                rect.inflate(-2, -2),
                border_radius=2
            )

class Fruit:
    """Represents a fruit object that the snake can eat.
    
    The fruit is randomly spawned on the game grid at positions not occupied
    by the snake. When the snake eats the fruit, its length increases.
    
    Attributes:
        pos (list): The [x, y] grid coordinates where the fruit is located.
    """
    
    def __init__(self):
        """Initialize the fruit at the origin position (0, 0).
        
        The actual position is set later by calling spawn_fruit().
        """
        self.pos = [0, 0]

    def spawn_fruit(self, snake_body):
        """Spawn the fruit at a random location not occupied by the snake.
        
        Continuously generates random grid positions until finding one that
        is not part of the snake's body, then places the fruit there.
        
        Args:
            snake_body (list): List of [x, y] coordinates representing the snake's body segments.
        """
        while True:
            candidate_pos = [
                random.randint(0, COLS - 1),
                random.randint(0, ROWS - 1)
            ]
            if candidate_pos not in snake_body:
                self.pos = candidate_pos
                return
    
    def draw(self, screen, image):
        """Draw the fruit sprite on the game screen at its current position.
        
        Converts grid coordinates to pixel coordinates before rendering.
        
        Args:
            screen (pygame.Surface): The game screen surface to draw the fruit on.
            image (pygame.Surface): The fruit sprite image to render.
        """
        pos_x = self.pos[0] * CELL_SIZE
        pos_y = self.pos[1] * CELL_SIZE
        screen.blit(image, (pos_x, pos_y))
            
class Game:
    """Main game class to manage the game loop and state.
    
    This class initializes the game, handles events, updates game objects,
    and manages rendering of the game screen.
    """
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.assets = Assets()
 
        self.state: GameState = GameState.MENU
        self.move_delay: int = DIFFICULTY_DELAYS["normal"]
        self.last_move_time: int = 0
        self.score: int = 0
        self.highscore: int = 0
 
        self.snake: Snake = None
        self.fruit: Fruit = None
 
        self._create_buttons()
    
    def _create_buttons(self):
        """Create button instances for the main menu and game over screens."""
        self.easy_button = button.Button(6, 400, self.assets.easy_image, 1)
        self.normal_button = button.Button(275, 400, self.assets.normal_image, 1)
        self.hard_button = button.Button(550, 400, self.assets.hard_image, 1)
        self.start_button = button.Button(150, 5, self.assets.start_image, 1)
        self.retry_button = button.Button(130, 200, self.assets.retry_image, 1)
    
    def draw_text(self, text, x, y, font=pygame.font.SysFont("arialblack", 40), text_col=TEXT_COL):
        """Draw text on the game screen at the specified position."""
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))
    
    def start_game(self):
        """Initialize a new game session by creating a snake and spawning a fruit."""
        self.snake = Snake()
        self.fruit = Fruit()
        self.fruit.spawn_fruit(self.snake.body)
        self.score = 0
        self.last_move_time = pygame.time.get_ticks()
        self.state = GameState.PLAYING
    
    def end_game(self):
        self.highscore = max(self.score, self.highscore)
        self.state = GameState.GAME_OVER

    def handle_menu_click(self, mouse_pos):
        if self.easy_button.rect.collidepoint(mouse_pos):
            self.move_delay = DIFFICULTY_DELAYS["easy"]
        elif self.normal_button.rect.collidepoint(mouse_pos):
            self.move_delay = DIFFICULTY_DELAYS["normal"]
        elif self.hard_button.rect.collidepoint(mouse_pos):
            self.move_delay = DIFFICULTY_DELAYS["hard"]
        elif self.start_button.rect.collidepoint(mouse_pos):
            self.start_game()
    
    def handle_game_over(self, mouse_pos):
        if self.retry_button.rect.collidepoint(mouse_pos):
            self.state = GameState.MENU

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                # Handle menu UI clicks
                if self.state == GameState.MENU:
                    self.handle_menu_click(mouse_pos)
                elif self.state == GameState.GAME_OVER:
                    self.handle_game_over(mouse_pos)
                
            if self.state == GameState.PLAYING and event.type == pygame.KEYDOWN:
                new_dir = DIRECTIONS.get(event.key)
                # Only set new direction if WASD key was pressed
                if new_dir:
                    self.snake.set_direction(new_dir)
        return True
    
    def update(self):
        if self.state != GameState.PLAYING:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay:
            return
        
        self.last_move_time = current_time

        new_head = self.snake.check_next_move()
        grow = (new_head == self.fruit.pos)

        collision_body = self.snake.body if grow else self.snake.body[:-1]
        # check walls
        if (self.snake.check_wall(new_head)) or new_head in collision_body:
            self.end_game()
            return
        else:
            self.snake.move(new_head, grow)
            if grow:
                self.score += 1
                self.fruit.spawn_fruit(self.snake.body)
        # Draw the snake
        self.snake.draw(screen)

    def draw(self):
        self.screen.fill(BG_COL)
 
        if self.state == GameState.MENU:
            self.easy_button.draw(self.screen)
            self.normal_button.draw(self.screen)
            self.hard_button.draw(self.screen)
            self.start_button.draw(self.screen)
            
            
 
        elif self.state == GameState.GAME_OVER:
            self.retry_button.draw(self.screen)
            self.draw_text("Game over!", 280, 180)
            self.draw_text(f"Your score: {self.score}", 50, 500, font=pygame.font.SysFont("arialblack", 36))
            self.draw_text(f"Your highscore: {self.highscore}", 400, 500, font=pygame.font.SysFont("arialblack", 36))
 
        elif self.state == GameState.PLAYING:
            self.fruit.draw(self.screen, self.assets.fruit_image)
            self.snake.draw(self.screen)
 
        pygame.display.update()
    
    def run(self):
        run = True

        while run:
            run = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()