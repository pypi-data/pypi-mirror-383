from typing import Optional
"""
Convert a PIL Image to ASCII art with color codes.
This function converts an image to colored ASCII art representation using terminal color codes.
It supports two modes: doubled mode (default) where each character represents two vertical pixels
using half-block characters, and single mode where each character represents one pixel.
Args:
	img (PIL.Image.Image): The input PIL Image to convert to ASCII art
	character (str, optional): The character to use for ASCII art. Defaults to "▀" (upper half block)
	size (Optional[int], optional): If provided, resizes the image to size x size pixels before conversion. Defaults to None
	doubled (bool, optional): If True, uses doubled mode where each character represents two vertical pixels.
							 If False, uses single mode where each character represents one pixel. Defaults to True
Returns:
	str: ASCII art representation of the image with terminal color codes embedded
Note:
	- In doubled mode, the character represents two pixels vertically with foreground color as top pixel
	  and background color as bottom pixel
	- In single mode, each character represents one pixel and uses two characters horizontally
	  to compensate for terminal character aspect ratio
	- Color codes are in the format [#rrggbb] for single colors or [#rrggbb on #rrggbb] for doubled colors
"""
import PIL.Image

def _convert_color_single(r: int, g: int, b: int) -> str:
		"""Convert RGB to hex color code"""
		return f"[#{r:02x}{g:02x}{b:02x}]"

def _convert_color_double(r1: int, g1: int, b1: int, r2: int, g2: int, b2: int) -> str:
		"""Convert RGB to hex color code"""
		return f"[#{r1:02x}{g1:02x}{b1:02x} on #{r2:02x}{g2:02x}{b2:02x}]"

def _img_to_art(img: PIL.Image.Image, character: str, doubled=True) -> str:
		"""Convert image to ASCII art with color codes"""
		width, height = img.size
		ascii_lines = []
		
		if not doubled:
			# Single pixel per character
			for y in range(height):
				line = ""
				for x in range(width):
					r, g, b = img.getpixel((x, y))[:3] # type: ignore
					color_code = _convert_color_single(r, g, b)
					# terminal pixels are taller than wide, so use two characters per pixel
					# to make it look more square
					line += f"{color_code}{character}{character}"
				ascii_lines.append(line)
			return "\n".join(ascii_lines)
		else:
			# two lines at a time. so each character represents two pixels vertically
			# using '▀' character (upper half block)
			# foreground color is top pixel, background color is bottom pixel
			# if odd height, last row uses same color for both fg and bg
			for y in range(0, height, 2):  # Step by 2 to go two lines at a time
				line = ""
				for x in range(width):
					# First row (top half of character)
					r1, g1, b1 = img.getpixel((x, y))[:3] # type: ignore
					# Second row (bottom half of character)
					if y + 1 < height:
						r2, g2, b2 = img.getpixel((x, y + 1))[:3] # type: ignore
					else:
						r2, g2, b2 = r1, g1, b1  # Use same color if odd height
					color_code = _convert_color_double(r1, g1, b1, r2, g2, b2)
					line += f"{color_code}{character}"
				ascii_lines.append(line)
			
			return "\n".join(ascii_lines)


def to_ascii(img: PIL.Image.Image, character: str = "▀", size: Optional[tuple[int,int]] = None, doubled: bool = True) -> str:
	if size is not None:
		img = img.resize((size[0], size[1]))
	if not doubled and character == "▀":
		character = "█"  # Full block for single pixel mode
	ascii = _img_to_art(img, character=character, doubled=doubled)
	return ascii