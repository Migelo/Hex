from collections import namedtuple#, queue
from pprint import pprint as pp
from multiprocessing import Queue
from collections import deque
 
VELIKOST, SIZE = 8, 8
MODRI = 'M'
RDECI = 'R'

inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')
 
class Graph():
	def __init__(self, edges):
		self.edges = edges2 = [Edge(*edge) for edge in edges]
		self.vertices = set(sum(([e.start, e.end] for e in edges2), []))
		# self.edges = 
 
	def dijkstra(self, source, dest):
		if not source in self.vertices:
			return None
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
				if alt < dist[v]:                        # Relax (u,v,a)
					dist[v] = alt
					previous[v] = u
		#pp(previous)
		s, u = deque(), dest
		while previous[u]:
			s.appendleft(u)
			u = previous[u]
		s.appendleft(u)
		if len(s) == 1: return None
		else: return s
 
 
# graph = Graph([("a", "b", 7),  ("a", "c", 9),  ("a", "f", 14), ("b", "c", 10),
#                ("b", "d", 15), ("c", "d", 11), ("c", "f", 2),  ("d", "e", 6),
#                ("e", "f", 9)])

class Igra():

	def __init__(self):
		self.plosca = [['PRAZNO' for x in range(VELIKOST)] for y in range(VELIKOST)]
		self.na_potezi = MODRI
		# print self.plosca
		# return self.plosca

	def sosedi(self, y, x):
		"""Metoda preveri, kateri so sosedi izbranega polja."""
		sosedi = []
		for (dy, dx) in ((-1,0), (-1,1),
				 "x",     (0, 1),
				 (1, -1), (1, 0)):
			if 0 <= x + dx < SIZE and 0 <= y + dy < SIZE:
				sosedi.append((y + dy, x + dx))
		# logging.debug ("Sosedi od ({0}, {1}) so {2}".format(y,x,sosedi))
		return sosedi

	def nasprotnik(self, igralec):
		"Vrne nasprotnika"
		if igralec == MODRI:
			return RDECI
		elif igralec == RDECI:
			return MODRI
		else:
			assert False, "neveljaven nasprotnik"

	def sestaviGraf(self, plosca):
		"""Sestavi graf trenutne poteze. Format zapisa v queue"""
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


# igra = Igra()
# graph = set(igra.sestaviGraf(igra.plosca))
# graph=list(graph)
# test = []
# for i in range(len(graph)):
# 	if graph[i][0][1] == 3 or graph[i][1][1] == 3: 
# 		test.append(graph[i])
# # print test

graph = [("x", "a", 1), ("b", "y", 1), ("x", "c", 1), ("d", "y", 1), ("x", "e", 1), ("f", "y", 1)]

graph = Graph(graph)
# del graph2
pp(graph.dijkstra("x", "y"))
