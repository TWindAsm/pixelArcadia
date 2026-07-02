import pygame

#This file is from https://github.com/russs123

class Button():
	"""Represents a clickable button UI element.
	
	This class manages a button's appearance, position, and rendering on screen.
	The button image is scaled based on the provided scale factor and can be
	drawn on any pygame surface.
	
	Attributes:
		image (pygame.Surface): The scaled button image.
		rect (pygame.Rect): The rectangle defining the button's position and bounds.
		clicked (bool): Flag to track if the button has been clicked.
	"""
	
	def __init__(self, x, y, image, scale):
		"""Initialize a button at the specified position.
		
		Args:
			x (int): The x-coordinate of the button's top-left corner.
			y (int): The y-coordinate of the button's top-left corner.
			image (pygame.Surface): The original button image to display.
			scale (float): The scale factor to resize the image (1.0 = original size).
		"""
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		"""Draw the button on the specified pygame surface.
		
		Args:
			surface (pygame.Surface): The surface to draw the button on.
		"""
		surface.blit(self.image, (self.rect.x, self.rect.y))