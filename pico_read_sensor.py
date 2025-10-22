from machine import SoftI2C, Pin


def extract_temperature(data: bytearray) -> float:
    raw_temperature = ((data[3] & 0xF) << 16) + (data[4] << 8) + data[5]

    calculated_temperature = 200 * (float(raw_temperature) / (2**20)) - 50

    return round(calculated_temperature, 1)


def extract_humidity(data: bytearray) -> float:
    raw_humidity = (data[1] << 12) + (data[2] << 4) + ((data[3] & 0xF0) >> 4)

    calculated_humidity = 100 * (float(raw_humidity) / (2**20))

    return round(calculated_humidity, 1)


if __name__ == "__main__":
    device_id = 0x38
    sda_pin = Pin(0)
    scl_pin = Pin(1)
    i2c = SoftI2C(sda=sda_pin, scl=scl_pin, freq=90000)

    status = bytearray(1)
    i2c.writeto(device_id, bytes([0x71]))
    i2c.readfrom_into(device_id, status)

    if status[0] == 0x18:
        print("Ready to read")

    i2c.writeto(device_id, bytes([0xAC, 0x33, 0x00]))

    raw_reading = bytearray(8)
    i2c.readfrom_into(device_id, raw_reading)

    t = extract_temperature(raw_reading)
    h = extract_humidity(raw_reading)

    print(f"Temp: {t} Humidity: {h}")
