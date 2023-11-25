#include <Arduino.h>

#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>

#define u8 uint8_t
#define u16 uint16_t
#define u32 uint32_t

PN532_I2C pn532i2c(Wire);
PN532 nfc(pn532i2c);

constexpr u8 UID_LENGTH = 8;
u8 prevIDm[UID_LENGTH];
u32 prevTime;

void setup()
{
    // Add initial delay to allow the serial monitor to catch up
    delay(1000);

    // Initialize serial port
    USBSerial.begin(115200);
    USBSerial.println("Hello!");

    // Initialize I2C communication
    Wire.setPins(GPIO_NUM_4, GPIO_NUM_5);

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
    memset(prevIDm, 0, 8);
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
    for (u8 i = 0; i < len; i++)
        USBSerial.print(uid[i], HEX);
    USBSerial.println("");

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
    USBSerial.print("F");
    if (nfc.felica_Polling(0xFFFF, 0x00, idm, pmm, &systemCode, 5))
        foundCard(idm, UID_LENGTH, "FeliCa");

    // Wait for an ISO14443A type cards (MIFARE, etc.).  When one is found
    u8 uidLength;
    USBSerial.print("M");
    if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, idm, &uidLength, 5))
        foundCard(idm, uidLength, "ISO14443A");
}
