import cocos
import cocos.collision_model as cm
import cocos.euclid as eu
from pyglet.window import key
from collections import defaultdict

'''
Cocos test game where we control a ball that has to pick up
other balls that are on the map
'''

# Generic class for replicating our ball sprites
class Actor(cocos.sprite.Sprite):
	def __init__(self, x, y, color):
		super(Actor, self).__init__('ball.png', color = color)
		self.position = pos = eu.Vector2(x,y)
		self.cshape = cm.CircleShape(pos, self.width/2)

# The "Main" layer of the game, containing the interactible elements
# such as the player 
class MainLayer(cocos.layer.Layer):
	# Define this class as an event-handler class
	# cocos uses Pyglet lib to perform event handling using
	# reserved function names as event listeners
	is_event_handler = True

	def __init__(self):
		# Call the constructor from the parent class (cocos.layer.Layer)
		super(MainLayer, self).__init__()
		# Define the player sprite (blue) using Actor class
		self.player = Actor(320, 240, (0,0,255))
		self.add(self.player)
		# Define all of the red sprites our blue player will collect
		for pos in [(100,100), (540,380), (540,100), (100,380)]:
			self.add(Actor(pos[0], pos[1], (255,0,0)))

		# Define the cell dimensions relative to player sprite width
		# and use this cell to construct the collision grid
		cell = self.player.width*1.25
		self.collman = cm.CollisionManagerGrid(0, 640, 0, 480,
												cell, cell)
		# Define speed constant
		self.speed = 100.0
		# Define pressed dict to store pressed keys
		self.pressed = defaultdict(int)
		# Schedule update method
		self.schedule(self.update)

	# Define pressed state as 1 for any given key
	def on_key_press(self, k, m):
		self.pressed[k] = 1

	# Release state as 0 for any given key
	def on_key_release(self, k, m):
		self.pressed[k] = 0

	# Main update method
	def update(self, dt):
		# Clear the collision manager
		self.collman.clear()
		# Add actors to the set of known entities
		for _, node in self.children:
			self.collman.add(node)
		# Remove a ball if the player sprite collides with it
		for other in self.collman.iter_colliding(self.player):
			self.remove(other)

		# Calculate movement outcome based on which keys are pressed
		# Subtract opposing directional inputs so that 
		# 1) Pressing both simultaneously doesn't result in any movement
		# 2) The sign of x/y indicates direction
		x = self.pressed[key.RIGHT] - self.pressed[key.LEFT]
		y = self.pressed[key.UP] - self.pressed[key.DOWN]

		# If the input results in a movement, calculate it
		# using kinematics (w/ some fixed speed, dt) and update position
		if x != 0 or y != 0:
			pos = self.player.position
			new_x = pos[0] + self.speed*x*dt
			new_y = pos[1] + self.speed*y*dt
			# Update the sprite's position 
			self.player.position = (new_x, new_y)
			# Update the cshape (collision box) to overlap with the
			# sprite's new position 
			self.player.cshape.center = self.player.position

if __name__ == '__main__':
	# Initialize the director, which is a shared object that 
	# starts the main window / controls the scene
	cocos.director.director.init(caption='Hello, Cocos!')
	# Instantiate the main layer, and place it into a Scene object
	layer = MainLayer()
	scene = cocos.scene.Scene(layer)
	# Run the scene
	cocos.director.director.run(scene)
