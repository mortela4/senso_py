"""
@file sensors_consolidated.py
@brief Sensor class constructed using a given (sensor-)baseclass as argument,
and using parameter packs for adding sensor *properties*.
Sensor base classes can be (for example) of type
INTERNAL:
- internal direct --> e.g. MCU/SoC-internal temp-sensor with digital reading
  (need possibly only address of control&data-registers)
- internal indirect --> e.g. internal ADC of SoC/MCU;
  input may need adaptation & data must possibly be scaled
EXTERNAL:
- external generic --> e.g. SPI, I2C, UART, 1-wire, CAN-bus etc. (also MIPI/GreyBus)
- external dedicated --> e.g. USB-device (typically) or FireWire-client
  (access via device class-driver)
In all, this yields a minimum of 2 generic base-classes (w. fields for distinction),
or 4 base-classes that are more specialized.
"""

import time


# TODO: add clk-speed(s) etc!
MAX_BAUD_RATE = 921400
MIN_BAUD_RATE = 2400
MAX_CS_VAL = 7
MAX_I2C_ADDR = 127


MOCKED_DRIVER_TEST = False

"""
if MOCKED_DRIVER_TEST:
    from sensor_drivers.mocked_sensor_driver import *
else:
    from sensor_drivers.sensor_driver import *
"""

# Simple, static functions for sensor-READ&CONFIG:
# ================================================


def configure_i2c_sensor(bus_no=None, i2c_addr=None):
    print("Configuring I2C-sensor with bus#: %s and address: %s..." % (bus_no, i2c_addr))


def configure_spi_sensor(bus_no=None, cs_no=None):
    print("Configuring SPI-sensor with bus#: %s and CS-num: %s..." % (bus_no, cs_no))


def get_i2c_val():
    print("Reading I2C-sensor ...")
    return 5.555


def get_spi_val():
    print("Reading SPI-sensor ...")
    return 7.777


def get_uart_val():
    print("Reading I2C-sensor ...")
    return 3.1234


class ExternalSensorBase:
    """
    Base sensor class no.1 (external sensors, connected to a bus)
    """
    bus_property1 = {"i2c": "bus-address", "spi": "ChipSelect-number", "uart": "baud_rate"}

    def __init__(self, type_name=None, bus_no=None, dev_name=None, alias=None, config=None, read=None):
        #
        self.config = config
        self.read = read
        self.type_name = type_name
        self.bus_no = bus_no
        if dev_name:
            self.dev_name = dev_name
        else:
            self.dev_name = "none"
        #
        if alias:
            self.alias = alias
        else:
            self.alias = "none"
        #
        self.bus_prop1 = self.bus_property1[self.type_name]

    def get_info(self):
        if self.type_name is None:
            print("Unknown sensor type - cannot show info!")
            return
        # INFO:
        bus_type_name = self.type_name.upper()
        print("%s-sensor properties:" % bus_type_name)
        print("---------------------")
        print("%s-interface no: %d" % (bus_type_name, self.bus_no))
        print("%s connected device: %s" % (bus_type_name, self.dev_name))
        print("%s sensor alias: %s" % (bus_type_name, self.alias))
        print("Bus-specific properties:")


class InternalSensorBase:
    """
    Base sensor class no.2 (MCU/SoC-internal sensors)
    """
    def __init__(self, type_name=None, dev_no=None, dev_addr=None, dev_name=None, use_irq=False, alias=None, read=None):
        self.read = read
        # TODO: throw error if =None or negative (and possibly above some limit)!
        self.type_name = type_name
        self.dev_no = dev_no
        self.dev_addr = dev_addr   # Start of register-block for peripheral, e.g. ADC0, ADC1 etc.
        if dev_name:
            self.dev_name = dev_name
        else:
            self.dev_name = "none"
        #
        if alias:
            self.alias = alias
        else:
            self.alias = "none"
        #
        self.use_irq = use_irq

    def get_info(self):
        if self.type_name is None:
            print("Unknown sensor type - cannot show info!")
            return
        # INFO:
        print("Internal sensor properties:")
        print("---------------------------")
        print("%Device no: %d" % self.dev_no)
        print("Sensor alias: %s" % self.alias)
        print("Device-specific properties:")
        print("Device address: %x" % self.dev_addr)
        print("Using IRQ: %s" % self.use_irq)


# Types:
internal_sensor_type = InternalSensorBase
external_sensor_type = ExternalSensorBase


def create_instance(class_type: type) -> object:
    inst = class_type.__call__()
    print("Instance info: " + repr(inst))
    return inst


# Bus-specific sensor classes ...
class I2cSensor(object):
    global MAX_I2C_ADDR

    def __init__(self, base_type=None):
        print("Creating a I2C sensor ...")
        self.type_name = "i2c"
        self.i2c_addr = None
        if base_type is None:
            print("ERROR: 'base_type' NOT defined!")
        self.base = base_type(type_name="i2c", config=configure_i2c_sensor, read=get_i2c_val)
        # Configure/Initialize sensor if needed:
        if self.base.config is None:
            print("No configuration/initialization of sensor specified initially - skipping.")
        else:
            self.base.config(self.base.bus_no, self.i2c_addr)

    def get_info(self):
        self.base.get_info()
        print("I2C-address: %d" % self.i2c_addr)
        print("")


class SpiSensor(object):
    global MAX_CS_VAL

    def __init__(self, base_type=None):
        print("Creating a SPI sensor ...")
        self.type_name = "spi"
        self.cs_no = None
        if base_type is None:
            print("ERROR: 'base_type' NOT defined!")
        self.base = base_type(type_name="spi", config=configure_spi_sensor, read=get_spi_val)
        # Configure/Initialize sensor if needed:
        if self.base.config is None:
            print("No configuration/initialization of sensor specified - skipping.")
        else:
            self.base.config(self.base.bus_no, self.cs_no)

    def get_info(self):
        self.base.get_info()
        print("SPI ChipSelect-num: %d" % self.cs_no)
        print("")


class UartSensor(object):
    global MIN_BAUD_RATE
    global MAX_BAUD_RATE

    def __init__(self, base_type=None):
        print("Creating a UART sensor ...")
        self.type_name = "uart"
        self.bus_no = None
        self.baud_rate = None
        if base_type is None:
            print("ERROR: 'base_type' NOT defined!")
        self.base = base_type(type_name="uart", read=get_uart_val)
        # Configure/Initialize sensor if needed:
        if self.base.config is None:
            print("No configuration/initialization of sensor specified - skipping.")
        else:
            self.base.config(self.base.bus_no, self.cs_no)

    def get_info(self):
        self.base.get_info()
        print("UART baudrate: %d" % self.baud_rate)
        print("")


# **************** SENSOR-BUILDER ********************
class SensorBuilder(object):
    """
    Generic (almost ...) sensor builder.
    """
    def __init__(self, sensor_instance=None):
        print("SensorBuilder() running ...")
        self.sensor_obj = sensor_instance
        print("Created sensor object of type: %s" % repr(self.sensor_obj))

    def with_field(self, field_name, field_value):
        existing_base_props = self.sensor_obj.base.__dict__
        existing_dev_props = self.sensor_obj.__dict__
        # Start with 'base' object = base class:
        if field_name not in existing_base_props:
            print("Warning: field named '%s' - not in (base)class! Possibly extending class ..." % field_name)
            # Then device-specific props:
            if field_name not in existing_dev_props:
                print("Warning: field named '%s' - not in (sub)class! Possibly extending class ..." % field_name)
            else:
                self.sensor_obj.__dict__[field_name] = field_value
                print("Sensor-update: field named '%s' - updated with value=%s ..." % (field_name, field_value))
        else:
            self.sensor_obj.base.__dict__[field_name] = field_value
            print("Sensor-update: field named '%s' - updated with value=%s ..." % (field_name, field_value))
        #
        return self

    def build(self):
        return self.sensor_obj


# *********************** SENSORS-CLASS ***********************

# TODO: these lists should rather come from (JSON-)config or as globals from other module!
# base_prop_list = ['bus_no', 'dev_name', 'alias']
uart_prop_list = ['bus_no', 'baud_rate', 'dev_name', 'alias']
spi_prop_list = ['bus_no', 'cs_no', 'dev_name', 'alias']
i2c_prop_list = ['bus_no', 'i2c_addr', 'dev_name', 'alias']
# TODO: same here ...
sensor_type_map = {"i2c": I2cSensor, "spi": SpiSensor, "uart": UartSensor}


class Sensors:
    """
    Class which is a PLACEHOLDER for multiple sensors of different type.
    """
    def __init__(self, sensors=[]):
        self.sensors = sensors

    def i2c_validate(self, sensor):
        i2c_sensors = self.get_i2c_sensors()
        for i2c_sensor in i2c_sensors:
            if sensor.i2c_addr == i2c_sensor.i2c_addr:
                print("ERROR validating I2C-sensor: address=%d already in use on bus#=%d!" %
                      (sensor.i2c_addr, sensor.base.bus_no))
                return False
        return True

    def spi_validate(self, sensor):
        spi_sensors = self.get_spi_sensors()
        for spi_sensor in spi_sensors:
            if sensor.base.bus_no == spi_sensor.base.bus_no and sensor.cs_no == spi_sensor.cs_no:
                print("ERROR validating SPI-sensor: CS=%d already in use on bus#=%d!" %
                      (sensor.cs_no, sensor.base.bus_no))
                return False
        return True

    def uart_validate(self, sensor):
        uart_sensors = self.get_uart_sensors()
        for uart_sensor in uart_sensors:
            if sensor.base.bus_no == uart_sensor.base.bus_no:
                print("ERROR validating UART-sensor: serialport=%d already in use!" % sensor.base.bus_no)
                return False
        return True

    @staticmethod
    def build_sensor(sensor_clsname=None, base_clsname=None, ppack=None):
        if sensor_clsname is None or base_clsname is None or ppack is None:
            # TODO: possibly emit ERROR msg here - and/or throw??
            print("ERROR: build_sensor() requires all of 'sensor_clsname', "
                  "'base_clsname' and 'ppack' parameters to be provided!")
            return None
        #
        print("Building sensor using class '%s' with base '%s' ..." % (sensor_clsname, base_clsname))
        for pidx, param in enumerate(ppack):
            print("Parameter %s: %s" % (pidx, param))
        raw_obj = sensor_clsname(base_type=base_clsname)
        print("Created raw sensor object: %s" % repr(raw_obj))
        sensor_builder = SensorBuilder(sensor_instance=raw_obj)
        print("Created sensor builder: %s" % repr(sensor_builder))
        # Set up list of props:
        prop_list = None
        # TODO: strong coupling here! Bad design (?) ...
        if raw_obj.type_name == "uart":
            print("Using UART properties ...")
            prop_list = uart_prop_list
        elif raw_obj.type_name == "spi":
            print("Using SPI properties ...")
            prop_list = spi_prop_list
        elif raw_obj.type_name == "i2c":
            print("Using I2C properties ...")
            prop_list = i2c_prop_list
        else:
            print("BUILDER ERROR: sensor is of UNKNOWN type!!")
            # TODO: throw here! (e.g. 'ArgumentError' ??)
        # Build sensor:
        tmp = None
        for idx, sensor_prop_name in enumerate(prop_list):
            field_val = ppack[idx]
            print("Building sensor with property %s = '%s'" % (sensor_prop_name, field_val))
            if idx == 0:
                tmp = sensor_builder.with_field(sensor_prop_name, field_val)
            else:
                tmp = tmp.with_field(sensor_prop_name, field_val)
        # Get final object:
        sensor = tmp.build()
        print("Built sensor: %s" % repr(sensor))
        #
        return sensor

    def add_sensor(self, ppack):
        validators = {"i2c": self.i2c_validate, "spi": self.spi_validate, "uart": self.uart_validate}
        sensor_type = ppack[0]
        print("Type: ", sensor_type)
        sensor_class_type = sensor_type_map[sensor_type]
        # Create sensor ...
        try:
            sensor = self.build_sensor(sensor_clsname=sensor_class_type,
                                       base_clsname=ExternalSensorBase,
                                       ppack=ppack[1:])
            # Validating sensor instance BEFORE appending to list:
            print("Validating sensor properties ...")
            validator = validators[sensor.base.type_name]
            if validator(sensor):
                self.sensors.append(sensor)
            else:
                raise Exception("Parameter ERROR: cannot add sensor to sensor-list!")
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
            val = sensor.base.read()
            print("Sensor no.%d: %s (type=%s) value = %s" % (idx, sensor.base.alias, sensor.base.dev_name, val))
            if type(val) is not float:
                # Check if list or complex value:
                if type(val) is list:
                    print("Value list:")
                    print("------------")
                    for val_no, item_val in enumerate(val):
                        print("Value no.%d = %d" % (val_no, item_val))
                    print("")
                else:
                    print("Reading sensor: complex value - cannot parse!")
                    """
                    if isinstance(val, ComplexValue):
                        print("Complex value:")
                        print("--------------")
                        print("Triggered: ", val.triggered)
                        print("Channel no: ", val.channel)
                        print("Value: ", val.ch_val)
                        print("")
                    else:
                        print("ERROR: cannot parse sensor readout result!")
                    """

    def get_sensor_data(self):
        """ Generator version of 'read_sensors()' which may be more usable. """
        for sensor in self.sensors:
            sensor_val = sensor.base.read()
            sensor_name = sensor.base.alias
            yield (sensor_name, sensor_val)  # use 'sdata_gen = sensors.get_sensor_data()' to obtain generator.

    def get_i2c_sensors(self):
        i2c_sensors = []
        for sensor in self.sensors:
            if sensor.base.type_name == "i2c":
                i2c_sensors.append(sensor)
        return i2c_sensors

    def get_spi_sensors(self):
        spi_sensors = []
        for sensor in self.sensors:
            if sensor.base.type_name == "spi":
                spi_sensors.append(sensor)
        return spi_sensors

    def get_uart_sensors(self):
        uart_sensors = []
        for sensor in self.sensors:
            if sensor.base.type_name == "uart":
                uart_sensors.append(sensor)
        return uart_sensors


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
    # Alt1:
    sensors.read_sensors()
    # Alt2 (no special handling of list-data or ComplexValue-data here):
    print("Sensor data from dataset:")
    print("=========================")
    sdata = sensors.get_sensor_data()
    for num in range(len(sensors.sensors)):
        name, value = next(sdata)
        print("Sensor %d named '%s' value: %s" % (num, name, value))
    # Alt3 (using generator just as Alt2 - but simpler):
    print("Sensor data from generator:")
    print("===========================")
    sdata = sensors.get_sensor_data()
    for sd_item in sdata:
        name, value = sd_item   # indirectly calling 'next(sdata)'
        print("Sensor named '%s' value: %s" % (name, value))
    #
    print("")
    print("Adding some more sensors ...")
    sensors.add_sensor(("uart", 4, 38400, "CustomHygrometerSubmodule", "RHT-sensor4"))
    sensors.add_sensor(("spi", 1, 3, "MPU6050", "IMU-A1"))
    sensors.add_sensor(("spi", 1, 4, "MPU6050", "IMU-A1"))
    sensors.add_sensor(("i2c", 2, 78, "BM281", "sensor2C"))
    sensors.add_sensor(("i2c", 2, 77, "BM281", "sensor2C"))
    #
    sensors.list_sensors()




