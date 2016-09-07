# -*- coding: utf-8-*-
from Tkinter import *
import threading
import logging
import argparse

VELIKOST = 8
MODRI = 'M'
RDECI = 'R'

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
		self.plosca = [['NaN' for x in range(VELIKOST)] for y in range(VELIKOST)]
		self.naPotezi = MODRI

	def naredi_potezo(self):
		#TODO: veljavnost poteze
		self.na_potezi = nasprotnik(self.na_potezi)

#########################################

class Gui():

	TAG_FIGURA = 'fig'

	def __init__(self, root):
		self.plosca = Canvas(root, width=50*(VELIKOST+1), height=40*(VELIKOST+1))
		self.plosca.grid(row=0, column=0)

		self.narisiPlosco()

		# self.plosca.bind('<Button-1>', self.klik)

		self.igra = Igra()

	def onObjectClick(self, event):                  
		print('Got object click', event.x, event.y)
		print(event.widget.find_closest(event.x, event.y))

	def narisiPlosco(self):
		radij=20.
		premik=radij*.87
		zamik = 50.

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
				self.plosca.create_polygon([x1+zamik+2*x*premik+y*premik,y1+zamik+radij*1.5*y, x2+zamik+2*x*premik+y*premik, y2+zamik+radij*1.5*y, x2+zamik+2*x*premik+y*premik, y2+zamik+radij*1.5*y, x3+zamik+2*x*premik+y*premik, y3+zamik+radij*1.5*y, x3+zamik+2*x*premik+y*premik, y3+zamik+radij*1.5*y, x4+zamik+2*x*premik+y*premik, y4+zamik+radij*1.5*y, x4+zamik+2*x*premik+y*premik, y4+zamik+radij*1.5*y, x5+zamik+2*x*premik+y*premik, y5+zamik+radij*1.5*y, x5+zamik+2*x*premik+y*premik, y5+zamik+radij*1.5*y, x6+zamik+2*x*premik+y*premik, y6+zamik+radij*1.5*y],
					outline='black', fill='gray', width=2, tags = tag)
				self.plosca.tag_bind(tag, '<ButtonPress-1>', self.onObjectClick)
			



	# def klik(self, event):
	#     """Pretvori klik v koordinate."""
	#     column = (event.x - 50) // 100
	#     row = (event.y - 50) // 100
		
	#     if 0 <= st < SIZE and 0 <= vr < SIZE and self.igra.veljavna_poteza(vr, st):
	#         if self.igra.na_potezi == IGRALEC_MODRI:
	#             self.igralec_modri.klik(vr,st)
				
	#         elif self.igra.na_potezi == IGRALEC_RDECI:
	#             self.igralec_rdeci.klik(vr,st)
					
	#         else:
	#             assert False, "Nisem se zmotil, to se ne bo zgodilo"

	def zapriOkno(self, root):
		"Ta metoda se pokliče, ko uporabnik zapre aplikacijo."
		root.destroy()
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