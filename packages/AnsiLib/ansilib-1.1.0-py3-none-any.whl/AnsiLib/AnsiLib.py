from collections.abc import Iterable
import re
import sys
from typing import Any, Callable, Dict, List, Optional, Union

# Import literal type for different versions of Python.
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from .chars import CHARS

# Colors class.
from .color import color as c

# Styling function.
from .utils import style

# Quick styles.
s  : Callable[[str], str] = style('s')
d  : Callable[[str], str] = style('d')
i  : Callable[[str], str] = style('i')
u  : Callable[[str], str] = style('u')
k  : Callable[[str], str] = style('k')
h  : Callable[[str], str] = style('h')
x  : Callable[[str], str] = style('x')
du : Callable[[str], str] = style('du')
rev: Callable[[str], str] = style('rev')

# Quick colors.
r  : Callable[[str], str] = style('r')
g  : Callable[[str], str] = style('g')
y  : Callable[[str], str] = style('y')
b  : Callable[[str], str] = style('b')
m  : Callable[[str], str] = style('m')
cy : Callable[[str], str] = style('c')
w  : Callable[[str], str] = style('w')

def available() -> List[str]:
    """ Returns the available styles.

    Returns:
        List[str]: The available styles.
    """

    # Get the available styles.
    ints: Dict[int, str] = {v: '' for v in set(CHARS.values())}
    for sty in CHARS.keys():
        i: int = CHARS[sty]
        if i in ints.keys() and not ints[i]:
            ints[i] = sty
    
    return list(ints.values())

def color(r: int, g: int, b: int, type: Literal['fg', 'bg'] = 'fg') -> str:
    """ Returns the ANSI escape sequence for the given RGB color.
    
    Args:
        r (int): The red value.
        g (int): The green value.
        b (int): The blue value.
        type (str): The type of color. (defaults to 'fg')

    Returns:
        str: The ANSI escape sequence.
    """

    # Check if the type is valid.
    if type not in ['fg', 'bg']:
        raise ValueError("Type must be 'fg' (foreground) or 'bg' (background).")

    # Check if the RGB values are all integers.
    if not all(isinstance(v, int) for v in [r, g, b]):
        raise TypeError("RGB values must be integers.")
    
    # Check if the RGB values are in the range 0-255.
    if not all(0 <= v <= 255 for v in [r, g, b]):
        raise ValueError("RGB values must be in the range 0-255.")

    # Set the type.
    type_: Literal['38', '48'] = '38' if type == 'fg' else '48'
    
    # Generate the ANSI escape sequence.
    code: str = f'CODE{type_};2;{r};{g};{b}'
    
    return code

# Regex patterns for inline styles.
# $[r,b]text : header only at the very start
_PATTERN_LONG  = re.compile(r'^\$\[([A-Za-z0-9]+(?:\s*,\s*[A-Za-z0-9]+)*)\](.*)\Z', re.S)
# $rtext     : single 1-char style at the very start
_PATTERN_SHORT = re.compile(r'^\$([A-Za-z0-9])(.*)\Z', re.S)

def prints(
    *values: object,
    s: Optional[Union[str, List[str], Callable[[str], str]]] = None,
    **kwargs: Any
) -> None:
    """ Print values with inline styles.
    Inline (per value): "$[a,b]text"  or  "$atext"  (single char), use "$$" to escape styling.
    Fallback (overall): s="a" | s=["a","b"] | s=callable

    Args:
        *values (object): The values to print. Each value can contain inline style tags in the format "$[s1,s2,...]text".
        s (Optional[Union[str, List[str], Callable[[str], str]]]): The style to apply to the text. (defaults to None)
        **kwargs (Any): The keyword arguments to pass to the print function.
    """

    # Set the style to empty function.
    style_: Callable[[str], str] = style()

    if not s:
        # No style was given.
        pass
    elif isinstance(s, str):
        # The style is a single string.
        style_ = style(s)
    elif isinstance(s, Iterable):
        # The style is an array.
        style_ = style(*s)
    elif callable(s):
        # The style is a function.
        style_ = s
    else:
        # Invalid style.
        raise TypeError('Style must be an array or a function.')

    # Style each value and print them.
    out: List[str] = []
    for v in values:
        text = str(v)
        
        # Safe way to use $ at the start of the text, by using $$.
        if text.startswith('$$'):
            # Don't catch any pattern.
            out.append(text[1:])
            continue

        # Match the style tag syntax.
        m_long : Optional[re.Match] = _PATTERN_LONG.match(text)
        m_short: Optional[re.Match] = _PATTERN_SHORT.match(text)

        tags: List[str] = []
        body: str = text

        if m_short and not m_long:
            # Short syntax matched.
            tags = [m_short.group(1).strip()]
            body = m_short.group(2)
        if m_long and not m_short:
            # Long syntax matched.
            tags = [t.strip() for t in m_long.group(1).split(',')]
            body  = m_long.group(2)

        # Apply the style tags.
        for tag in tags:
            if tag in CHARS.keys():
                body = style(tag)(body)
        out.append(body)

    # Apply the overall style.
    out = [style_(o) for o in out]

    print(*out, **kwargs)