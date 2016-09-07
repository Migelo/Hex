# -*- coding: utf-8-*-
from Tkinter import *
import threading
import logging
import argparse

VELIKOST = 6
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


#########################################

class Gui():

	TAG_FIGURA = 'fig'

	def __init__(self, root):
		self.plosca = Canvas(root, width=100*(VELIKOST+1), height=100*(VELIKOST+1))


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