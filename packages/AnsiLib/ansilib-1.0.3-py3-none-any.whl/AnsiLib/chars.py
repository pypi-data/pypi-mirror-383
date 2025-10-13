CHARS = {
    'reset': 0, '_': 0,

    # TEXT EFFECTS
    'bold': 1, 's': 1,
    'faint': 2, 'dim': 2, 'd': 2,
    'italic': 3, 'i': 3,
    'underline': 4, 'u': 4,
    'blink': 5, 'blink_slow': 5,
    'blink_fast': 6,
    'reverse': 7, 'invert': 7, 'rev': 7,
    'conceal': 8, 'hide': 8, 'h': 8,
    'crossed': 9, 'strike': 9, 'x': 9,
    'double_underline': 21, 'du': 21,
    'normal': 22,
    'no_italic': 23,
    'no_underline': 24,
    'no_blink': 25,
    'no_reverse': 27,
    'no_conceal': 28,
    'no_crossed': 29,

    # FOREGROUND COLORS
    'black_t0': 30, 'kt0': 30, 'black': 30, 'k': 30,
    'red_t0': 31, 'rt0': 31, 'red': 31, 'r': 31,
    'green_t0': 32, 'gt0': 32, 'green': 32, 'g': 32,
    'yellow_t0': 33, 'yt0': 33, 'yellow': 33, 'y': 33,
    'blue_t0': 34, 'bt0': 34, 'blue': 34, 'b': 34,
    'magenta_t0': 35, 'mt0': 35, 'magenta': 35, 'm': 35,
    'cyan_t0': 36, 'ct0': 36, 'cyan': 36, 'c': 36,
    'white_t0': 37, 'wt0': 37, 'white': 37, 'w': 37,
    'default_t0': 39, 'dt0': 39,

    # BACKGROUND COLORS
    'black_b0': 40, 'kb0': 40, 'kb': 40,
    'red_b0': 41, 'rb0': 41, 'rb': 41,
    'green_b0': 42, 'gb0': 42, 'gb': 42,
    'yellow_b0': 43, 'yb0': 43, 'yb': 43,
    'blue_b0': 44, 'bb0': 44, 'bb': 44,
    'magenta_b0': 45, 'mb0': 45, 'mb': 45,
    'cyan_b0': 46, 'cb0': 46, 'cb': 46,
    'white_b0': 47, 'wb0': 47, 'wb': 47,
    'default_b0': 49, 'db0': 49,

    # BRIGHT FOREGROUND COLORS
    'black_t1': 90, 'kt1': 90,
    'red_t1': 91, 'rt1': 91,
    'green_t1': 92, 'gt1': 92,
    'yellow_t1': 93, 'yt1': 93,
    'blue_t1': 94, 'bt1': 94,
    'magenta_t1': 95, 'mt1': 95,
    'cyan_t1': 96, 'ct1': 96,
    'white_t1': 97, 'wt1': 97,

    # BRIGHT BACKGROUND COLORS
    'black_b1': 100, 'kb1': 100,
    'red_b1': 101, 'rb1': 101,
    'green_b1': 102, 'gb1': 102,
    'yellow_b1': 103, 'yb1': 103,
    'blue_b1': 104, 'bb1': 104,
    'magenta_b1': 105, 'mb1': 105,
    'cyan_b1': 106, 'cb1': 106,
    'white_b1': 107, 'wb1': 107,
}