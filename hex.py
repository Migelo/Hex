# -*- coding: utf-8-*-
from Tkinter import *
import threading
import logging
import argparse
from collections import namedtuple, deque
from pprint import pprint as pp

MINIMAX_GLOBINA = 8
VELIKOST = 4
MODRI = 'M'
RDECI = 'R'
PRAZNO = 'PRAZNO'
seznam= []
ZMAGOVALEC = None
NI_KONEC = "ni konec"
NEODLOCENO = "neodloceno"

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
        print igralec
        assert False, "neveljaven nasprotnik"

#########################################

class Igra():

    def __init__(self):
        self.plosca = [['PRAZNO' for x in range(VELIKOST)] for y in range(VELIKOST)]
        self.na_potezi = MODRI
        # self.gui = gui
        self.zgodovina = []

    def shrani_pozicijo(self):
        """Shrani trenutno pozicijo, da se bomo lahko kasneje vrnili vanjo
           z metodo razveljavi."""
        p = [self.plosca[i][:] for i in range(VELIKOST)]
        self.zgodovina.append((p, self.na_potezi))

    def kopija(self):
        """Vrni kopijo te igre, brez zgodovine."""
        # Kopijo igre naredimo, ko poženemo na njej algoritem.
        # Če bi algoritem poganjali kar na glavni igri, ki jo
        # uporablja GUI, potem bi GUI mislil, da se menja stanje
        # igre (kdo je na potezi, kdo je zmagal) medtem, ko bi
        # algoritem vlekel poteze
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
            if self.plosca[i / VELIKOST][i % VELIKOST] is PRAZNO:
                    poteze.append((i))
        return poteze

    def povleci_potezo(self, polje):
        """Povleci potezo p, ne naredi nič, če je neveljavna.
           Vrne stanje_igre() po potezi ali None, ce je poteza neveljavna."""
        print(polje)
        y = polje / VELIKOST
        x = polje % VELIKOST
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
        """
        #print self.plosca

        # graph=list(graph)

        graph_modri = self.sestaviGraf(self.plosca, MODRI)
        # print len(graph_modri)
        # print graph_modri
        graph_modri = Graph(graph_modri)
        graph_rdeci = self.sestaviGraf(self.plosca, RDECI)
        # print graph_rdeci
        graph_rdeci = Graph(graph_rdeci)
        # print self.plosca

        stanje_MODRI = graph_modri.dijkstra((0,-1), (0,VELIKOST))
        # print("iscemo pot: ", (0,-1), (0,VELIKOST))
        # print "stanje M: ", stanje_MODRI
        stanje_RDECI = graph_rdeci.dijkstra((-1,0), (VELIKOST, 0))
        # print "stanje R: ", stanje_RDECI


        if stanje_MODRI != NI_KONEC:
            return MODRI
        elif stanje_RDECI != NI_KONEC:
            return RDECI
        elif len(self.veljavne_poteze()) == 0:
            return NEODLOCENO
        elif stanje_MODRI == NI_KONEC and stanje_RDECI == NI_KONEC:
            return NI_KONEC
        else:
            print("Nemore se zgoditi, pa se je, igra.stanje_igre().")


    def sosedi(self, y, x):
        """Metoda preveri, kateri so sosedi izbranega polja."""
        sosedi = []
        for (dy, dx) in ((-1,0), (-1,1),
                 (0, -1),     (0, 1),
                 (1, -1), (1, 0)):
            if 0 <= x + dx < VELIKOST and 0 <= y + dy < VELIKOST:
                sosedi.append((y + dy, x + dx))
        logging.debug ("Sosedi od ({0}, {1}) so {2}".format(y,x,sosedi))
        return sosedi

    def sestaviGraf(self, plosca, barva, ai=False):
        """Sestavi graf trenutne poteze."""
        queue = []
        if ai:
            for vr in range(VELIKOST):
                    for st in range(VELIKOST):
                        seznamSosedov = self.sosedi(vr, st)
                        for sosed in seznamSosedov:
                            if plosca[vr][st] == 'PRAZNO':
                                queue.append(((vr, st),(sosed[0], sosed[1]), 1))
                            elif plosca[vr][st] == barva:
                                queue.append(((vr, st),(sosed[0], sosed[1]), 0))
                            else:
                                pass
        else:
            for vr in range(VELIKOST):
                    for st in range(VELIKOST):
                        seznamSosedov = self.sosedi(vr, st)
                        for sosed in seznamSosedov:
                            if plosca[vr][st] == barva and plosca[sosed[0]][sosed[1]] == barva:
                                queue.append(((vr, st),(sosed[0], sosed[1]), 0))
                            else:
                                pass
        if barva == MODRI:
            # print "barva: ", barva
            for vr in range(VELIKOST):
                queue.append(((0, -1),(vr, 0), 1))
                queue.append(((vr, VELIKOST - 1),(0, VELIKOST), 1))

        if barva == RDECI:
            for st in range(VELIKOST):
                queue.append(((-1, 0),(0, st), 1))
                queue.append(((VELIKOST - 1, st),(VELIKOST , 0), 1))

        return queue
                    
#########################################

#########################################

class Clovek():
    def __init__(self, gui):
        self.gui = gui

    def igraj(self):
        # Smo na potezi. Zaenkrat ne naredimo nič, ampak
        # čakamo, da bo uporanik kliknil na ploščo. Ko se
        # bo to zgodilo, nas bo Gui obvestil preko metode
        # klik.
        pass

    def prekini(self):
        # To metodo kliče GUI, če je treba prekiniti razmišljanje.
        # Človek jo lahko ignorira.
        pass

    def klik(self, p):
        # Povlečemo potezo. Če ni veljavna, se ne bo zgodilo nič.
        self.gui.povleci_potezo(p)

#########################################

class Racunalnik():
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem # Algoritem, ki izračuna potezo
        self.mislec = None # Vlakno (thread), ki razmišlja

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""
        # Tu sprožimo vzporedno vlakno, ki računa potezo. Ker tkinter ne deluje,
        # če vzporedno vlakno direktno uporablja tkinter (glej http://effbot.org/zone/tkinter-threads.htm),
        # zadeve organiziramo takole:
        # - poženemo vlakno, ki poišče potezo
        # - to vlakno nekam zapiše potezo, ki jo je našlo
        # - glavno vlakno, ki sme uporabljati tkinter, vsakih 100ms pogleda, ali
        #   je že bila najdena poteza (metoda preveri_potezo spodaj).
        # Ta rešitev je precej amaterska. Z resno knjižnico za GUI bi zadeve lahko
        # naredili bolje (vlakno bi samo sporočilo GUI-ju, da je treba narediti potezo).

        # Naredimo vlakno, ki mu podamo *kopijo* igre (da ne bo zmedel GUIja):
        self.mislec = threading.Thread(
            target=lambda: self.algoritem.izracunaj_potezo(self.gui.igra.kopija()))

        # Poženemo vlakno:
        self.mislec.start()

        # Gremo preverjat, ali je bila najdena poteza:
        self.gui.plosca.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        """Vsakih 100ms preveri, ali je algoritem že izračunal potezo."""
        if self.algoritem.poteza is not None:
            # Algoritem je našel potezo, povleci jo, če ni bilo prekinitve
            self.gui.povleci_potezo(self.algoritem.poteza)
            # Vzporedno vlakno ni več aktivno, zato ga "pozabimo"
            self.mislec = None
        else:
            # Algoritem še ni našel poteze, preveri še enkrat čez 100ms
            self.gui.plosca.after(100, self.preveri_potezo)

    def prekini(self):
        # To metodo kliče GUI, če je treba prekiniti razmišljanje.
        if self.mislec:
            logging.debug ("Prekinjamo {0}".format(self.mislec))
            # Algoritmu sporočimo, da mora nehati z razmišljanjem
            self.algoritem.prekini()
            # Počakamo, da se vlakno ustavi
            self.mislec.join()
            self.mislec = None

    def klik(self, p):
        # Računalnik ignorira klike
        pass


#########################################

class Gui():

    TAG_FIGURA = 'fig'

    def __init__(self, root, globina):
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
                                        self.zacni_igro(Clovek(self), Clovek(self)))
        menu_moznosti.add_command(label="Človek proti računalniku", command=lambda:
                                        self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina))))
        menu_moznosti.add_command(label="Računalnik proti računalniku", command=lambda:
                                        self.zacni_igro(Racunalnik(self, Minimax(globina)), Racunalnik(self, Minimax(globina))))
        menu_moznosti.add_command(label="Računalnik proti človeku", command=lambda:
                                        self.zacni_igro(Racunalnik(self, AlfaBeta(globina)), Clovek(self)))

        self.napis1 = StringVar(root, value="Hex")
        Label(root, textvariable=self.napis1).grid(row=0, column=0)

        self.napis2 = StringVar(root, value="Na potezi je modri.")
        Label(root, textvariable=self.napis2).grid(row=1, column=0)

        # self.igra = Igra()
        # self.restart(Clovek(self), Clovek(self))
        # Prični igro v načinu človek proti računalniku
        self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina)))

    def zacni_igro(self, igralec_modri, igralec_rdeci):
        """Nastavi stanje igre na zacetek igre.
           Za igralca uporabi dana igralca."""
        # Ustavimo vsa vlakna, ki trenutno razmišljajo
        self.prekini_igralce()
        # Pobrišemo vse figure s polja
        for i in range(VELIKOST**2): self.plosca.itemconfig(seznamSestkotnikov[i], fill='Grey')
        # Ustvarimo novo igro
        self.igra = Igra()
        # Shranimo igralce
        self.igralec_modri = igralec_modri
        self.igralec_rdeci = igralec_rdeci
        # Križec je prvi na potezi
        self.napis2.set("Na potezi je MODRI.")
        self.igralec_modri.igraj()


    def plosca_klik(self, event):                  
        # print('Got object click', event.x, event.y)
        # print(int(event.widget.find_closest(event.x, event.y)[0]))
        
        polje = int(event.widget.find_closest(event.x, event.y)[0])
        polje -= 1
        print(self.igra.na_potezi)
        if self.igra.na_potezi == MODRI:
            self.igralec_modri.klik(polje)
        elif self.igra.na_potezi == RDECI:
            self.igralec_rdeci.klik(polje)



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
                self.plosca.tag_bind(tag, '<ButtonPress-1>', self.plosca_klik)



    def povleci_potezo(self, p):
        """Povleci potezo p, če je veljavna. Če ni veljavna, ne naredi nič."""
        # Najprej povlečemo potezo v igri, še pred tem si zapomnimo, kdo jo je povlekel
        # (ker bo self.igra.povleci_potezo spremenil stanje igre).
        # GUI se *ne* ukvarja z logiko igre, zato ne preverja, ali je poteza veljavna.
        # Ta del za njega opravi self.igra.
        igralec = self.igra.na_potezi
        r = self.igra.povleci_potezo(p)
        if r is None:
            # Poteza ni bila veljavna, nič se ni spremenilo
            pass
        else:
            # Poteza je bila veljavna, narišemo jo na zaslon
            if igralec == MODRI:
                self.pobarvaj_modro(p)
            elif igralec == RDECI:
                self.pobarvaj_rdece(p)
            # Ugotovimo, kako nadaljevati
            zmagovalec = r
            if zmagovalec == NI_KONEC:
                # Igra se nadaljuje
                if self.igra.na_potezi == MODRI:
                    self.napis2.set("Na potezi je MODRI.")
                    self.igralec_modri.igraj()
                elif self.igra.na_potezi == RDECI:
                    self.napis2.set("Na potezi je RDEČI.")
                    self.igralec_rdeci.igraj()
            else:
                # Igre je konec, koncaj
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
        logging.debug ("prekinjam igralce")
        if self.igralec_modri: self.igralec_modri.prekini()
        if self.igralec_rdeci: self.igralec_rdeci.prekini()
        
    def zapriOkno(self, root):
        """Ta metoda se pokliče, ko uporabnik zapre aplikacijo."""
        root.destroy()

        
    def konec(self, zmagovalec):
        """Izpiše zmagovalca in rezultat."""
        if zmagovalec != 'NEODLOCENO': self.napis2.set("Zmagal je " + zmagovalec +".")
        else: self.napis2.set("Igra je neodločena.")
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


class Minimax():
    ZMAGA = 1000000
    NESKONCNO = ZMAGA + 1

    def __init__(self, globina):
        self.globina = globina  # do katere globine iscemo?
        self.prekinitev = False # ali moramo koncati?
        self.igra = None # objekt, ki opisuje igro (ga dobimo kasneje)
        self.jaz = None  # katerega igralca igramo (podatek dobimo kasneje)
        self.poteza = None # sem napisemo potezo, ko jo najdemo

    def prekini(self):
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izracunaj potezo za trenutno stanje dane igre."""
        # To metodo poklicemo iz vzporednega vlakna
        self.igra = igra
        self.prekinitev = False # Glavno vlakno bo to nastvilo na True, ce moramo nehati
        self.jaz = self.igra.na_potezi
        self.poteza = None # Sem napisemo potezo, ko jo najdemo
        # Pozenemo minimax
        (poteza, vrednost) = self.minimax(self.globina, -Minimax.NESKONCNO, Minimax.NESKONCNO, True)
        self.jaz = None
        self.igra = None

        if not self.prekinitev:
            logging.debug ("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
            print poteza, vrednost
            self.poteza = poteza
            return poteza



    def minimax(self, globina, alfa, beta, maksimiziramo):
        """Glavna metoda minimax."""
        if self.prekinitev:
            # Sporocili so nam, da moramo prekiniti
            logging.debug ("Minimax prekinja, globina = {0}".format(globina))
            return (None, 0)
        zmagovalec = self.igra.stanje_igre()
        if zmagovalec in (MODRI, RDECI, NEODLOCENO):
            # Igre je konec, vrnemo njeno vrednost
            if zmagovalec == self.jaz:
                return (None, Minimax.ZMAGA)
            elif zmagovalec == nasprotnik(self.jaz):
                return (None, -Minimax.ZMAGA)
            else:
                return (None, 0)
        elif zmagovalec == NI_KONEC:
            # Igre ni konec
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                # Naredimo eno stopnjo minimax
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    for p in self.igra.veljavne_poteze():
                        self.igra.povleci_potezo(p)
                        vrednost = self.minimax(globina-1, alfa, beta, not maksimiziramo)[1]
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
                    vrednost_najboljse = Minimax.NESKONCNO
                    for p in self.igra.veljavne_poteze():
                        self.igra.povleci_potezo(p)
                        vrednost = self.minimax(globina-1, alfa, beta, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost > alfa:
                            alfa = vrednost
                            najboljsa_poteza = p
                        if alfa >= beta:
                            break
                    return (najboljsa_poteza, beta)

                assert (najboljsa_poteza is not None), "minimax: izracunana poteza je None"
                # return (najboljsa_poteza, vrednost_najboljse)
        else:
            assert False, "minimax: nedefinirano stanje igre"

    def vrednost_pozicije(self):
        """Metoda ovrednoti pozicijo glede na najkrajšo pot, igra potem prvo v vrsti."""
        graph_modri = self.igra.sestaviGraf(self.igra.plosca, MODRI, True)
        graph_modri = Graph(graph_modri)
        stanje_MODRI = graph_modri.dijkstra((0,-1), (0,VELIKOST))

        graph_rdeci = self.igra.sestaviGraf(self.igra.plosca, RDECI, True)
        graph_rdeci = Graph(graph_rdeci)
        stanje_RDECI = graph_rdeci.dijkstra((-1,0), (VELIKOST, 0))
        
        vrednost = 0
        stM=0
        stR=0


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