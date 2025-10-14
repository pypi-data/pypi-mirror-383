import adafruit_ads1x15.ads1115 as ADS
import board
import busio
from adafruit_ads1x15.analog_in import AnalogIn


class ModuloAdcAds1115(object):
	"""
	Analog to digital converter - ONLY for ADS1115
	Check that I2c ports are enabled on raspi-config
	"""
	
	def __init__(self):
		self.channels:dict[int,AnalogIn]={}
		self.ads:ADS.ADS1115|None=None
	
	def populate(self):
		# Create the I2C bus
		i2c=busio.I2C(board.SCL,board.SDA)
		# Create the ADC object using the I2C bus
		self.ads=ADS.ADS1115(i2c)
	
	def addChannel(self,analogInputPin:int):
		if analogInputPin in self.channels:
			return
		# Create single-ended input on channel N
		self.channels[analogInputPin]=AnalogIn(self.ads,analogInputPin)
		# Create differential input between channel 0 and 1
		# AnalogIn(ads, ADS.P0, ADS.P1)
