# Taiko-stick / 电子太鼓槌

A pair of drumsticks that can be used to play Taiko no Tatsujin on any surface.

一对可以在任何表面上打太鼓达人的鼓槌.

## 1. Build / 制作

### Materials Required / 材料

* 2x Thick-enough drumsticks  
(The one I used: [taobao link](https://item.taobao.com/item.htm?id=665108049486))
* 2x Piezo sensors (压电/蜂鸣陶瓷片)
* 2x 1MΩ resistors
* 1x Arduino Nano  
(or any other dev board, just change the platformio config)
* Many wires

### Tools Required / 工具

* Either a breadboard, SPL2 solder-less connectors, or a soldering kit
* A computer

### Connections / 连接

1. Glue piezo sensors to the drumstick
2. Connect the ground of each sensor to the ground
3. Connect the output of one sensor to A0 and another to A1. 
4. Connect 1M resistors between ground and the sensor outputs, one for each sensor.

> If you want to protect the ADC from high voltages that the sensor might generate, you can connect an extra 5.1v zener diode in reverse bias from ground to each sensor
> so that voltages flowing to the ADC will be at most 5.1v.

![img.png](doc/img.png)

## 2. Run / 运行

### Flash Firmware / 烧录固件

1. Install PlatformIO Core ([Guide](https://platformio.org/install/cli))
2. Connect the Arduino Nano to your computer
3. Upload firmware using `platformio run --target upload`

### Run Backend / 运行后端

I'm too lazy to write a HID device driver, so I'm using a python script to read the serial output from the Arduino and send keystrokes to the computer.

1. Install Python 3.11+ ([Guide](https://www.python.org/downloads/))
2. Install dependencies using `pip install -r requirements.txt`
3. Run `python reader.py`
4. Use `Ctrl+C` to exit.

Note: If you're using osu-stable, you might want to change the key settings either in the python script or in the game. By default, the script uses F for don and D for ka.
