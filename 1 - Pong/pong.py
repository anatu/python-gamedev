import tkinter as tk

# Master Game class which configures the canvas and frame widgets
# and packs them + declares useful constants
class Game(tk.Frame):
	def __init__(self, master):
		super(Game, self).__init__(master)
		self.lives = 3
		self.canv_w = 610
		self.canv_h = 400
		self.canvas = tk.Canvas(self, bg='#aaaaff',
								width=self.canv_w, height=self.canv_h)
		self.canvas.pack()
		self.pack()

# Game Object class that we'll use to facilitate
# drawing objects on the canvas with simple helper functions.
# More complex objects will inherit this
class GameObject(object):
	def __init__(self, canvas, item):
		self.canvas = canvas
		self.item = item

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

if __name__ == '__main__':
	root = tk.Tk()
	root.title('Hello, Pong!')
