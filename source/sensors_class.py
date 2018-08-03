"""
@file sensor_class
@brief Sensor class constructed using parameter packs
"""

# static functions - could as well be @staticmethod-decorated methods in 'Sensors' class.

def get_i2c_val():
    print("Getting UART-sensor value ...")
    return 1


def get_spi_val():
    print("Getting UART-sensor value ...")
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
    def __init__(self, ppack=None):
        bus_no, i2c_addr, dev_name, alias = ppack
        # TODO: validate I2C-properties before assignment!
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
    def __init__(self, ppack=None):
        bus_no, cs_no, dev_name, alias = ppack
        # TODO: validate SPI-properties before assignment!
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
    def __init__(self, ppack=None):
        bus_no, baud_rate, dev_name, alias = ppack
        # TODO: validate UART-properties before assignment!
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
        sensor = sensor_creator(sub_ppack)
        # TODO: validate sensor instance BEFORE appending to list!
        self.sensors.append(sensor)

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


# *********** TEST ******************
if __name__ == "__main__":
    sensors = Sensors()
    sensors.list_sensors()
    #
    params = ("i2c", 2, 78, "BM280", "RHT-sensor1")
    sensors.add_sensor(params)
    #
    params = ("spi", 1, 3, "SHT721", "RHT-sensor2")
    sensors.add_sensor(params)
    #
    sensors.add_sensor(("uart", 4, 115200, "CustomHygrometerSubmodule", "RHT-sensor3"))
    sensors.list_sensors()

