#include <Wire.h>

/* defines */
#define D6F_ADDR 0x6C  // D6F-PH I2C client address at 7bit expression


uint8_t conv16_u8_h(int16_t a) {
    return (uint8_t)(a >> 8);
}

uint8_t conv16_u8_l(int16_t a) {
    return (uint8_t)(a & 0xFF);
}

uint16_t conv8us_u16_be(uint8_t* buf) {
    return (uint16_t)(((uint32_t)buf[0] << 8) | (uint32_t)buf[1]);
}


/** <!-- i2c_write_reg16 {{{1 --> I2C write bytes with a 16bit register.
 */
bool i2c_write_reg16(uint8_t slave_addr, uint16_t register_addr,
                     uint8_t *write_buff, uint8_t len) {
    Wire.beginTransmission(slave_addr);

    Wire.write(conv16_u8_h(register_addr));
    Wire.write(conv16_u8_l(register_addr));

    if (len != 0) {
        for (uint8_t i = 0; i < len; i++) {
            Wire.write(write_buff[i]);
        }
    }
    Wire.endTransmission();
    return false;
}


/** <!-- i2c_read_reg8 {{{1 --> I2C read bytes with a 8bit register.
 */
bool i2c_read_reg8(uint8_t slave_addr, uint8_t register_addr,
                   uint8_t *read_buff, uint8_t len) {
    Wire.beginTransmission(slave_addr);
    Wire.write(register_addr);
    Wire.endTransmission();

    Wire.requestFrom(slave_addr, len);

    if (Wire.available() != len) {
        return true;
    }
    for (uint16_t i = 0; i < len; i++) {
        read_buff[i] = Wire.read();
    }
    return false;
}
