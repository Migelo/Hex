# -*- coding: utf-8-*-
from tkinter import *
import threading
import logging
import argparse
from collections import namedtuple, deque

MINIMAX_GLOBINA = 3
VELIKOST = 5
MODRI = 'M'
RDECI = 'R'
PRAZNO = 'PRAZNO'
seznam = []
ZMAGOVALEC = None
NI_KONEC = "ni konec"
NEODLOCENO = "neodloceno"

radij = 20.
premik = radij*.87
zamik = 50.

"""Stvari potrebne za Dijkstra's algorithm"""
inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')


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
        self.zgodovina = []

    def shrani_pozicijo(self):
        """Shrani trenutno pozicijo, da se bomo lahko kasneje vrnili vanjo
           z metodo razveljavi."""
        p = [self.plosca[i][:] for i in range(VELIKOST)]
        self.zgodovina.append((p, self.na_potezi))

    def kopija(self):
        """Vrni kopijo te igre, brez zgodovine."""
        k = Igra()
        k.plosca = [self.plosca[i][:] for i in range(VELIKOST)]
        k.na_potezi = self.na_potezi
        return k

    def razveljavi(self):
        """Razveljavi potezo in se vrni v prejšnje stanje."""
        (self.plosca, self.na_potezi) = self.zgodovina.pop()

    def veljavne_poteze(self):
        """Vrni seznam veljavnih potez."""
        poteze = []
        for i in range(VELIKOST**2):
            if self.plosca[int(i / VELIKOST)][int(i % VELIKOST)] is PRAZNO:
                    poteze.append((i))
        return poteze

    def povleci_potezo(self, polje):
        """Povleci potezo p, ne naredi nič, če je neveljavna.
           Vrne stanje_igre() po potezi ali None, ce je poteza neveljavna."""
        y = int(polje / VELIKOST)
        x = int(polje % VELIKOST)
        if (self.plosca[y][x] != PRAZNO) or (self.na_potezi == None):
            # neveljavna poteza
            return None
        else:
            self.shrani_pozicijo()
            self.plosca[y][x] = self.na_potezi
            zmagovalec = self.stanje_igre()
            if zmagovalec == NI_KONEC:
                # Igre ni konec, zdaj je na potezi nasprotnik
                self.na_potezi = nasprotnik(self.na_potezi)
            else:
                # Igre je konec
                self.na_potezi = None
            return zmagovalec

    def stanje_igre(self):
        """Ugotovi, kakšno je trenutno stanje igre. Vrne:
           - (MODRI), če je igre konec in je zmagal MODRI
           - (RDECI), če je igre konec in je zmagal RDEČI
           - (NEODLOCENO), če je igre konec in je neodločeno
           - (NI_KONEC), če igre še ni konec
           Pri sestavljanju grafa upostevamo samo polja od igralca, ki igra
        """
        graph_modri = self.sestaviGraf(self.plosca, MODRI)
        graph_modri = Graph(graph_modri)
        graph_rdeci = self.sestaviGraf(self.plosca, RDECI)
        graph_rdeci = Graph(graph_rdeci)

        stanje_MODRI = graph_modri.dijkstra((0, -1), (0, VELIKOST))
        stanje_RDECI = graph_rdeci.dijkstra((-1, 0), (VELIKOST, 0))


        if stanje_MODRI != NI_KONEC:
            return MODRI
        elif stanje_RDECI != NI_KONEC:
            return RDECI
        elif len(self.veljavne_poteze()) == 0:
            return NEODLOCENO
        elif stanje_MODRI == NI_KONEC and stanje_RDECI == NI_KONEC:
            return NI_KONEC
        else:
            logging.debug("Nemore se zgoditi, pa se je, igra.stanje_igre().")


    def sosedi(self, y, x):
        """Metoda preveri, kateri so sosedi izbranega polja."""
        sosedi = []
        for (dy, dx) in ((-1, 0), (-1, 1),
                         (0, -1), (0, 1),
                         (1, -1), (1, 0)):
            if 0 <= x + dx < VELIKOST and 0 <= y + dy < VELIKOST:
                sosedi.append((y + dy, x + dx))
        logging.debug("Sosedi od ({0}, {1}) so {2}".format(y, x, sosedi))
        return sosedi

    def sestaviGraf(self, plosca, barva, ai=False):
        """Sestavi graf trenutne poteze."""
        # Graf je sestavljen iz vseh vseh moznih povezav med polji.
        # V primeru, ko igra racunalnik, iscemo najkrajso povezavo med dvema
        # nasprotnima stranema, zato pri sestavljanju grafa polja v barvi
        # igralca in prazna polja.
        # V nasprotnem primeru graf sestoji le iz polj v barvi igralca
        queue = []
        if ai:
            for vr in range(VELIKOST):
                    for st in range(VELIKOST):
                        seznamSosedov = self.sosedi(vr, st)
                        for sosed in seznamSosedov:
                            if plosca[vr][st] == 'PRAZNO':
                                queue.append(((vr, st), (sosed[0], sosed[1]), 1))
                            elif plosca[vr][st] == barva:
                                queue.append(((vr, st), (sosed[0], sosed[1]), 0))
                            else:
                                pass
        else:
            for vr in range(VELIKOST):
                    for st in range(VELIKOST):
                        seznamSosedov = self.sosedi(vr, st)
                        for sosed in seznamSosedov:
                            if plosca[vr][st] == barva and plosca[sosed[0]][sosed[1]] == barva:
                                queue.append(((vr, st), (sosed[0], sosed[1]), 0))
                            else:
                                pass
        if barva == MODRI:
            for vr in range(VELIKOST):
                queue.append(((0, -1), (vr, 0), 1))
                queue.append(((vr, VELIKOST - 1), (0, VELIKOST), 1))

        if barva == RDECI:
            for st in range(VELIKOST):
                queue.append(((-1, 0), (0, st), 1))
                queue.append(((VELIKOST - 1, st), (VELIKOST, 0), 1))

        return queue

#########################################

#########################################

class Clovek():
    def __init__(self, gui):
        self.gui = gui

    def igraj(self):
        pass

    def prekini(self):
        pass

    def klik(self, p):
        self.gui.povleci_potezo(p)

#########################################

class Racunalnik():
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem # Algoritem, ki izračuna potezo
        self.mislec = None # Vlakno (thread), ki razmišlja

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""

        # Naredimo vlakno, ki mu podamo *kopijo* igre (da ne bo zmedel GUIja):
        self.mislec = threading.Thread(
            target=lambda: self.algoritem.izracunaj_potezo(self.gui.igra.kopija()))

        self.mislec.start()

        self.gui.plosca.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        """Vsakih 100ms preveri, ali je algoritem že izračunal potezo."""
        if self.algoritem.poteza is not None:
            self.gui.povleci_potezo(self.algoritem.poteza)
            self.mislec = None
        else:
            self.gui.plosca.after(100, self.preveri_potezo)

    def prekini(self):
        if self.mislec:
            logging.debug("Prekinjamo {0}".format(self.mislec))
            self.algoritem.prekini()
            self.mislec.join()
            self.mislec = None

    def klik(self, p):
        pass


#########################################

class Gui():

    TAG_FIGURA = 'fig'

    def __init__(self, root, globina):
        self.plosca = Canvas(root, width=50*(VELIKOST+1), height=(VELIKOST)*2*radij)
        self.plosca.grid(row=2, column=0)
        width = 50*(VELIKOST+1)
        height=(VELIKOST)*2*radij+60
        self.plosca.create_oval(2*radij, height/2-10, 2*radij+10, height/2, fill='blue')
        self.plosca.create_oval(width-2*radij, height/2*2/3-10, width-2*radij+10, height/2*2/3, fill='blue')
        self.plosca.create_oval(width/2-5, 15, width/2+5, 25, fill='red')
        self.plosca.create_oval(width/2-5, (VELIKOST)*2*radij-10, width/2+5, (VELIKOST)*2*radij, fill='red')

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
                                  self.zacni_igro(Clovek(self), Clovek(self)))
        menu_moznosti.add_command(label="Človek proti računalniku", command=lambda:
                                  self.zacni_igro(Clovek(self), Racunalnik(self, AlfaBeta(globina))))
        menu_moznosti.add_command(label="Računalnik proti računalniku", command=lambda:
                                  self.zacni_igro(Racunalnik(self, AlfaBeta(globina)), Racunalnik(self, AlfaBeta(globina))))
        menu_moznosti.add_command(label="Računalnik proti človeku", command=lambda:
                                  self.zacni_igro(Racunalnik(self, AlfaBeta(globina)), Clovek(self)))

        self.napis1 = StringVar(root, value="Hex")
        Label(root, textvariable=self.napis1).grid(row=0, column=0)

        self.napis2 = StringVar(root, value="Na potezi je modri.")
        Label(root, textvariable=self.napis2).grid(row=1, column=0)

        # Prični igro v načinu človek proti računalniku
        self.zacni_igro(Clovek(self), Racunalnik(self, AlfaBeta(globina)))

    def zacni_igro(self, igralec_modri, igralec_rdeci):
        """Nastavi stanje igre na zacetek igre.
           Za igralca uporabi dana igralca."""
        self.prekini_igralce()
        for i in range(VELIKOST**2): self.plosca.itemconfig(seznamSestkotnikov[i], fill='Grey')
        self.igra = Igra()
        self.igralec_modri = igralec_modri
        self.igralec_rdeci = igralec_rdeci
        self.napis2.set("Na potezi je MODRI.")
        self.igralec_modri.igraj()


    def plosca_klik(self, event):
        polje = int(event.widget.find_closest(event.x, event.y)[0])
        polje -= 1
        if self.igra.na_potezi == MODRI:
            self.igralec_modri.klik(polje)
        elif self.igra.na_potezi == RDECI:
            self.igralec_rdeci.klik(polje)


    def narisiPlosco(self):
        """Narisemo sestkotnike, katerih (x, y) koordinate so podane ospodi"""
        global seznamSestkotnikov
        seznamSestkotnikov = []
        x1, y1 = 0, radij
        x2, y2 = .87*radij, radij/2
        x3, y3 = .87*radij, -radij/2
        x4, y4 = 0, -radij
        x5, y5 = -.87*radij, -radij/2
        x6, y6 = -.87*radij, radij/2
        for y in range(0, VELIKOST):
            for x in range(0, VELIKOST):
                tag = 'hex' + str(x) + str(y)
                seznamSestkotnikov.append(self.plosca.create_polygon([x1+zamik+2*x*premik+y*premik,y1+zamik+radij*1.5*y, x2+zamik+2*x*premik+y*premik, y2+zamik+radij*1.5*y, x2+zamik+2*x*premik+y*premik, y2+zamik+radij*1.5*y, x3+zamik+2*x*premik+y*premik, y3+zamik+radij*1.5*y, x3+zamik+2*x*premik+y*premik, y3+zamik+radij*1.5*y, x4+zamik+2*x*premik+y*premik, y4+zamik+radij*1.5*y, x4+zamik+2*x*premik+y*premik, y4+zamik+radij*1.5*y, x5+zamik+2*x*premik+y*premik, y5+zamik+radij*1.5*y, x5+zamik+2*x*premik+y*premik, y5+zamik+radij*1.5*y, x6+zamik+2*x*premik+y*premik, y6+zamik+radij*1.5*y],
                                                                     outline='black', fill='gray', width=2, tags = tag))
                self.plosca.tag_bind(tag, '<ButtonPress-1>', self.plosca_klik)



    def povleci_potezo(self, p):
        """Povleci potezo p, če je veljavna. Če ni veljavna, ne naredi nič."""
        igralec = self.igra.na_potezi
        r = self.igra.povleci_potezo(p)
        if r is None:
            pass
        else:
            if igralec == MODRI:
                self.pobarvaj_modro(p)
            elif igralec == RDECI:
                self.pobarvaj_rdece(p)
            zmagovalec = r
            if zmagovalec == NI_KONEC:
                if self.igra.na_potezi == MODRI:
                    self.napis2.set("Na potezi je MODRI.")
                    self.igralec_modri.igraj()
                elif self.igra.na_potezi == RDECI:
                    self.napis2.set("Na potezi je RDEČI.")
                    self.igralec_rdeci.igraj()
            else:
                self.koncaj_igro(zmagovalec)


    def koncaj_igro(self, zmagovalec):
        """Nastavi stanje igre na konec igre."""
        if zmagovalec == MODRI:
            self.napis2.set("Zmagal je modri.")
        elif zmagovalec == RDECI:
            self.napis2.set("Zmagal je rdeči.")
        else:
            self.napis1.set("Neodločeno.")


    def pobarvaj_modro(self, tag):
        """Pobarva polje na modro"""
        if ZMAGOVALEC == None: self.plosca.itemconfig(seznamSestkotnikov[tag], fill='blue')

    def pobarvaj_rdece(self, tag):
        """Pobarva polje na rdece"""
        if ZMAGOVALEC == None: self.plosca.itemconfig(seznamSestkotnikov[tag], fill='red')

    def prekini_igralce(self):
        """Sporoči igralcem, da morajo nehati razmišljati."""
        logging.debug("prekinjam igralce")
        if self.igralec_modri: self.igralec_modri.prekini()
        if self.igralec_rdeci: self.igralec_rdeci.prekini()

    def zapriOkno(self, root):
        """Ta metoda se pokliče, ko uporabnik zapre aplikacijo."""
        root.destroy()


    def konec(self, zmagovalec):
        """Izpiše zmagovalca in rezultat."""
        if zmagovalec != 'NEODLOCENO': self.napis2.set("Zmagal je " + zmagovalec +".")
        else: self.napis2.set("Igra je neodločena.")
        logging.debug("Konec")

#########################################


class Minimax():
    ZMAGA = 1000000
    NESKONCNO = ZMAGA + 1

    def __init__(self, globina):
        self.globina = globina  
        self.prekinitev = False
        self.igra = None
        self.jaz = None
        self.poteza = None

    def prekini(self):
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izracunaj potezo za trenutno stanje dane igre."""
        self.igra = igra
        self.prekinitev = False
        self.jaz = self.igra.na_potezi
        self.poteza = None
        (poteza, vrednost) = self.minimax(self.globina, True)
        self.jaz = None
        self.igra = None

        if not self.prekinitev:
            logging.debug("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
            self.poteza = poteza
            return poteza



    def minimax(self, globina, maksimiziramo):
        """Glavna metoda minimax."""
        if self.prekinitev:
            logging.debug("Minimax prekinja, globina = {0}".format(globina))
            return (None, 0)
        zmagovalec = self.igra.stanje_igre()
        if zmagovalec in (MODRI, RDECI, NEODLOCENO):
            if zmagovalec == self.jaz:
                return (None, Minimax.ZMAGA)
            elif zmagovalec == nasprotnik(self.jaz):
                return (None, -Minimax.ZMAGA)
            else:
                return (None, 0)
        elif zmagovalec == NI_KONEC:
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    for p in self.igra.veljavne_poteze():
                        self.igra.povleci_potezo(p)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = p
                else:
                    # Minimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = Minimax.NESKONCNO
                    for p in self.igra.veljavne_poteze():
                        self.igra.povleci_potezo(p)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = p

                assert (najboljsa_poteza is not None), "minimax: izracunana poteza je None"
                return (najboljsa_poteza, vrednost_najboljse)
        else:
            assert False, "minimax: nedefinirano stanje igre"

    def vrednost_pozicije(self):
        """Metoda ovrednoti pozicijo glede na najkrajšo pot.
        Pozicija ima vecjo vrednost, ce je del najkrajse poti."""
        graph_modri = self.igra.sestaviGraf(self.igra.plosca, MODRI, True)
        graph_modri = Graph(graph_modri)
        stanje_MODRI = graph_modri.dijkstra((0, -1), (0, VELIKOST))

        graph_rdeci = self.igra.sestaviGraf(self.igra.plosca, RDECI, True)
        graph_rdeci = Graph(graph_rdeci)
        stanje_RDECI = graph_rdeci.dijkstra((-1, 0), (VELIKOST, 0))

        vrednost = 0
        stM = 0
        stR = 0

        for item in stanje_MODRI:
            if item != (0,-1) and item != (0, VELIKOST) and self.igra.plosca[item[0]][item[1]] == PRAZNO: stM += 1

        for item in stanje_RDECI:
            if item != (-1, 0) and item != (VELIKOST, 0) and self.igra.plosca[item[0]][item[1]] == PRAZNO: stR += 1

        if self.jaz == MODRI:
            vrednost = VELIKOST**2 - stM
            return vrednost
        elif self.jaz == RDECI:
            vrednost = VELIKOST**2 - stR
            return vrednost
        else:
            assert False, "Vrednost pozicij ima neveljavnega igralca."


#########################################


class AlfaBeta():

    ZMAGA = 1000000
    NESKONCNO = ZMAGA + 1

    def __init__(self, globina):
        self.globina = globina
        self.prekinitev = False
        self.igra = None
        self.jaz = None
        self.poteza = None

    def prekini(self):
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izracunaj potezo za trenutno stanje dane igre."""
        self.igra = igra
        self.prekinitev = False
        self.jaz = self.igra.na_potezi
        self.poteza = None
        (poteza, vrednost) = self.alfabeta(
            self.globina, -AlfaBeta.NESKONCNO, AlfaBeta.NESKONCNO, True)
        self.jaz = None
        self.igra = None

        if not self.prekinitev:
            logging.debug("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
            self.poteza = poteza
            return poteza


    def alfabeta(self, globina, alfa, beta, maksimiziramo):
        """Optimiziran minimax."""
        if self.prekinitev:
            logging.debug("AlfaBeta prekinja, globina = {0}".format(globina))
            return (None, 0)
        zmagovalec = self.igra.stanje_igre()
        if zmagovalec in (MODRI, RDECI, NEODLOCENO):
            if zmagovalec == self.jaz:
                return (None, AlfaBeta.ZMAGA)
            elif zmagovalec == nasprotnik(self.jaz):
                return (None, -AlfaBeta.ZMAGA)
            else:
                return (None, 0)
        elif zmagovalec == NI_KONEC:
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    for p in self.igra.veljavne_poteze():
                        self.igra.povleci_potezo(p)
                        vrednost = self.alfabeta(globina-1, alfa, beta, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost > alfa:
                            alfa = vrednost
                            najboljsa_poteza = p
                        if alfa >= beta:
                            break
                    return (najboljsa_poteza, alfa)
                else:
                    # Minimiziramo
                    najboljsa_poteza = None
                    for p in self.igra.veljavne_poteze():
                        self.igra.povleci_potezo(p)
                        vrednost = self.alfabeta(globina-1, alfa, beta, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost < beta:
                            beta = vrednost
                            najboljsa_poteza = p
                        if alfa >= beta:
                            break
                    return (najboljsa_poteza, beta)

                assert (najboljsa_poteza is not None), "alfabeta: izracunana poteza je None"
        else:
            assert False, "alfabeta: nedefinirano stanje igre"

    def vrednost_pozicije(self):
        """Metoda ovrednoti pozicijo glede na najkrajšo pot.
        Pozicija ima vecjo vrednost, ce je del najkrajse poti."""
        graph_modri = self.igra.sestaviGraf(self.igra.plosca, MODRI, True)
        graph_modri = Graph(graph_modri)
        stanje_MODRI = graph_modri.dijkstra((0, -1), (0, VELIKOST))

        graph_rdeci = self.igra.sestaviGraf(self.igra.plosca, RDECI, True)
        graph_rdeci = Graph(graph_rdeci)
        stanje_RDECI = graph_rdeci.dijkstra((-1, 0), (VELIKOST, 0))

        vrednost = 0
        stM = 0
        stR = 0

        for item in stanje_MODRI:
            if item != (0, -1) and item != (0, VELIKOST) and self.igra.plosca[item[0]][item[1]] == PRAZNO: stM += 1

        for item in stanje_RDECI:
            if item != (-1, 0) and item != (VELIKOST, 0) and self.igra.plosca[item[0]][item[1]] == PRAZNO: stR += 1

        if self.jaz == MODRI:
            vrednost = VELIKOST**2 - stM
            return vrednost
        elif self.jaz == RDECI:
            vrednost = VELIKOST**2 - stR
            return vrednost
        else:
            assert False, "Vrednost pozicij ima neveljavnega igralca."


#########################################
# class za izračun povezanosti strani: https://rosettacode.org/wiki/Dijkstra's_algorithm#Python
class Graph():
    def __init__(self, edges):
        self.edges = edges2 = [Edge(*edge) for edge in edges]
        self.vertices = set(sum(([e.start, e.end] for e in edges2), []))

    def dijkstra(self, source, dest):
        if not source in self.vertices:
            return NI_KONEC
        dist = {vertex: inf for vertex in self.vertices}
        previous = {vertex: None for vertex in self.vertices}
        dist[source] = 0
        q = self.vertices.copy()
        neighbours = {vertex: set() for vertex in self.vertices}
        for start, end, cost in self.edges:
            neighbours[start].add((end, cost))

        while q:
            u = min(q, key=lambda vertex: dist[vertex])
            q.remove(u)
            if dist[u] == inf or u == dest:
                break
            for v, cost in neighbours[u]:
                alt = dist[u] + cost
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = u
        s, u = deque(), dest
        while previous[u]:
            s.appendleft(u)
            u = previous[u]
        s.appendleft(u)
        if len(s) == 1: return NI_KONEC
        else: return s 

#########################################
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Igrica Hex")

    parser.add_argument('--globina',
                        default=MINIMAX_GLOBINA,
                        type=int,
                        help='globina iskanja za minimax ali alfabeta algoritem')

    parser.add_argument('--debug',
                        action='store_true',
                        help='vklopi sporočila o dogajanju')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    root = Tk()
    root.title("Hex")

    aplikacija = Gui(root, args.globina)

    root.mainloop()
