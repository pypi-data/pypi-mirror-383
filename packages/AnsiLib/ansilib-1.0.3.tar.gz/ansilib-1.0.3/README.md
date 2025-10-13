# AnsiLib

AnsiLib is a Python module for handling text style and color shortcuts from ANSI escape codes.

**Author:** Bora Boyacıoğlu
* E-Mail: boyacioglu20@itu.edu.tr
* GitHub: [@boraboyacioglu-itu](https://github.com/boraboyacioglu-itu)

## Installation

To install AnsiLib, use pip:

```sh
pip install ansilib
```

If you are running Python 3.7 or below, you also need to install `typing_extensions`, which comes as a dependency. 

## Usage

```python
import AnsiLib as al
```

You can use the quick styles and colors to simply format your text.

```python
print(al.s("This text is bold."))
print(al.r("This text is red."))
print(al.u(al.b("This text is underlined and blue.")))
```

Also you can reach all of the colors using `al.c` class.

```python
print(al.c.t.r("This text is red."))
print(al.c.b.c("This text has cyan background."))
print(al.c.t.g_("This text is bright green."))
```

To define styles, use `al.style()` function.

```python
sty1 = al.style('bold', 'r', 'kb1')
print(sty1("This text is bold, red and has a background color of bright black."))
```

Get the complete list of styles and colors with `al.available()`.

```python
print(al.available())
```

Create an RGB color using `al.color()` function.

```python
my_color = al.color(56, 12, 74)
sty2 = al.style('x', 'italic', my_color)
print(sty2("This text is italic, crossed and has an RGB color of (56, 12, 74)."))
```

Finally, you can use the AnsiLib's `prints()` function to print a styled text.

```python
al.prints("This text is bold, red and has a background color of bright black.", s=['bold', 'r', 'kb1'])
```

## Contributions

I welcome contributions and suggestions to the AnsiLib Python library! Contact me about the details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.