import deskinfo

def in_box(check_x, check_y, area_x, area_y, area_width, area_height):
    """Checks if the given position inside the provided area"""
    horizontal = False
    vertical   = False
    if area_y + area_height > check_y > area_y: vertical   = True
    if area_x + area_width  > check_x > area_x: horizontal = True
    return horizontal and vertical

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b

def queue_draw(drawType: str = "box",
               x: int = 0, y: int = 0,
               width: int = 32, height: int = 32,
               color: str = "white"):
    """Draws an element inside an environment"""
    match drawType:
        case "box":  deskinfo.drawingQueue.append(f"canvas.create_rectangle({x}, {y}, {x} + {width}, {y} + {height}, fill='{color}')")
        case _:      print(f"queue_draw, {type}: No such thing!")

def queue_text(x: int = 0, y: int = 0,
               color: str = "white",
               text: str = "Hello World",
               centered: bool = True,
               shadowed: bool = False):
    if shadowed:
        deskinfo.drawingQueue.append(
            f"canvas.create_text({x + 2}, {y + 2}, fill='black', text='{text}', anchor={'tkinter.CENTER' if centered else 'tkinter.NW'})")
    deskinfo.drawingQueue.append(f"canvas.create_text({x}, {y}, fill='{color}', text='{text}', anchor={'tkinter.CENTER' if centered else 'tkinter.NW'})")