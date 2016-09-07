# -*- coding: utf-8-*-
from Tkinter import *
import threading
import logging
import argparse

VELIKOST = 8
MODRI = 'M'
RDECI = 'R'
seznam= []

radij=20.
premik=radij*.87
zamik = 50.

#########################################

def nasprotnik(igralec):
	"Vrne nasprotnika"
	if igralec == MODRI:
		return RDECI
	elif igralec == RDECI:
		return MODRI
	else:
		assert False, "neveljaven nasprotnik"

#########################################

class Igra():

	def __init__(self):
		self.plosca = [['PRAZNO' for x in range(VELIKOST)] for y in range(VELIKOST)]
		self.na_potezi = MODRI

	def naredi_potezo(self, polje):
		# polje -= 1
		# x = polje % VELIKOST
		# y = polje / VELIKOST
		self.na_potezi = nasprotnik(self.na_potezi)

	def veljavna_poteza(self, polje, na_potezi):
		"Metoda preverja ali je dana poteza veljavna."
		polje -= 1
		x = polje % VELIKOST
		y = polje / VELIKOST
		print('x: ' + str(x))
		print('y: ' + str(y))
		if self.plosca[y][x] != 'PRAZNO':
			return False
		else:
			print("Veljavna!")
			self.plosca[y][x] = na_potezi
			return True

	def je_konec(self):
		"Zaenkrat vrnemo false"
		return False
#########################################

class Gui():

	TAG_FIGURA = 'fig'

	def __init__(self, root):
		self.plosca = Canvas(root, width=50*(VELIKOST+1), height=(VELIKOST)*2*radij)
		self.plosca.grid(row=2, column=0)

		self.narisiPlosco()

		self.igralec_modri = None
		self.igralec_rdeci = None
		self.igra = None 

		#Glavni menu
		menu = Menu(root)
		root.config(menu=menu)
		menu_moznosti = Menu(menu)
		menu.add_cascade(label="Možnosti", menu=menu_moznosti)
		menu_moznosti.add_command(label="Človek proti človeku", command=lambda:
										self.restart(Clovek(self), Clovek(self)))
		menu_moznosti.add_command(label="Človek proti računalniku", command=lambda:
										self.restart(Clovek(self), Racunalnik(self, AlfaBeta(globina))))
		menu_moznosti.add_command(label="Računalnik proti računalniku", command=lambda:
										self.restart(Racunalnik(self, AlfaBeta(globina)), Racunalnik(self, AlfaBeta(globina))))
		menu_moznosti.add_command(label="Računalnik proti človeku", command=lambda:
										self.restart(Racunalnik(self, AlfaBeta(globina)), Clovek(self)))

		self.napis1 = StringVar(root, value="Space Me!")
		Label(root, textvariable=self.napis1).grid(row=0, column=0)

		self.napis2 = StringVar(root, value="Na potezi je modri.")
		Label(root, textvariable=self.napis2).grid(row=1, column=0)

		# self.igra = Igra()
		self.restart(Clovek(self), Clovek(self))


	def onObjectClick(self, event):                  
		print('Got object click', event.x, event.y)
		print(int(event.widget.find_closest(event.x, event.y)[0]))
		
		polje = int(event.widget.find_closest(event.x, event.y)[0])
		print('Polje: ' + str(polje))
		if self.igra.veljavna_poteza(polje, self.igra.na_potezi):
			polje -= 1
			x = polje % VELIKOST
			y = polje / VELIKOST
			print(self.igra.na_potezi)
			if self.igra.na_potezi == MODRI:
				print('Modri klik')
				self.pobarvaj_modro(polje)
				self.igralec_modri.klik(y,x)
				self.igra.na_potezi = RDECI
				
			elif self.igra.na_potezi == RDECI:
				print('Rdeči klik')
				self.pobarvaj_rdece(polje)
				self.igralec_rdeci.klik(y,x)
				self.igra.na_potezi = MODRI
		else:
			print('Neveljavna!')

		# if self.igra.veljavna_poteza()
		# self.igraNarediPotezo()


	def narisiPlosco(self):
		global seznamSestkotnikov
		seznamSestkotnikov = []
		x1, y1 = 0, radij
		x2, y2 = .87*radij, radij/2
		x3, y3 = .87*radij, -radij/2
		x4, y4 = 0 , -radij
		x5, y5 = -.87*radij, -radij/2
		x6, y6 = -.87*radij, radij/2
		for y in range(0,VELIKOST):
			for x in range(0,VELIKOST):
				tag = 'hex' + str(x) + str(y)
				print(tag)
				seznamSestkotnikov.append(self.plosca.create_polygon([x1+zamik+2*x*premik+y*premik,y1+zamik+radij*1.5*y, x2+zamik+2*x*premik+y*premik, y2+zamik+radij*1.5*y, x2+zamik+2*x*premik+y*premik, y2+zamik+radij*1.5*y, x3+zamik+2*x*premik+y*premik, y3+zamik+radij*1.5*y, x3+zamik+2*x*premik+y*premik, y3+zamik+radij*1.5*y, x4+zamik+2*x*premik+y*premik, y4+zamik+radij*1.5*y, x4+zamik+2*x*premik+y*premik, y4+zamik+radij*1.5*y, x5+zamik+2*x*premik+y*premik, y5+zamik+radij*1.5*y, x5+zamik+2*x*premik+y*premik, y5+zamik+radij*1.5*y, x6+zamik+2*x*premik+y*premik, y6+zamik+radij*1.5*y],
					outline='black', fill='gray', width=2, tags = tag))
				self.plosca.tag_bind(tag, '<ButtonPress-1>', self.onObjectClick)
		print(seznamSestkotnikov)
			
	def naredi_potezo(self, vr, st):
		"Metoda naredi potezo in spremeni napis o stanju"
		# if self.igra.na_potezi == MODRI:
		# 	seznam=self.igra.naredi_potezo()
		# 	self.pobarvaj_modro(seznam)
		# elif self.igra.na_potezi == IGRALEC_RDECI:
		# 	seznam=self.igra.naredi_potezo(vr, st)
		# 	self.pobarvaj_rdece(seznam)
		# else:
		# 	assert False, "nemore se zgodit"

		if self.igra.je_konec():
			self.konec()
		elif self.igra.na_potezi == MODRI:
			self.napis2.set("Na potezi je rdeči.")
			# self.igralec_modri.igraj()
		elif self.igra.na_potezi == RDECI:
			self.napis2.set("Na potezi je modri.")
			# self.igralec_rdeci.igraj()
		else:
			assert False, "nemore se zgodit"

	def restart(self, igralec_modri, igralec_rdeci):
		"Metoda ponastavi igro"
		# self.prekini_igralce()
		self.plosca.delete(Gui.TAG_FIGURA)
		#pobarvaj začetni poziciji
		self.napis1.set("Hex")
		self.napis2.set("Na potezi je modri.")
		self.igra = Igra()

		self.igralec_modri = igralec_modri
		self.igralec_rdeci = igralec_rdeci
		self.igralec_modri.igraj()

	def pobarvaj_modro(self, tag):
		"""Pobarva polje na modro"""
		self.plosca.itemconfig(seznamSestkotnikov[tag], fill='blue')
		
	def pobarvaj_rdece(self, tag):
		"""Pobarva polje na rdece"""
		self.plosca.itemconfig(seznamSestkotnikov[tag], fill='red')
		
	def zapriOkno(self, root):
		"Ta metoda se pokliče, ko uporabnik zapre aplikacijo."
		root.destroy()

#########################################

class Clovek():
	 def __init__(self, gui):
		 self.gui = gui

	 def igraj(self):
		 pass
	 def prekini(self):
		 pass

	 def klik(self, vr, st):
	 	# a=1
		 self.gui.naredi_potezo(vr, st)

#########################################
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Igrica Hex")
	
	# parser.add_argument('--globina',
	#                     default=MINIMAX_GLOBINA,
	#                     type=int,
	#                     help='globina iskanja za minimax ali alfabeta algoritem')
	
	parser.add_argument('--debug',
						action='store_true',
						help='vklopi sporočila o dogajanju')

	args = parser.parse_args()

	if args.debug:
		logging.basicConfig(level=logging.DEBUG)

	root = Tk()
	root.title("Hex")
	
	aplikacija = Gui(root)

	root.mainloop()