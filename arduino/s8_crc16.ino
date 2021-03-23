#include <crc16.h>

static const int pinTEST = 41;
static const uint8_t channels = 8;
String str_out;

unsigned long previousMillis = 0; // will store last time LED was updated
const long interval = 5;          // interval at which to blink (milliseconds)
volatile uint8_t t = 0;
uint16_t datas[16];

inline uint16_t read_i(uint8_t i)
{
  digitalWrite(3, i & (0x01 << 0));
  digitalWrite(4, i & (0x01 << 1));
  digitalWrite(5, i & (0x01 << 2));
  digitalWrite(6, i & (0x01 << 3));
  // delayMicroseconds(500);
  return analogRead(A0);
}

void setup()
{
  // put your setup code here, to run once:

  pinMode(A0, INPUT);

  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);

  pinMode(pinTEST, OUTPUT);
  // Serial2.begin(230400);
  Serial.begin(256000);
}

void loop()
{
  // put your main code here, to run repeatedly:
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval)
  {
    previousMillis = currentMillis;

    for (uint8_t i = 0; i < 16; i++)
    {
      datas[i] = read_i(i);
    }

    // str_out="$";
    // for(uint8_t i=0;i<channels-1;i++)
    // {
    //   str_out+=datas[i] + 50*i;
    //   str_out+=" ";
    // }
    // str_out+=datas[channels-1]+50*(channels-1);
    // str_out+=";";
    // Serial2.print(str_out);

    uint8_t send_data[2 + 1 + 8 * 2 + 2];
    send_data[0] = 0x7f;
    send_data[1] = 0xfe;
    send_data[2] = 8 * 2;
    for (int i = 0; i < 8; i++)
    {
      int16_t d = datas[i] + 50 * i;
      send_data[3 + i * 2] = d >> 8;
      send_data[3 + i * 2 + 1] = d & 0xff;
    }
    uint16_t crc = crc16(&send_data[3], 16);
    send_data[19] = crc >> 8;
    send_data[20] = crc;
    Serial.write(send_data, sizeof(send_data));

    t = ~t;
    digitalWrite(pinTEST, t);
  }
}