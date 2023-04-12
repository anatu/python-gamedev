'''
Space Invaders

Base Classes
a) Actor (base actor class)
b) GameLayer (custom layer for game logic)

Actors
1) PlayerCannon: Character controlled by the player. <space> to shoot, and 
<left>, <right> to move the cannon horizontally. No vertical movement.
2) Alien: Each of the descending enemies w/ different looks/scores
depending on type
3) AlienColumn: A column of 5 aliens
4) AlienGroup: An entire group of enemies, which moves uniformly
both horizontally as well as down towards the player
5) Shoot: The projectile that the enemies launch at the player
6) PlayerShoot: The projectile that the player launches at the enemies
which we will implement by extending Shoot
'''

import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu
import cocos.layer

from collections import defaultdict
from pyglet.window import key


### BASE SUBCLASSES ###
#########################################################

# Superclass that all our actors will extend
class Actor(cocos.sprite.Sprite):
	def __init__(self, image, x ,y):
		# Call Sprite constructor on the image path
		super(Actor, self).__init__(image)
		# Convert x,y coords into Euclidean vector
		self.position = eu.Vector2(x,y)
		# Initialize rectangular (AARectShape) hitbox
		# NOTE: by defining collision like this we're
		# forcing all our actors to have rectangular hitboxes
		self.cshape = cm.AARectShape(self.position, 
									self.width*0.5,
									self.height*0.5)

	# Moves an actor and its hitbox by a fixed offset amount
	# in a single euclidean direction
	def move(self, offset):
		self.position += offset
		self.cshape.center += offset

	def update(self, elapsed):
		pass

	def collide(self, other):
		pass

class GameLayer(cocos.layer.Layer):
	is_event_handler = True

	def __init__(self):
		# Construct layer using superclass
		super(GameLayer, self).__init__()
		# Get window dimensions 
		w, h = cocos.director.director.get_window_size()
		self.width = w
		self.height = h
		# Initialize lives/score
		self.lives = 3
		self.score = 0
		# Call helper methods to set the starting game state
		self.update_score()
		self.create_player()
		self.create_alien_group(100, 300)
		# Initialize the collision grid
		cell = 1.25*50
		self.collman = cm.CollisionManagerGrid(0, w, 0, h, cell, cell)
		self.schedule(self.update)

	# Load key-press/release state updates into PlayerCannon utility dict
	def on_key_press(self, k, _):
		PlayerCannon.KEYS_PRESSED[k] = 1

	def on_key_release(self, k, _):
		PlayerCannon.KEYS_PRESSED[k] = 0


### ACTOR SUBCLASSES ###
#########################################################

# Player character actor
class PlayerCannon(Actor):
	# Dict which stores press states of keys
	KEYS_PRESSED = defaultdict(int)

	def __init__(self, x, y):
		# Build sprite with Actor class constructor
		super(PlayerCannon, self).__init__('img/cannon.png', x, y)
		# Speed vector has no y-component (only horizontal mvmt)
		self.speed = eu.Vector2(200, 0)

	def update(self, elapsed):
		pressed = PlayerCannon.KEYS_PRESSED
		# Calculate net movement input
		movement = pressed[key.RIGHT] - pressed[key.LEFT]
		# Perform movement if it stays within the collision manager grid
		w = self.width * 0.5
		if movement != 0 and w <= self.x <= self.parent.width - w:
			self.move(self.speed*movement*elapsed)

	def collide(self, other):
		other.kill()
		self.kill()


