# -*- coding: utf-8-*-
from Tkinter import *
import threading
import logging
import argparse
from pprint import pprint as pp
from collections import deque
from collections import namedtuple

VELIKOST = 8
MODRI = 'M'
RDECI = 'R'
seznam= []
ZMAGOVALEC = None

radij=20.
premik=radij*.87
zamik = 50.

inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')

#########################################
#splošna struktura programa:
#   s classom Gui začnemo
#   narišemo igralno ploščo z narišiPloščo
#   restart funkcija nastavi igro na Človek vs. Človek 
#   med risanjem ploce predamo onObjectClick kontrolo nad plosco, ker ima vsak heksagon svoj unique ID
#   onObjectClick ob kliku preveri pravilnost poteze z Igra.veljavna_poteza() in ustrezno pobarva polje
#algoritem
#   igra eno naključno pozicijo
#   z vrednostPozicije() ovrednoti posamezno pozicijo
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

    def __init__(self, gui):
        self.plosca = [['PRAZNO' for x in range(VELIKOST)] for y in range(VELIKOST)]
        self.na_potezi = MODRI
        self.gui = gui

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
        #print('x: ' + str(x))
        #print('y: ' + str(y))
        if self.plosca[y][x] != 'PRAZNO':
            return False
        else:
            #print("Veljavna!")
            self.plosca[y][x] = na_potezi
            return True

    def sosedi(self, y, x):
        """Metoda preveri, kateri so sosedi izbranega polja."""
        sosedi = []
        for (dy, dx) in ((-1,0), (-1,1),
                 (0, -1),     (0, 1),
                 (1, -1), (1, 0)):
            if 0 <= x + dx < SIZE and 0 <= y + dy < SIZE:
                sosedi.append((y + dy, x + dx))
        logging.debug ("Sosedi od ({0}, {1}) so {2}".format(y,x,sosedi))
        return sosedi

    def sestaviGraf(plosca):
        "Sestavi graf trenutne poteze."
        queue = []
        # sosedi = deque()
        for st in range(SIZE):
            queue.append(((-1, 0),(0, st), 1))
            queue.append(((SIZE-1, st),(SIZE, 0), 1))
        # print queue
        for vr in range(SIZE):
                for st in range(SIZE):
                    seznamSosedov = sosedi(vr, st)
                    for sosed in seznamSosedov:
                        if plosca[vr][st] == 'PRAZNO':
                            queue.append(((vr, st),(sosed[0], sosed[1]), 1))
                        elif plosca[vr][st] == plosca[sosed[0]][sosed[1]]:
                            queue.append(((vr, st),(sosed[0], sosed[1]), 0))
                        else:
                            pass
        return queue

    def je_konec(self):
        global ZMAGOVALEC
        print "Zmagal: ",ZMAGOVALEC
        for x in range(0, VELIKOST):
            obstaja_x = False
            for y in range(0, VELIKOST):
                if self.plosca[y][x] == 'M':
                    obstaja_x = True
            if obstaja_x == False:
                return False
            if obstaja_x == True and x == VELIKOST - 1:
                x = 0
                for y in range(0, VELIKOST):
                    if self.plosca[y][x] == 'M':
                        print("Kličemo povezani M!")
                        print("y: " + str(y))
                        seznam.append(self.povezano('M', x, y))
        if ZMAGOVALEC != None:
            return True


        # for y in range(0, VELIKOST):
        #     obstaja_y = False
        #     for x in range(0, VELIKOST):
        #         if self.plosca[y][x] == 'R':
        #             obstaja_y = True
        #     if obstaja_y == False:
        #         return False
        #     if obstaja_y == True and y == VELIKOST - 1:
        #         return self.povezano('R', x, y)

    def povezano(self, barva, x_dan, y_dan, obiskani=[]):
        global ZMAGOVALEC
        if (y_dan, x_dan) not in obiskani: obiskani.append((y_dan, x_dan))
        for (dy, dx) in ((-1,0), (-1,1),
                 (0, -1), (0, 1),
                 (1, -1), (1, 0)):
            if 0 <= x_dan + dx < VELIKOST and 0 <= y_dan + dy < VELIKOST and self.plosca[y_dan][x_dan] == barva and (y_dan + dy, x_dan + dx) not in obiskani:
                #print self.plosca[y_dan+dy][x_dan+dx]
                if x_dan == VELIKOST - 1:
                    if barva == 'M':
                        #print("x: " + str(x_dan))
                        #print("y: " + str(y_dan))
                        print(barva + " je povezala!")
                        ZMAGOVALEC = MODRI
                if y_dan == VELIKOST - 1:
                    if barva == 'R':
                        print(barva + " je povezala!")
                        ZMAGOVALEC = RDECI
                else:
                    self.povezano(barva, x_dan + dx, y_dan + dy, obiskani)

    def sestaviGraf(self, plosca):
        "Sestavi graf trenutne poteze."
        queue = []
        # sosedi = deque()
        for st in range(SIZE):
            queue.append(((-1, 0),(0, st), 1))
            queue.append(((SIZE-1, st),(SIZE, 0), 1))
        # print queue
        for vr in range(SIZE):
                for st in range(SIZE):
                    seznamSosedov = self.sosedi(vr, st)
                    for sosed in seznamSosedov:
                        if plosca[vr][st] == 'PRAZNO':
                            queue.append(((vr, st),(sosed[0], sosed[1]), 1))
                        elif plosca[vr][st] == plosca[sosed[0]][sosed[1]]:
                            queue.append(((vr, st),(sosed[0], sosed[1]), 0))
                        else:
                            pass
        return queue
                    
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
        # print('Got object click', event.x, event.y)
        # print(int(event.widget.find_closest(event.x, event.y)[0]))
        
        polje = int(event.widget.find_closest(event.x, event.y)[0])
        #print('Polje: ' + str(polje))
        if self.igra.veljavna_poteza(polje, self.igra.na_potezi):
            polje -= 1
            x = polje % VELIKOST
            y = polje / VELIKOST
            print(self.igra.na_potezi)
            if self.igra.na_potezi == MODRI:
                #print('Modri klik')
                self.pobarvaj_modro(polje)
                self.igralec_modri.klik(y,x)
                self.igra.na_potezi = RDECI
                
            elif self.igra.na_potezi == RDECI:
                #print('Rdeči klik')
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
                #print(tag)
                seznamSestkotnikov.append(self.plosca.create_polygon([x1+zamik+2*x*premik+y*premik,y1+zamik+radij*1.5*y, x2+zamik+2*x*premik+y*premik, y2+zamik+radij*1.5*y, x2+zamik+2*x*premik+y*premik, y2+zamik+radij*1.5*y, x3+zamik+2*x*premik+y*premik, y3+zamik+radij*1.5*y, x3+zamik+2*x*premik+y*premik, y3+zamik+radij*1.5*y, x4+zamik+2*x*premik+y*premik, y4+zamik+radij*1.5*y, x4+zamik+2*x*premik+y*premik, y4+zamik+radij*1.5*y, x5+zamik+2*x*premik+y*premik, y5+zamik+radij*1.5*y, x5+zamik+2*x*premik+y*premik, y5+zamik+radij*1.5*y, x6+zamik+2*x*premik+y*premik, y6+zamik+radij*1.5*y],
                    outline='black', fill='gray', width=2, tags = tag))
                self.plosca.tag_bind(tag, '<ButtonPress-1>', self.onObjectClick)
        #print(seznamSestkotnikov)
            
    def naredi_potezo(self, vr, st):
        "Metoda naredi potezo in spremeni napis o stanju"
        # if self.igra.na_potezi == MODRI:
        #   seznam=self.igra.naredi_potezo()
        #   self.pobarvaj_modro(seznam)
        # elif self.igra.na_potezi == IGRALEC_RDECI:
        #   seznam=self.igra.naredi_potezo(vr, st)
        #   self.pobarvaj_rdece(seznam)
        # else:
        #   assert False, "nemore se zgodit"

        if self.igra.je_konec():
            self.konec(ZMAGOVALEC)
        elif self.igra.na_potezi == MODRI:
            self.napis2.set("Na potezi je rdeči.")
            # self.igralec_modri.igraj()
        elif self.igra.na_potezi == RDECI:
            self.napis2.set("Na potezi je modri.")
            # self.igralec_rdeci.igraj()
        else:
            assert False, "nemore se zgodit, a se je. funkcija: naredi_potezo"
        

    def restart(self, igralec_modri, igralec_rdeci):
        "Metoda ponastavi igro"
        # self.prekini_igralce()
        self.plosca.delete(Gui.TAG_FIGURA)
        #pobarvaj začetni poziciji
        self.napis1.set("Hex")
        self.napis2.set("Na potezi je modri.")
        self.igra = Igra(Gui)

        self.igralec_modri = igralec_modri
        self.igralec_rdeci = igralec_rdeci
        self.igralec_modri.igraj()

    def pobarvaj_modro(self, tag):
        """Pobarva polje na modro"""
        if ZMAGOVALEC == None: self.plosca.itemconfig(seznamSestkotnikov[tag], fill='blue')
        
    def pobarvaj_rdece(self, tag):
        """Pobarva polje na rdece"""
        if ZMAGOVALEC == None: self.plosca.itemconfig(seznamSestkotnikov[tag], fill='red')
        
    def zapriOkno(self, root):
        "Ta metoda se pokliče, ko uporabnik zapre aplikacijo."
        root.destroy()

    def ni_klika(self):
        """Ko je igre konec unbindamo klik iz plošče"""
        print "Nič več klikov zate."
        
    def konec(self, zmagovalec):
        """Izpiše zmagovalca in rezultat."""
        self.napis2.set("Zmagal je " + zmagovalec)
        #print(seznamSestkotnikov)
        print("Konec")
        # stanje=self.igra.stanje()
        # if stanje[0]>stanje[1]:
        #     self.napis2.set("Zmagal je modri s {0} proti {1}.".format(stanje[0], stanje[1]))
        # elif stanje[0]<stanje[1]:
        #     self.napis2.set("Zmagal je rdeči s {1} proti {0}.".format(stanje[0], stanje[1]))
        # else:
        #     self.napis2.set("Igra je neodločena!")

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

class Racunalnik():
    """docstring for Racunalnik"""
    def __init__(self, gui):
        self.gui = gui
        
    #def igraj():


    # def preveri_potezo():

#########################################

class Minimax():
    def __init__(self, globina):
        self.globina = globina
        self.igra = None
        self.igram = None
        self.poteza = None
        self.prekinitev = None

    def prekini(self):
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        self.igra = igra
        self.igram = self.igra.na_potezi
        self.poteza = None
        self.prekinitev = False

        (poteza, vrednost) = self.minimax(self.globina, True)
        self.igra = None
        self.igram = None

        if not self.prekinitev:
            logging.debug ("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
            self.poteza = poteza
            return poteza

    ZMAGA = 1000000
    NESKONCNO = ZMAGA + 1

    def minimax(self, globina, maksimiziramo):
        if self.prekinitev:
            logging.debug ("Minimax prekinja.")
            return (None, 0)
        if self.igra.je_konec():
            stanje = self.igra.stanje()
            zmagovalec = stanje[2]
            if zmagovalec == self.igram:
                return (None, Minimax.ZMAGA)
            elif zmagovalec == nasprotnik(self.igram):
                return (None, -Minimax.ZMAGA)
            else:
                return (None, 0)
        else:
            if globina == 0:
                vrednost = self.vrednost_pozicije()
                return (None, vrednost)
            else:
                if maksimiziramo:
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    for poteza in self.igra.veljavne_poteze():
                        self.igra.shrani_pozicijo()
                        self.igra.naredi_potezo(poteza[0], poteza[1])
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = poteza
                else:
                    najboljsa_poteza = None
                    vrednost_najboljse = Minimax.NESKONCNO
                    for poteza in self.igra.veljavne_poteze():
                        self.igra.shrani_pozicijo()
                        self.igra.naredi_potezo(poteza[0], poteza[1])
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = poteza

                assert (najboljsa_poteza is not None), "minimax: izračunana poteza je None"
                logging.debug (("---" * (MINIMAX_GLOBINA - globina)) + 
                           "{0}: poteza={1}, vrednost={2}, max={3}".format(
                               globina, najboljsa_poteza, vrednost_najboljse, maksimiziramo))
                return (najboljsa_poteza, vrednost_najboljse)

    def vrednost_pozicije(self):
        "Metoda ovrednoti pozicijo glede na najkrajšo pot, igra potem prvo v vrsti."
        vrednost = 0
        stM=0
        stR=0
        for vr in range(SIZE):
            for st in range(SIZE):
                if self.igra.plosca[vr][st]=='M':
                    stM+=1
                elif self.igra.plosca[vr][st]=='R':
                    stR+=1
        if self.igram == IGRALEC_MODRI:
            vrednost = (stM-stR)
            return vrednost
        elif self.igram == IGRALEC_RDECI:
            vrednost = (stR-stM)
            return vrednost
        else:
            assert False, "Vrednost pozicij ima neveljavnega igralca."

#########################################
class Graph():
    def __init__(self, edges):
        self.edges = edges2 = [Edge(*edge) for edge in edges]
        self.vertices = set(sum(([e.start, e.end] for e in edges2), []))

    def dijkstra(self, source, dest):
        assert source in self.vertices
        dist = {vertex: inf for vertex in self.vertices}
        previous = {vertex: None for vertex in self.vertices}
        dist[source] = 0
        q = self.vertices.copy()
        neighbours = {vertex: set() for vertex in self.vertices}
        for start, end, cost in self.edges:
            neighbours[start].add((end, cost))
        #pp(neighbours)
 
        while q:
            u = min(q, key=lambda vertex: dist[vertex])
            q.remove(u)
            if dist[u] == inf or u == dest:
                break
            for v, cost in neighbours[u]:
                alt = dist[u] + cost
                if alt < dist[v]:   # Relax (u,v,a)
                    dist[v] = alt
                    previous[v] = u
        #pp(previous)
        s, u = deque(), dest
        while previous[u]:
            s.pushleft(u)
            u = previous[u]
        s.pushleft(u)
        return s
 
 
#  def sestaviGraf(self):
#   "Sestavi graf trenutne poteze."
#   queue = deque([])
#   for st in range(SIZE):
#       queue.append([(-1, 0),(0, st), 1])
#       queue.append([(SIZE, 0),(SIZE+1, st), 1])
#   for vr in range(SIZE):
#           for st in range(SIZE):
#               sosedi = sosedi(vr, st)
#               for sosed in sosedi:
#                   if self.plosca[vr][st] == self.plosca[sosed[0]][sosed[1]]
#                       queue.append([(vr, st),(sosed[0], sosed[1]), 0])
#                   elif self.plosca[vr][st] == "PRAZNO":
#                       queue.append([(vr, st),(sosed[0], sosed[1]), 1])
#                   else:
#                       pass



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