import math


class ModuloAdcNtc(object):
	"""
	Utility di conversione per sensore di temperatura NTC (Negative Temperature Coefficient)
	La resistenza elettrica diminuisce esponenzialmente con l’aumento della temperatura.
	Di conseguenza se la temperatura sale, anche la tensione letta in input sarà maggiore.
	"""
	
	__REFERENCE_TEMP=1/298.15
	
	@classmethod
	def fromVoltageToDegreeKelvin(cls,r1:int,rSensor:int,r2:int,
			vo:float,vcc:float,coefficent:int)->float:
		"""
		@param r1: resistenza in Ohm
		@param rSensor: resistenza del sensore in Ohm a 25 gradi Celsius
		@param r2: resistenza in Ohm
		@param vo: valore in Volt in output al sensore, cioè letto dal sistema, deve essere > 0 e < di VCC
		@param vcc: valore in Volt
		@param coefficent: Coefficente del sensore, varia in base al tipo di sensore
		"""
		# calcolo la resistenza di R1 + RNTC
		r1ENtc=(vcc/(vo/r2))-r2
		# calcolo la resistenza di RNTC
		rNtc=r1ENtc-r1
		# ora che ho la resistenza del sensore posso calcolare la temperatura
		return 1/((math.log(rNtc/rSensor)/coefficent)+cls.__REFERENCE_TEMP)

	@classmethod
	def fromVoltageToDegreeCelsius(cls,r1:int,rSensor:int,r2:int,
			vo:float,vcc:float,coefficent:int)->float:
		"""
		Vedi documentazione del metodo fromVoltageToDegreeKelvin()
		"""
		return cls.fromVoltageToDegreeKelvin(r1,rSensor,r2,vo,vcc,coefficent)-273.15
