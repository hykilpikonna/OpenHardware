#include <Arduino.h>
#include <FastLED.h>
#include "sweets.h"

constexpr u8 N_TOUCH_PINS = 12;
constexpr u8 TOUCH_PINS[N_TOUCH_PINS] = {
    GPIO_NUM_5, GPIO_NUM_6, GPIO_NUM_7, GPIO_NUM_8,
    GPIO_NUM_1, GPIO_NUM_2, GPIO_NUM_3, GPIO_NUM_4,
    GPIO_NUM_9, GPIO_NUM_10, GPIO_NUM_11, GPIO_NUM_12
};

// WS2812B LED data pin for the 12 touch sensors
constexpr u8 LED_PIN = GPIO_NUM_37;
CRGB leds[N_TOUCH_PINS];

// One single WS2812B status LED
constexpr u8 STATUS_LED_PIN = GPIO_NUM_38;
CRGB status_led[1];

void setup()
{
    // Initialize the LED pin as an output
    pinMode(LED_PIN, OUTPUT);
    pinMode(STATUS_LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    digitalWrite(STATUS_LED_PIN, LOW);

    // Initialize the touch pins as inputs
    for (val &pin : TOUCH_PINS) {
        pinMode(pin, INPUT);
    }

    // Initialize the LED strip
    CFastLED::addLeds<WS2812B, LED_PIN>(leds, N_TOUCH_PINS);
    CFastLED::addLeds<WS2812B, STATUS_LED_PIN>(status_led, 1);

    // Initialize the serial port
    Serial.begin(115200);
}

void loop() {
    // Read the touch pins,
    for (val &pin : TOUCH_PINS) {
        // Set the LED color to red if the pin is touched
        leds[pin] = digitalRead(pin) ? CRGB::Red : CRGB::Black;
    }

    // Update the LED strip
    CFastLED::show();
}