"""Test different accessory types: Sensors."""
import unittest

from homeassistant.components.homekit.const import PROP_CELSIUS
from homeassistant.components.homekit.type_sensors import (
    TemperatureSensor, HumiditySensor, BinarySensor, BINARY_SENSOR_SERVICE_MAP)
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT, ATTR_DEVICE_CLASS, STATE_UNKNOWN, STATE_ON,
    STATE_OFF, STATE_HOME, STATE_NOT_HOME, TEMP_CELSIUS, TEMP_FAHRENHEIT)

from tests.common import get_test_home_assistant


class TestHomekitSensors(unittest.TestCase):
    """Test class for all accessory types regarding sensors."""

    def setUp(self):
        """Setup things to be run when tests are started."""
        self.hass = get_test_home_assistant()

    def tearDown(self):
        """Stop down everything that was started."""
        self.hass.stop()

    def test_temperature(self):
        """Test if accessory is updated after state change."""
        entity_id = 'sensor.temperature'

        acc = TemperatureSensor(self.hass, entity_id, 'Temperature', aid=2)
        acc.run()

        self.assertEqual(acc.aid, 2)
        self.assertEqual(acc.category, 10)  # Sensor

        self.assertEqual(acc.char_temp.value, 0.0)
        for key, value in PROP_CELSIUS.items():
            self.assertEqual(acc.char_temp.properties[key], value)

        self.hass.states.set(entity_id, STATE_UNKNOWN,
                             {ATTR_UNIT_OF_MEASUREMENT: TEMP_CELSIUS})
        self.hass.block_till_done()

        self.hass.states.set(entity_id, '20',
                             {ATTR_UNIT_OF_MEASUREMENT: TEMP_CELSIUS})
        self.hass.block_till_done()
        self.assertEqual(acc.char_temp.value, 20)

        self.hass.states.set(entity_id, '75.2',
                             {ATTR_UNIT_OF_MEASUREMENT: TEMP_FAHRENHEIT})
        self.hass.block_till_done()
        self.assertEqual(acc.char_temp.value, 24)

    def test_humidity(self):
        """Test if accessory is updated after state change."""
        entity_id = 'sensor.humidity'

        acc = HumiditySensor(self.hass, entity_id, 'Humidity', aid=2)
        acc.run()

        self.assertEqual(acc.aid, 2)
        self.assertEqual(acc.category, 10)  # Sensor

        self.assertEqual(acc.char_humidity.value, 0)

        self.hass.states.set(entity_id, STATE_UNKNOWN,
                             {ATTR_UNIT_OF_MEASUREMENT: "%"})
        self.hass.block_till_done()

        self.hass.states.set(entity_id, '20', {ATTR_UNIT_OF_MEASUREMENT: "%"})
        self.hass.block_till_done()
        self.assertEqual(acc.char_humidity.value, 20)

    def test_binary(self):
        """Test if accessory is updated after state change."""
        entity_id = 'binary_sensor.opening'

        self.hass.states.set(entity_id, STATE_UNKNOWN,
                             {ATTR_DEVICE_CLASS: "opening"})
        self.hass.block_till_done()

        acc = BinarySensor(self.hass, entity_id, 'Window Opening', aid=2)
        acc.run()

        self.assertEqual(acc.aid, 2)
        self.assertEqual(acc.category, 10)  # Sensor

        self.assertEqual(acc.char_detected.value, 0)

        self.hass.states.set(entity_id, STATE_ON,
                             {ATTR_DEVICE_CLASS: "opening"})
        self.hass.block_till_done()
        self.assertEqual(acc.char_detected.value, 1)

        self.hass.states.set(entity_id, STATE_OFF,
                             {ATTR_DEVICE_CLASS: "opening"})
        self.hass.block_till_done()
        self.assertEqual(acc.char_detected.value, 0)

        self.hass.states.set(entity_id, STATE_HOME,
                             {ATTR_DEVICE_CLASS: "opening"})
        self.hass.block_till_done()
        self.assertEqual(acc.char_detected.value, 1)

        self.hass.states.set(entity_id, STATE_NOT_HOME,
                             {ATTR_DEVICE_CLASS: "opening"})
        self.hass.block_till_done()
        self.assertEqual(acc.char_detected.value, 0)

        self.hass.states.remove(entity_id)
        self.hass.block_till_done()

    def test_binary_device_classes(self):
        """Test if services and characteristics are assigned correctly."""
        entity_id = 'binary_sensor.demo'

        for device_class, (service, char) in BINARY_SENSOR_SERVICE_MAP.items():
            self.hass.states.set(entity_id, STATE_OFF,
                                 {ATTR_DEVICE_CLASS: device_class})
            self.hass.block_till_done()

            acc = BinarySensor(self.hass, entity_id, 'Binary Sensor', aid=2)
            self.assertEqual(acc.get_service(service).display_name, service)
            self.assertEqual(acc.char_detected.display_name, char)
