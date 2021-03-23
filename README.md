# Start

qt_plot.py

# Main modify

plot_widget.py

# Communication Protocol

## Example

```
HEX
数据头：   7F FE
数据长度： 05
数据正文： 01 02 03 04 05
校验：    93 04
```

## Arduino crc16 code

[arduino/crc16](./lib/arduino/crc16)

## Arduino example

```
// 200Hz 8 Channels

unsigned long previousMillis = 0;
const long interval = 5;
uint16_t datas[16];

void loop() {
  // put your main code here, to run repeatedly:
    unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    for(uint8_t i=0;i<16;i++)
    {
      datas[i] = read_i(i);
    }
    
    
    uint8_t send_data[2+1+8*2+2];
    send_data[0] = 0x7f;
    send_data[1] = 0xfe;
    send_data[2] = 8*2;
    for(int i=0;i<8;i++)
    {
    int16_t d = datas[i] + 50*i;
    send_data[3+i*2] =  d >> 8;
    send_data[3+i*2+1] = d&0xff;
    }
    uint16_t crc = crc16(&send_data[3], 16);
    send_data[19]=crc>>8;
    send_data[20]=crc;
    Serial.write(send_data, sizeof(send_data));
  }
}
```