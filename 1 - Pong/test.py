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
	# Constructor takes a canvas and an item in it (e.g. canvas.create_rectangle()) 	

	def __init__(self, canvas, item):
		self.canvas = canvas
		self.item = item

	def get_position(self):
		return self.canvas.coords(self.item)

	def move(self, x, y):
		self.canvas.move(self.item, x, y)

	def delete(self):
		self.canvas.delete(self.item)

# Sample code for this class: 
# item = canvas.create_rectangle(10,10,100,80, fill='green')
# game_object = GameObject(canvas,item) #create new instance



if __name__ == '__main__':	

	# Tk instance
	root = tk.Tk()
	root.title('Hello, Pong!')
	# Create Game object
	game = Game(root)
	game.mainloop()
