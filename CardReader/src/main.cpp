#include <Arduino.h>

#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>
#include <FastLED.h>
#include <types.h>

constexpr u8 NUM_LEDS = 7;
constexpr u8 BR_DIM = 8;
constexpr u8 BR_BRIGHT = 14;
CRGB leds[NUM_LEDS];

PN532_I2C pn532i2c(Wire);
PN532 nfc(pn532i2c);

constexpr u8 UID_LENGTH = 8;
u8 prevIDm[UID_LENGTH];
u32 prevTime;

void setup()
{
    // Add initial delay to allow the serial monitor to catch up
    delay(500);

    // Initialize serial port
    USBSerial.begin(115200);
    USBSerial.println("Hello!");

    // Initialize I2C communication
    Wire.setPins(GPIO_NUM_4, GPIO_NUM_5);

    // Initialize the LED
    CFastLED::addLeds<NEOPIXEL, GPIO_NUM_6>(leds, NUM_LEDS);
    FastLED.setBrightness(BR_DIM);

    // Find the PN532 NFC module
    nfc.begin();
    u32 versiondata;
    while ((versiondata = nfc.getFirmwareVersion()) == 0)
    {
        USBSerial.println("Didn't find PN53x board");
        delay(100);
    }

    // Got ok data, print it out!
    USBSerial.print("Found chip PN5");
    USBSerial.println(versiondata >> 24 & 0xFF, HEX);
    USBSerial.print("Firmware ver. ");
    USBSerial.print(versiondata >> 16 & 0xFF, DEC);
    USBSerial.print('.');
    USBSerial.println(versiondata >> 8 & 0xFF, DEC);

    // Set the max number of retry attempts to read from a card
    // This prevents us from waiting forever for a card, which is the default behaviour of the PN532.
    nfc.setPassiveActivationRetries(0xFF);
    nfc.SAMConfig();

    // Clear the IDm buffer
    memset(prevIDm, 0, UID_LENGTH);
}

void led_animation()
{
    FastLED.setBrightness(BR_BRIGHT);
    CRGB colors[] = {CRGB::LimeGreen, CRGB::Black, CRGB::Gold, CRGB::Black};

    for (const auto color : colors)
    {
        for (u8 i = 1; i < NUM_LEDS; i++)
        {
            leds[i] = color;
            FastLED.show();
            delay(35);
        }
    }

    FastLED.setBrightness(BR_DIM);
}

void foundCard(const u8* uid, const u8 len, const char* cardType)
{
    // Check if the same card is present
    if (memcmp(uid, prevIDm, UID_LENGTH) == 0 && millis() - prevTime < 3000)
    {
        delay(5);
        return;
    }

    USBSerial.printf("\nFound a %s card!\n", cardType);
    USBSerial.print("UID Value: ");
    for (u8 i = 0; i < len; i++) {
        if (uid[i] < 0x10) USBSerial.print("0");
        USBSerial.print(uid[i], HEX);
    }
    USBSerial.println("");

    led_animation();

    memcpy(prevIDm, uid, UID_LENGTH);
    prevTime = millis();
}

void loop()
{
    u8 idm[UID_LENGTH] = {0};
    u8 pmm[8];
    u16 systemCode;

    // Wait for an FeliCa type cards.
    // When one is found, some basic information such as IDm, PMm, and System Code are retrieved.
    leds[0] = CRGB::BlueViolet;
    FastLED.show();
    if (nfc.felica_Polling(0xFFFF, 0x00, idm, pmm, &systemCode, 5) == 1)
        foundCard(idm, UID_LENGTH, "FeliCa");

    // Wait for an ISO14443A type cards (MIFARE, etc.).  When one is found
    u8 uidLength;
    leds[0] = CRGB::OrangeRed;
    FastLED.show();
    if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, idm, &uidLength, 5) == 1)
        foundCard(idm, uidLength, "ISO14443A");
}
