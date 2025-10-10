# NOTE: Time timings have proven my Enums are the fastest
from ...util import Enum

class Position(Enum):
    '''How the element should be placed on the screen'''
    static   = Enum.auto(first=True) # Normal flow of the page
    relative = Enum.auto() # Get normal position but can move itself
    fixed    = Enum.auto() # Positioned wrt the body (cannot scroll)
    absolute = Enum.auto() # Position wrt the nearest relative parent
    #sticky   = Enum.auto() # Static until a point then fixed


class Display(Enum):
    '''How the element should be displayed'''
    none = Enum.auto(first=True)
    block = Enum.auto() # default width is to fill
    inline = Enum.auto() # width is the widht of content
    inline_block = Enum.auto() # best of both worlds
    outset = Enum.auto()
    flex = Enum.auto()
    inline_flex = Enum.auto()
    grid = Enum.auto() # not implemented
    #inlineGrid = Enum.auto()
    #flowRoot = Enum.auto()

class Overflow(Enum):
    hidden = Enum.auto(first=True)
    scroll = Enum.auto()

class Visibility(Enum):
    visible = Enum.auto(first=True)
    hidden  = Enum.auto()

class BoxSizing(Enum):
    content_box = Enum.auto(first=True)
    border_box  = Enum.auto()

class FontVariant(Enum):
    normal = Enum.auto(first=True)
    small_caps = Enum.auto()

class BorderWidth(Enum):
    medium = Enum.auto(first=True)
    thin = Enum.auto()
    thick = Enum.auto()

class JustifyContent(Enum):
    '''How flex items are aligned along the main axis'''
    flex_start = Enum.auto(first=True)
    flex_end = Enum.auto()
    center = Enum.auto()
    space_between = Enum.auto()
    space_around = Enum.auto()
    space_evenly = Enum.auto()


class AlignItems(Enum):
    '''How flex items are aligned along the cross axis'''
    flex_start = Enum.auto(first=True)
    flex_end = Enum.auto()
    center = Enum.auto()
    baseline = Enum.auto()
    stretch = Enum.auto()


class FlexDirection(Enum):
    '''Direction of the main axis'''
    row = Enum.auto(first=True)
    row_reverse = Enum.auto()
    column = Enum.auto()
    column_reverse = Enum.auto()
