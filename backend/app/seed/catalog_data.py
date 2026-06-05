"""Programmatic catalog for Wiring AI (50+ beginner components)."""

from __future__ import annotations

from typing import Any


def handle(component_id: str, pin_id: str) -> str:
    return f"{component_id}_{pin_id}"


def pin(
    component_id: str,
    pin_id: str,
    label: str,
    pin_type: str,
    direction: str,
    position: str = "right",
    **extra: Any,
) -> dict[str, Any]:
    return {
        "id": f"{component_id}_{pin_id}",
        "component_id": component_id,
        "pin_id": pin_id,
        "name": pin_id,
        "label": label,
        "pin_type": pin_type,
        "direction": direction,
        "position": position,
        "react_flow_handle_id": handle(component_id, pin_id),
        **extra,
    }


def power_pins(cid: str, logic: float = 5.0) -> list[dict]:
    if logic >= 5:
        return [
            pin(cid, "5v", "5V", "power_5v", "power_output", "left", allowed_voltage_min=5, allowed_voltage_max=5),
            pin(cid, "3v3", "3.3V", "power_33v", "power_output", "left", allowed_voltage_min=3.3, allowed_voltage_max=3.3),
            pin(cid, "gnd_1", "GND", "ground", "ground", "left"),
            pin(cid, "gnd_2", "GND", "ground", "ground", "left"),
        ]
    return [
        pin(cid, "3v3", "3.3V", "power_33v", "power_output", "left", allowed_voltage_min=3.3, allowed_voltage_max=3.3),
        pin(cid, "gnd_1", "GND", "ground", "ground", "left"),
        pin(cid, "gnd_2", "GND", "ground", "ground", "left"),
    ]


def arduino_digital_pins(cid: str, count: int = 14) -> list[dict]:
    pins = []
    for i in range(count):
        ptype = "pwm" if i in (3, 5, 6, 9, 10, 11) else "digital_io"
        pins.append(pin(cid, f"d{i}", f"D{i}", ptype, "bidirectional", "right", logic_voltage=5))
    return pins


def arduino_analog_pins(cid: str, count: int = 6, i2c_on: tuple[int, int] = (4, 5)) -> list[dict]:
    pins = []
    for i in range(count):
        if i == i2c_on[0]:
            pins.append(pin(cid, f"a{i}", f"A{i}/SDA", "i2c_sda", "bidirectional", "right", protocol="i2c"))
        elif i == i2c_on[1]:
            pins.append(pin(cid, f"a{i}", f"A{i}/SCL", "i2c_scl", "bidirectional", "right", protocol="i2c"))
        else:
            pins.append(pin(cid, f"a{i}", f"A{i}", "analog_input", "bidirectional", "right", logic_voltage=5))
    return pins


def sensor_module_pins(cid: str, logic: float = 5.0) -> list[dict]:
    vtype = "power_5v" if logic >= 5 else "power_33v"
    return [
        pin(cid, "vcc", "VCC", vtype, "power_input", "left", allowed_voltage_min=logic, allowed_voltage_max=logic),
        pin(cid, "gnd", "GND", "ground", "ground", "left"),
        pin(cid, "ao", "AO", "analog_output", "output", "right"),
        pin(cid, "do", "DO", "digital_output", "output", "right"),
    ]


def simple_sensor_pins(cid: str, logic: float = 5.0) -> list[dict]:
    vtype = "power_5v" if logic >= 5 else "power_33v"
    return [
        pin(cid, "vcc", "VCC", vtype, "power_input", "left", allowed_voltage_min=logic, allowed_voltage_max=logic),
        pin(cid, "gnd", "GND", "ground", "ground", "left"),
        pin(cid, "out", "OUT", "digital_output", "output", "right"),
    ]


def i2c_sensor_pins(cid: str, logic: float = 3.3) -> list[dict]:
    vtype = "power_33v" if logic <= 3.3 else "power_5v"
    return [
        pin(cid, "vcc", "VCC", vtype, "power_input", "left", allowed_voltage_min=logic, allowed_voltage_max=logic),
        pin(cid, "gnd", "GND", "ground", "ground", "left"),
        pin(cid, "sda", "SDA", "i2c_sda", "bidirectional", "right", protocol="i2c"),
        pin(cid, "scl", "SCL", "i2c_scl", "bidirectional", "right", protocol="i2c"),
    ]


def passive_terminals(cid: str) -> list[dict]:
    return [
        pin(cid, "terminal_1", "T1", "passive_terminal", "passive", "left"),
        pin(cid, "terminal_2", "T2", "passive_terminal", "passive", "right"),
    ]


def comp(
    cid: str,
    name: str,
    category: str,
    node_type: str,
    pins: list[dict],
    *,
    description: str = "",
    logic_voltage: float | None = None,
    voltage_min: float | None = None,
    voltage_max: float | None = None,
    protocols: list[str] | None = None,
    requires_power: bool = True,
    provides_power: bool = False,
    is_passive: bool = False,
    safety_level: str = "safe_beginner",
    current_draw_ma: float | None = None,
) -> tuple[dict, list[dict]]:
    component = {
        "id": cid,
        "name": name,
        "slug": cid.replace("_", "-"),
        "category": category,
        "description": description or f"{name} for beginner electronics projects.",
        "frontend_node_type": node_type,
        "logic_voltage": logic_voltage,
        "voltage_min": voltage_min,
        "voltage_max": voltage_max,
        "communication_protocols": protocols or [],
        "requires_power": requires_power,
        "provides_power": provides_power,
        "is_passive": is_passive,
        "safety_level": safety_level,
        "current_draw_ma": current_draw_ma,
        "is_active": True,
    }
    return component, pins


def build_catalog() -> tuple[list[dict], list[dict], list[dict]]:
    components: list[dict] = []
    pins: list[dict] = []

    def add(c: dict, p: list[dict]) -> None:
        components.append(c)
        pins.extend(p)

    # Controllers
    for cid, name, node, d_count, a_count in [
        ("arduino_uno", "Arduino Uno", "arduinoUnoNode", 14, 6),
        ("arduino_nano", "Arduino Nano", "arduinoNanoNode", 14, 8),
        ("arduino_mega", "Arduino Mega", "genericControllerNode", 54, 16),
    ]:
        p = power_pins(cid, 5) + arduino_digital_pins(cid, d_count) + arduino_analog_pins(cid, a_count)
        add(*comp(cid, name, "controller", node, p, logic_voltage=5, voltage_min=5, voltage_max=12, protocols=["digital", "analog", "pwm", "i2c", "spi", "uart"], provides_power=True))

    esp32_pins = power_pins("esp32_devkit", 3.3) + [
        pin("esp32_devkit", f"gpio{i}", f"GPIO{i}", "digital_io", "bidirectional", "right", logic_voltage=3.3)
        for i in range(2, 14)
    ] + [
        pin("esp32_devkit", "sda", "SDA", "i2c_sda", "bidirectional", "right", protocol="i2c"),
        pin("esp32_devkit", "scl", "SCL", "i2c_scl", "bidirectional", "right", protocol="i2c"),
    ]
    add(*comp("esp32_devkit", "ESP32 DevKit", "controller", "esp32Node", esp32_pins, logic_voltage=3.3, voltage_min=3.3, voltage_max=5, protocols=["digital", "pwm", "i2c", "spi", "uart"], provides_power=True))

    add(*comp(
        "esp8266_nodemcu", "ESP8266 NodeMCU", "controller", "genericControllerNode",
        power_pins("esp8266_nodemcu", 3.3) + arduino_digital_pins("esp8266_nodemcu", 9) + [pin("esp8266_nodemcu", "a0", "A0", "analog_input", "input", "right")],
        logic_voltage=3.3, protocols=["digital", "uart"],
    ))

    pico_pins = power_pins("raspberry_pi_pico", 3.3) + [pin("raspberry_pi_pico", f"gp{i}", f"GP{i}", "digital_io", "bidirectional", "right", logic_voltage=3.3) for i in range(29)]
    add(*comp("raspberry_pi_pico", "Raspberry Pi Pico", "controller", "genericControllerNode", pico_pins, logic_voltage=3.3, protocols=["digital", "analog", "pwm", "i2c"]))

    add(*comp(
        "microbit_v2", "BBC Micro:bit V2", "controller", "genericControllerNode",
        [pin("microbit_v2", "3v", "3V", "power_33v", "power_output", "left"), pin("microbit_v2", "gnd", "GND", "ground", "ground", "left")]
        + [pin("microbit_v2", f"p{i}", f"P{i}", "digital_io", "bidirectional", "right") for i in range(3)]
        + [pin("microbit_v2", "sda", "SDA", "i2c_sda", "bidirectional", "right"), pin("microbit_v2", "scl", "SCL", "i2c_scl", "bidirectional", "right")],
        logic_voltage=3.3, protocols=["digital", "i2c"],
    ))

    add(*comp("attiny85_module", "ATtiny85 Module", "controller", "genericControllerNode", power_pins("attiny85_module", 5) + [pin("attiny85_module", f"pb{i}", f"PB{i}", "digital_io", "bidirectional", "right") for i in range(6)], logic_voltage=5))
    add(*comp("stm32_blue_pill", "STM32 Blue Pill", "controller", "genericControllerNode", power_pins("stm32_blue_pill", 3.3) + [pin("stm32_blue_pill", f"pa{i}", f"PA{i}", "digital_io", "bidirectional", "right") for i in range(8)], logic_voltage=3.3))
    add(*comp("teensy_lc", "Teensy LC", "controller", "genericControllerNode", power_pins("teensy_lc", 3.3) + [pin("teensy_lc", f"d{i}", f"D{i}", "digital_io", "bidirectional", "right") for i in range(12)], logic_voltage=3.3))

    # Ultrasonic
    hc_pins = [
        pin("hc_sr04", "vcc", "VCC", "power_5v", "power_input", "left", allowed_voltage_min=5, allowed_voltage_max=5),
        pin("hc_sr04", "gnd", "GND", "ground", "ground", "left"),
        pin("hc_sr04", "trig", "TRIG", "digital_input", "input", "right"),
        pin("hc_sr04", "echo", "ECHO", "digital_output", "output", "right", logic_voltage=5),
    ]
    add(*comp("hc_sr04", "HC-SR04 Ultrasonic Sensor", "sensor", "ultrasonicSensorNode", hc_pins, logic_voltage=5, safety_level="safe_beginner"))

    for cid, name, node in [
        ("dht11", "DHT11 Temperature Humidity Sensor", "dhtSensorNode"),
        ("dht22", "DHT22 Temperature Humidity Sensor", "dhtSensorNode"),
    ]:
        add(*comp(cid, name, "sensor", node, simple_sensor_pins(cid, 5) + [pin(cid, "data", "DATA", "data", "bidirectional", "right")], logic_voltage=5))

    add(*comp("lm35", "LM35 Temperature Sensor", "sensor", "genericSensorNode", simple_sensor_pins("lm35", 5)))
    add(*comp("ds18b20", "DS18B20 Temperature Sensor", "sensor", "genericSensorNode", simple_sensor_pins("ds18b20", 5) + [pin("ds18b20", "data", "DATA", "data", "bidirectional", "right")]))

    for cid, name in [
        ("pir_sensor", "PIR Motion Sensor"), ("ir_line_sensor", "IR Line Tracking Sensor"),
        ("ir_receiver", "IR Receiver Module"), ("reed_switch", "Reed Switch Module"),
        ("hall_sensor", "Hall Effect Sensor"), ("touch_sensor", "Capacitive Touch Sensor"),
        ("tilt_sensor", "Tilt Sensor Module"),
    ]:
        node = "pirSensorNode" if cid == "pir_sensor" else "genericSensorNode"
        add(*comp(cid, name, "sensor", node, simple_sensor_pins(cid, 5)))

    for cid, name in [
        ("ldr_module", "LDR Light Sensor Module"), ("soil_moisture_sensor", "Soil Moisture Sensor"),
        ("rain_sensor", "Rain Sensor Module"), ("flame_sensor", "Flame Sensor Module"),
        ("mq2_gas_sensor", "MQ-2 Gas Sensor"), ("sound_sensor", "Sound Sensor Module"),
    ]:
        add(*comp(cid, name, "sensor", "genericSensorNode", sensor_module_pins(cid, 5)))

    for cid, name in [("mpu6050", "MPU-6050 Accelerometer Gyroscope"), ("bmp280", "BMP280 Pressure Sensor"), ("bme280", "BME280 Environmental Sensor")]:
        add(*comp(cid, name, "sensor", "genericSensorNode", i2c_sensor_pins(cid, 3.3), logic_voltage=3.3, protocols=["i2c"]))

    add(*comp(
        "rotary_encoder", "Rotary Encoder", "input", "genericSensorNode",
        [pin("rotary_encoder", "clk", "CLK", "digital_output", "output", "right"), pin("rotary_encoder", "dt", "DT", "digital_output", "output", "right"),
         pin("rotary_encoder", "sw", "SW", "digital_input", "input", "right")] + power_pins("rotary_encoder", 5)[2:],
    ))
    add(*comp("potentiometer", "Potentiometer", "input", "genericSensorNode", passive_terminals("potentiometer") + [pin("potentiometer", "out", "OUT", "analog_output", "output", "right")], requires_power=False, is_passive=True))
    add(*comp("push_button", "Push Button", "input", "genericSensorNode", passive_terminals("push_button"), requires_power=False, is_passive=True))
    add(*comp(
        "joystick_module", "Joystick Module", "input", "genericSensorNode",
        power_pins("joystick_module", 5)[:2] + [pin("joystick_module", "gnd", "GND", "ground", "ground", "left"),
        pin("joystick_module", "vrx", "VRX", "analog_output", "output", "right"), pin("joystick_module", "vry", "VRY", "analog_output", "output", "right"),
        pin("joystick_module", "sw", "SW", "digital_input", "input", "right")],
    ))

    # Outputs
    for cid, name, color in [("led_red", "Red LED", "red"), ("led_green", "Green LED", "green"), ("led_blue", "Blue LED", "blue")]:
        add(*comp(cid, name, "output", "ledNode", [
            pin(cid, "anode", "A+", "signal", "input", "left"),
            pin(cid, "cathode", "C-", "ground", "ground", "right"),
        ], requires_power=False, is_passive=True, safety_level="caution"))

    add(*comp("rgb_led_common_cathode", "RGB LED Common Cathode", "output", "rgbLedNode", [
        pin("rgb_led_common_cathode", "r", "R", "signal", "input", "left"),
        pin("rgb_led_common_cathode", "g", "G", "signal", "input", "left"),
        pin("rgb_led_common_cathode", "b", "B", "signal", "input", "left"),
        pin("rgb_led_common_cathode", "cathode", "Cathode", "ground", "ground", "right"),
    ], requires_power=False, is_passive=True, safety_level="caution"))

    for cid, name in [("active_buzzer", "Active Buzzer"), ("passive_buzzer", "Passive Buzzer")]:
        add(*comp(cid, name, "output", "buzzerNode", [
            pin(cid, "positive", "+", "power_input", "power_input", "left"),
            pin(cid, "negative", "-", "ground", "ground", "right"),
        ]))

    add(*comp("sg90_servo", "SG90 Servo Motor", "output", "servoNode", [
        pin("sg90_servo", "vcc", "VCC", "power_5v", "power_input", "left"),
        pin("sg90_servo", "gnd", "GND", "ground", "ground", "left"),
        pin("sg90_servo", "signal", "SIGNAL", "pwm", "input", "right"),
    ], safety_level="caution", current_draw_ma=250))

    add(*comp("dc_motor_small", "Small DC Motor", "output", "motorNode", passive_terminals("dc_motor_small"), safety_level="requires_driver", requires_power=True))
    add(*comp("vibration_motor", "Vibration Motor", "output", "motorNode", [
        pin("vibration_motor", "positive", "+", "motor_terminal", "passive", "left"),
        pin("vibration_motor", "negative", "-", "ground", "ground", "right"),
    ], safety_level="requires_driver"))

    stepper_pins = [pin("stepper_28byj48", f"in{i}", f"IN{i}", "digital_input", "input", "left") for i in range(1, 5)] + power_pins("stepper_28byj48", 5)[:2]
    add(*comp("stepper_28byj48", "28BYJ-48 Stepper Motor", "output", "motorNode", stepper_pins, safety_level="requires_driver"))

    add(*comp("relay_module_5v", "5V Relay Module", "output", "driverModuleNode", [
        pin("relay_module_5v", "vcc", "VCC", "power_5v", "power_input", "left"),
        pin("relay_module_5v", "gnd", "GND", "ground", "ground", "left"),
        pin("relay_module_5v", "in", "IN", "digital_input", "input", "right"),
        pin("relay_module_5v", "com", "COM", "relay_terminal", "bidirectional", "right"),
        pin("relay_module_5v", "no", "NO", "relay_terminal", "bidirectional", "right"),
        pin("relay_module_5v", "nc", "NC", "relay_terminal", "bidirectional", "right"),
    ], safety_level="caution"))

    for cid, name in [("oled_i2c_096", "0.96 inch OLED I2C Display"), ("lcd_16x2_i2c", "16x2 LCD I2C Display")]:
        add(*comp(cid, name, "display", "displayNode", i2c_sensor_pins(cid, 3.3), protocols=["i2c"]))

    add(*comp("seven_segment_display", "7 Segment Display", "display", "displayNode", [pin("seven_segment_display", "common", "COM", "power_input", "power_input", "left")] + [pin("seven_segment_display", f"seg{i}", f"SEG{i}", "digital_input", "input", "right") for i in range(8)]))
    add(*comp("max7219_led_matrix", "MAX7219 LED Matrix", "display", "displayNode", i2c_sensor_pins("max7219_led_matrix", 5) + [pin("max7219_led_matrix", "din", "DIN", "spi_mosi", "input", "right"), pin("max7219_led_matrix", "cs", "CS", "spi_cs", "input", "right"), pin("max7219_led_matrix", "clk", "CLK", "spi_sck", "input", "right")], protocols=["spi"]))
    add(*comp("neopixel_strip", "NeoPixel LED Strip", "output", "displayNode", power_pins("neopixel_strip", 5)[:3] + [pin("neopixel_strip", "data", "DATA", "data", "input", "right")]))
    add(*comp("small_speaker", "Small Speaker", "output", "genericComponentNode", passive_terminals("small_speaker")))

    # Drivers & modules
    add(*comp("l298n_motor_driver", "L298N Motor Driver", "driver", "driverModuleNode", power_pins("l298n_motor_driver", 5) + [
        pin("l298n_motor_driver", f"in{i}", f"IN{i}", "driver_input", "input", "left") for i in (1, 2)
    ] + [pin("l298n_motor_driver", "ena", "ENA", "pwm", "input", "left")] + [
        pin("l298n_motor_driver", f"out{i}", f"OUT{i}", "driver_output", "output", "right") for i in (1, 2)
    ]))
    add(*comp("tb6612fng_motor_driver", "TB6612FNG Motor Driver", "driver", "driverModuleNode", [
        pin("tb6612fng_motor_driver", "vm", "VM", "power_input", "power_input", "left"),
        pin("tb6612fng_motor_driver", "vcc", "VCC", "power_5v", "power_input", "left"),
        pin("tb6612fng_motor_driver", "gnd", "GND", "ground", "ground", "left"),
    ] + [pin("tb6612fng_motor_driver", f"ain{i}", f"AIN{i}", "driver_input", "input", "left") for i in (1, 2)]
      + [pin("tb6612fng_motor_driver", "pwma", "PWMA", "pwm", "input", "left")]
      + [pin("tb6612fng_motor_driver", f"ao{i}", f"AO{i}", "motor_output", "output", "right") for i in (1, 2)]))
    add(*comp("uln2003_driver", "ULN2003 Stepper Driver", "driver", "driverModuleNode", power_pins("uln2003_driver", 5) + [pin("uln2003_driver", f"in{i}", f"IN{i}", "driver_input", "input", "left") for i in range(1, 5)]))
    add(*comp("logic_level_shifter", "Logic Level Shifter", "interface", "driverModuleNode", [
        pin("logic_level_shifter", "hv", "HV", "power_5v", "power_input", "left"),
        pin("logic_level_shifter", "lv", "LV", "power_33v", "power_input", "left"),
        pin("logic_level_shifter", "gnd", "GND", "ground", "ground", "left"),
    ] + [pin("logic_level_shifter", f"hv{i}", f"HV{i}", "digital_io", "bidirectional", "right") for i in range(1, 5)]
      + [pin("logic_level_shifter", f"lv{i}", f"LV{i}", "digital_io", "bidirectional", "right") for i in range(1, 5)]))
    add(*comp("mosfet_module", "MOSFET Driver Module", "driver", "driverModuleNode", power_pins("mosfet_module", 5) + [pin("mosfet_module", "sig", "SIG", "digital_input", "input", "right")]))

    for cid, name in [("npn_transistor", "NPN Transistor"), ("pn2222_transistor", "PN2222 Transistor")]:
        add(*comp(cid, name, "support", "transistorNode", [
            pin(cid, "base", "B", "digital_input", "input", "left"),
            pin(cid, "collector", "C", "passive_terminal", "passive", "right"),
            pin(cid, "emitter", "E", "ground", "ground", "right"),
        ], requires_power=False, is_passive=True))

    add(*comp("flyback_diode", "Flyback Diode", "protection", "diodeNode", [
        pin("flyback_diode", "anode", "A", "passive_terminal", "passive", "left"),
        pin("flyback_diode", "cathode", "C", "passive_terminal", "passive", "right"),
    ], requires_power=False, is_passive=True))

    add(*comp("rc522_rfid", "RC522 RFID Module", "module", "genericComponentNode", i2c_sensor_pins("rc522_rfid", 3.3) + [
        pin("rc522_rfid", "sck", "SCK", "spi_sck", "input", "right"),
        pin("rc522_rfid", "mosi", "MOSI", "spi_mosi", "input", "right"),
        pin("rc522_rfid", "miso", "MISO", "spi_miso", "output", "right"),
        pin("rc522_rfid", "rst", "RST", "digital_input", "input", "right"),
    ], protocols=["spi"]))
    add(*comp("micro_sd_module", "MicroSD Card Module", "module", "genericComponentNode", power_pins("micro_sd_module", 3.3)[:2] + [pin("micro_sd_module", "gnd", "GND", "ground", "ground", "left")] + [
        pin("micro_sd_module", "cs", "CS", "spi_cs", "input", "right"),
        pin("micro_sd_module", "sck", "SCK", "spi_sck", "input", "right"),
        pin("micro_sd_module", "mosi", "MOSI", "spi_mosi", "input", "right"),
        pin("micro_sd_module", "miso", "MISO", "spi_miso", "output", "right"),
    ], logic_voltage=3.3, protocols=["spi"]))
    add(*comp("rtc_ds3231", "DS3231 RTC Module", "module", "genericComponentNode", i2c_sensor_pins("rtc_ds3231", 5), protocols=["i2c"]))
    add(*comp("bluetooth_hc05", "HC-05 Bluetooth Module", "module", "genericComponentNode", power_pins("bluetooth_hc05", 5)[:2] + [
        pin("bluetooth_hc05", "gnd", "GND", "ground", "ground", "left"),
        pin("bluetooth_hc05", "txd", "TXD", "uart_tx", "output", "right"),
        pin("bluetooth_hc05", "rxd", "RXD", "uart_rx", "input", "right"),
    ], protocols=["uart"]))
    add(*comp("shift_register_74hc595", "74HC595 Shift Register", "ic", "genericComponentNode", power_pins("shift_register_74hc595", 5) + [
        pin("shift_register_74hc595", "ser", "SER", "spi_mosi", "input", "right"),
        pin("shift_register_74hc595", "rclk", "RCLK", "digital_input", "input", "right"),
        pin("shift_register_74hc595", "srclk", "SRCLK", "spi_sck", "input", "right"),
    ] + [pin("shift_register_74hc595", f"q{i}", f"Q{i}", "digital_output", "output", "right") for i in range(8)]))

    # Passives & support
    for cid, name in [
        ("resistor_220", "220 Ohm Resistor"), ("resistor_330", "330 Ohm Resistor"),
        ("resistor_1k", "1k Ohm Resistor"), ("resistor_10k", "10k Ohm Resistor"),
    ]:
        add(*comp(cid, name, "passive", "resistorNode", passive_terminals(cid), requires_power=False, is_passive=True))

    for cid, name in [("capacitor_100nf", "100nF Ceramic Capacitor")]:
        add(*comp(cid, name, "passive", "genericComponentNode", passive_terminals(cid), requires_power=False, is_passive=True))

    for cid, name in [("capacitor_10uf", "10uF Capacitor"), ("capacitor_100uf", "100uF Capacitor")]:
        add(*comp(cid, name, "passive", "genericComponentNode", [
            pin(cid, "positive", "+", "passive_terminal", "passive", "left"),
            pin(cid, "negative", "-", "ground", "ground", "right"),
        ], requires_power=False, is_passive=True))

    add(*comp("breadboard", "Breadboard", "support", "breadboardNode", [
        pin("breadboard", "power_rails", "Power Rails", "power_input", "power_input", "top"),
        pin("breadboard", "terminals", "Terminals", "passive_terminal", "passive", "bottom"),
    ], requires_power=False))
    add(*comp("jumper_wires", "Jumper Wires", "support", "genericComponentNode", [pin("jumper_wires", "generic", "Wire", "passive_terminal", "passive", "right")], requires_power=False))
    add(*comp("aa_battery_pack", "AA Battery Pack", "power", "genericComponentNode", [
        pin("aa_battery_pack", "positive", "+", "power_input", "power_output", "right"),
        pin("aa_battery_pack", "negative", "-", "ground", "ground", "right"),
    ], provides_power=True, requires_power=False))
    add(*comp("battery_9v_connector", "9V Battery Connector", "power", "genericComponentNode", [
        pin("battery_9v_connector", "positive", "+", "power_input", "power_output", "right"),
        pin("battery_9v_connector", "negative", "-", "ground", "ground", "right"),
    ], provides_power=True, requires_power=False))
    add(*comp("usb_power_module", "USB Breadboard Power Module", "power", "genericComponentNode", power_pins("usb_power_module", 5), provides_power=True))
    for cid, name, vout in [("voltage_regulator_5v", "5V Voltage Regulator", 5), ("voltage_regulator_33v", "3.3V Voltage Regulator", 3.3)]:
        add(*comp(cid, name, "power", "genericComponentNode", [
            pin(cid, "vin", "VIN", "power_input", "power_input", "left"),
            pin(cid, "gnd", "GND", "ground", "ground", "left"),
            pin(cid, "vout", "VOUT", "power_5v" if vout >= 5 else "power_33v", "power_output", "right", allowed_voltage_min=vout, allowed_voltage_max=vout),
        ], provides_power=True))

    rules = [
        {
            "id": "rule_led_resistor",
            "rule_name": "LED requires resistor",
            "applies_to_category": "output",
            "condition_json": {"requires_component_categories": ["passive"], "led_ids": ["led_red", "led_green", "led_blue", "rgb_led_common_cathode"]},
            "severity": "blocking",
            "message": "LEDs require a current-limiting resistor in series.",
            "required_component_ids": ["resistor_220", "resistor_330"],
            "required_component_categories": [],
            "blocking": True,
        },
        {
            "id": "rule_motor_driver",
            "rule_name": "DC motor requires driver",
            "applies_to_component_id": "dc_motor_small",
            "condition_json": {"requires_driver": True},
            "severity": "blocking",
            "message": "A DC motor should not connect directly to a microcontroller pin. Use a motor driver.",
            "required_component_ids": ["l298n_motor_driver", "tb6612fng_motor_driver"],
            "required_component_categories": ["driver"],
            "blocking": True,
        },
        {
            "id": "rule_common_ground",
            "rule_name": "Common ground required",
            "applies_to_category": None,
            "condition_json": {"requires_common_ground": True},
            "severity": "warning",
            "message": "All powered modules should share a common ground.",
            "required_component_ids": [],
            "required_component_categories": [],
            "blocking": False,
        },
        {
            "id": "rule_level_shifter",
            "rule_name": "3.3V protection from 5V",
            "applies_to_category": "controller",
            "condition_json": {"logic_mismatch": [5, 3.3]},
            "severity": "blocking",
            "message": "5V signals may damage 3.3V-only inputs. Use a logic level shifter.",
            "required_component_ids": ["logic_level_shifter"],
            "required_component_categories": [],
            "blocking": True,
        },
    ]

    return components, pins, rules
