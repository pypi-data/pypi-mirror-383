# Textual ASCII image

A small, single file, package to convert a PIL image into a Rich / Textual compatible ascii image.

### Why not another ascii library like ascii-magic?

Textual / rich don't use ANSI colours or codes. instead using `[]` to define colours.

`[red]hello[/red]` -> <code style="color: red">hello</code>

## Installation

```bash
pip install textual-ascii-image
```

## Requirements

- Pillow - an image library

## Usage

```python
	from ascii_image import to_ascii
	from PIL import Image


	image = Image.Image("path/to/image.png")
	ascii_image = to_ascii(image)

	#Textual
	from textual.app import App
	from textual.widgets import Label
	class App(App):
		def compose(self):
			yield Label(ascii_image)

	#######################################

	#Rich
	from rich import print
	print(ascii_image)
```

![img](./example/output.png)

## Docs

```python
	def to_ascii(img: PIL.Image.Image, character: str = "▀", size: Optional[tuple[int,int]] = None, doubled: bool = True) -> str:
```

- img: A Pillow image
- size (Optional): used to resize image. (would recommend below 64x64)
- character (Optional): The ASCII character.
  - defaults to `▀` if in doubled mode, or `█` if not
- doubled (Optional): decides if should sample two rows per column, or one

when in doubled mode, each character represents a top and bottom pixel

When not in doubled mode, each pixel takes up 2 characters horizontally.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
