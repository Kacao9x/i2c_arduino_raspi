#import RPi.GPIO as GPIO
# import smbus
from smbus2 import SMBus, SMBusWrapper
import RPi.GPIO as GPIO

import subprocess, re, sys
import time as time
from enum import Enum
import os, json
# import time, os, json

import unittest

ARDUINO_ENCLOSURE_ADDR  = 0x04
ARDUINO_BOOL_PIN        = 23
# bus     = smbus.SMBus(1)    #pm

class Arduino_opcode_command(Enum):
    # softReset           = 100   # Reset arduino by software
    ready               = 101   # ready for test mode
    button_wait         = 102   # user push button
    lower_arm           = 103   # lower arm
    raise_arm           = 104   # send capture complete signal
    read_temp           = 105	# read object and ambient temperature
    softReset           = 20    # software Reset control by Pi

class Enclosure(object):
    # bus     = smbus.SMBus(1)        # pm

    i2c_addr    = None
    reg_values  = []

    def __init__(self, i2c_addr = ARDUINO_ENCLOSURE_ADDR, debug=False, debug_level = 1):
        '''
        Contructor
        '''
        self._debug         = debug
        self._debug_level   = debug_level
        self._class         = self.__class__.__name__

        self.i2c_addr       = i2c_addr

        # setup Arduino -> RPi boolean comm
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ARDUINO_BOOL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        #GPIO.add_event_detect(ARDUINO_BOOL_PIN, GPIO.RISING)


        # # check RPi -> Arduino I2C comm
        p = subprocess.Popen(['i2cdetect', '-y', '1'], stdout=subprocess.PIPE, )
        for i in range(0, 9):
            line = str(p.stdout.readline())
            for match in re.finditer("[0-9][0-9]:.*[0-9][0-9]", line):
                if not match.group():
                    print("Error connecting to Arduino")
                    exit(0)

        # self.turnOnTestMode()

        # with SMBusWrapper(1) as bus:
        #     try:
        #         readval = bus.read_i2c_block_data(self.i2c_addr, 0, 3)
        #         print ('[Init] readval i2c: {}'.format(readval))
        #     except:
        #         # To-do: determine exception here

        #         if i2c_addr != ARDUINO_ENCLOSURE_ADDR:
        #             self.dprint("Error: Arduino not detected")
        #         os._exit(1)
        # print ("I2C comm to Arduino successful")

    def write_request(self, value):
        self.dprint('LOCKED... for send_request')
        with SMBusWrapper(1) as bus:
            bus.write_i2c_block_data(self.i2c_addr, 0, value)
        bus.close()
        return -1

    def read_response(self):
        response = -1
        self.dprint('LOCKED... for read_request')
        with SMBusWrapper(1) as bus:
            response = bus.read_i2c_block_data(self.i2c_addr, 0, 4)
        bus.close()
        return response

    def writeRequest_readResponse(self, request):
        print("Starting w/r...")
        try:
            #Optional: send a request param (such as critical force)
            #request_cmd = [request, param]
            request_cmd = [request, 0]
            self.write_request(request_cmd)

            initial_time = int(round(time.time()))

            #waits 15 seconds for a response from Arduino
            while ( (int(round(time.time())) - initial_time) < 15 ):
                try:
                    if GPIO.input(ARDUINO_BOOL_PIN):
                        try:
                            time.sleep(0.05)
                            response_data = self.read_response()
                            print(response_data)
                            return response_data
                        except OSError:
                            #OSError while waiting for response (rare, every 150 tests or so)
                            return -1
                except KeyboardInterrupt:
                    GPIO.cleanup()
            return -1  #timeout, didn't receive response
        except OSError:
            return -1

    def writeNumber(self, value):
        with SMBusWrapper(1) as bus:
            bus.write_byte(self.i2c_addr, value)
            # bus.write_byte_data(address, 0, value)
        bus.close()
        return -1

    def readNumber(self):
        """
        Not currently in used
        """
        number = -1
        with SMBusWrapper(1) as bus:
            number = bus.read_byte(self.i2c_addr)
        bus.close()
        return number

    def errorHandler(self, value):
        if not os.path.exists(os.getcwd() + '/logs/'):
            os.makedirs(os.getcwd() + '/logs/')
        
        with open(os.getcwd() + '/logs/error_logs.json', 'wb') as writeout:
            writeout.write(json.dumps(value, indent=2))
        writeout.close()

        self.dprint("Error.")
        return


    def _check_runtime(self, value, timeout=2.0):
        init_time = time.time()
        response_data = self.writeRequest_readResponse(value)
        run_time = round(time.time() - init_time, 2)
        self.dprint ('run_time: {}'.format(run_time))
        if (run_time < timeout):
            self.dprint ('too short. Runtime {}'.format(run_time))
            raise RuntimeError

        return response_data


    def turnOnTestMode(self, value=Arduino_opcode_command.ready.value):
        '''
        Signal arduino to Enter the test mode
        :param value: 101
        :return: True if Arduino response back, False otherwise
        '''
        self.dprint ('[Debug] Send OP-code: 101 - "ready" to arduino...')
        response_data = self.writeRequest_readResponse(value)

        if response_data[2] == 201:                                         #NEEDS TO BE UPGRADED - (READ) -- PETE $$$$$
            print ('[debug] Arduino replied "Request Received. Starting Process..."')
            return True
        else:
            print ('[Debug] No reponse from arduino...')
            return False


    def pushButton(self, value=Arduino_opcode_command.button_wait.value):
        '''
        Signal arduino to wait for button held by user
        :param value: 102
        :return:
        '''
        self.dprint ('[Debug] Send OP-code: 102 - "push_button" to arduino...')

        response_data = self.writeRequest_readResponse(value)
        #response_data = self._check_runtime(value, timeout = 2.5)

        buttonPushed = False

        if response_data == -1:
            self.dprint ("[debug] Error reading / writing'")
            buttonPushed = False
        elif response_data[2] == 201:
            buttonPushed = True
            self.dprint("[debug] button Pushed ...")
        elif response_data[2] == 202:
            buttonPushed = False
            self.dprint("[debug] button Timeout ...")

        return buttonPushed == True


    def lowerArm(self, value=Arduino_opcode_command.lower_arm.value):
        '''
        Signal arduino to lower the arm
        :param value: 103
        :return:
        '''
        self.dprint ('[Debug] Send OP-code: 103 - "lower_arm" to arduino...')
           
        response_data = self._check_runtime(value, timeout=2.0)
        # response_data = self.writeRequest_readResponse(value)
        
        if response_data == -1:
            self.dprint ("[debug] Error reading / writing'")
            return False
        elif response_data[2] == 201:
            self.dprint ("[debug] Arduino responsed : response_201, 'Timeout, no force detected... ''")
            return True
        elif response_data[2] == 202:
            self.dprint("[debug] Arduino responded: response_202, 'Arm lowered, critical force reached... ''")
            return True
        elif response_data[2] == 1:
            self.dprint("[debug] Arduino hang. Raise arm or software reset''")
            return False


    def raiseArm(self, value=Arduino_opcode_command.raise_arm.value):
        '''
        Signal arduino to lyft tail after taking capture
        :param value: 104
        :return: True if done, false otherwise
        '''
        self.dprint ('[Debug] Send OP-code: 104 - "raise arm" to arduino...')

        response_data = self._check_runtime(value,timeout=2.0)
        # response_data = self.writeRequest_readResponse(value)

        if response_data == -1:
            self.dprint ("[debug] Error reading / writing'")
            return False
        if response_data[2] == 201:
            self.dprint("[debug] Enclosure Arm raised back to the top (time) ...")
            return True


    def readTempC(self, value=Arduino_opcode_command.read_temp.value):
        '''
        Signal arduino to read temperature
        :param value: 105
        :return:
        '''
        self.dprint ('[Debug] Send OP-code: 105 - "temperature reading" to arduino...')

        # response_data = self.writeRequest_readResponse(value)
        response_data = self._check_runtime(value, timeout=0.2)

        tempRead = False

        if response_data == -1:
            self.dprint ("[debug] Error reading / writing'")
            buttonPushed = False
        elif response_data[2] != -1:
            tempRead = True
            obj_temp_C = round((response_data[2]-32)*5/9, 3)
            sensor_temp_C = response_data[3]
            self.dprint("[debug] TempF {}F TempC {}C ...".format(response_data[2], obj_temp_C))
            self.dprint("ambient temp: {}C".format(sensor_temp_C))

        return obj_temp_C, sensor_temp_C


    def resetArduino(self, value=Arduino_opcode_command.softReset.value):
        """
        Reset arduino in case the clamming is stuck
        TO-DO: why the arm is not reset to starting position
        :param value: 20
        :return:
        """
        self.writeRequest_readResponse(value)


    # Prints messages with function and class
    def dprint(self, txt, timestamp=False, error=False, level = 1):

        if level <= self._debug_level:
            if self._debug or error:
                function_name = sys._getframe(1).f_code.co_name
                if timestamp:
                    print("  "+str(datetime.datetime.now())+" "+self._class+":"+function_name+"(): "+txt)
                else:
                    print("  "+self._class+":"+function_name+"(): "+txt)


class MLX90614():

    MLX90614_RAWIR1=0x04
    MLX90614_RAWIR2=0x05
    MLX90614_TA=0x06
    MLX90614_TOBJ1=0x07
    MLX90614_TOBJ2=0x08

    MLX90614_TOMAX=0x20
    MLX90614_TOMIN=0x21
    MLX90614_PWMCTRL=0x22
    MLX90614_TARANGE=0x23
    MLX90614_EMISS=0x24
    MLX90614_CONFIG=0x25
    MLX90614_ADDR=0x0E
    MLX90614_ID1=0x3C
    MLX90614_ID2=0x3D
    MLX90614_ID3=0x3E
    MLX90614_ID4=0x3F

    comm_retries = 5
    comm_sleep_amount = 0.1

    def __init__(self, i2c_address=0x5a, bus_num=1):
        self.bus_num = bus_num
        self.i2c_addr = i2c_address
        # self.bus = smbus.SMBus(bus=bus_num)

    def read_reg(self, reg_addr):
        err = None
        for i in range(self.comm_retries):
            try:
                with SMBusWrapper(1) as bus:
                    return bus.read_i2c_block_data(self.i2c_addr, reg_addr, 2)
                    # return bus.read_word_data(self.i2c_addr, reg_addr)
                bus.close()
                # return self.bus.read_word_data(self.i2c_addr, reg_addr)
            except IOError as e:
                err = e
                #"Rate limiting" - sleeping to prevent problems with sensor
                #when requesting data too quickly
                time.sleep(self.comm_sleep_amount)
        #By this time, we made a couple requests and the sensor didn't respond
        #(judging by the fact we haven't returned from this function yet)
        #So let's just re-raise the last IOError we got
        raise err

    def data_to_temp(self, data):
        temp_msb = data[1]
        temp_lsb = data[0]
        
        hex_temp = (temp_msb << 8 | temp_lsb)
        temp = float(hex_temp)*0.02 - 273.15
        
        ''' for using read_word_data'''
        # temp = float(data)*0.02 - 273.15
        return round(temp,3)


    def get_amb_temp(self):
        data = self.read_reg(self.MLX90614_TA)
        print ("amb_temp float {}".format(data))
        return self.data_to_temp(data)

    def get_obj_temp(self):
        data = self.read_reg(self.MLX90614_TOBJ1)
        print ("amb_temp float {}".format(data))
        return self.data_to_temp(data)


class Test(unittest.TestCase):

    Enclosure = Enclosure(debug=True, debug_level = 4)
    # Temp_sensor = MLX90614()

    def test_comm(self):
        result = self.Enclosure.turnOnTestMode()
        print ("successful" if result else "failed")


    def test_lower_arm(self):
        isComplete = self.Enclosure.lowerArm()

        if isComplete:
            print("test_lower_servo completed")
        else:
            print ("Servo Jam or crashed")


    def test_raise_arm(self):
        #self.test_lower_arm()
        isComplete = self.Enclosure.raiseArm()

        if isComplete:
            print("test_lower_servo completed")
        else:
            print ("Servo Jam or crashed")


    def test_push_button(self):
        for _ in range(100):
            buttonPushed = False
            buttonPushed = self.Enclosure.pushButton()

            if buttonPushed:
                time.sleep(0.1)
                try:
                    loweringServo = self.Enclosure.lowerArm()
                except OSError:
                    print ("reset arduino")
                    self.Enclosure.resetArduino()
                    
                time.sleep(3)
                self.Enclosure.readTempC()
                print ("read value successfully\n")
                time.sleep(1)

                try:
                    raisingTail = self.Enclosure.raiseArm()
                except:
                    # continue
                    print ("reset arduino")
                    self.Enclosure.resetArduino()
                    

                print ('test completed\n')
                time.sleep(3)
            else:
                print('test failed')


    def test_auto_mode(self):
        scan_num = 300

        failed_raising = 0
        failed_lowering = 0
        for counter in range(scan_num):
            try:
                loweringServo = self.Enclosure.lowerArm()
            except OSError:
                # continue
                print ("reset arduino")
                self.Enclosure.resetArduino()
            except RuntimeError:
                time.sleep(2.5)
                print ("lower mode run too fast")
                failed_lowering += 1
                # os._exit(1)

            time.sleep(3) #5
            self.Enclosure.readTempC()
            print ("read value successfully\n")
            time.sleep(1)
            #print (self.Temp_sensor.get_amb_temp())
            #print (self.Temp_sensor.get_obj_temp())

            try:
                raisingTail = self.Enclosure.raiseArm()
            except OSError:
                # continue
                print ("reset arduino")
                self.Enclosure.resetArduino()
                
            except RuntimeError:
                time.sleep(2.5)
                print ("raise mode run too fast")
                failed_raising += 1
                # os._exit(1)

            print ('counter {}, lower_fail {}, raise_fail {}\n'.
                format(counter,failed_lowering, failed_raising))
            time.sleep(3) #3


    def test_software_reset(self):
        # doesn't trigger servo to original position
        self.Enclosure.resetArduino(Arduino_opcode_command.softReset.value)
        print('Arduino reset successfully')


    def test_read_temp(self):
        num_of_retries = 20

        for _ in range(num_of_retries):
            self.Enclosure.readTempC()
            print ("read value successfully\n")
            time.sleep(10)


    def test_read_from_arduino(self):
        pass

    def test_temp_reading(self):
        print (self.Temp_sensor.get_amb_temp())
        print (self.Temp_sensor.get_obj_temp())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
