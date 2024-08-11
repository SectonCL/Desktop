import deskinfo

def in_box(check_x, check_y, area_x, area_y, area_width, area_height):
    """Checks if the given position inside the provided area"""
    horizontal = False
    vertical   = False
    if area_y + area_height > check_y > area_y: vertical   = True
    if area_x + area_width  > check_x > area_x: horizontal = True
    return horizontal and vertical

def out_of_screen_BOX(box_x, box_y, box_width, box_height) -> bool:
    """Checks if the given box is colliding outside of screen.
    Examples:
        ________
        |      |  Does not collide
        |  ██  |
        |______|

    ------------------------------
        ________
        |      |  Does collide
        |     ███
        |______|
    """
    horizontal = False
    vertical   = False
    if box_x + box_width  > deskinfo.screenSize[0] or box_x < 0: horizontal = True
    if box_y + box_height > deskinfo.screenSize[1] or box_y < 0: vertical   = True
    return horizontal and vertical

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples:
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b

def queue_draw(x: int = 0, y: int = 0,
               width: int = 32, height: int = 32,
               color: str = "white"):
    """Draws a box inside an environment"""
    deskinfo.drawingQueue.append(f"canvas.create_rectangle({x}, {y}, {x} + {width}, {y} + {height}, fill='{color}')")

def queue_text(x: int = 0, y: int = 0,
               color: str = "white",
               text: str = "Hello World",
               anchor: str = "center",
               shadowed: bool = False,
               maxwidth: int = -1,
               rotation: float = 0.0,
               font: str | None = None):
    processingCMD = f"canvas.create_text({x}, {y}, fill='{color}', text='{text}', anchor='{anchor}'"
    if rotation != 0.0: processingCMD += f", angle=-{rotation}"
    if font: processingCMD += f", font={font}"
    if shadowed:
        deskinfo.drawingQueue.append(
            f"canvas.create_text({x + 2}, {y + 2}, fill='black', text='{text}', anchor='{anchor}')")
    deskinfo.drawingQueue.append(processingCMD + ")")

def queue_line(begin: list[int], end: list[int], color: str = "red", shadowed: bool = False):
    """Draws a line inside an environment. The end position is not relative"""
    if shadowed: deskinfo.drawingQueue.append(f"canvas.create_line({begin[0]}, {begin[1]}, {end[0]}, {end[1]}, fill='black', smooth={deskinfo.detailLevel > 0})")
    deskinfo.drawingQueue.append(f"canvas.create_line({begin[0]}, {begin[1]}, {end[0]}, {end[1]}, fill='{color}', smooth={deskinfo.detailLevel > 0})")