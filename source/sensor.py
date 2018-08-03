""" Sensor class using parameter packs """

# Lets play first ...


def i2c_sensor(ppack):
    bus_no, i2c_addr, dev_name, alias = ppack
    print("I2C-sensor properties:")
    print("I2C-bus no: %d" % bus_no)
    print("I2C-bus address: %d" % i2c_addr)
    print("I2C-bus connected device: %s" % dev_name)
    print("I2C-bus sensor alias: %s" % alias)
    print("")


def spi_sensor(ppack):
    bus_no, cs_no, dev_name, alias = ppack
    print("SPI-sensor properties:")
    print("SPI-bus no: %d" % bus_no)
    print("SPI-bus ChipSelect no: %d" % cs_no)
    print("SPI-bus connected device: %s" % dev_name)
    print("SPI-bus sensor alias: %s" % alias)
    print("")


def uart_sensor(ppack):
    bus_no, baud_rate, dev_name, alias = ppack
    print("UART-sensor properties:")
    print("UART-interface no: %d" % bus_no)
    print("UART-bus baudrate no: %d" % baud_rate)
    print("UART-bus connected device: %s" % dev_name)
    print("UART-bus sensor alias: %s" % alias)
    print("")


sensor_type_map = {"i2c": i2c_sensor, "spi": spi_sensor, "uart": uart_sensor}


def create_sensor(ppack):
    type = ppack[0]
    sub_ppack = ppack[1:]
    print("Type: ", type)
    sensor_creator = sensor_type_map[type]
    # Create sensor ...
    sensor_creator(sub_ppack)


# *********** TEST ******************
if __name__ == "__main__":
    params = ("i2c", 2, 78, "BM280", "RHT-sensor1")
    create_sensor(params)
    #
    params = ("spi", 1, 3, "SHT721", "RHT-sensor2")
    create_sensor(params)
    #
    create_sensor(("uart", 4, 115200, "CustomHygrometerSubmodule", "RHT-sensor3"))


