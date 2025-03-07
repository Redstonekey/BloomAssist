class FakePCF8574_GPIO:
    def __init__(self, address):
        self.address = address
        self.output_values = {}
        self.lcd_messages = []
        self.cursor_pos = (0, 0)
        self.display_on = True

    def output(self, pin, value):
        self.output_values[pin] = value

    def get_output(self, pin):
        return self.output_values.get(pin, 0)

class FakeAdafruit_CharLCD:
    def __init__(self, pin_rs, pin_e, pins_db, GPIO):
        self.GPIO = GPIO
        self.messages = []
        self.cursor_pos = (0, 0)
        self.display_on = True

    def begin(self, cols, lines):
        pass

    def clear(self):
        self.messages = []

    def display(self):
        self.display_on = True

    def setCursor(self, col, row):
        self.cursor_pos = (row, col) #row and col are switched.

    def message(self, text):
        self.messages.append((self.cursor_pos, text))
        self.print_lcd()

    def print_lcd(self):
        print("\n" * 20)
        print("-----Fake LCD-----") #Added starting and ending symbols
        display = [[" " for _ in range(16)] for _ in range(2)]
        for pos, msg in self.messages:
            row, col = pos
            for char in msg:
                if char == '\n':
                    row += 1
                    col = 0
                else:
                    if 0 <= row < 2 and 0 <= col < 16:
                        display[row][col] = char
                        col += 1
        for line in display:
            print("|" + "".join(line) + "|") #Added starting and ending symbols
        print("------------------") # no more starting and ending symbols here

    def get_messages(self):
        return self.messages

    def get_cursor_pos(self):
        return self.cursor_pos

    def get_display_on(self):
        return self.display_on