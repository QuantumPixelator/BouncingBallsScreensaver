# Bouncing Balls Screensaver

A Python screensaver app using the Arcade library. Multiple circles bounce around the screen, smoothly fading between colors. The app supports fullscreen, keyboard exit, and configurable options for the number of circles, speed, and fill/outline mode.

## Features
- Fullscreen, borderless display
- Configurable number of circles (`NUM_CIRCLES`)
- Adjustable movement speed (`SPEED_MULTIPLIER`)
- Color-fading effect for each circle
- Option to show filled or outlined circles (`FILL_CIRCLES`)
- Exits on key press or mouse movement (after a short delay)
- Hides mouse pointer while running

## Requirements
- Python 3.7+
- arcade (install with `pip install arcade`)

## Usage
1. Edit `main.py` to adjust the number of circles, speed, or fill/outline mode as desired.
2. Run the app:
   ```
   python main.py
   ```
3. The app will exit if you press any key or move the mouse.

- There is also a text-based bouncing screensaver: text.py

## License

MIT License

Copyright (c) 2025 Quantum Pixelator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
