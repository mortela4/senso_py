"""
@file sensor_class
@brief Sensor class constructed using parameter packs
"""

import sys


# TODO: add clk-speed(s) etc!
MAX_BAUD_RATE = 921400
MIN_BAUD_RATE = 2400
MAX_CS_VAL = 7
MAX_I2C_ADDR = 127


# static functions - could as well be @staticmethod-decorated methods in 'Sensors' class.
def get_i2c_val():
    print("Getting I2C-sensor value ...")
    return 1


def get_spi_val():
    print("Getting SPI-sensor value ...")
    return 2


def get_uart_val():
    print("Getting UART-sensor value ...")
    return 3


# Base sensor class ...
class SensorBase:
    def __init__(self, bus_no=None, dev_name=None, alias=None, read=None):
        self.read = read
        # TODO: throw error if =None or negative (and possibly above some limit)!
        self.bus_no = bus_no
        #
        if dev_name:
            self.dev_name = dev_name
        else:
            self.dev_name = "none"
        #
        if alias:
            self.alias = alias
        else:
            self.alias = "none"


# Bus-specific sensor classes ...
class I2cSensor(SensorBase):
    global MAX_I2C_ADDR

    def __init__(self, ppack=None):
        bus_no, i2c_addr, dev_name, alias = ppack
        if i2c_addr < 0 or i2c_addr > MAX_I2C_ADDR:
            raise ValueError("Invalid I2C-address specified!")
        self.i2c_addr = i2c_addr
        super().__init__(bus_no, dev_name, alias, read=get_i2c_val)

    def get_info(self):
        print("I2C-sensor properties:")
        print("I2C-bus no: %d" % self.bus_no)
        print("I2C-bus address: %d" % self.i2c_addr)
        print("I2C-bus connected device: %s" % self.dev_name)
        print("I2C-bus sensor alias: %s" % self.alias)
        print("")


class SpiSensor(SensorBase):
    global MAX_CS_VAL

    def __init__(self, ppack=None):
        bus_no, cs_no, dev_name, alias = ppack
        if cs_no < 0 or cs_no > MAX_CS_VAL:
            raise ValueError("Invalid CS-number specified!")
        self.cs_no = cs_no
        super().__init__(bus_no, dev_name, alias, read=get_spi_val)

    def get_info(self):
        print("SPI-sensor properties:")
        print("SPI-bus no: %d" % self.bus_no)
        print("SPI-bus ChipSelect no: %d" % self.cs_no)
        print("SPI-bus connected device: %s" % self.dev_name)
        print("SPI-bus sensor alias: %s" % self.alias)
        print("")


class UartSensor(SensorBase):
    global MIN_BAUD_RATE
    global MAX_BAUD_RATE

    def __init__(self, ppack=None):
        bus_no, baud_rate, dev_name, alias = ppack
        if baud_rate < MIN_BAUD_RATE or baud_rate > MAX_BAUD_RATE:
            raise ValueError("Invalid baud-rate specified!")
        self.baud_rate = baud_rate
        super().__init__(bus_no, dev_name, alias, read=get_uart_val)

    def get_info(self):
        print("UART-sensor properties:")
        print("UART-interface no: %d" % self.bus_no)
        print("UART-bus baudrate no: %d" % self.baud_rate)
        print("UART-bus connected device: %s" % self.dev_name)
        print("UART-bus sensor alias: %s" % self.alias)
        print("")


# Class which is a PLACEHOLDER for multiple sensors of different type:
class Sensors:
    sensor_type_map = {"i2c": I2cSensor, "spi": SpiSensor, "uart": UartSensor}

    def __init__(self, sensors=[]):
        self.sensors = sensors

    def add_sensor(self, ppack):
        type = ppack[0]
        sub_ppack = ppack[1:]
        print("Type: ", type)
        sensor_creator = self.sensor_type_map[type]
        # Create sensor ...
        try:
            sensor = sensor_creator(sub_ppack)
            # TODO: validate sensor instance BEFORE appending to list!
            self.sensors.append(sensor)
        except Exception as exc:
            print("ERROR creating sensor!!")
            # print(sys.exc_info())
            print(exc.args)

    def list_sensors(self):
        if len(self.sensors) == 0:
            print("No sensors registered!")
            return
        print("")
        print("Registered sensors:")
        print("===================")
        for sensor in self.sensors:
            # TODO: check if 'sensor' has attribute(=method) 'get_info()' before attempting invocation!
            sensor.get_info()

    def read_sensors(self):
        print("Registered sensors:")
        print("===================")
        for idx, sensor in enumerate(self.sensors):
            val = sensor.read()
            print("Sensor no.%d: %s (type=%s) value = %d" % (idx, sensor.alias, sensor.dev_name, val))



# *********** TEST ******************
if __name__ == "__main__":
    sensors = Sensors()
    sensors.list_sensors()
    #
    params = ("i2c", 2, 78, "BM280", "RHT-sensor1")
    sensors.add_sensor(params)
    #
    params = ("spi", 1, 3, "SHT721", "RHT-sensor2A")
    sensors.add_sensor(params)
    #
    params = ("spi", 1, 8, "SHT721", "RHT-sensor2B")
    sensors.add_sensor(params)
    #
    sensors.add_sensor(("uart", 4, 115200, "CustomHygrometerSubmodule", "RHT-sensor3"))
    sensors.list_sensors()
    #
    sensors.read_sensors()

