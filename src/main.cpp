#include <Arduino.h>

#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>

PN532_I2C pn532i2c(Wire);
PN532 nfc(pn532i2c);

#define Serial USBSerial

#include <PN532_debug.h>

uint8_t        _prevIDm[8];
unsigned long  _prevTime;

void setup()
{
  delay(1000);
  Serial.begin(115200);
  Serial.println("Hello!");
  Wire.setPins(4, 5);

  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata)
  {
    Serial.print("Didn't find PN53x board");
    while (1) {delay(10);};      // halt
  }

  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata >> 24) & 0xFF, HEX);
  Serial.print("Firmware ver. "); Serial.print((versiondata >> 16) & 0xFF, DEC);
  Serial.print('.'); Serial.println((versiondata >> 8) & 0xFF, DEC);

  // Set the max number of retry attempts to read from a card
  // This prevents us from waiting forever for a card, which is
  // the default behaviour of the PN532.
  nfc.setPassiveActivationRetries(0xFF);
  nfc.SAMConfig();

  memset(_prevIDm, 0, 8);
}

void printUid(uint8_t* uid, uint8_t uidLength) {
  Serial.print("UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
  Serial.print("UID Value: ");
  for (uint8_t i = 0; i < uidLength; i++) {
    Serial.print(uid[i], HEX);
  }
  Serial.println("");
}

void loop()
{
  uint8_t ret;
  uint16_t systemCode = 0xFFFF;
  uint8_t requestCode = 0x00;       // System Code request
  uint8_t idm[8];
  uint8_t pmm[8];
  uint16_t systemCodeResponse;

  // Wait for an FeliCa type cards.
  // When one is found, some basic information such as IDm, PMm, and System Code are retrieved.
  Serial.print("F");
  ret = nfc.felica_Polling(systemCode, requestCode, idm, pmm, &systemCodeResponse, 5);

  if (ret == 1) {
    if ( memcmp(idm, _prevIDm, 8) == 0 ) {
      if ( (millis() - _prevTime) < 3000 ) {
        delay(5);
        return;
      }
    }

    Serial.println("\nFound a Felica card!");
    printUid(idm, 8);

    memcpy(_prevIDm, idm, 8);
    _prevTime = millis();
    return;
  }

  Serial.print("M");
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 }; // Buffer to store the returned UID
  uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)

  if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 5)) {
    // Check if the same card is present
    if (memcmp(uid, _prevIDm, uidLength) == 0 && (millis() - _prevTime) < 3000) {
      delay(5);
      return;
    }

    Serial.println("\nFound a MIFARE card!");
    printUid(uid, uidLength);

    memcpy(_prevIDm, uid, uidLength);
    _prevTime = millis();
    return;
  }
}
