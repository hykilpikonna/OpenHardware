#include <Arduino.h>

#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>

#define u8 uint8_t
#define u16 uint16_t
#define u32 uint32_t

PN532_I2C pn532i2c(Wire);
PN532 nfc(pn532i2c);

uint8_t prevIDm[8];
unsigned long prevTime;

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

void printUid(const uint8_t* uid, const uint8_t uidLength)
{
    USBSerial.print("UID Length: ");
    USBSerial.print(uidLength, DEC);
    USBSerial.println(" bytes");
    USBSerial.print("UID Value: ");
    for (u8 i = 0; i < uidLength; i++)
        USBSerial.print(uid[i], HEX);
    USBSerial.println("");
}

void loop()
{
    u8 idm[8];
    u8 pmm[8];
    u16 systemCode;

    // Wait for an FeliCa type cards.
    // When one is found, some basic information such as IDm, PMm, and System Code are retrieved.
    USBSerial.print("F");
    if (nfc.felica_Polling(0xFFFF, 0x00, idm, pmm, &systemCode, 5) == 1)
    {
        if (memcmp(idm, prevIDm, 8) == 0 && millis() - prevTime < 3000)
        {
            delay(5);
            return;
        }

        USBSerial.println("\nFound a Felica card!");
        printUid(idm, 8);

        memcpy(prevIDm, idm, 8);
        prevTime = millis();
        return;
    }

    u8 uidLength; // Length of the UID (4 or 7 bytes depending on ISO14443A card type)

    USBSerial.print("M");
    if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, idm, &uidLength, 5))
    {
        // Check if the same card is present
        if (memcmp(idm, prevIDm, uidLength) == 0 && millis() - prevTime < 3000)
        {
            delay(5);
            return;
        }

        USBSerial.println("\nFound a MIFARE card!");
        printUid(idm, uidLength);

        memcpy(prevIDm, idm, uidLength);
        prevTime = millis();
    }
}
