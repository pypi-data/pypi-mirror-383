class FontSize:
    FONT_SIZES = {
        "NORMAL": '\033[0m',
        "BOLD": '\033[1m',
        "DIM": '\033[2m',
        "ITALIC": '\033[3m',
        "UNDERLINE": '\033[4m',
        "BLINK": '\033[5m',
        "REVERSE": '\033[7m',
        "STRIKETHROUGH": '\033[9m'
    }
    
    def __init__(self, font_style: str = "NORMAL"):
        self.font_style = font_style.upper()
        
        if self.font_style not in self.FONT_SIZES:
            raise ValueError(f"Invalid font style: {self.font_style}")
    
    def _get_font_style(self):
        return self.FONT_SIZES[self.font_style]