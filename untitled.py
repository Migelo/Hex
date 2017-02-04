import tkinter    # za uporabniski vmesnik
import threading  # za vzporedno izvajanje
import argparse   # za argumente iz ukazne vrstice
import logging    # za odpravljanje napak

# Privzeta minimax globina, ce je nismo podali ob zagonu v ukazni vrstici
MINIMAX_GLOBINA = 3

######################################################################
## Igra

IGRALEC_X = "X"
IGRALEC_O = "O"
PRAZNO = "."
NEODLOCENO = "neodloceno"
NI_KONEC = "ni konec"

def nasprotnik(igralec):
    """Vrni nasprotnika od igralca."""
    if igralec == IGRALEC_X:
        return IGRALEC_O
    elif igralec == IGRALEC_O:
        return IGRALEC_X
    else:
        # Do sem ne smemo priti, ce pridemo, je napaka v programu.
        # V ta namen ima Python ukaz assert, s katerim lahko preverimo,
        # ali dani pogoj velja. V nasem primeru, ko vemo, da do sem
        # sploh ne bi smeli priti, napisemo za pogoj False, tako da
        # bo program crknil, ce bo prisel do assert. Spodaj je se nekaj
        # uporab assert, kjer dejansko preverjamo pogoje, ki bi morali
        # veljati. To je zelo uporabno za odpravljanje napak.
        # Assert uporabimo takrat, ko bi program lahko deloval naprej kljub
        # napaki (ce bo itak takoj crknil, potem assert ni potreben).
        assert False, "neveljaven nasprotnik"


class Igra():
    def __init__(self):
        self.plosca = [[PRAZNO, PRAZNO, PRAZNO],
                      [PRAZNO, PRAZNO, PRAZNO],
                      [PRAZNO, PRAZNO, PRAZNO]]
        self.na_potezi = IGRALEC_X
        self.zgodovina = []

    def shrani_pozicijo(self):
        """Shrani trenutno pozicijo, da se bomo lahko kasneje vrnili vanjo
           z metodo razveljavi."""
        p = [self.plosca[i][:] for i in range(3)]
        self.zgodovina.append((p, self.na_potezi))

    def kopija(self):
        """Vrni kopijo te igre, brez zgodovine."""
        # Kopijo igre naredimo, ko pozenemo na njej algoritem.
        # ce bi algoritem poganjali kar na glavni igri, ki jo
        # uporablja GUI, potem bi GUI mislil, da se menja stanje
        # igre (kdo je na potezi, kdo je zmagal) medtem, ko bi
        # algoritem vlekel poteze
        k = Igra()
        k.plosca = [self.plosca[i][:] for i in range(3)]
        k.na_potezi = self.na_potezi
        return k

    def razveljavi(self):
        """Razveljavi potezo in se vrni v prejsnje stanje."""
        (self.plosca, self.na_potezi) = self.zgodovina.pop()

    def veljavne_poteze(self):
        """Vrni seznam veljavnih potez."""
        poteze = []
        for i in range(3):
            for j in range(3):
                if self.plosca[i][j] is PRAZNO:
                    poteze.append((i,j))
        return poteze

    def povleci_potezo(self, p):
        """Povleci potezo p, ne naredi nic, ce je neveljavna.
           Vrne stanje_igre() po potezi ali None, ce je poteza neveljavna."""
        (i,j) = p
        if (self.plosca[i][j] != PRAZNO) or (self.na_potezi == None):
            # neveljavna poteza
            return None
        else:
            self.shrani_pozicijo()
            self.plosca[i][j] = self.na_potezi
            (zmagovalec, trojka) = self.stanje_igre()
            if zmagovalec == NI_KONEC:
                # Igre ni konec, zdaj je na potezi nasprotnik
                self.na_potezi = nasprotnik(self.na_potezi)
            else:
                # Igre je konec
                self.na_potezi = None
            return (zmagovalec, trojka)

    # Tabela vseh trojk, ki nastopajo v igralnem polju
    trojke = [
        # Vodoravne
        [(0,0), (0,1), (0,2)],
        [(1,0), (1,1), (1,2)],
        [(2,0), (2,1), (2,2)],
        # Navpicne
        [(0,0), (1,0), (2,0)],
        [(0,1), (1,1), (2,1)],
        [(0,2), (1,2), (2,2)],
        # Diagonali
        [(0,0), (1,1), (2,2)],
        [(0,2), (1,1), (2,0)]
    ]

    def stanje_igre(self):
        """Ugotovi, kaksno je trenutno stanje igre. Vrne:
           - (IGRALEC_X, trojka), ce je igre konec in je zmagal IGRALEC_X z dano zmagovalno trojko
           - (IGRALEC_O, trojka), ce je igre konec in je zmagal IGRALEC_O z dano zmagovalno trojko
           - (NEODLOCENO, None), ce je igre konec in je neodloceno
           - (NI_KONEC, None), ce igre se ni konec
        """
        for t in Igra.trojke:
            ((i1,j1),(i2,j2),(i3,j3)) = t
            p = self.plosca[i1][j1]
            if p != PRAZNO and p == self.plosca[i2][j2] == self.plosca[i3][j3]:
                # Nasli smo zmagovalno trojko
                return (p, [t[0], t[1], t[2]])
        # Ni zmagovalca, ali je igre konec?
        for i in range(3):
            for j in range(3):
                if self.plosca[i][j] is PRAZNO:
                    # Nasli smo prazno plosca, igre ni konec
                    return (NI_KONEC, None)
        # Vsa polja so polna, rezultat je neodlocen
        return (NEODLOCENO, None)


######################################################################
## Igralec clovek

class Clovek():
    def __init__(self, gui):
        self.gui = gui

    def igraj(self):
        # Smo na potezi. Zaenkrat ne naredimo nic, ampak
        # cakamo, da bo uporanik kliknil na plosco. Ko se
        # bo to zgodilo, nas bo Gui obvestil preko metode
        # klik.
        pass

    def prekini(self):
        # To metodo klice GUI, ce je treba prekiniti razmisljanje.
        # clovek jo lahko ignorira.
        pass

    def klik(self, p):
        # Povlecemo potezo. ce ni veljavna, se ne bo zgodilo nic.
        self.gui.povleci_potezo(p)

######################################################################
## Igralec racunalnik

class Racunalnik():
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem # Algoritem, ki izracuna potezo
        self.mislec = None # Vlakno (thread), ki razmislja

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""
        # Tu sprozimo vzporedno vlakno, ki racuna potezo. Ker tkinter ne deluje,
        # ce vzporedno vlakno direktno uporablja tkinter (glej http://effbot.org/zone/tkinter-threads.htm),
        # zadeve organiziramo takole:
        # - pozenemo vlakno, ki poisce potezo
        # - to vlakno nekam zapise potezo, ki jo je naslo
        # - glavno vlakno, ki sme uporabljati tkinter, vsakih 100ms pogleda, ali
        #   je ze bila najdena poteza (metoda preveri_potezo spodaj).
        # Ta resitev je precej amaterska. Z resno knjiznico za GUI bi zadeve lahko
        # naredili bolje (vlakno bi samo sporocilo GUI-ju, da je treba narediti potezo).

        # Naredimo vlakno, ki mu podamo *kopijo* igre (da ne bo zmedel GUIja):
        self.mislec = threading.Thread(
            target=lambda: self.algoritem.izracunaj_potezo(self.gui.igra.kopija()))

        # Pozenemo vlakno:
        self.mislec.start()

        # Gremo preverjat, ali je bila najdena poteza:
        self.gui.plosca.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        """Vsakih 100ms preveri, ali je algoritem ze izracunal potezo."""
        if self.algoritem.poteza is not None:
            # Algoritem je nasel potezo, povleci jo, ce ni bilo prekinitve
            self.gui.povleci_potezo(self.algoritem.poteza)
            # Vzporedno vlakno ni vec aktivno, zato ga "pozabimo"
            self.mislec = None
        else:
            # Algoritem se ni nasel poteze, preveri se enkrat cez 100ms
            self.gui.plosca.after(100, self.preveri_potezo)

    def prekini(self):
        # To metodo klice GUI, ce je treba prekiniti razmisljanje.
        if self.mislec:
            logging.debug ("Prekinjamo {0}".format(self.mislec))
            # Algoritmu sporocimo, da mora nehati z razmisljanjem
            self.algoritem.prekini()
            # Pocakamo, da se vlakno ustavi
            self.mislec.join()
            self.mislec = None

    def klik(self, p):
        # Racunalnik ignorira klike
        pass


######################################################################
## Algoritem minimax

class Minimax:
    # Algoritem minimax predstavimo z objektom, ki hrani stanje igre in
    # algoritma, nima pa dostopa do GUI (ker ga ne sme uporabljati, saj deluje
    # v drugem vlaknu kot tkinter).

    def __init__(self, globina):
        self.globina = globina  # do katere globine iscemo?
        self.prekinitev = False # ali moramo koncati?
        self.igra = None # objekt, ki opisuje igro (ga dobimo kasneje)
        self.jaz = None  # katerega igralca jao (podatek dobimo kasneje)
        self.poteza = None # sem napisemo potezo, ko jo najdemo

    def prekini(self):
        """Metoda, ki jo poklice GUI, ce je treba nehati razmisljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izracunaj potezo za trenutno stanje dane igre."""
        # To metodo poklicemo iz vzporednega vlakna
        self.igra = igra
        self.prekinitev = False # Glavno vlakno bo to nastvilo na True, ce moramo nehati
        self.jaz = self.igra.na_potezi
        self.poteza = None # Sem napisemo potezo, ko jo najdemo
        # Pozenemo minimax
        (poteza, vrednost) = self.minimax(self.globina, True)
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            # Potezo izvedemo v primeru, da nismo bili prekinjeni
            logging.debug("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
            self.poteza = poteza

    # Vrednosti igre
    ZMAGA = 100000 # Mora biti vsaj 10^5
    NESKONCNO = ZMAGA + 1 # Vec kot zmaga

    def vrednost_pozicije(self):
        """Ocena vrednosti pozicije: sesteje vrednosti vseh trojk na plosci."""
        # Slovar, ki pove, koliko so vredne posamezne trojke, kjer "(x,y) : v" pomeni:
        # ce imamo v trojki x znakov igralca in y znakov nasprotnika (in 3-x-y praznih polj),
        # potem je taka trojka za self.jaz vredna v.
        # Trojke, ki se ne pojavljajo v slovarju, so vredne 0.
        vrednost_trojke = {
            (3,0) : Minimax.ZMAGA,
            (0,3) : -Minimax.ZMAGA//10,
            (2,0) : Minimax.ZMAGA//100,
            (0,2) : -Minimax.ZMAGA//1000,
            (1,0) : Minimax.ZMAGA//10000,
            (0,1) : -Minimax.ZMAGA//100000
        }
        vrednost = 0
        for t in self.igra.trojke:
            x = 0
            y = 0
            for (i,j) in t:
                if self.igra.plosca[i][j] == self.jaz:
                    x += 1
                elif self.igra.plosca[i][j] == nasprotnik(self.jaz):
                    y += 1
            vrednost += vrednost_trojke.get((x,y), 0)
        return vrednost

    def minimax(self, globina, maksimiziramo):
        """Glavna metoda minimax."""
        if self.prekinitev:
            # Sporocili so nam, da moramo prekiniti
            logging.debug ("Minimax prekinja, globina = {0}".format(globina))
            return (None, 0)
        (zmagovalec, lst) = self.igra.stanje_igre()
        if zmagovalec in (IGRALEC_X, IGRALEC_O, NEODLOCENO):
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

######################################################################
## Uporabniski vmesnik

class Gui():
    # S to oznako so oznaceni vsi graficni elementi v self.plosca, ki se
    # pobrisejo, ko se zacne nova igra (torej, krizci in krozci)
    TAG_FIGURA = 'figura'

    # Oznaka za crte
    TAG_OKVIR = 'okvir'

    # Velikost polja
    VELIKOST_POLJA = 100

    def __init__(self, master, globina):
        self.igralec_x = None # Objekt, ki igra X (nastavimo ob zacetku igre)
        self.igralec_o = None # Objekt, ki igra O (nastavimo ob zacetku igre)
        self.igra = None # Objekt, ki predstavlja igro (nastavimo ob zacetku igre)

        # ce uporabnik zapre okno naj se poklice self.zapri_okno
        master.protocol("WM_DELETE_WINDOW", lambda: self.zapri_okno(master))

        # Glavni menu
        menu = tkinter.Menu(master)
        master.config(menu=menu) # Dodamo glavni menu v okno

        # Podmenu za izbiro igre
        menu_igra = tkinter.Menu(menu)
        menu.add_cascade(label="Igra", menu=menu_igra)
        menu_igra.add_command(label="X=clovek, O=clovek",
                              command=lambda: self.zacni_igro(Clovek(self),
                                                              Clovek(self)))
        menu_igra.add_command(label="X=clovek, O=Racunalnik",
                              command=lambda: self.zacni_igro(Clovek(self),
                                                              Racunalnik(self, Minimax(globina))))
        menu_igra.add_command(label="X=Racunalnik, O=clovek",
                              command=lambda: self.zacni_igro(Racunalnik(self, Minimax(globina)),
                                                              Clovek(self)))
        menu_igra.add_command(label="X=Racunalnik, O=Racunalnik",
                              command=lambda: self.zacni_igro(Racunalnik(self, Minimax(globina)),
                                                              Racunalnik(self, Minimax(globina))))

        # Napis, ki prikazuje stanje igre
        self.napis = tkinter.StringVar(master, value="Dobrodosli v 3 x 3!")
        tkinter.Label(master, textvariable=self.napis).grid(row=0, column=0)

        # Igralno obmocje
        self.plosca = tkinter.Canvas(master, width=3*Gui.VELIKOST_POLJA, height=3*Gui.VELIKOST_POLJA)
        self.plosca.grid(row=1, column=0)

        # crte na igralnem polju
        self.narisi_crte()

        # Narocimo se na dogodek Button-1 na self.plosca,
        self.plosca.bind("<Button-1>", self.plosca_klik)

        # Pricni igro v nacinu clovek proti racunalniku
        self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina)))


    def zacni_igro(self, igralec_x, igralec_o):
        """Nastavi stanje igre na zacetek igre.
           Za igralca uporabi dana igralca."""
        # Ustavimo vsa vlakna, ki trenutno razmisljajo
        self.prekini_igralce()
        # Pobrisemo vse figure s polja
        self.plosca.delete(Gui.TAG_FIGURA)
        # Ustvarimo novo igro
        self.igra = Igra()
        # Shranimo igralce
        self.igralec_x = igralec_x
        self.igralec_o = igralec_o
        # Krizec je prvi na potezi
        self.napis.set("Na potezi je X.")
        self.igralec_x.igraj()

    def koncaj_igro(self, zmagovalec, trojka):
        """Nastavi stanje igre na konec igre."""
        if zmagovalec == IGRALEC_X:
            self.napis.set("Zmagal je X.")
            self.narisi_zmagovalno_trojico(zmagovalec, trojka)
        elif zmagovalec == IGRALEC_O:
            self.napis.set("Zmagal je O.")
            self.narisi_zmagovalno_trojico(zmagovalec, trojka)
        else:
            self.napis.set("Neodloceno.")

    def prekini_igralce(self):
        """Sporoci igralcem, da morajo nehati razmisljati."""
        logging.debug ("prekinjam igralce")
        if self.igralec_x: self.igralec_x.prekini()
        if self.igralec_o: self.igralec_o.prekini()

    def zapri_okno(self, master):
        """Ta metoda se poklice, ko uporabnik zapre aplikacijo."""
        # Vlaknom, ki tecejo vzporedno, je treba sporociti, da morajo
        # koncati, sicer se bo okno zaprlo, aplikacija pa bo se vedno
        # delovala.
        self.prekini_igralce()
        # Dejansko zapremo okno.
        master.destroy()

    def narisi_crte(self):
        """Narisi crte v igralnem polju"""
        self.plosca.delete(Gui.TAG_OKVIR)
        d = Gui.VELIKOST_POLJA
        self.plosca.create_line(1*d, 0*d, 1*d, 3*d, tag=Gui.TAG_OKVIR)
        self.plosca.create_line(2*d, 0*d, 2*d, 3*d, tag=Gui.TAG_OKVIR)
        self.plosca.create_line(0*d, 1*d, 3*d, 1*d, tag=Gui.TAG_OKVIR)
        self.plosca.create_line(0*d, 2*d, 3*d, 2*d, tag=Gui.TAG_OKVIR)

    def narisi_X(self, p, zmagovalni=False):
        """Narisi krizec v polje (i, j)."""
        x = p[0] * 100
        y = p[1] * 100
        sirina = (10 if zmagovalni else 3)
        self.plosca.create_line(x+5, y+5, x+95, y+95, width=sirina, tag=Gui.TAG_FIGURA)
        self.plosca.create_line(x+95, y+5, x+5, y+95, width=sirina, tag=Gui.TAG_FIGURA)

    def narisi_O(self, p, zmagovalni=False):
        """Narisi krozec v polje (i, j)."""
        x = p[0] * 100
        y = p[1] * 100
        sirina = (10 if zmagovalni else 3)
        self.plosca.create_oval(x+5, y+5, x+95, y+95, width=sirina,tag=Gui.TAG_FIGURA)

    def narisi_zmagovalno_trojico(self, zmagovalec, trojka):
        for p in trojka:
            if zmagovalec == IGRALEC_X:
                self.narisi_X(p, zmagovalni=True)
            elif zmagovalec == IGRALEC_O:
                self.narisi_O(p, zmagovalni=True)

    def plosca_klik(self, event):
        """Obdelaj klik na plosco."""
        # Tistemu, ki je na potezi, povemo, da je uporabnik kliknil na plosco.
        # Podamo mu potezo p.
        i = event.x // 100
        j = event.y // 100
        if 0 <= i <= 2 and 0 <= j <= 2:
            if self.igra.na_potezi == IGRALEC_X:
                self.igralec_x.klik((i,j))
            elif self.igra.na_potezi == IGRALEC_O:
                self.igralec_o.klik((i,j))
            else:
                # Nihce ni na potezi, ne naredimo nic
                pass
        else:
            logging.debug("klik izven plosce {0}, polje {1}".format((event.x,event.y), (i,j)))

    def povleci_potezo(self, p):
        """Povleci potezo p, ce je veljavna. ce ni veljavna, ne naredi nic."""
        # Najprej povlecemo potezo v igri, se pred tem si zapomnimo, kdo jo je povlekel
        # (ker bo self.igra.povleci_potezo spremenil stanje igre).
        # GUI se *ne* ukvarja z logiko igre, zato ne preverja, ali je poteza veljavna.
        # Ta del za njega opravi self.igra.
        igralec = self.igra.na_potezi
        r = self.igra.povleci_potezo(p)
        if r is None:
            # Poteza ni bila veljavna, nic se ni spremenilo
            pass
        else:
            # Poteza je bila veljavna, narisemo jo na zaslon
            if igralec == IGRALEC_X:
                self.narisi_X(p)
            elif igralec == IGRALEC_O:
                self.narisi_O(p)
            # Ugotovimo, kako nadaljevati
            (zmagovalec, trojka) = r
            if zmagovalec == NI_KONEC:
                # Igra se nadaljuje
                if self.igra.na_potezi == IGRALEC_X:
                    self.napis.set("Na potezi je X.")
                    self.igralec_x.igraj()
                elif self.igra.na_potezi == IGRALEC_O:
                    self.napis.set("Na potezi je O.")
                    self.igralec_o.igraj()
            else:
                # Igre je konec, koncaj
                self.koncaj_igro(zmagovalec, trojka)

######################################################################
## Glavni program

# Glavnemu oknu recemo "root" (koren), ker so graficni elementi
# organizirani v drevo, glavno okno pa je koren tega drevesa

if __name__ == "__main__":
    # Iz ukazne vrstice poberemo globino za minimax, uporabimo
    # modul argparse, glej https://docs.python.org/3.4/library/argparse.html

    # Opisemo argumente, ki jih sprejmemo iz ukazne vrstice
    parser = argparse.ArgumentParser(description="Igrica tri v vrsto")
    # Argument --globina n, s privzeto vrednostjo MINIMAX_GLOBINA
    parser.add_argument('--globina',
                        default=MINIMAX_GLOBINA,
                        type=int,
                        help='globina iskanja za minimax algoritem')
    # Argument --debug, ki vklopi sporocila o tem, kaj se dogaja
    parser.add_argument('--debug',
                        action='store_true',
                        help='vklopi sporocila o dogajanju')

    # Obdelamo argumente iz ukazne vrstice
    args = parser.parse_args()

    # Vklopimo sporocila, ce je uporabnik podal --debug
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    # Naredimo glavno okno in nastavimo ime
    root = tkinter.Tk()
    root.title("Tri v vrsto")

    # Naredimo objekt razreda Gui in ga spravimo v spremenljivko,
    # sicer bo Python mislil, da je objekt neuporabljen in ga bo pobrisal
    # iz pomnilnika.
    aplikacija = Gui(root, args.globina)

    # Kontrolo prepustimo glavnemu oknu. Funkcija mainloop neha
    # delovati, ko okno zapremo.
    root.mainloop()