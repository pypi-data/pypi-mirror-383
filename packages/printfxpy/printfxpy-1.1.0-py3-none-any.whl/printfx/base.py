from typing import Optional
from .colors import ColorsSet
from .fontsize import FontSize

class PrintFX:
    def __init__(self, color: str = "WHITE", font_style: str = "NORMAL"):
        self.color_list = ColorsSet(color)
        self.font_style = FontSize(font_style)

    def printfx(self, text: str, color: Optional[str] = None, font_style: Optional[str] = None, end: str = "\n") -> None:
        if color:
            temp_color = ColorsSet(color)
            color_code = temp_color._getcolor()
        else:
            color_code = self.color_list._getcolor()
        
        if font_style:
            temp_font_style = FontSize(font_style)
            font_code = temp_font_style._get_font_style()
        else:
            font_code = self.font_style._get_font_style()
        
        reset_code = '\033[0m'
        print(f"{color_code}{font_code}{text}{reset_code}", end=end)