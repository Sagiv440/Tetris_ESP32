Tetris_ESP32 (University Final Project)
======
![Image_1](https://github.com/Sagiv440/Tetris_ESP32/blob/main/Assets/Tetris-ESP32-Logo.png?raw=true)

# Description
Tetris ESP32 is my university final project. It’s a custom-built Tetris machine powered by an ESP-32 microcontroller and controlled using a PS2 game controller.
Under the hood, the controller runs a MicroPython interpreter that reads, decodes, and executes Python scripts in real time, allowing us to modify, add, or remove code as needed.

# PS2 Controller
The PlayStation 2 controller uses the SPI protocol for communication, which the ESP32 supports. This allows us to read and occasionally write data to the controller.

# Wifi
For an extra challenge, I decided that in order to view high scores from all players, the ESP32 should connect to Wi-Fi and display them through a browser interface.
In the game's options menu, there is a “Network” option that lets the ESP32 connect to any nearby Wi-Fi network.

# Tetris
There isn’t much to say — it’s Tetris, or at least a close version of it. The game itself was originally an older project of mine written in C++. Feeling confident that I could adapt it, and knowing that squares are the easiest thing to draw on the screen, it was the perfect fit for our project.


  
# Screen Shots
![Image_1](https://github.com/Sagiv440/Tetris_ESP32/blob/main/Assets/Photos/Game1.jpg?raw=true)
![Image_2](https://github.com/Sagiv440/Tetris_ESP32/blob/main/Assets/Photos/Home_screen.jpg?raw=true)
