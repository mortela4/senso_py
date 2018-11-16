"""
@file sensors_builder_validatedjson.py
@brief Sensor class constructed using a given (sensor-)baseclass as argument,
and using parameter packs created from JSON for adding sensor *properties*,
where only base-class properties are fixed, while device-specific attributes
can be added by extending the subclass.
Sensor *base* classes can be (for example) of type
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

@note Schema-validation of JSON input is included to avoid faulty input to propagate errors!
"""

import json
# from collections import OrderedDict
from jsonschema import Draft4Validator, exceptions


# TODO: add clk-speed(s) etc!
MAX_BAUD_RATE = 921400
MIN_BAUD_RATE = 2400
MAX_CS_VAL = 7
MAX_I2C_ADDR = 127


MOCKED_DRIVER_TEST = False

if MOCKED_DRIVER_TEST:
    from sensor_drivers.mocked_sensor_driver import *
else:
    from sensor_drivers.sensor_driver import *


# JSON schemas
# =============
# TODO: these should be imported from other (config-)module!
# ----------------------------------------------------------
# Base-level schema:
sensor_base_schema = {
    "type": "object",
    "required": ["sensor_type", "bus_no", "dev_name"],
    "properties": {
        "sensor_type": {"type": "string"},
        "bus_no": {"type": "integer"},
        "dev_name": {"type": "string"},
    },
}

# Device-specific schemas:
sensor_i2c_schema = {
    "type": "object",
    "required": ["i2c_addr"],
    "properties": {
        "i2c_addr": {"type": "integer"},
    },
}
sensor_spi_schema = {
    "type": "object",
    "required": ["cs_no"],
    "properties": {
        "cs_no": {"type": "integer"},
    },
}
sensor_uart_schema = {
    "type": "object",
    "required": ["baud_rate"],
    "properties": {
        "baud_rate": {"type": "integer"},
    },
}

# ******************* JSON-validation ************************

class JsonValidator:
    def __init__(self, schema=None, formal_check=True, debug=False):
        self.schema = schema
        self.formal_check = formal_check
        self.debug = debug
        if schema is None:
            print("ERROR: cannot construct class correctly without schema argument given!!")
        else:
            self.validator = Draft4Validator(schema)

    def check(self, json_input=None):
        if json_input is None:
            print("ERROR: no input to check!")
            return False
        # Check for required:
        try:
            self.validator.validate(json_input)
        except exceptions.ValidationError:
            for error in self.validator.iter_errors(json_input):
                first_err_line = str(error).splitlines()[0]
                prop_name = first_err_line.split()[0]
                if first_err_line.endswith('required property'):
                    print("JSON-validation ERROR: missing required property %s" % prop_name)
                elif first_err_line.find('not of type') >= 0:
                    print("JSON-validation ERROR: property %s has wrong type." % prop_name)
                else:
                    print("JSON-validation ERROR: %s" % first_err_line)
            return False
        #
        if self.formal_check:
            if self.validator.is_valid(json_input):
                if self.debug:
                    if self.debug:
                        print("JSON has valid format.")
            else:
                print("ERROR: JSON input has invalid format!")
                return False
        if self.debug:
            print("SUCCESS: JSON is valid! :-)")
        return True


# ***************************** Sensor BASE-classes ********************************

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


# Helper function(s) and class(es):

class SensorHelper(object):
    def get_info(self):
        # First - get BASE sensor properties (common to ALL sensors):
        self.base.get_info()
        # Then - get DEVICE-SPECIFIC properties, (possibly) unique to the given sensor type(I2C/SPI/UART):
        for sensor_prop, prop_value in self.__dict__.items():
            if sensor_prop != 'base' and sensor_prop != 'type_name':
                print("Sensor property %s = %s" % (sensor_prop, prop_value))


# Bus-specific sensor classes ...


class I2cSensor(SensorHelper):

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


class SpiSensor(SensorHelper):

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


class UartSensor(SensorHelper):

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


# **************** SENSOR-BUILDER ********************
class SensorBuilder(object):
    """
    Generic (almost ...) sensor builder.
    """
    def __init__(self, sensor_instance=None):
        self.sensor_obj = sensor_instance

    def with_field(self, field_name, field_value):
        existing_base_props = self.sensor_obj.base.__dict__
        existing_dev_props = self.sensor_obj.__dict__
        # Start with 'base' object = base class:
        if field_name not in existing_base_props:
            # Then device-specific props:
            self.sensor_obj.__dict__[field_name] = field_value
            if field_name not in existing_dev_props:
                print("Warning: field named '%s' - not in (sub)class! Possibly extending class ..." % field_name)
        else:
            self.sensor_obj.base.__dict__[field_name] = field_value
        #
        return self

    def build(self):
        return self.sensor_obj


# *********************** SENSORS-CLASS ***********************

# TODO: this map should rather come from (JSON-)config or as globals from other module!
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
                print("ERROR: validating SPI-sensor: CS=%d already in use on bus#=%d!" %
                      (sensor.cs_no, sensor.base.bus_no))
                return False
        return True

    def uart_validate(self, sensor):
        uart_sensors = self.get_uart_sensors()
        for uart_sensor in uart_sensors:
            if sensor.base.bus_no == uart_sensor.base.bus_no:
                print("ERROR: validating UART-sensor: serialport=%d already in use!" % sensor.base.bus_no)
                return False
        return True

    @staticmethod
    def build_sensor(sensor_clsname=None, base_clsname=None, props=None):
        if sensor_clsname is None or base_clsname is None or props is None:
            # TODO: possibly emit ERROR msg here - and/or throw??
            print("ERROR: build_sensor() requires all of 'sensor_clsname', "
                  "'base_clsname' and 'ppack' parameters to be provided!")
            return None
        #
        raw_obj = sensor_clsname(base_type=base_clsname)
        sensor_builder = SensorBuilder(sensor_instance=raw_obj)
        #
        # Set up list of props:
        # Build sensor:
        first_pass = True
        for sensor_prop_name, prop_value in props.items():
            if sensor_prop_name != "sensor_type":
                if first_pass:
                    tmp = sensor_builder.with_field(sensor_prop_name, prop_value)
                    first_pass = False
                else:
                    tmp = tmp.with_field(sensor_prop_name, prop_value)
        # Get final object:
        sensor = tmp.build()
        #
        return sensor

    def add_sensor(self, json_spec):
        # TODO: bring these dicts in from a config module or similar!
        # Dictionaries for sensor-type-to-<mapped instance> mapping:
        json_dev_schemas = {"i2c": sensor_i2c_schema, "spi": sensor_spi_schema, "uart": sensor_uart_schema}
        validators = {"i2c": self.i2c_validate, "spi": self.spi_validate, "uart": self.uart_validate}
        #
        json_base_validator = JsonValidator(sensor_base_schema)
        #
        # Turn JSON-input into dictionary:
        sensor_spec = json.loads(json_spec)
        # Validate JSON:
        if json_base_validator.check(sensor_spec):
            # May log something for DEBUG-purposes here ...
            pass
        else:
            print("ERROR: invalid sensor JSON input!")
            return
        #
        sensor_type = sensor_spec["sensor_type"]
        sensor_class_type = sensor_type_map[sensor_type]
        # Can validate device-specific JSON:
        json_dev_spec_schema = json_dev_schemas[sensor_type]
        json_dev_spec_validator = JsonValidator(json_dev_spec_schema)
        # Validate ...
        if json_dev_spec_validator.check(sensor_spec):
            # May log something for DEBUG-purposes here ...
            pass
        else:
            print("ERROR: invalid device-specific JSON input!")
            return
        # Create sensor ...
        try:
            sensor = self.build_sensor(sensor_clsname=sensor_class_type,
                                       base_clsname=ExternalSensorBase,
                                       props=sensor_spec)
            # Validating sensor instance BEFORE appending to list:
            validator = validators[sensor.base.type_name]
            if validator(sensor):
                self.sensors.append(sensor)
            else:
                raise Exception("Parameter ERROR: cannot add sensor to sensor-list!")
        except Exception as exc:
            print("ERROR creating sensor!!")
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
            if type(val) is not float:
                # Check if list or complex value:
                if type(val) is list:
                    print("Value list:")
                    print("------------")
                    for val_no, item_val in enumerate(val):
                        print("Value no.%d = %d" % (val_no, item_val))
                    print("")
                else:
                    if isinstance(val, ComplexValue):
                        print("Complex value:")
                        print("--------------")
                        print("Triggered: ", val.triggered)
                        print("Channel no: ", val.channel)
                        print("Value: ", val.ch_val)
                        print("")
                    else:
                        print("ERROR: cannot parse sensor readout result!")
            else:
                print("Sensor no.%d: %s (type=%s) value = %s" % (idx, sensor.base.alias, sensor.base.dev_name, val))

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

    def get_sensor_by_alias(self, s_alias=None):
        """
        Find sensor by alias - which SHOULD be unique.
        This is NOT the case with attribute 'dev_name'.
        TODO: infer checks for alias uniqueness! (on input also ...)
        """
        sensor_found = None
        if s_alias is None:
            # TODO: rather throw ArgumentException error ... (no?)
            print("ERROR: no sensor name specified!")
        else:
            for sensor in self.sensors:
                if s_alias == sensor.base.alias:
                    sensor_found = sensor
                    break
        return sensor_found


# *********** TEST ******************
if __name__ == "__main__":
    sensors = Sensors()
    sensors.list_sensors()
    #
    # Example JSON-data:
    params = """{"sensor_type": "i2c", "bus_no": 2, "i2c_addr": 78, "dev_name": "BM280", "alias": "RHT-sensor1"}"""
    sensors.add_sensor(params)
    #
    params = """{"sensor_type": "spi", "bus_no": 1, "cs_no": 3, "dev_name": "SHT721", "alias": "RHT-sensor2A"}"""
    sensors.add_sensor(params)
    #
    params = """{"sensor_type": "spi", "bus_no": 1, "cs_no": 8, "dev_name": "SHT721", "alias": "RHT-sensor2B"}"""
    sensors.add_sensor(params)
    #
    params = {"sensor_type": "uart", "bus_no": 4, "baud_rate": 115200,
              "dev_name": "CustomHygrometerSubmodule", "alias": "RHT-sensor3"}
    sensors.add_sensor(json.dumps(params))
    #
    sensors.list_sensors()
    #
    # Alt1:
    sensors.read_sensors()
    #
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
    sensors.add_sensor(json.dumps({"sensor_type": "uart", "bus_no": 4, "baud_rate": 38400, "dev_name": "CustomHygrometerSubmodule", "alias": "RHT-sensor4"}))
    sensors.add_sensor(json.dumps({"sensor_type": "spi", "bus_no": 1, "cs_no": 3, "clk_speed": 5000000, "dev_name": "MPU6050", "alias": "IMU-A1"}))
    sensors.add_sensor(json.dumps({"sensor_type": "spi", "bus_no": 1, "cs_no": 4, "clk_speed": 5000000, "dev_name": "MPU6050", "alias": "IMU-A2"}))
    sensors.add_sensor(json.dumps({"sensor_type": "i2c", "bus_no": 2, "i2c_addr": 78, "clk_speed": 100000, "dev_name": "BM281", "alias": "sensor2C"}))
    sensors.add_sensor(json.dumps({"sensor_type": "i2c", "bus_no": 2, "i2c_addr": 77, "clk_speed": 100000, "dev_name": "BM281", "alias": "sensor2D"}))
    #
    sensors.list_sensors()
    #
    my_sensor = sensors.get_sensor_by_alias("sensor2D")
    if my_sensor is None:
        print("No sensor by alias 'sensor2D' found!")
    else:
        print("Sensor by alias 'sensor2D' found! Characteristics: %s" % repr(my_sensor))
        my_sensor.get_info()
        print("Full list:")
        print(my_sensor.base.__dict__)
        print(my_sensor.__dict__)
    #
    # Fails base-schema test:
    sensors.add_sensor("""{"sensor_type": "i2c", "i2c_addr": 77, "clk_speed": 100000, "dev_name": "BM281","alias": "sensor2E"}""")
    # Fails devspec-schema test:
    sensors.add_sensor("""{"sensor_type": "i2c", "bus_no": 2, "clk_speed": 100000, "dev_name": "BM281", "alias": "sensor2F"}""")






