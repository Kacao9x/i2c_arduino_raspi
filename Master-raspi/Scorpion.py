#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time, sys, inspect, os
from pathlib import Path
import qrcode
import random

import json
from pprint import pprint
import datetime
import numpy as np
from pathlib import *
import unittest

''' Add project to system path '''
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,currentdir)
sys.path.insert(0,parentdir)
print ('Scorpion path: {}'.format(Path(currentdir)))
print ('Scorpion''s parentdir: {}'.format(Path(parentdir)))


from api.echoes_hardware_api import *
from api.echoes_signal_processing_api import *
from api.echoes_models_api import *
# from api.echoes_database_api import *

class Scorpion(object):

	_class		= None
	_debug 		= False
	_debug_level= None
	
	_PRODUCT_NUM_ = 8															#TO-DOs: get the length of supported product list

	status = {"CurrentStatus": "ReadyForUser",}
	timestamp = ''

	user_request= {"ProductId" : 0}

	result 		= None
	QrBarcode	= None
	_result_template = {
		"IsTestValid"	: False,
		"TestId"		: 0,
		"ProductId"		: 0,
		"QrBarcode"		: "",
		"Soh"			: -1,
		"Soc"			: -1,
		"BatteryTemp"	: 0,
		"AmbientTemp"	: 0,
		"Timestamp"		: None,
	}


	def __init__(self, debug=False, debug_level = 1):
		"""Constructor"""

		self._debug 		= debug
		self._debug_level	= debug_level
		self._class			= self._class

		# Create instace of Echoes board and hw_enclosure
		
		self.echoes_2 		= echoes_spi_api(debug=debug, debug_level=debug_level)		# Initiate echoes board instance	
		self.echoes_2.set_total_adc_captures(64)
		self.echoes_dsp		= echoes_dsp(7200000.0)
		
		self.echoes_2.set_capture_channel(1)
		self.echoes_2.set_impulse_type(IMPULSE_FULL_NEG)
		self.echoes_2.set_vga_gain(0.75)

		secondary_path 		= self.echoes_2.set_capture_adc(ADC_SECONDARY)

		# TO-DOs: Establish connection to Front-end??
		# Return 'ready' status to front-end
		with open(Path(parentdir + "/Exchange/status.json"), 'w') as writeout:
			writeout.write(json.dumps(self.status))
		writeout.close()

		# Load previous result. Create an empty template if file not existing
		if not os.path.exists(Path(parentdir + "Exchange/result.json")):
		 	self.result = self._result_template
		else:
		 	with open(Path(parentdir + "Exchange/result.json")) as readout:
		 		self.result = json.load(readout)
		 	readout.close()

		 	os.remove(Path(parentdir + "Exchange/result.json"))

	def initEnclosure(self):
		pass

	def initEchoesBoard(self):
		pass

	@staticmethod
	def _isValidRequest(self):
		''' deJsonify and find the matching id Value'''
		with open(Path(parentdir + "/Exchange/request.json")) as readout:
			self.user_request = json.load(readout)
		readout.close()

		if self.user_request is None:
			self.dprint("No user input specified", error=True)
			return False
		
		if self.user_request['ProductId'] in range(1, self._PRODUCT_NUM_):
			return True
		else:
			self.dprint("Selected product is not in suppport list")
			return False


	def readyForTest(self):
		if self._isValidRequest(self):# and self.enclosure.loweringServo():
			self.status['CurrentStatus'] = 'ReadyForTest'
			with open(Path(parentdir + "/Exchange/status.json"), 'w') as writeout:
				writeout.write(json.dumps(self.status))
			writeout.close()
			return True
		else:
			self.status['CurrentStatus'] = 'InvalidProductId'
			with open(Path(parentdir + "/Exchange/status.json"), 'w') as writeout:
				writeout.write(json.dumps(self.status))
			writeout.close()
			return False

	def capture_and_read_adc(self, remove_bad_reads=False, bandpass=True):
		""" Capture ultrasound signal - Select tramission signal 2nd path
			Return signal after bandpass filter		
		"""
		adc_captures_filtered = []
		adc_captures_float = []

		adc_captures = self.echoes_2.capture_and_read(send_impulse=True)
		adc_captures_float = self.echoes_2.convert_adc_raw_to_float(adc_captures)
		self.timestamp = datetime.datetime.now().replace(microsecond=0)
		
		if remove_bad_reads:
			adc_captures_float = self.echoes_2.remove_bad_reads(adc_captures_float)
		
		if bandpass and adc_captures_float is not None:
			bandpass_fir_filter = self.echoes_dsp.create_fir_filter(cutoffHz=
				[300000.0, 1200000.0],
				taps=51, type="bandpass")
			# adc_capture_filtered = self.echoes_dsp.apply_bandpass_filter_fir(signal_avg,bandpass_fir_filter)
			for idx, adc_capture in enumerate(adc_captures_float):
				adc_capture = self.echoes_dsp.apply_bandpass_filter_fir(adc_capture, 
                                                        bandpass_fir_filter) 
				adc_captures_float[idx] = adc_capture
			
			# Average all samples and keep 1 signal
			adc_captures_filtered = np.mean(adc_captures_float, axis=0)
		
		else:
			adc_captures_filtered = []


		return adc_captures_float, adc_captures_filtered



	def scan(self, remove_bad_reads=True, bandpass=True):
		""" Capture ultrasound signal - Select tramission signal 2nd path"""
		# adc_captures 		= self.echoes_2.capture_and_read(send_impulse=True)
		# adc_captures_float 	= self.echoes_2.convert_adc_raw_to_float(adc_captures)
		# if bandpass:
		# 	bandpass_fir_filter = self.echoes_dsp.create_fir_filter(cutoffHz=
		# 		[300000.0, 1200000.0],
		# 		taps=51, type="bandpass")
		# 	# adc_capture_filtered = self.echoes_dsp.apply_bandpass_filter_fir(signal_avg,bandpass_fir_filter)
		# 	for idx, adc_capture in enumerate(adc_captures_float):
		# 		adc_capture = self.echoes_dsp.apply_bandpass_filter_fir(adc_capture, 
        #                                                 bandpass_fir_filter) 
		# 		adc_captures_float[idx] = adc_capture
		
		# adc_captures_readout = np.mean(adc_captures_float, axis=0)
		
		_, adc_captures_filtered = self.capture_and_read_adc(remove_bad_reads, bandpass)
		try:
			soh = SoH_GradientBoosting(adc_captures_filtered)
			soh = round(soh, 1)
		except:
			print ("\nError in soh model. Return -1\n")
			soh = -1
   
   
		''' MOCK-UP: generate dummy data if no echoes board'''
		soc = -1																#an arbitrary value for SOC
		battTemp = round(random.uniform(22.21, 23.0), 2)
		ambientTemp = battTemp

		return soh, soc, battTemp


	def save_scan_result(self, soh, soc, battTemp, ambientTemp):

		if soh is None or soh > 85.0 or soh < 50.0:
			soh 		= -1
			self.status['CurrentStatus'] = 'TestFailed'							# echoes-board returns a value
			_validTest = False
		else:
			self.status['CurrentStatus'] = 'TestSuccessful'						# no response from echoes board
			_validTest = True

		self.QrBarcode = "Titan2l"
          
		new_result = {
			"IsTestValid"	: _validTest,
			"TestId"		: self.result['TestId']+1,
			"ProductId"		: self.user_request["ProductId"],
			"QrBarcode"		: self.QrBarcode,
			"Soh"			: soh,
			"Soc"			: soc,
			"BatteryTemp"	: battTemp,
			"AmbientTemp"	: ambientTemp,
			"Timestamp"		: self.timestamp.isoformat(),
		}

		self.result = new_result

		with open(Path(parentdir + '/Exchange/result.json'), 'w') as writeout:
			writeout.write(json.dumps(new_result))
		writeout.close()

		# fn = '/Exchange/capture{}-{}.json'.format(new_result['TestId'],
		# 											self.timestamp)
		# with open(Path(parentdir + fn), 'w') as writeout:
		# 	writeout.write(json.dumps(new_result))
		# writeout.close()

		return
		

	def qr_generator(self):
		result_str = json.dumps(self.result)
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data(result_str)
		qr.make(fit=True)

		fn = "/Exchange/QR-code/result{}-{}.png".format(self.result['TestId']+1, self.timestamp)
		img = qr.make_image(fill_color="black", back_color="white")
		img.save(Path(parentdir + fn))

		return


	def get_json_result(self):
		return json.dumps(self.result)

	def get_json_status(self):
		return json.dumps(self.status)

	def get_test_id(self):
		return self.result['TestId']

	def get_soh_value(self):
		return self.result['Soh']

	def get_soc_value(self):
		return self.result['Soc']

	def get_battery_temperature(self):
		return self.result['BatteryTemp']

	def get_scan_time(self):
		return self.result['Timestamp']


	def dprint(self, txt, timestamp=False, error=False):
		# Prints messages with function and class
		if self._debug or error:
			function_name = sys._getframe(1).f_code.co_name
			if timestamp:
				print("  "+str(datetime.datetime.now())+" "+self._class+":"
					  +function_name+"(): "+txt)
			else:
				print("  "+self._class+":"+function_name+"(): "+txt)


class Test(unittest.TestCase):

	Scorpion = Scorpion()

	def test_setUp(self):

		print('Init status: {}'.format(self.Scorpion.get_json_status()))
		self.Scorpion.readyForTest()
		# print (self.Scorpion.enclosure.isArduinoReady())

		print ('old test result: {}'.format(self.Scorpion.get_json_result()))
		print ('status: {}'.format(self.Scorpion.get_json_status()))


	def test_read_previous_test_result(self):
		print('SOH: {}'.format(self.Scorpion.get_soc_value()))
		print('SOC: {}'.format(self.Scorpion.get_soh_value()))
		print('testID: {}'.format(self.Scorpion.get_test_id()))
		print('battTemp: {}'.format(self.Scorpion.get_battery_temperature()))
		print('timestatmp:{}'.format(self.Scorpion.get_scan_time()))



	def test_START_button(self):
		Test.test_setUp(self)
		self.Scorpion.scan()

		# Check the test result
		print ('all data {}'.format(self.Scorpion.get_json_result()))
		print ('status {}'.format(self.Scorpion.get_json_status()))
		print('SOH: {}'.format(self.Scorpion.get_soc_value()))
		print('SOC: {}'.format(self.Scorpion.get_soh_value()))
		print('testID: {}'.format(self.Scorpion.get_test_id()))
		print('battTemp: {}'.format(self.Scorpion.get_battery_temperature()))
		print('timestatmp:{}'.format(self.Scorpion.get_scan_time()))

