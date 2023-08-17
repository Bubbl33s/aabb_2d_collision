import pygame

from abc import ABC, abstractmethod

# CONSTANTS
WIDTH, HEIGHT = 800, 800
SQR_A_SIZE, SQR_B_SIZE = 75, 150

AXIS_CL = 120, 120, 120
GREEN_CL = 0, 255, 0
RED_CL = 255, 0, 0
WHITE_CL = 255, 255, 255


class AABB:
    def __init__(self, width, height):
        pygame.init()
        pygame.font.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(
            "Axis-Aligned Bounding Box 2D Collision Detection")
        self.clock = pygame.time.Clock()
        self.fps = 120
        self.done = False
        self.create_squares(SQR_A_SIZE, SQR_B_SIZE)
        self.mouse_inside = False
        self.init_texts_vars()
        pygame.mouse.set_visible(False)

    # MAIN LOOP
    def run_game(self):
        while not self.done:
            self.handle_events()

            self.screen.fill((0, 0, 0))
            self.square_a.update_and_draw()
            self.square_b.update_and_draw()

            self.display_bools_text()
            self.display_squares_text(self.square_a, self.square_b)

            self.clock.tick(self.fps)
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            self.update_mouse_inside(event)

        self.square_a.check_axis_collision(self.square_b)
        self.square_b.check_axis_collision(self.square_a)
        self.square_b.check_square_collision()
        self.check_bools_text(self.square_a, self.square_b)

    def create_squares(self, sqr_a_size, sqr_b_size):
        # Get coords for center square on window
        sqr_a_x = self.width/2 - sqr_a_size/2
        sqr_a_y = self.height/2 - sqr_a_size/2

        self.square_a = SquareA(self, sqr_a_x, sqr_a_y, sqr_a_size)

        # Same as above
        sqr_b_x = self.width/2 - sqr_b_size/2
        sqr_b_y = self.height/2 - sqr_b_size/2

        self.square_b = SquareB(self, sqr_b_x, sqr_b_y, sqr_b_size)

    # Verifies if mouse is inside or not of screen
    def update_mouse_inside(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            if 0 <= mx < self.width and 0 <= my < self.height:
                self.mouse_inside = True
            else:
                self.mouse_inside = False

    # text template method
    def display_text(self, text, color, size, pos):
        font = pygame.font.SysFont("Consolas", size)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, pos)

    def init_texts_vars(self):
        # Chained assignment
        self.is_above = self.is_below = self.is_to_the_right = self.is_to_the_left = False
        self.is_colliding = True

        self.header_text_color = self.a_txt_color = self.b_txt_color = GREEN_CL

    def check_bools_text(self, square_a, square_b):
        if square_a.y + square_a.size < square_b.y:
            self.is_above = True
        else:
            self.is_above = False

        if square_a.y > square_b.y + square_b.size:
            self.is_below = True
        else:
            self.is_below = False

        if square_a.x + square_a.size < square_b.x:
            self.is_to_the_left = True
        else:
            self.is_to_the_left = False

        if square_a.x > square_b.x + square_b.size:
            self.is_to_the_right = True
        else:
            self.is_to_the_right = False

    def display_bools_text(self):
        is_colliding_text = f"Collision between squares? {self.is_colliding}"
        x_pos = 15
        text_size = 14

        texts_and_positions = {
            f"Is A to the right of B? {self.is_to_the_right}": (x_pos, 40),
            f"Is A to the left of B? {self.is_to_the_left}": (x_pos, 55),
            f"Is A above B? {self.is_above}": (x_pos, 70),
            f"Is A below B? {self.is_below}": (x_pos, 85),
            (f"Collision between squares? {not self.is_to_the_right} && "
             f"{not self.is_to_the_left} && { not self.is_above} && "
             f"{not self.is_below}"): (x_pos, 115),
            "[How to use]": (x_pos, 145),
            f"Mouse: move smaller rectangle.": (x_pos, 160),
            f"WASD/Arrows: move larger rectangle.": (x_pos, 175)
        }

        for text, pos in texts_and_positions.items():
            self.display_text(text, WHITE_CL, text_size, pos)

        self.display_text(is_colliding_text, self.header_text_color,
                          20, (x_pos, 10))

    def display_squares_text(self, square_a, square_b):
        size = 24
        x_offset = size/4
        y_offset = size/2

        # Calculates the coords for the perfect center position
        a_text_pos = ((square_a.x + square_a.size/2) - x_offset,
                      (square_a.y + square_a.size/2) - y_offset)
        b_text_pos = ((square_b.x + square_b.size/2) - x_offset,
                      (square_b.y + square_b.size/2) - y_offset)

        self.display_text("A", self.a_txt_color, size, a_text_pos)
        self.display_text("B", self.b_txt_color, size, b_text_pos)


class Square(ABC):
    def __init__(self, window, x, y, size):
        self.window = window
        self.size = size
        self.x = x
        self.y = y
        self.color = GREEN_CL

        self.axis_x1_cl = self.axis_x2_cl = self.axis_y1_cl = self.axis_y2_cl = AXIS_CL

    def draw_square(self):
        pygame.draw.rect(self.window.screen, self.color,
                         pygame.Rect(self.x, self.y, self.size, self.size), 4)

    def draw_axis(self):
        line_width = 2
        # For align the axis with the square's line
        offset = line_width / 2

        # X AXIS
        pygame.draw.line(self.window.screen, self.axis_x1_cl, (0, self.y + offset),
                         (self.window.width, self.y + offset), line_width)

        pygame.draw.line(self.window.screen, self.axis_x2_cl, (0, self.y + self.size - offset),
                         (self.window.width, self.y + self.size - offset), line_width)

        # Y AXIS
        pygame.draw.line(self.window.screen, self.axis_y1_cl, (self.x + offset, 0),
                         (self.x + offset, self.window.height), line_width)

        pygame.draw.line(self.window.screen, self.axis_y2_cl, (self.x + self.size - offset, 0),
                         (self.x + self.size - offset, self.window.height), line_width)

    def update_and_draw(self):
        self.draw_axis()
        self.draw_square()
        self.movement()

    def check_axis_collision(self, collider):
        if collider.x < self.x < collider.x + collider.size:
            self.axis_y1_cl = RED_CL
        else:
            self.axis_y1_cl = AXIS_CL

        if collider.x < self.x + self.size < collider.x + collider.size:
            self.axis_y2_cl = RED_CL
        else:
            self.axis_y2_cl = AXIS_CL

        if collider.y < self.y < collider.y + collider.size:
            self.axis_x1_cl = RED_CL
        else:
            self.axis_x1_cl = AXIS_CL

        if collider.y < self.y + self.size < collider.y + collider.size:
            self.axis_x2_cl = RED_CL
        else:
            self.axis_x2_cl = AXIS_CL

    @abstractmethod
    def movement(self):
        pass


class SquareA(Square):
    def movement(self):
        if self.window.mouse_inside:
            nx, ny = pygame.mouse.get_pos()

            self.x = nx - self.size / 2
            self.y = ny - self.size / 2


class SquareB(Square):
    def movement(self):
        # Speed scales with fps values
        speed = 4 * 120 / self.window.fps
        pressed = pygame.key.get_pressed()

        # Edges limits for movement
        can_move_up = ((pressed[pygame.K_w] or pressed[pygame.K_UP]) and
                       (self.y + self.size/2) > 0)
        can_move_down = ((pressed[pygame.K_s] or pressed[pygame.K_DOWN]) and
                         (self.y + self.size/2) < self.window.height)
        can_move_left = ((pressed[pygame.K_a] or pressed[pygame.K_LEFT]) and
                         (self.x + self.size/2) > 0)
        can_move_right = ((pressed[pygame.K_d] or pressed[pygame.K_RIGHT]) and
                          (self.x + self.size/2) < self.window.width)

        # 8-direction movement
        if can_move_up:
            self.y -= speed

        if can_move_down:
            self.y += speed

        if can_move_left:
            self.x -= speed

        if can_move_right:
            self.x += speed

    def check_square_collision(self):
        collider = self.window.square_a
        is_colliding = (self.x < collider.x + collider.size and
                        self.x + self.size > collider.x and
                        self.y < collider.y + collider.size and
                        self.y + self.size > collider.y)

        self.window.is_colliding = is_colliding

        updated_color = RED_CL if is_colliding else GREEN_CL

        self.color = collider.color = updated_color
        self.window.header_text_color = updated_color
        self.window.a_txt_color = self.window.b_txt_color = updated_color


if __name__ == '__main__':
    window = AABB(WIDTH, HEIGHT)
    window.run_game()
