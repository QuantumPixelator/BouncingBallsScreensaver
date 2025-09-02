# Bouncing Balls screensaver app

# Import the Arcade library, and other libraries
import arcade
import random
import math
import time

# Set the window title
SCREEN_TITLE = "Bouncing Balls"

# Configuration
NUM_CIRCLES = 25  # Change this to set how many circles you want
SPEED_MULTIPLIER = 4  # Increase to make circles move faster (without reducing framerate)
MOVE_AMOUNT = 1  # How far to move each circle per frame
FILL_CIRCLES = False  # Set to False for outlines, True for filled
FADE_SPEED = 0.01  # How fast to fade between colors

# Bevel factors for 3D effect
DARKER_FACTOR = 0.5
LIGHTER_FACTOR = 1.5
OUTER_WIDTH = 6
INNER_WIDTH = 2

# Color list
COLOR_LIST = [
    arcade.color.RED,
    arcade.color.ORANGE,
    arcade.color.YELLOW,
    arcade.color.GREEN,
    arcade.color.BLUE,
    arcade.color.PURPLE,
    arcade.color.PINK,
    arcade.color.CYAN,
    arcade.color.AQUA,
    arcade.color.MAGENTA,
    arcade.color.GOLD,
    arcade.color.LIME,
    arcade.color.TURQUOISE,
    arcade.color.WHITE,
]

def lerp_color(color1, color2, t):
    # Optimized lerp with integer output
    return (
        int(color1[0] + (color2[0] - color1[0]) * t),
        int(color1[1] + (color2[1] - color1[1]) * t),
        int(color1[2] + (color2[2] - color1[2]) * t)
    )

class FadingCircle:
    def __init__(self, x, y, dx, dy, color_index=0, next_color_index=1, radius=75):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.color_index = color_index
        self.next_color_index = next_color_index
        self.fade_t = 0.0

    def update(self, screen_width, screen_height):
        self.x += self.dx * SPEED_MULTIPLIER
        self.y += self.dy * SPEED_MULTIPLIER

        # Bounce off left/right
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.dx *= -1
        elif self.x + self.radius >= screen_width:
            self.x = screen_width - self.radius
            self.dx *= -1

        # Bounce off top/bottom
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.dy *= -1
        elif self.y + self.radius >= screen_height:
            self.y = screen_height - self.radius
            self.dy *= -1

        # Fade color
        self.fade_t += FADE_SPEED
        if self.fade_t >= 1.0:
            self.fade_t = 0.0
            self.color_index = self.next_color_index
            self.next_color_index = (self.next_color_index + 1) % len(COLOR_LIST)

    def get_color(self):
        color1 = COLOR_LIST[self.color_index]
        color2 = COLOR_LIST[self.next_color_index]
        return lerp_color(color1, color2, self.fade_t)

class CircleWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=True)
        # Hide the mouse pointer
        self.set_mouse_visible(False)
        # Cache screen size
        self.screen_width, self.screen_height = self.get_size()
        arcade.set_background_color(arcade.color.BLACK)
        self.start_time = time.time()
        # Generate circles with random positions and velocities
        self.circles = []
        for i in range(NUM_CIRCLES):
            radius = random.randint(35, 75)
            angle = random.uniform(0, 2 * math.pi)
            speed = MOVE_AMOUNT
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            # Avoid spawning at the very edge
            x = random.uniform(radius, self.screen_width - radius)
            y = random.uniform(radius, self.screen_height - radius)
            color_index = i % len(COLOR_LIST)
            next_color_index = (color_index + 1) % len(COLOR_LIST)
            self.circles.append(FadingCircle(x, y, dx, dy, color_index, next_color_index, radius))

    def on_draw(self):
        self.clear()
        for circle in self.circles:
            color = circle.get_color()
            if FILL_CIRCLES:
                arcade.draw_circle_filled(circle.x, circle.y, circle.radius, color)
            else:
                # Beveled effect for outlines
                # Compute darker color for outer bevel
                darker_color = (int(color[0] * DARKER_FACTOR), int(color[1] * DARKER_FACTOR), int(color[2] * DARKER_FACTOR))
                # Compute lighter color for inner bevel
                lighter_color = (min(255, int(color[0] * LIGHTER_FACTOR)), min(255, int(color[1] * LIGHTER_FACTOR)), min(255, int(color[2] * LIGHTER_FACTOR)))
                
                # Draw outer outline (darker, thicker)
                arcade.draw_circle_outline(circle.x, circle.y, circle.radius, darker_color, border_width=OUTER_WIDTH)
                
                # Draw inner outline (lighter, thinner)
                arcade.draw_circle_outline(circle.x, circle.y, circle.radius, lighter_color, border_width=INNER_WIDTH)

    def on_update(self, delta_time):
        # Update screen size only if changed
        new_width, new_height = self.get_size()
        if new_width != self.screen_width or new_height != self.screen_height:
            self.screen_width = new_width
            self.screen_height = new_height
        
        for circle in self.circles:
            circle.update(self.screen_width, self.screen_height)

        # Check for collisions between all pairs of circles
        for i in range(len(self.circles)):
            for j in range(i + 1, len(self.circles)):
                c1 = self.circles[i]
                c2 = self.circles[j]
                dx = c1.x - c2.x
                dy = c1.y - c2.y
                dist_sq = dx * dx + dy * dy  # Avoid sqrt for performance
                min_dist_sq = (c1.radius + c2.radius) ** 2
                if dist_sq < min_dist_sq:
                    # Simple elastic collision: swap velocities
                    c1.dx, c2.dx = c2.dx, c1.dx
                    c1.dy, c2.dy = c2.dy, c1.dy
                    # Move them apart so they don't stick
                    dist = math.sqrt(dist_sq)
                    overlap = (c1.radius + c2.radius) - dist
                    if dist > 0:
                        angle = math.atan2(dy, dx)
                        c1.x += math.cos(angle) * (overlap / 2)
                        c1.y += math.sin(angle) * (overlap / 2)
                        c2.x -= math.cos(angle) * (overlap / 2)
                        c2.y -= math.sin(angle) * (overlap / 2)

    def on_key_press(self, symbol, modifiers):
        self.close()  # Close the app if a key is pressed

    def on_mouse_motion(self, x, y, dx, dy):
        if time.time() - self.start_time > 2.0 and (abs(dx) > 5 or abs(dy) > 5):
            self.close()

def main():
    # Use a default size, but CircleWindow will detect and use the real screen size
    window = CircleWindow(800, 600, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()
