import arcade
import random
import math

SCREEN_TITLE = "Screensaver"
MESSAGE = "I am to misbehave"   # Change this to your desired message
FONT_SIZE = 45        # Change this to your desired font size
SPEED_MULTIPLIER = 4  # Increase to make text move faster
FADE_SPEED = 0.01     # How fast to fade between colors
FONT_NAME = "Arial"

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
    return (
        int(color1[0] + (color2[0] - color1[0]) * t),
        int(color1[1] + (color2[1] - color1[1]) * t),
        int(color1[2] + (color2[2] - color1[2]) * t)
    )

class BouncingText:
    def __init__(self, text, font_size, screen_width, screen_height):
        self.text = text
        self.font_size = font_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2
        self.y = screen_height // 2
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle)
        self.dy = math.sin(angle)
        self.color_index = 0
        self.next_color_index = 1
        self.fade_t = 0.0
        self._update_text_size()

    def _update_text_size(self):
        # Create a temporary Text object to measure dimensions
        text_obj = arcade.Text(
            self.text,
            0, 0,  # Position doesn't matter for size calculation
            arcade.color.WHITE,  # Color doesn't matter
            self.font_size,
            font_name=FONT_NAME,
            bold=True
        )
        self.text_width = text_obj.content_width
        self.text_height = text_obj.content_height

    def update(self):
        self.x += self.dx * SPEED_MULTIPLIER
        self.y += self.dy * SPEED_MULTIPLIER

        # Bounce off left/right
        if self.x - self.text_width/2 <= 0:
            self.x = self.text_width/2
            self.dx *= -1
        elif self.x + self.text_width/2 >= self.screen_width:
            self.x = self.screen_width - self.text_width/2
            self.dx *= -1

        # Bounce off top/bottom
        if self.y - self.text_height/2 <= 0:
            self.y = self.text_height/2
            self.dy *= -1
        elif self.y + self.text_height/2 >= self.screen_height:
            self.y = self.screen_height - self.text_height/2
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

class BouncingTextWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=True)
        self.set_mouse_visible(False)
        self.screen_width, self.screen_height = self.get_size()
        arcade.set_background_color(arcade.color.BLACK)
        self.bouncing_text = BouncingText(MESSAGE, FONT_SIZE, self.screen_width, self.screen_height)

    def on_draw(self):
        self.clear()
        color = self.bouncing_text.get_color()
        arcade.draw_text(
            self.bouncing_text.text,
            self.bouncing_text.x - self.bouncing_text.text_width/2,
            self.bouncing_text.y - self.bouncing_text.text_height/2,
            color,
            self.bouncing_text.font_size,
            font_name=FONT_NAME,
            bold=True
        )

    def on_update(self, delta_time):
        self.screen_width, self.screen_height = self.get_size()
        self.bouncing_text.screen_width = self.screen_width
        self.bouncing_text.screen_height = self.screen_height
        self.bouncing_text._update_text_size()
        self.bouncing_text.update()

    def on_key_press(self, symbol, modifiers):
        self.close()

def main():
    window = BouncingTextWindow(800, 600, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()