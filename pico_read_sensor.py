from machine import I2C, Pin
import time
from ssd1306 import SSD1306_I2C


class RoomConditionSensor:
    def __init__(
        self, i2c_interface: int = 0, sda_pin: Pin = Pin(0), scl_pin: Pin = Pin(1)
    ):
        self.device_id = 0x38
        self.i2c: I2C = I2C(i2c_interface, sda=sda_pin, scl=scl_pin, freq=90000)
        time.sleep(1)  # Delay to avoid I2C problems
        self.i2c.writeto(self.device_id, bytes([0x71]))
        status_byte = self.i2c.readfrom(self.device_id, 1)[0]

        if status_byte != 0x18:
            print("Sensor may not have initialised :(")

    def get_current_conditions(self):
        self.i2c.writeto(self.device_id, bytes([0xAC, 0x33, 0x00]))

        raw_reading = bytearray(8)
        self.i2c.readfrom_into(self.device_id, raw_reading)

        t = self._extract_temperature(raw_reading)
        h = self._extract_humidity(raw_reading)

        return (t, h)

    def _extract_temperature(self, data: bytearray) -> float:
        raw_temperature = ((data[3] & 0xF) << 16) + (data[4] << 8) + data[5]

        calculated_temperature = 200 * (float(raw_temperature) / (2**20)) - 50

        return round(calculated_temperature, 1)

    def _extract_humidity(self, data: bytearray) -> float:
        raw_humidity = (data[1] << 12) + (data[2] << 4) + ((data[3] & 0xF0) >> 4)

        calculated_humidity = 100 * (float(raw_humidity) / (2**20))

        return round(calculated_humidity, 1)


class Display:
    def __init__(
        self, i2c_interface: int = 1, sda_pin: Pin = Pin(10), scl_pin: Pin = Pin(11)
    ):
        display_i2c = I2C(i2c_interface, sda=sda_pin, scl=scl_pin, freq=400000)
        time.sleep(1)
        self.display = SSD1306_I2C(128, 32, display_i2c)

    def display_conditions(self, temperature, humidity):
        self.display.fill(0)

        self.display.text(f"Humidity {humidity}%", 0, 12)
        self.display.text(f"Temp {temperature} deg C", 0, 0)

        self.display.show()

    def clear_display(self):
        self.display.fill(0)
        self.display.show()


if __name__ == "__main__":
    sensor = RoomConditionSensor()
    display = Display()
    button = Pin(15, Pin.IN, Pin.PULL_DOWN)

    while True:
        if button.value() == 1:
            t, h = sensor.get_current_conditions()
            display.display_conditions(t, h)
            time.sleep(10)
            display.clear_display()
        time.sleep(0.2)
