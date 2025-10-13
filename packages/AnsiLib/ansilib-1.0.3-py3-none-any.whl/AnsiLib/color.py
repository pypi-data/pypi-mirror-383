from typing import Callable
from .utils import style

class color:
    # Text colors.
    class t:
        k: Callable[[str], str] = style('kt0')
        r: Callable[[str], str] = style('rt0')
        g: Callable[[str], str] = style('gt0')
        y: Callable[[str], str] = style('yt0')
        b: Callable[[str], str] = style('bt0')
        m: Callable[[str], str] = style('mt0')
        c: Callable[[str], str] = style('ct0')
        w: Callable[[str], str] = style('wt0')
        d: Callable[[str], str] = style('dt0')

    # Background colors.
    class b:
        k: Callable[[str], str] = style('kb0')
        r: Callable[[str], str] = style('rb0')
        g: Callable[[str], str] = style('gb0')
        y: Callable[[str], str] = style('yb0')
        b: Callable[[str], str] = style('bb0')
        m: Callable[[str], str] = style('mb0')
        c: Callable[[str], str] = style('cb0')
        w: Callable[[str], str] = style('wb0')
        d: Callable[[str], str] = style('db0')

    # Bright text colors.
    class t_:
        k: Callable[[str], str] = style('kt1')
        r: Callable[[str], str] = style('rt1')
        g: Callable[[str], str] = style('gt1')
        y: Callable[[str], str] = style('yt1')
        b: Callable[[str], str] = style('bt1')
        m: Callable[[str], str] = style('mt1')
        c: Callable[[str], str] = style('ct1')
        w: Callable[[str], str] = style('wt1')

    # Bright background colors.
    class b_:
        k: Callable[[str], str] = style('kb1')
        r: Callable[[str], str] = style('rb1')
        g: Callable[[str], str] = style('gb1')
        y: Callable[[str], str] = style('yb1')
        b: Callable[[str], str] = style('bb1')
        m: Callable[[str], str] = style('mb1')
        c: Callable[[str], str] = style('cb1')
        w: Callable[[str], str] = style('wb1')