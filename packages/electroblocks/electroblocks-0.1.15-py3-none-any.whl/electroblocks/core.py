import serial
import serial.tools.list_ports
import time
from enum import Enum

class ComponentPins(Enum):
    UNKNOWN = 0
    LCD = 1
    RGBLED = 2
    DIGITAL_WRITE = 3
    ANALOG_WRITE = 4
    RGB_LED_STRIP = 5
    SERVO = 6
    LED_MATRIX = 7
    DIGITAL_DISPLAY_TM = 8
    MOTOR = 9
    PASSIVE_BUZZER = 10
    STEPPER_MOTOR = 11
    BUTTON = 12
    IR_REMOTE = 13
    DIGITAL_READ = 14
    JOYSTICK = 16
    ULTRASONIC_SENSOR = 17
    RFID = 18,
    TEMP = 19,
    THERMISTOR = 20


class ElectroBlocks:

    last_sense_data = ""
    verbose = False
    pins = {}

    # Known vendor IDs (decimal) 
    KNOWN_VIDS = {
        9025,   # 0x2341 - Arduino
        6790,   # 0x1A86 - WCH (CH340/CH341)
        4292,   # 0x10C4 - Silicon Labs (CP210x)
        1027,   # 0x0403 - FTDI
        1659,   # 0x067B - Prolific
    }

    # Known product IDs (decimal)
    KNOWN_PIDS = {
        67,       # 0x0043 - Uno R3 PID
        66,       # 0x0042 - Mega R3 PID (common variant)
        16,       # 0x0010 - Mega2560 pre-R3
        60000,    # 0xEA60 - CP210x example (Silicon Labs)
        29987,    # 0x7523 - CH340 common PID
        24577,    # 0x6001 - FTDI FT232
        24592,    # 0x6010 - FTDI FT2232
        24593,    # 0x6011 - FTDI FT4232
        24596,    # 0x6014 - FTDI variant
        24597,    # 0x6015 - FTDI FT231X
    }

    def __init__(self, baudrate=115200, timeout=2, verbose = False):
        self.ser = self._auto_connect(baudrate, timeout)
        self.verbose = verbose
        self._wait_for_ready()
        self._cache = None
        self._cache_time = 0
        self._cache_ttl = 0.08  # 80 milliseconds
 
    def _auto_connect(self, baudrate, timeout):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if p.vid in self.KNOWN_VIDS or p.pid in self.KNOWN_VIDS: 
                try:
                    ser = serial.Serial(p.device, baudrate, timeout=timeout)
                    time.sleep(2)  # Give Arduino time to reset
                    return ser
                except serial.SerialException as e:
                    print(f"Failed to connect to {e}. Trying next port...")
                    continue
        raise Exception("No Arduino Uno or Mega found.")
    
    def _drain_serial(self):
        """Drains/clears the serial port input buffer of any unread messages."""
        if self.ser and self.ser.is_open:
            self.ser.reset_input_buffer()


    def _add_pin(self, pinType, pin):
        if pinType not in self.pins:
            self.pins[pinType] = [str(pin)]
        else:
            self.pins[pinType].append(str(pin))


    def _wait_for_message(self, message):
        count = 0
        while count < 10:
            if self.ser.in_waiting:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if message in line:
                    return line
            count += 1
            time.sleep(0.05)
        if self.verbose:
            print(f"DEBUG: MESSAGE NOT FOUND: '{message}'")
        return ""

    def _get_sensor_str(self):
        now = time.monotonic()
        
        # If cached value is still fresh, return it
        if self._cache and (now - self._cache_time) < self._cache_ttl:
            if self.verbose:
                print("Using cached sensor message")
            return self._cache
        
        # Otherwise fetch new data
        self.ser.write(b"sense|")
        message = self._wait_for_message("SENSE_COMPLETE")
        if self.verbose:
            print(f"FULL SENSOR MESSAGE: {message}")
        message = message.replace("SENSE_COMPLETE", "")
        sensorsStr = message.split(";")

        # Update cache
        self._cache = sensorsStr
        self._cache_time = now

        return sensorsStr
    
    # return the result of pin read that is being sensed
    def _find_sensor_str(self, sensorPin, sensorType):
        sensorsStr = self._get_sensor_str()
        for sensor in sensorsStr:
            if len(sensor) == 0:
                continue
            [type, pin, result] = sensor.split(":")
            if (type == sensorType and pin == str(sensorPin)):
                return result

        return ""

    def _wait_for_ready(self):
        self.ser.write(b"IAM_READY|")
        self._wait_for_message("System:READY")

    def _send(self, cmd):
        self.ser.write((cmd + "|\n").encode())
        self._wait_for_message("OK")

    # Digital Write Method
    def config_digital_read(self, pin):
        self._add_pin(ComponentPins.DIGITAL_READ, pin)
        self._send(f"register::dr::{pin}")

    def digital_read(self, pin):
        return self._find_sensor_str(pin, "dr") == "1"
    
    # RFID
    def config_rfid(self, rxPin, txPin):
        self._add_pin(ComponentPins.RFID, rxPin)
        self._add_pin(ComponentPins.RFID, txPin)
        self._send(f"register::rfi::{rxPin}::{txPin}::9600")

    def rfid_tag_number(self):
        pin = self.pins[ComponentPins.RFID][0]
        tag = self._find_sensor_str(pin, "rfi")
        if tag == "0":
            return ""
        else:
            return tag

    def rfid_sensed_card(self):
        pin = self.pins[ComponentPins.RFID][0]
        return self._find_sensor_str(pin, "rfi") != "0"
    
    # Joysick
    def config_joystick(self, x, y, sw):
        self._send(f"register::js::{x}::{y}::{sw}")
        self._add_pin(ComponentPins.JOYSTICK, x)
        self._add_pin(ComponentPins.JOYSTICK, y)
        self._add_pin(ComponentPins.JOYSTICK, sw)

    def joystick_angle(self):
        pin = self.pins[ComponentPins.JOYSTICK][0]
        [pressed, angle, engaged] = self._find_sensor_str(pin, "js").split('-')
        return angle

    def is_joystick_button_pressed(self):
        pin = self.pins[ComponentPins.JOYSTICK][0]
        [pressed, angle, engaged] = self._find_sensor_str(pin, "js").split('-')
        return pressed

    def is_joystick_engaged(self):
        pin = self.pins[ComponentPins.JOYSTICK][0]
        [pressed, angle, engaged] = self._find_sensor_str(pin, "js").split('-')
        return pressed

    # Temp
    def config_dht_temp(self, pin, type):
        tempType = "1" if type == "DHT11" else "2"
        self._send(f"register::dht::{pin}::{tempType}")
        self._add_pin(ComponentPins.TEMP, pin)

    def dht_temp_celcius(self):
        pin = self.pins[ComponentPins.TEMP][0]
        [humidity, temp] = self._find_sensor_str(pin, "dht").split('-')
        return temp

    def dht_temp_humidity(self):
        pin = self.pins[ComponentPins.TEMP][0]
        [humidity, temp] = self._find_sensor_str(pin, "dht").split('-')
        return humidity

    # Thermistor

    def config_thermistor(self, pin):
        self._send(f"register::th::{pin}")
        self._add_pin(ComponentPins.THERMISTOR, pin)

    def thermistor_celsius(self):
        pin = self.pins[ComponentPins.THERMISTOR][0]
        return self._find_sensor_str(pin, "th")

    def thermistor_fahrenheit(self):
        pin = self.pins[ComponentPins.THERMISTOR][0]
        temp = self._find_sensor_str(pin, "th")
        if (temp == ''):
            return ''
        else:
            return 32 + (9/5 * float(temp))

    #IR Remote

    def config_ir_remote(self, pin):
        self._send(f"register::ir::{pin}")
        self._add_pin(ComponentPins.IR_REMOTE, pin)

    def ir_remote_has_sensed_code(self):
        pin = self.pins[ComponentPins.IR_REMOTE][0]
        return len(self._find_sensor_str(pin, "ir")) > 0
    
    def ir_remote_get_code(self):
        pin = self.pins[ComponentPins.IR_REMOTE][0]
        return self._find_sensor_str(pin, "ir")

    # Motion Sensors
    def config_motion_sensor(self, echoPin, trigPin):
        self._add_pin(ComponentPins.ULTRASONIC_SENSOR, trigPin)
        self._add_pin(ComponentPins.ULTRASONIC_SENSOR, echoPin)
        self._send(f"register::ul::{trigPin}::{echoPin}")

    def motion_distance_cm(self):
        pin = self.pins[ComponentPins.ULTRASONIC_SENSOR][0]
        return self._find_sensor_str(pin, "ul")

    # Button Methods
    def config_button(self, pin):
        self._send(f"register:bt::{pin}")
        self._add_pin(ComponentPins.BUTTON, pin)

    def is_button_pressed(self, pin):
        return self._find_sensor_str(pin, "bt") == "0"

    # Servo Methods
    def config_servo(self, pin):
        self._send(f"register::servo::{pin}")

    def move_servo(self, pin, angle):
        self._send(f"write::servo::{pin}::{angle}")

    # RGB Methods
    def config_rgbled(self, r_pin, g_pin, b_pin):
        self._add_pin(ComponentPins.RGBLED, r_pin)
        self._add_pin(ComponentPins.RGBLED, g_pin)
        self._add_pin(ComponentPins.RGBLED, b_pin)
        self._send(f"register::rgb::{r_pin}::{g_pin}::{b_pin}")

    def set_color_rgbled(self, r, g, b):
        redpin = self.pins[ComponentPins.RGBLED][0]
        self._send(f"write::rgb::{redpin}::{r}::{g}::{b}")

    # LCD Methods
    def config_lcd(self, rows=2, cols=16, addr=39):
        self._add_pin(ComponentPins.DIGITAL_WRITE, "A5")
        self._add_pin(ComponentPins.DIGITAL_WRITE, "A4")
        self._send(f"register::lcd::{rows}::{cols}::{addr}")

    def lcd_print(self, row, col, message):
        self._send(f"write::lcd::A5::9::{row}::{col}::{message}")

    def lcd_clear(self):
        self._send("write::lcd::A5::1")

    def lcd_toggle_backlight(self, on):
        if on:
            self._send("write::lcd::A5::2")
        else:
            self._send("write::lcd::A5::3")

    def lcd_blink_curor(self, row, col, on):
        if on == True:
            self._send(f"write::lcd::A5::5::{row}::{col}")
        else:
            self._send(f"write::lcd::A5::4")

    def lcd_scrollright(self):
        self._send("write::lcd::A5::6")

    def lcd_scrollleft(self):
        self._send("write::lcd::A5::7")

    # LED Methods

    def digital_config(self, pin):
        self._add_pin(ComponentPins.DIGITAL_WRITE, pin)
        self._send(f"register::dw::{pin}")

    def digital_write(self, pin, value):
        self._send(f"write::dw::{pin}::{value}")

    def analog_write(self, pin, value):
        self._send(f"write::aw::{pin}::{value}")
    
    def analog_config(self, pin):
        self._send(f"register::aw::{pin}")
        self._add_pin(ComponentPins.ANALOG_WRITE, pin)

    # LED MATRIX

    def config_led_matrix(self, data_pin, cs_pin, clk_pin):
        self._add_pin(ComponentPins.LED_MATRIX, data_pin)
        self._add_pin(ComponentPins.LED_MATRIX, cs_pin)
        self._add_pin(ComponentPins.LED_MATRIX, clk_pin)
        self._send(f"register::ma::{data_pin}::{cs_pin}::{clk_pin}")

    def set_led_matrix_led(self, row, col, isOn):
        pin = self.pins[ComponentPins.LED_MATRIX][0]
        isLedOnNumber = "1" if isOn else "0"
        self._send(f"write::ma::{pin}::1::{col - 1}::{8 - row}::{isLedOnNumber}")
    
    # TM Digital Display

    def config_digital_display(self, dio, clk):
        self._add_pin(ComponentPins.DIGITAL_DISPLAY_TM, dio)
        self._add_pin(ComponentPins.DIGITAL_DISPLAY_TM, clk)
        self._send(f"register::tm::{dio}::{clk}")

    def set_digital_display(self, colonOn, message):
        pin = self.pins[ComponentPins.DIGITAL_DISPLAY_TM][0]
        colon = "1" if colonOn else "0"
        self._send(f"write::tm::{pin}::{colon}::{message}")

    # Stepper Motors

    def config_stepper_motor(self, pin1, pin2, pin3, pin4, steps, speed):
        self._add_pin(ComponentPins.STEPPER_MOTOR, pin1)
        self._add_pin(ComponentPins.STEPPER_MOTOR, pin2)
        self._add_pin(ComponentPins.STEPPER_MOTOR, pin3)
        self._add_pin(ComponentPins.STEPPER_MOTOR, pin4)
        self._send(f"register::ste::{pin1}::{pin2}::{pin3}::{pin4}::{steps}::{speed}")

    def move_stepper_motor(self, steps):
        pin = self.pins[ComponentPins.STEPPER_MOTOR][0]
        self._send(f"write::ste::{pin}::{steps}")


    # Motors

    def config_motor(self, en1, in1, in2, en2 = None, in3 = None, in4 = None):
        self._add_pin(ComponentPins.MOTOR, en1)
        self._add_pin(ComponentPins.MOTOR, in1)
        self._add_pin(ComponentPins.MOTOR, in2)
        if en2 == None or in3 == None or in4 == None:
            self._send(f"register::mo::{en1}::{in1}::{in2}")
        else:
            self._add_pin(ComponentPins.MOTOR, en2)
            self._add_pin(ComponentPins.MOTOR, in3)
            self._add_pin(ComponentPins.MOTOR, in4)
            self._send(f"register::mo::{en1}::{in1}::{in2}::{en2}::{in3}::{in4}")

    def move_motor(self, which_motor, direction, speed):
            pin = self.pins[ComponentPins.MOTOR][0]
            direction_num = "1" if direction == "clockwise" else "2"
            self._send(f"write::mo::{pin}::{which_motor}::{speed}::{direction_num}")

    
    def stop_motor(self, which_motor):
        pin = self.pins[ComponentPins.MOTOR][0]
        self._send(f"write::mo::{pin}::{which_motor}::0::3")

    # NEO PIXELS

    def config_rgb_strip(self, pin, count, colorOrderString, brightness):
        orderToNumber = {
            "RGB": 128,
            "GRB": 129,
            "RBG": 130,
            "GBR": 131,
            "BRG": 132,
            "BGR": 133,
        }
        colorOrder = orderToNumber.get(colorOrderString) or 128
        self._add_pin(ComponentPins.RGB_LED_STRIP, pin)
        self._send(f"register::leds::{pin}::{count}::{colorOrder}::{brightness}")


    def rgb_strip_set_color(self, position, red, green, blue):
        """Set color for RGB LED strip at specified position"""
        pin = self.pins[ComponentPins.RGB_LED_STRIP][0]
        color = self.rgb_to_hex(red, green, blue)
        self._send(f"write::leds::{pin}::2::{position}::{color}")

    def rgb_strip_show_all(self):
        pin = self.pins[ComponentPins.RGB_LED_STRIP][0]
        self._send(f"write::leds::{pin}::1")

    # Passive Buzzer

    def config_passive_buzzer(self, pin):
        self._add_pin(ComponentPins.PASSIVE_BUZZER, pin)
        self._send(f"register::bu::{pin}")

    def play_passive_buzzer(self, pin, note):
        self._send(f"write::bu::{pin}::{note}")

    def turn_off_buzzer(self, pin):
        self._send(f"write::bu::{pin}::0")

    # Helpers

    def rgb_to_hex(self, red, green, blue):
        """
        Convert RGB values (0-255) to a hex color string format (#RRGGBB)
        
        Args:
            red (int): Red value (0-255)
            green (int): Green value (0-255)  
            blue (int): Blue value (0-255)
            
        Returns:
            str: Hex color string in format RRGGBB
        """
        # Ensure values are within valid range (0-255)
        red = max(0, min(255, int(red)))
        green = max(0, min(255, int(green)))
        blue = max(0, min(255, int(blue)))
        
        # Convert to hex and format with leading zeros if needed
        return f"{red:02x}{green:02x}{blue:02x}".upper()


    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()