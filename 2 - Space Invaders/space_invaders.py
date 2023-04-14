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
from pyglet.image import load, ImageGrid, Animation

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

	# Create the player cannon in the horizontal midpoint
	# of the canvas
	def create_player(self):
		self.player = PlayerCannon(self.width*0.5, 50)

	# Simple helper function to update the score by a defined amount
	def update_score(self, score=0):
		self.score += score

	# Create the group of aliens
	def create_alien_group(self, x, y):
		pass

	# Define the update callback method which is executed for each frame
	# with latency dt (milliseconds) which implicitly define framerate
	def update(self, dt):
		self.collman.clear()
		for _, node in self.children:
			self.collman.add(node)
			# knows() method checks whether an object is in the set
			# of known entities. Object should only be unknown if it 
			# leaves the area covered by the collision manager
			if not self.collman.knows(node):
				self.remove(node)

		for _, node in self.children:
			node.update(dt) 

	# Checks if there are any valid objects to calculate collisions for
	# using iter_colliding(), and then perform collision with collide() 
	def collide(self, node):
		if node is not None:
			for other in self.collman.iter_colliding(node):
				node.collide(other)
				return True
		return False



### ACTOR SUBCLASSES ###
#########################################################

# Player character actor
class PlayerCannon(Actor):
	# Dict which stores press states of keys
	KEYS_PRESSED = defaultdict(int)

	def __init__(self, x, y):
		# Build sprite with Actor superclass constructor
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

# Alien actor - this is the base class for all three Alien types.
class Alien(Actor):
	def __init__(self, img, x, y, score, column=None):
		# Build sprite w/ superclass constructor
		super(Alien, self).__init__(img, x, y)
		# Define the score that is accrued on killing the alien
		# and the column it goes into
		self.score = score
		self.column = column

	# Helper method to take an image path and build an animation
	# for the sprite
	def load_animation(image):
		seq = ImageGrid(load(image), 2, 1)
		return Animation.from_image_sequence(seq, 0.5)

	# Define the three alien types by loading the animation sprites
	# for each type, and defining the score gained by killing each
	TYPES = {
		'1': (load_animation('img/alien1.png'), 40)
		'2': (load_animation('img/alien2.png'), 20)
		'3': (load_animation('img/alien3.png'), 10)
	}

	# Actual constructor method which uses the base constructor
	# to build an alien of the type specified in the call to this method
	def from_type(x, y, alien_type, column):
		animation, score = Alien.TYPES[alien_type]
		return Alien(animation, x, y, score, column)

	# Callback method when a node is removed, 
	# which has been overriden to inform its corresponding column
	# (i.e. to make sure the AlienColumn class "knows" its member alien
	# has been removed)
	def on_exit(self):
		super(Alien, self).on_exit()
		if self.column:
			self.column.remove(self)


### MAIN FUNCTION ###
#########################################################

if __name__ == '__main__':
	cocos.director.director.init(caption = 'Cocos Invaders',
								width=800, height=650)
	game_layer = GameLayer()
	main_scene = cocos.scene.Scene(game_layer)
	cocos.director.director.run(main_scene)


