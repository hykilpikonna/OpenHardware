#include <Arduino.h>
#include <USBHIDKeyboard.h>
#include "sweets.h"

#define KEY_COUNT 5

USBHIDKeyboard keyboard;
constexpr u8 keys[] = {'1', '2', '3', 'a', 'b'};
constexpr u8 pins[] = {GPIO_NUM_3, GPIO_NUM_4, GPIO_NUM_5, GPIO_NUM_6, GPIO_NUM_7};
bool keyStates[KEY_COUNT] = {false};

val led_pin = GPIO_NUM_15;

void setup()
{
    // Set up the GPIO pins
    for (val pin : pins) pinMode(pin, INPUT_PULLUP);
    pinMode(led_pin, OUTPUT);

    // Set up the USB keyboard
    keyboard.begin();
    Serial.begin();
}

void loop()
{
    // Check for key presses
    for (var i = 0; i < KEY_COUNT; i++)
    {
        val state = !digitalRead(pins[i]);

        if (state != keyStates[i])
        {
            if (state) keyboard.press(keys[i]);
            else keyboard.release(keys[i]);

            digitalWrite(led_pin, state);
            keyStates[i] = state;
        }
    }
}
