import tkinter as tk
from tkinter import font
import math

class Calculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Kalkulator Modern")
        self.window.geometry("350x500")
        self.window.resizable(False, False)
        self.window.configure(bg='#2C2C2C')
        
        # Variabel untuk menyimpan operasi
        self.current_input = ""
        self.result_var = tk.StringVar()
        self.result_var.set("0")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Font customization
        display_font = font.Font(family="Arial", size=20, weight="bold")
        button_font = font.Font(family="Arial", size=12, weight="bold")
        
        # Display frame
        display_frame = tk.Frame(self.window, bg='#2C2C2C')
        display_frame.pack(pady=20, padx=20, fill='x')
        
        # Display label
        display = tk.Label(
            display_frame,
            textvariable=self.result_var,
            font=display_font,
            bg='#1A1A1A',
            fg='#FFFFFF',
            anchor='e',
            padx=20,
            pady=15,
            relief='flat'
        )
        display.pack(fill='x')
        
        # Button frame
        button_frame = tk.Frame(self.window, bg='#2C2C2C')
        button_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Button layout
        buttons = [
            ['C', '±', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '', '.', '=']
        ]
        
        # Color scheme
        button_colors = {
            'numbers': {'bg': '#404040', 'fg': 'white', 'hover': '#505050'},
            'operations': {'bg': '#FF9500', 'fg': 'white', 'hover': '#FFB143'},
            'special': {'bg': '#A6A6A6', 'fg': 'black', 'hover': '#B6B6B6'}
        }
        
        # Create buttons
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                if text == '':
                    continue
                    
                # Determine button type
                if text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
                    btn_color = button_colors['numbers']
                elif text in ['÷', '×', '-', '+', '=']:
                    btn_color = button_colors['operations']
                else:
                    btn_color = button_colors['special']
                
                # Special handling for '0' button (span 2 columns)
                if text == '0':
                    btn = tk.Button(
                        button_frame,
                        text=text,
                        font=button_font,
                        bg=btn_color['bg'],
                        fg=btn_color['fg'],
                        relief='flat',
                        border=0,
                        command=lambda t=text: self.button_click(t)
                    )
                    btn.grid(row=i, column=j, columnspan=2, sticky='ew', padx=1, pady=1)
                else:
                    btn = tk.Button(
                        button_frame,
                        text=text,
                        font=button_font,
                        bg=btn_color['bg'],
                        fg=btn_color['fg'],
                        relief='flat',
                        border=0,
                        command=lambda t=text: self.button_click(t)
                    )
                    btn.grid(row=i, column=j, sticky='ew', padx=1, pady=1)
                
                # Add hover effect
                self.add_hover_effect(btn, btn_color['bg'], btn_color['hover'])
        
        # Configure grid weights
        for i in range(5):
            button_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            button_frame.grid_columnconfigure(j, weight=1)
    
    def add_hover_effect(self, button, original_color, hover_color):
        def on_enter(e):
            button.config(bg=hover_color)
        
        def on_leave(e):
            button.config(bg=original_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def button_click(self, value):
        if value == 'C':
            self.current_input = ""
            self.result_var.set("0")
        
        elif value == '=':
            try:
                # Replace display operators with Python operators
                expression = self.current_input.replace('×', '*').replace('÷', '/')
                result = eval(expression)
                self.result_var.set(str(result))
                self.current_input = str(result)
            except:
                self.result_var.set("Error")
                self.current_input = ""
        
        elif value == '±':
            if self.current_input:
                if self.current_input[0] == '-':
                    self.current_input = self.current_input[1:]
                else:
                    self.current_input = '-' + self.current_input
                self.result_var.set(self.current_input)
        
        elif value == '%':
            try:
                expression = self.current_input.replace('×', '*').replace('÷', '/')
                result = eval(expression) / 100
                self.result_var.set(str(result))
                self.current_input = str(result)
            except:
                self.result_var.set("Error")
                self.current_input = ""
        
        else:
            if self.current_input == "0" or self.result_var.get() == "Error":
                self.current_input = ""
            
            self.current_input += value
            self.result_var.set(self.current_input)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    calc = Calculator()
    calc.run()