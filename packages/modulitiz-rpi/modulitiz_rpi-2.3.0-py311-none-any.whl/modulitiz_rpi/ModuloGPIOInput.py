import RPi.GPIO as GPIO


class ModuloGPIOInput(object):
	
	def __init__(self,gpioPin:int):
		self.gpioPin=gpioPin
	
	def populate(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.gpioPin,GPIO.IN)
	
	def isActive(self)->bool:
		return GPIO.input(self.gpioPin)
