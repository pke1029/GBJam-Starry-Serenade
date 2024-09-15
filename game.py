from pyxel import *

def randlist(mylist=[]):
	n = len(mylist)
	i = rndi(0, n-1)
	return mylist[i]

def partition(n, k, a, b):
	key = list(range(k))
	val = [a for i in range(k)]
	for i in range(n-a*k):
		j = randlist(key)
		val[j] += 1 
		if val[j] >= b:
			key.remove(j)
			if len(key) == 0:
				break
	return val

def choices(mylist, k):
	if k >= len(mylist):
		return mylist
	a = []
	for i in range(k):
		a.append(mylist.pop(rndi(0,len(mylist)-1)))
	return a

def lerp(x, a, b):
	return (1-x)*a + x*b

def easein(x, t0):
	if x >= t0:
		return 1
	if x <= 0:
		return 0
	x = x/t0 
	return -x*x + 2*x 

def easecos(x, t0):
	if x > t0:
		return 1
	if x < 0:
		return 0
	x = x*180/t0 
	return 0.5*(1-cos(x))

def pol2cart(r, th):
	x = r*cos(th)
	y = r*sin(th)
	return x, y

def get(mylist, i):
	n = len(mylist)
	if n == 0:
		return None
	return mylist[i % n]

def clamp(x, a=0, b=1):
	if x < a:
		return a 
	if x > b:
		return b 
	return x 

class Graph:

	def __init__(self, n=6):
		self.n = n
		self.get_nodes()
		self.nodes[0].occupied = randlist([-2,-1,-1,0])
		for i in range(len(self.nodes)-1, -1, -1):
			self.add_edge(self.nodes[i])
		self.reset_col()
		self.is_complete = False
		self.speed = 1

	def update(self):
		for i in self.nodes:
			i.update()
		for i in self.edges:
			i.update()
		self.is_complete = all([i.col==Edge.CORRECT for i in self.edges])

	def draw(self):
		for i in self.edges:
			i.draw()
		for i in self.nodes:
			i.draw()

	def get_nodes(self):
		sizes = partition(self.n-1, 3, a=1, b=3)
		# layer 0 
		n0 = [Node(0, rndi(1,3))]
		# layer 1
		r1 = rndi(20,25)
		n1, e1 = Orbit.create(r1, sizes[0])
		# layer 3 
		r3 = rndi(55,60)
		n3, e3 = Orbit.create(r3, sizes[2])
		# layer 2 
		r2 = rndi(r1+20, r3-20)
		n2, e2 = Orbit.create(r2, sizes[1])
		# store 
		self.edges = [e1, e2, e3]
		self.nodes = n0 + n1 + n2 + n3
		self.layers = [n0, n1, n2, n3]
		self.orbit_r = [r1, r2, r3]
		self.shapes = [i.shape for i in self.nodes]
		self.firsts = [0, 1, 1+len(n1), 1+len(n1)+len(n2)]
		# print(self.shapes)

	def add_edge(self, n1):
		compat = [n2 for n2 in self.nodes if n2.shape!=n1.shape]
		compat = [n2 for n2 in compat if n2 not in n1.neighs]
		compat = [n2 for n2 in compat if n2.r < n1.r]
		compat = [n2 for n2 in compat if n2.occupied < 1]
		if len(compat) == 0:
			return 
		n2 = randlist(compat)
		n1.neighs.append(n2)
		n2.neighs.append(n1)
		n2.occupied += 1
		n2.follow(n1)
		self.edges.append(Edge([n1, n2]))

	def reset_col(self):
		for i in self.nodes:
			i.shape = 0

	def get_node(self, orbit_no, node_no):
		node_list = self.layers[orbit_no]
		return node_list[node_no % len(node_list)]

	def check(self):
		return all([i.col==Edge.CORRECT for i in self.edges])

	def next(self, node):
		# i = 
		pass

class Node:

	LERP_FAC = 0.2
	spd_multiplier = 1

	def __init__(self, r=0, shape=0):
		self.x = 0
		self.y = 0
		self.r = r
		self._r = 0
		self._th = 360
		self.shape = shape 
		self.th = rndf(0, 360)
		self.speed = 0 if r==0 else rndf(10, 40)/r
		self.neighs = []
		self.occupied = 0
		self.planet = None

	def update(self):
		self._r = lerp(Node.LERP_FAC, self._r, self.r) 
		self._th = lerp(Node.LERP_FAC, self._th, self.th) 
		self.x, self.y = pol2cart(self._r, self._th)
		self.th -= Node.spd_multiplier*self.speed

	def draw(self):
		# circ(self.x, self.y, 2, self.shape)
		circ(self.x, self.y, 2, 0)
		circb(self.x, self.y, 2, 1)

	def follow(self, node):
		self.th = node.th # + rndf(-10,10)
		self.speed = node.speed 

	def unparent(self):
		if self.planet == None:
			return
		self.planet.node = None
		self.planet = None
		self.shape = 0

class Edge:

	# color
	CORRECT = 2
	WRONG = 1

	def __init__(self, nodes=[]):
		self.nodes = nodes 
		self.n = len(nodes)
		self.col = Edge.WRONG

	def update(self):
		shapes = [i.shape for i in self.nodes]
		if 0 in shapes: 
			self.col = Edge.WRONG
			return
		shapes = set(shapes)
		self.col = Edge.CORRECT if len(shapes) == self.n else Edge.WRONG

	def draw(self):
		x1 = self.nodes[0].x
		y1 = self.nodes[0].y
		x2 = self.nodes[1].x
		y2 = self.nodes[1].y
		line(x1, y1, x2, y2, self.col)

class Orbit(Edge):

	LERP_FAC = 0.2

	def __init__(self, r, nodes=[]):
		super().__init__(nodes);
		self.r = r  
		self._r = 0

	def update(self):
		super().update()
		self._r = lerp(Orbit.LERP_FAC, self._r, self.r)

	def draw(self):
		circb(0, 0, self._r, self.col)
		# ellib(0-self.r, -self._r, 2*self.r, 2*self._r, self.col)

	def create(r, n):
		cols = choices([1,2,3], n)
		nodes = [Node(r, cols[i]) for i in range(n)]
		for i in nodes:
			i.neighs = nodes[:]
		orbit = Orbit(r, nodes=nodes)
		return nodes, orbit

class Invetory:

	SPACING = 13

	def __init__(self, shapes):
		self.w = 0
		self.n = len(shapes)
		self.y = 60
		self.get_planets(shapes)
		self._y = self.y

	def draw(self):
		rectb(-self.w/2, self._y-7, self.w, 15, 2)
		circ(-self.w/2, self._y, 7, 0)
		circb(-self.w/2, self._y, 7, 2)
		circ(self.w/2, self._y, 7, 0)
		circb(self.w/2, self._y, 7, 2)
		rect(-self.w/2+1, self._y-6, self.w-2, 13, 0)
		blt(-self.w/2-16, self._y-7, 0, 56, 0, 16, 16, 3)
		blt(self.w/2, self._y-7, 0, 56, 0, -16, 16, 3)
		for p in self.planets:
			p.draw()

	def update(self):
		self.selectable = [p for p in self.planets if p.node == None]
		self.n = len(self.selectable)
		self.w = max(lerp(0.1, self.w, self.n*Invetory.SPACING), Invetory.SPACING)
		for i in range(self.n):
			 self.selectable[i].x = i*Invetory.SPACING - (self.n-1)/2*Invetory.SPACING 
			 self.selectable[i].y = self.y
		for p in self.planets:
			p.update()
		# hide invent
		self.y = 80 if inventory.n == 0 else 60
		self._y = lerp(0.2, self._y, self.y)


	def get_planets(self, shapes=[]):
		self.planets = []
		shapes.sort()
		for i in range(len(shapes)):
			x = i*Invetory.SPACING - (self.n-1)/2*Invetory.SPACING 
			y = self.y
			self.planets.append(Planet(x, y, shape=shapes[i]))
		self.selectable = self.planets[:]

class Planet:

	SPRITE = {1:[2,3,4,5], 2:[2,3,4,6], 3:[2,3,4]}
	LERP_FAC = 0.1
	EASE_TIME = 60

	def __init__(self, x=0, y=0, shape=1):
		self._x = 0 	# this is not typor
		self._y = y
		self.x = x
		self.y = y
		self.t = rndi(0, 600)
		self.t_ease = 0
		self.shape = shape
		self.spr = randlist(Planet.SPRITE[shape])
		self.node = None

	def update(self):
		self.t += 1
		if self.node != None:
			self.x = self.node.x 
			self.y = self.node.y
			self.t_ease += 1 
			fac = easein(self.t_ease, Planet.EASE_TIME)
			self._x = lerp(fac, self._x, self.x)
			self._y = lerp(fac, self._y, self.y)
		else:
			self.t_ease = 0
			self._x = lerp(Planet.LERP_FAC, self._x, self.x)
			self._y = lerp(Planet.LERP_FAC, self._y, self.y)

	def draw(self):
		# if self.node == None:
			# blt(self._x-8, self._y-8 + self.t//30%2, 0, 0, self.spr*16, 16, 16, 0)
		# else:
		blt(self._x-8, self._y-8 + self.t//30%2, 0, 16*self.spr, 16*self.shape, 16, 16, 5)

	def parent(self, node):
		self.node = node
		node.planet = self
		node.shape = self.shape

	def unparent(self):
		self.node.planet = None
		self.node.shape = 0
		self.node = None

class Cursor:

	# FRAMES = [8, 16, 24, 32, 40, 48]
	FRAMES = [0, 16, 32, 48, 64, 80]
	N = 6
	LERP_FAC = 0.5
	KEYS = [KEY_Z, KEY_X, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]

	def __init__(self):
		self.x = 0
		self.y = 0
		self._x = 0
		self._y = 0
		self.t = 0
		self.show = True
		self.orbit_no = 0
		self.node_no = 0
		self.node = graph.nodes[0]
		self.invent = -1

	def update(self):
		# self.node = graph.get_node(self.orbit_no, self.node_no)
		self.node = graph.nodes[self.node_no]
		# position cursor
		if self.invent == -1:
			self.x = self.node.x
			self.y = self.node.y
		else:
			planet = get(inventory.selectable, self.invent)
			self.x = planet.x 
			self.y = planet.y
		self._x = lerp(Cursor.LERP_FAC, self._x, self.x)
		self._y = lerp(Cursor.LERP_FAC, self._y, self.y)
		if not cursor.show:
			return
		if scenemanager.is_busy:
			return
		if self.invent == -1:

			# if btnp(KEY_RIGHT):
			# 	self.node_no += 1
			# 	play(3, 50)
			# elif btnp(KEY_LEFT):
			# 	self.node_no -= 1
			# 	play(3, 50)
			# elif btnp(KEY_UP):
			# 	self.node_no = 0 
			# 	self.orbit_no = (self.orbit_no + 1) % 4
			# 	play(3, 50)
			# elif btnp(KEY_DOWN):
			# 	self.node_no = 0 
			# 	self.orbit_no = (self.orbit_no - 1) % 4
			# 	play(3, 50) 
			if btnp(KEY_RIGHT) or btnp(GAMEPAD1_BUTTON_DPAD_RIGHT):
				self.node_no = (self.node_no + 1) % graph.n
				play(3, 50)  
			elif btnp(KEY_LEFT) or btnp(GAMEPAD1_BUTTON_DPAD_LEFT):
				self.node_no = (self.node_no - 1) % graph.n
				play(3, 50) 
			if btnp(KEY_UP) or btnp(GAMEPAD1_BUTTON_DPAD_UP):
				if self.node_no >= graph.firsts[-1]:
					self.node_no = 0
				else:
					for i in graph.firsts:
						if self.node_no < i:
							self.node_no = i
							break
				play(3, 50)  
			if btnp(KEY_DOWN) or btnp(GAMEPAD1_BUTTON_DPAD_DOWN):
				if self.node_no == 0:
					self.node_no = graph.firsts[-1]
				elif self.node_no >= graph.firsts[3]:
					self.node_no = graph.firsts[2]
				elif self.node_no >= graph.firsts[2]:
					self.node_no = graph.firsts[1]
				else:
					self.node_no = 0
				play(3, 50)  
			# go to invent
			if btnp(KEY_Z) or btnp(GAMEPAD1_BUTTON_A):
				if len(inventory.selectable) > 0:
					self.invent = 0
					play(3, 51)
			# remove planet from node
			if btnp(KEY_X) or btnp(GAMEPAD1_BUTTON_B):
				if self.node.planet != None:
					self.node.unparent()
					play(3, 52)
		else: 
			# selecting invent
			if btnp(KEY_RIGHT) or btnp(KEY_UP) or btnp(GAMEPAD1_BUTTON_DPAD_RIGHT) or btnp(GAMEPAD1_BUTTON_DPAD_UP):
				self.invent = (self.invent + 1) % inventory.n
				play(3, 50)
			elif btnp(KEY_LEFT) or btnp(KEY_DOWN) or btnp(GAMEPAD1_BUTTON_DPAD_LEFT) or btnp(GAMEPAD1_BUTTON_DPAD_DOWN):
				self.invent = (self.invent - 1) % inventory.n
				play(3, 50)
			# exit invent
			if btnp(KEY_X) or btnp(GAMEPAD1_BUTTON_B):
				self.invent = -1
				play(3, 52)
			# assign/switch planet
			elif btnp(KEY_Z) or btnp(GAMEPAD1_BUTTON_A):
				if self.node.planet != None:
					self.node.unparent()
				planet = get(inventory.selectable, self.invent)
				planet.parent(self.node)
				self.invent = -1
				play(3, 55)

	def draw(self):
		self.t += 1
		padding = 0
		if self.invent != -1:
			padding = 4
		elif self.node.planet != None:
			padding = 3
		if self.show:
			# blt(self._x-4, self._y-12 + self.t//20%2 - padding, 0, Cursor.FRAMES[self.t//3 % Cursor.N], 8, 8, 8, 0)
			blt(self._x-8, self._y-12 + self.t//20%2 - padding, 0, Cursor.FRAMES[self.t//3 % Cursor.N], 64, 16, 8, 5)

class Menu:

	def __init__(self):
		self.x = -2
		self.y = -H2 + 2
		self.w = 60
		self.h = 28
		self.show = False
		self.current = 0
		self.t = 0
		self.speed = 2

	def update(self):
		self.t += 1
		Node.spd_multiplier = 0.5*self.speed 
		if scenemanager.is_busy:
			return
		if btnp(KEY_RETURN) or btnp(GAMEPAD1_BUTTON_X):
			self.toggle()
			play(3, 54)
		if not self.show:
			return
		if btnp(KEY_X) or btnp(GAMEPAD1_BUTTON_B):
			self.show = False
			cursor.show = True
			play(3, 52)
			return 
		if btnp(KEY_UP) or btnp(GAMEPAD1_BUTTON_DPAD_UP):
			self.current = (self.current - 1) % 3
			play(3, 50)
			return
		if btnp(KEY_DOWN) or btnp(GAMEPAD1_BUTTON_DPAD_DOWN):
			self.current = (self.current + 1) % 3
			play(3, 50)
			return 
		if not (btnp(KEY_Z) or btnp(GAMEPAD1_BUTTON_A)):
			return
		# return to title
		if self.current == 2:
			scenemanager.next(TitleScreen)
			self.toggle()
			return
		# reset level
		if self.current == 1:
			for node in graph.nodes:
				node.unparent()
			self.toggle()
			play(3, 51)
			return
		# change speed
		if self.current == 0:
			self.speed = (self.speed + 1) % 5
			play(3, 51)

	def draw(self):
		if not self.show:
			return
		blt(self.x, self.y, 0, 0, 72, 80, 32, 1)
		blt(self.x, self.y+24, 0, 0, 104, 80, 16, 1)
		blt(self.x+7, self.y+9+8*self.current, 0, 88+8*(self.t//15%2), 0, 8, 8, 0)
		text(self.x+13, self.y+10, 'Speed', 0)
		# text(self.x+13, self.y+18, 'Zen mode', 0)
		text(self.x+13, self.y+18, 'Reset level', 0)
		text(self.x+13, self.y+26, 'Return to title', 0)
		text(self.x+65, self.y+10, 'x'+str(self.speed), 1)
		# text(self.x+61, self.y+18, 'OFF', 1)

	def toggle(self):
		self.show = not self.show
		cursor.show = not cursor.show

class Decor:

	def __init__(self, x, y, ): 
		self.x = x 
		self.y = y 

	def _load(N=30, is_title=False):
		Star.instances = []
		Nebula.instances = []
		# random scatter
		for i in range(N):
			x = rndi(0, W) - W2
			y = rndi(0, H) - H2
			Star(x, y)
		# ring
		d1 = graph.orbit_r[1] - graph.orbit_r[0]
		d2 = graph.orbit_r[2] - graph.orbit_r[1]
		if is_title:
			Decor._ring(0.5*(graph.orbit_r[2] + graph.orbit_r[1]), spread=d2/4)
		elif d1 > d2:
			Decor._ring(0.5*(graph.orbit_r[1] + graph.orbit_r[0]), spread=d1/4)
		else:
			Decor._ring(0.5*(graph.orbit_r[2] + graph.orbit_r[1]), spread=d2/4)
		# ring outter
		Decor._ring(85, spread=15, k2=rndf(0,4), density=1.2, nebula=True)

	def update_all():
		ShootingStar.update_all()
		Particles.update_all()

	def draw_all():
		Nebula.draw_all()
		Star.draw_all()
		Particles.draw_all()

	def _ring(r=30, density=3, spread=3, k2=0, nebula=False):
		n = floor(density*spread*r/5) 
		dt = 360/n 
		th0 = rndf(0, 360)
		k = rndf(1, 3)
		b = rndf(0.2, 0.5)
		for i in range(n):
			th = i * dt + th0
			prob = sin(k*th) + b
			if rndf(0, 1+b) < prob:
				s = rndf(-1,1)
				r0 = r + spread*sgn(s)*s**2 + 5*sin(k2*th)
				x, y = pol2cart(r0, th)
				spr = rndi(1, 3)
				Star(x, y)
		if not nebula:
			return
		n = floor(density*spread*r/4) 
		b = 0.5
		for i in range(n):
			th = i * dt + th0
			prob = (sin(k*th) + b) / (1+b)
			nr = rndf(0, 1) 
			if nr < prob:
				s = rndf(-1,1)
				r0 = r + 0.9*spread*sgn(s)*s**2*prob + 5*sin(k2*th)
				x, y = pol2cart(r0, th)
				nr = rndi(2, ceil(8*prob))
				Nebula(x, y, nr)
		th0 = rndf(0, 360)
		k = rndf(3, 5)
		for i in range(n):
			th = i * dt + th0
			prob = sin(k*th)
			nr = rndf(0, 1) 
			if nr < prob:
				s = rndf(-1,1)
				r0 = r + 0.9*spread*sgn(s)*s**2*prob + 10
				x, y = pol2cart(r0, th)
				nr = rndi(3, ceil(8*prob))
				Nebula(x, y, nr, 2)

class Star(Decor):

	instances = []

	def __init__(self, x, y): 
		super().__init__(x, y)
		self.t = rndi(0, 600) 
		Star.instances.append(self)

	def draw(self):
		self.t += 1
		frame = self.t//30 % 10
		frame = 1 if frame == 9 else 0
		circ(self.x, self.y, frame, 2)

	def draw_all():
		for i in Star.instances:
			i.draw() 

class Nebula(Decor):

	instances = []

	def __init__(self, x, y, r, col=3): 
		self.r = r 
		self.col = col
		super().__init__(x, y)
		Nebula.instances.append(self)

	def draw(self):
		circ(self.x, self.y, self.r, self.col)

	def draw_all():
		for i in Nebula.instances:
			i.draw()

class Particles:

	instances = []

	def __init__(self, x, y, t=60, col=2):
		self.x = x 
		self.y = y 
		self.t = t 
		self.col = col
		Particles.instances.append(self)

	def update(self):
		self.t -= 1 

	def draw(self):
		if self.t > 6:
			pset(self.x, self.y, self.col)
		elif not self.t // 3 % 2 == 1:
			pset(self.x, self.y, self.col)

	def update_all():		
		for p in Particles.instances:
			p.update()
			if p.t <= 0:
				Particles.instances.remove(p)

	def draw_all():
		for p in Particles.instances:
			p.draw()

class ShootingStar:

	instances = []
	next_t = 10
	t = 0
	min_len = 10
	max_len = 20

	def __init__(self):
		self.x = rndi(0, W) - W2 
		self.y = rndi(0, H) - H2
		self.m = rndf(0.5, 1)
		self.l = rndi(ShootingStar.min_len, ShootingStar.max_len)
		self.i = self.l
		ShootingStar.instances.append(self)

	def update(self):
		for j in range(3):
			Particles(self.x+self.i, self.y-self.m*self.i, t=rndi(0,15)+1.5*(self.l-self.i))
			self.i -= 1

	def update_all():
		ShootingStar.emittimmer()
		ShootingStar.t = ShootingStar.t + 1
		for p in ShootingStar.instances:
			p.update()
			if p.i < 0:
				ShootingStar.instances.remove(p)

	def emittimmer():
		if ShootingStar.next_t <= ShootingStar.t:
			ShootingStar()
			ShootingStar.next_t = ShootingStar.next_t + rndi(30,100)

class Transition:

	instances = []
	target = -1
	status = 0
	t = 34

	def __init__(self, u, v, col=2):
		self.u = u 
		self.v = v 
		self.x = self.u * W - W2 
		self.y = self.v * W - W2 -5
		self.col = col 
		self.fac = 0
		self.r = 9
		Transition.instances.append(self)
		
	def draw(self):
		if self.fac*self.r < 1:
			return
		circ(self.x, self.y, self.fac*self.r, self.col)

	def update(self):
		if Transition.target == 1 and Transition.status == 1:
			return
		if Transition.target == -1 and Transition.status == 0:
			return
		offset = 10*(self.u + self.v) - 20
		offset *= Transition.target
		offset = offset + Transition.target*Transition.t
		target = clamp(offset) 
		self.fac = lerp(0.2, self.fac, target) 
		self.fac = clamp(self.fac)

	def update_all():
		Transition.t += 1
		if Transition.target == -1:
			Transition.status = 1-clamp(Transition.t / 34)
		elif Transition.target == 1:
			Transition.status = clamp(Transition.t / 34)
		# if btnp(KEY_J):
		# 	Transition.wipe()
		# elif btnp(KEY_K):
		# 	Transition.unwipe()
		for i in Transition.instances:
			i.update()

	def draw_all():
		for i in Transition.instances:
			i.draw()

	def load():
		dx = 0.08
		dy = 0.08
		randomness = 0
		N = ceil(1/dx)+1
		M = ceil(1/dx)+1
		for i in range(N):
			for j in range(M):
				u = i*dx + randomness*rndf(-1,1)
				v = j*dy + randomness*rndf(-1,1)
				col = 2 if u+v-rndf(-0.2,0.8) > 1 else 3
				p = Transition(u, v, col)
				Transition.instances.append(p)

	def change_col():
		for p in Transition.instances:
			p.col = 2 if p.u+p.v-rndf(-0.2,0.8) > 1 else 3

	def wipe():
		Transition.change_col()
		Transition.t = 0
		Transition.target = 1
		play(3, 53)

	def unwipe():
		Transition.target = -1 
		Transition.t = 0

def textbox(x, y, w, h):
	# outline
	line(x+1, y, x+w-2, y, 0)
	line(x+1, y+h-1, x+w-2, y+h-1, 0)
	line(x, y+1, x, y+h-2, 0)
	line(x+w-1, y+1, x+w-1, y+h-2, 0)
	# fill
	rect(x+1, y+1, w-2, h-2, 2)
	rect(x+1, y+1, w-2, 5, 3)
	# border 
	line(x+2, y+h-2, x+w-2, y+h-2, 3)
	line(x+1, y+1, x+1, y+h-2, 3)
	line(x+w-2, y+1, x+w-2, y+h-2, 3)
	
	# corner
	blt(x, y, 0, 48, 120, 16, 16, 1)
	blt(x+w-16, y, 0, 64, 120, 16, 16, 1)
	blt(x, y+h-16, 0, 48, 136, 16, 16, 1)
	blt(x+w-16, y+h-16, 0, 64, 136, 16, 16, 1)

def mytext(x, y, string):
	text(x, y+1, string, 1)
	text(x+1, y, string, 3)
	text(x, y, string, 2)
	
class GameScene:

	mode = 0
	level = 1
	final = 3

	def load():
		global graph
		global cursor
		global inventory
		global menu
		n = 6 
		if GameScene.mode == 0:
			# endless
			n = rndi(6,9)
		elif GameScene.level == 1:
			n = 4 
		elif GameScene.level == 2:
			n = 6
		elif GameScene.level == 3:
			n = 9
		# elif GameScene.level == 4:
		# 	n = 9 
		# elif GameScene.level == 5:
		# 	n = 9
		graph = Graph(n)
		menu = Menu()
		Decor._load()
		inventory = Invetory(graph.shapes)
		cursor = Cursor()

	def update():
		graph.update()
		cursor.update()
		menu.update()
		inventory.update()
		Decor.update_all()
		if not graph.is_complete: 
			return
		if not (btnp(KEY_Z) or btnp(GAMEPAD1_BUTTON_A)):
			return 
		if scenemanager.is_busy:
			return
		# endless
		if GameScene.mode == 0:
			scenemanager.next(GameScene)
			GameScene.level += 1
			return
		# standard
		if GameScene.mode == 1:
			GameScene.level += 1
			if GameScene.level > GameScene.final:
				scenemanager.next(EndScene)
			else:
				scenemanager.next(GameScene)

	def draw():
		cls(0)
		Decor.draw_all()
		graph.draw()
		inventory.draw()
		cursor.draw()
		menu.draw()
		if graph.is_complete and global_t//30%2:
			mytext(-W2+1, -H2+8, "Press Z to proceed")
		mytext(-W2+1, -H2+1, "Level "+str(GameScene.level))

class TitleScreen:

	current = 0

	def load():
		camera(-W2, -H2)
		playm(0, 0, True)
		global graph
		graph = Graph(6)
		Decor._load(is_title=True)

	def update():
		Decor.update_all()
		# if any([btnp(k) for k in TitleScreen.KEYS]):
		# 	scenemanager.next(GameScene)
		if btnp(KEY_Z) or btnp(KEY_RETURN) or btnp(GAMEPAD1_BUTTON_A):
			if TitleScreen.current == 0:
				GameScene.mode = 1
			elif TitleScreen.current == 1:
				GameScene.mode = 0
			GameScene.level = 1
			scenemanager.next(GameScene)
		elif btnp(KEY_UP) or btnp(KEY_LEFT) or btnp(GAMEPAD1_BUTTON_DPAD_UP) or btnp(GAMEPAD1_BUTTON_DPAD_LEFT):
			TitleScreen.current = (TitleScreen.current - 1) % 2
			play(3, 50)
		elif btnp(KEY_DOWN) or btnp(KEY_RIGHT) or btnp(GAMEPAD1_BUTTON_DPAD_DOWN) or btnp(GAMEPAD1_BUTTON_DPAD_RIGHT):
			TitleScreen.current = (TitleScreen.current + 1) % 2
			play(3, 50)

	def draw():
		cls(0)
		y = -45 + global_t//29%2
		blt(-70, y, 0, 0, 202, 115, 54, 5)
		blt(-70, y+35, 0, 115, 202, 141, 54, 5)
		Decor.draw_all()
		x = 20
		y = 30 + global_t//37%2
		blt(x, y, 0, 0, 120, 48, 32, 1)
		text(x+11, y+10, "Standard", 0)
		text(x+11, y+18, "Endless", 0)
		blt(x+6, y+9+8*TitleScreen.current, 0, 88+8*(global_t//15%2), 0, 8, 8, 0)
		
class EndScene:

	def load():
		camera(-W2, -H2+5)
		playm(1)
		global graph
		graph = Graph(6)
		Decor._load(is_title=True)

	def update():
		if scenemanager.is_busy:
			return
		if any([btnp(k) for k in KEYS]):
			scenemanager.next(TitleScreen)

	def draw():
		cls(0)
		Decor.draw_all()
		EndScene.anim(global_t//2%32)
		x = -75 
		y = 30 + global_t//30%2
		textbox(x, y, 64, 41)
		text(x+8, y+11, "pke1029", 3)
		text(x+8, y+10, "pke1029", 0)
		text(x+13, y+18, "Concept, \nArt and \nProgramming", 0)
		# text(x+13, y+25, "Art and", 0)
		# text(x+13, y+32, "Programming", 0)

		x = -15
		y = 39 + global_t//40%2
		textbox(x, y, 68, 35)
		text(x+8, y+11, "Andrea Baroni", 3)
		text(x+8, y+10, "Andrea Baroni", 0)
		text(x+13, y+18, "Music and \nSound Design", 0)

		k = global_t//32%2
		# if global_t//64%2:
		mytext(8, -38-k, "Thank you ")
		mytext(8, -30-k, "for playing")
		# else:
		# 	mytext(8, -38-k, "Press any key")
		# 	mytext(8, -30-k, "to restart")
		# text(2-W2, H2-12, "Music & Sound Design by Andrea Baroni", 4)


	def anim(i):
		x = i%4
		y = i//4
		blt(-32, -32, 1+y//4%2, x*64, y%4*64, 64, 64, 5)

class SceneManager:

	def __init__(self):
		self.current = TitleScreen
		# self.current = EndScene
		self.queue = None
		self.game_mode = 0
		self.is_busy = False
		self.load()

	def load(self):
		self.current.load()

	def update(self):
		self.switch_schedule()
		self.current.update()

	def draw(self):
		self.current.draw()

	def next(self, scene):
		if self.is_busy:
			return 
		Transition.wipe() 
		self.is_busy = True
		self.queue = scene 

	def switch_schedule(self):
		if not self.is_busy:
			return 
		if Transition.status == 1:
			Transition.unwipe()
			self.is_busy = False
			self.current = self.queue
			self.current.load()
			# play(3, 56)

def reload_game():
	global graph
	global cursor
	global inventory
	global menu
	graph = Graph(rndi(7,9))
	Decor._load()
	inventory = Invetory(graph.shapes)
	cursor = Cursor()
	menu = Menu()

# W, H = 320, 100
W, H = 160, 144
W2, H2 = W/2, H/2
pi = 3.1415
global_t = 0

# initialize
init(W, H)
camera(-W2, -H2)
load("game.pyxres", True)
load("music.pyxres", False, False, True, True)
image(0).load(0, 202, "title.png")
KEYS = [KEY_Z, KEY_X, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_RETURN, GAMEPAD1_BUTTON_DPAD_UP, GAMEPAD1_BUTTON_DPAD_DOWN, GAMEPAD1_BUTTON_DPAD_LEFT, GAMEPAD1_BUTTON_DPAD_RIGHT, GAMEPAD1_BUTTON_A, GAMEPAD1_BUTTON_B]

Transition.load()
scenemanager = SceneManager()

def update():
	global global_t
	global_t += 1
	# if btnp(KEY_R):
	# 	reload_game()
	# graph.update()
	# cursor.update()
	# menu.update()
	# inventory.update()
	# Decor.update_all()
	Transition.update_all()
	check1 = graph.check()
	scenemanager.update()
	check2 = graph.check()
	if check1 == False and check2 == True:
		play(3, 57)


def draw():
	
	# Decor.draw_all()
	# graph.draw()
	# inventory.draw()
	# cursor.draw()
	# menu.draw()
	# Transition.draw_all()
	# text(0, 0, "nodes "+str(len(graph.nodes)), 4)
	# text(0, 6, "edges "+str(len(graph.edges)), 4)
	# text(0, 12, "transition "+str(Transition.status), 4)
	scenemanager.draw()
	Transition.draw_all()
	# text(0-W2,0-H2,"mode "+str(GameScene.mode),4)

run(update, draw)