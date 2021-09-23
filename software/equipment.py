#Electronic Load
import easygui as eg
import controller2

class eLoads:
	def __init__(self):
		self.part_numbers = {
				'DL3000' : 'ELoad_DL3000'		
		}
		
	def choose_eload(self):
		msg = "In which series is the E-Load?"
		title = "E-Load Series Selection"
		class_name = eg.choicebox(msg, title, self.part_numbers.keys())
		module_name = self.part_numbers[class_name]
		if(class_name == 'DL3000'):
			eload = Eload_DL3000.DL3000()
			return eload
