# Bouncing Balls screensaver app

# Import the Arcade library
import arcade

# Set the window title
SCREEN_TITLE = "Bouncing Balls"

# Circle radius and movement
CIRCLE_RADIUS = 75
NUM_CIRCLES = 10  # Change this to set how many circles you want
SPEED_MULTIPLIER = 4  # Increase to make circles move faster (without reducing framerate)
MOVE_AMOUNT = 1  # How far to move each circle per frame
FILL_CIRCLES = False  # Set to False for outlines, True for filled

import random

def lerp_color(color1, color2, t):
    return (
        int(color1[0] + (color2[0] - color1[0]) * t),
        int(color1[1] + (color2[1] - color1[1]) * t),
        int(color1[2] + (color2[2] - color1[2]) * t)
    )

FADE_SPEED = 0.01  # How fast to fade between colors
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

import math

class FadingCircle:
    def __init__(self, x, y, dx, dy, color_index=0, next_color_index=1):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color_index = color_index
        self.next_color_index = next_color_index
        self.fade_t = 0.0

    def update(self, screen_width, screen_height):
        self.x += self.dx * SPEED_MULTIPLIER
        self.y += self.dy * SPEED_MULTIPLIER

        # Bounce off left/right
        if self.x - CIRCLE_RADIUS <= 0:
            self.x = CIRCLE_RADIUS
            self.dx *= -1
        elif self.x + CIRCLE_RADIUS >= screen_width:
            self.x = screen_width - CIRCLE_RADIUS
            self.dx *= -1

        # Bounce off top/bottom
        if self.y - CIRCLE_RADIUS <= 0:
            self.y = CIRCLE_RADIUS
            self.dy *= -1
        elif self.y + CIRCLE_RADIUS >= screen_height:
            self.y = screen_height - CIRCLE_RADIUS
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
        # Get the actual screen size
        self.screen_width, self.screen_height = self.get_size()
        arcade.set_background_color(arcade.color.BLACK)
        # Generate circles with random positions and velocities
        self.circles = []
        for i in range(NUM_CIRCLES):
            angle = random.uniform(0, 2 * math.pi)
            speed = MOVE_AMOUNT
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            # Avoid spawning at the very edge
            x = random.uniform(CIRCLE_RADIUS, self.screen_width - CIRCLE_RADIUS)
            y = random.uniform(CIRCLE_RADIUS, self.screen_height - CIRCLE_RADIUS)
            color_index = i % len(COLOR_LIST)
            next_color_index = (color_index + 1) % len(COLOR_LIST)
            self.circles.append(FadingCircle(x, y, dx, dy, color_index, next_color_index))

    def on_draw(self):
        self.clear()
        for circle in self.circles:
            color = circle.get_color()
            if FILL_CIRCLES:
                arcade.draw_circle_filled(circle.x, circle.y, CIRCLE_RADIUS, color)
            else:
                arcade.draw_circle_outline(circle.x, circle.y, CIRCLE_RADIUS, color, border_width=4)

    def on_update(self, delta_time):
        # Always use the current screen size in case of display changes
        self.screen_width, self.screen_height = self.get_size()
        for circle in self.circles:
            circle.update(self.screen_width, self.screen_height)

        # Check for collisions between all pairs of circles
        for i in range(len(self.circles)):
            for j in range(i + 1, len(self.circles)):
                c1 = self.circles[i]
                c2 = self.circles[j]
                dx = c1.x - c2.x
                dy = c1.y - c2.y
                dist = math.hypot(dx, dy)
                min_dist = 2 * CIRCLE_RADIUS
                if dist < min_dist:
                    # Simple elastic collision: swap velocities
                    c1.dx, c2.dx = c2.dx, c1.dx
                    c1.dy, c2.dy = c2.dy, c1.dy
                    # Move them apart so they don't stick
                    overlap = min_dist - dist
                    angle = math.atan2(dy, dx)
                    c1.x += math.cos(angle) * (overlap / 2)
                    c1.y += math.sin(angle) * (overlap / 2)
                    c2.x -= math.cos(angle) * (overlap / 2)
                    c2.y -= math.sin(angle) * (overlap / 2)

    def on_key_press(self, symbol, modifiers):
        self.close()  # Close the app if a key is pressed

        # I had the mouse movement to close the app but couldn't get it working correctly:
        # def on_mouse_motion(self, x, y, dx, dy):
        #     distance = math.sqrt(dx**2 + dy**2)
        #     if distance > min_distance_threshold:
        #         self.close()

def main():
    # Use a default size, but CircleWindow will detect and use the real screen size
    window = CircleWindow(800, 600, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()
