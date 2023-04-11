import tkinter as tk

# Master Game class which configures the canvas and frame widgets
# and packs them + declares useful constants
class Game(tk.Frame):
	def __init__(self, master):
		# Create the canvas widget
		super(Game, self).__init__(master)
		self.lives = 3
		self.canv_w = 610
		self.canv_h = 400
		self.canvas = tk.Canvas(self, bg='#aaaaff',
								width=self.canv_w, height=self.canv_h)
		self.canvas.pack()
		self.pack()

		# items dict contains all the canvas items that can collide
		# with the ball. 
		self.items = {}
		self.ball = None
		self.paddle = Paddle(self.canvas, self.canv_w/2, 326)
		self.items[self.paddle.item] = self.paddle
		for x in range(5, self.canv_w-5, 75):
			self.add_brick(x+37.5, 50, 2)
			self.add_brick(x+37.5, 70, 1)
			self.add_brick(x+37.5, 90, 1)

		self.hud = None
		self.setup_game()
		# Sets the focus on the canvas widget so that 
		# our defined control scheme is bound/applies to that widget
		self.canvas.focus_set()
		# Define controls. One arg is the input key, 
		# the other is the function triggered when the key is pressed
		# which are defined using inline lambda functions
		self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
		self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

	def setup_game(self):
		self.add_ball()
		self.update_lives_text()
		self.text = self.draw_text(300, 200, 'Press Space to Start')
		self.canvas.bind('<space>', lambda _: self.start_game())

	# Adds ball to the canvas on the paddle
	# does not add to item dict since that's only
	# for objects that the ball can collide with
	def add_ball(self):
		# Check if a ball already exists and delete it
		if self.ball is not None:
			self.ball.delete()
		paddle_coords = self.paddle.get_position()
		# Draw the ball in the center of the paddle, (x1+x2)/2
		x = (paddle_coords[0] + paddle_coords[2]) * 0.5
		self.ball = Ball(self.canvas, x, 310)
		# "Fix" the ball to the paddle
		# so that they move together
		self.paddle.set_ball(self.ball)

	# Adds a brick object to canvas
	# and to item dict
	def add_brick(self, x, y, hits):
		brick = Brick(self.canvas, x, y, hits)
		self.items[brick.item] = brick

	def draw_text(self, x, y, text, size='40'):
		font = ('Helvetica', size)
		return self.canvas.create_text(x, y, text=text, font=font)

	# Updates the utility text with # lives remaining
	def update_lives_text(self):
		text = 'Lives: %s' % (self.lives)
		# Make a new text object as HUD if none exists,
		# otherwise update the existing one
		if self.hud is None:
			self.hud = self.draw_text(50, 20, text, 15)
		else:
			self.canvas.itemconfig(self.hud, text=text)

	def start_game(self):
		# Unbind spacebar on start so the player can't start
		# the game twice
		self.canvas.unbind('<space>')
		# Delete splash text 
		self.canvas.delete(self.text)
		# Unbind the ball from the paddle, setting it into motion
		self.paddle.ball = None
		self.game_loop()

	def game_loop(self):
		# Check collisions
		self.check_collisions()
		# Get all brick objects (using the 'brick' tag defined
		# in the constructor of the Brick class)
		num_bricks = len(self.canvas.find_withtag('brick'))
		# Check win condition (# bricks = 0)
		if num_bricks == 0:
			self.ball.speed = None
			self.draw_text(300, 200, 'You win!')
		# Life loss condition (ball goes past lower edge of canvas)
		elif self.ball.get_position()[3] >= self.canv_h:
			self.ball.speed = None
			self.lives -= 1
			# If lives = 0, game loss
			if self.lives < 0:
				self.draw_text(300, 200, 'Game Over!')
			# Otherwise, reset the game for the next life
			else:
				self.after(1000, self.setup_game)
		else:
			self.ball.update()
			self.after(50, self.game_loop)

	# Checks and calculates collisions of the ball at each
	# update step of the game loop
	def check_collisions(self):
		# Get ball coords and find all the objects that overlap with it
		ball_coords = self.ball.get_position()
		items = self.canvas.find_overlapping(*ball_coords)
		# Filter out the list of objects that can't collide w/ the ball
		# by cross-referencing the "items" dict we made in the constructor
		objects = [self.items[x] for x in items if x in self.items]
		# Calculate collisions for all collide-able objects
		self.ball.collide(objects)



# Game Object class that we'll use to facilitate
# drawing objects on the canvas with simple helper functions.
# The in-game objects will extend this class
class GameObject(object):
	def __init__(self, canvas, item):
		self.canvas = canvas
		self.item = item

	# Returns coordinates of the game object.
	# Usually in the form (x1, y1, x2, y2)
	def get_position(self):
		return self.canvas.coords(self.item)

	def move(self, x, y):
		self.canvas.move(self.item, x, y)

	def delete(self):
		self.canvas.delete(self.item)

# Ball that the player hits, extending GameObject
class Ball(GameObject):
	# x/y coords are for the center of the shape
	def __init__(self,canvas,x,y):
		# Define the properties of the ball + construct canvas item
		self.radius = 10
		# Initial direction. For this game we assume the ball can only have  [+-1, +-1] 
		# directional vectors
		self.direction = [1, -1]
		self.speed = 10
		# Draw the oval with the x/y values specified at instantiation 
		item = canvas.create_oval(x-self.radius, y-self.radius,
								x+self.radius, y+self.radius,
								fill='white')
		# Use the superclass (GameObject) constructor to assign canvas/item vars
		super(Ball, self).__init__(canvas, item)

	# Update function for ball movement
	# also includes collision logic for the edges of the canvas
	def update(self):
		coords = self.get_position()
		width = self.canvas.winfo_width()
		# Collision check for x-coords
		# invert x-component of "velocity" if at a wall
		if (coords[0] <= 0) or (coords[2] >= width):
			self.direction[0] *= -1
		# Same for y-component hitting top edge of screen
		if coords[1] <= 0:
			self.direction[1] *= -1
		# Calculate dx, dy based on speed
		x = self.direction[0] * self.speed
		y = self.direction[1] * self.speed
		# Perform movement
		self.move(x,y)

	# General function for calculating collision logic
	# with in-game objects (i.e. paddle or bricks)
	def collide(self, game_objects):
		coords = self.get_position()
		# Find x-coordinate of the center of the ball
		x = (coords[0] + coords[2])*0.5
		# If the ball collides w/ 2+ bricks at once, 
		# only invert y-direction once 
		if len(game_objects) > 1:
			self.direction[1] *= -1
		# If only 1 brick being hit, calculate collision logic
		# based on where the brick is being hit by the ball
		elif len(game_objects) == 1:
			game_object = game_objects[0]
			coords = game_object.get_position()
			# If the ball hits the side of a brick (i.e. ball's x-centroid
			# is past the left or right edge of the brick),
			# set the ball to left/right x-velocity depending
			# on which edge it's past  
			if x > coords[2]:
				self.direction[0] = 1
			elif x < coords[0]:
				self.direction[0] = -1
			# If the ball is "over" the brick (i.e. it's x-centroid
			# is between the left/right edges of the brick)
			# then just invert y-velocity, x-vel is unchanged
			else:
				self.direction[1] *= -1

			# If the object being collided w/ is a Brick,
			# call that Brick object's method to register the hit
			for game_object in game_objects:
				if isinstance(game_object, Brick):
					game_object.hit()

# Paddle that the player moves around to hit the ball
class Paddle(GameObject):
	# x/y coords are for the center of the shape
	def __init__(self, canvas, x, y):
		self.width = 80
		self.height = 10
		self.ball = None
		item = canvas.create_rectangle(x - self.width / 2,
									y - self.height / 2,
									x + self.width / 2,
									y + self.height / 2,
									fill='blue')
		super(Paddle, self).__init__(canvas, item)

	# Sets the ball onto the paddle (starting position)
	def set_ball(self, ball):
		self.ball = ball

	# Move the paddle by a defined offset
	def move(self, offset):
		# Get starting position
		coords = self.get_position()
		# Calculate width of canvas
		width = self.canvas.winfo_width()
		# Determine movement outcome based on position 
		# relative to the canvas bounds.
		if coords[0] + offset >= 0 and \
			coords[2] + offset <= width:
			# Use the super-method to move by offset (only x-component)
			super(Paddle, self).move(offset, 0)
			# Move the ball with the paddle if it's still attached
			if self.ball is not None:
				self.ball.move(offset, 0)

# Definition for the bricks that are broken when the ball hits
class Brick(GameObject):
	# Define key-value pairs for the colors
	# The key is the # of hits the brick has taken, 
	# and the value is the hex color code
	COLORS = {1: '#999999', 2: '#555555', 3: '#222222'}

	def __init__(self, canvas, x, y, hits):
		# Dimensions
		self.width = 75
		self.height = 20
		# Set color based on # hits remaining
		# Total # of hits for all bricks will be the same,
		# given by the constant "hits"
		self.hits = hits
		color = Brick.COLORS[hits]
		# Create in canvas
		item = canvas.create_rectangle(x - self.width / 2,
									y - self.height / 2,
									x + self.width / 2,
									y + self.height / 2,
									fill=color, tags='brick')
		super(Brick, self).__init__(canvas, item)		

	# Call whenever brick is hit
	def hit(self):
		# Decrement # hits remaining
		self.hits -= 1
		# Delete if no hits remain, otherwise change color
		if self.hits == 0:
			self.delete()
		else:
				self.canvas.itemconfig(self.item, 
									fill=Brick.COLORS[self.hits])


if __name__ == '__main__':
	root = tk.Tk()
	root.title('Hello, Pong!')
	game = Game(root)
	game.mainloop()
