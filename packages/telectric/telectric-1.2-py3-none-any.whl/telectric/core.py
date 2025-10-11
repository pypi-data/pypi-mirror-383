import math
import tkinter as tk
from tkinter import ttk

e = 0

def eleman():
    global e 
    e = 1

def power(current=None, voltage=None, resistance=None):
    global e
    if current is not None and voltage is not None:
        # P = I * V
        result = current * voltage
    elif current is not None and resistance is not None:
        # P = I² * R
        result = current ** 2 * resistance
    elif voltage is not None and resistance is not None:
        # P = V² / R
        result = voltage ** 2 / resistance
    else:
        raise ValueError("لطفاً از بین جریان، ولتاژ، مقاومت دو مقدار وارد کنید.")

    return f'{result} P' if e == 1 else result

def current(power=None, voltage=None, resistance=None):
    global e 
    if power is not None and voltage is not None:
        # I = P / V
        result = power / voltage
    elif voltage is not None and resistance is not None:
        # I = V / R
        result = voltage / resistance
    elif power is not None and resistance is not None:
        # I = √(P / R)
        result = math.sqrt(power / resistance)
    else:
        raise ValueError("لطفاً از بین توان، ولتاژ، مقاومت دو مقدار وارد کنید.")

    return f'{result} C' if e == 1 else result

def resistance(voltage=None, current=None, power=None):
    global e
    if voltage is not None and current is not None:
        # R = V / I
        result = voltage / current
    elif voltage is not None and power is not None:
        # R = V² / P
        result = voltage ** 2 / power
    elif power is not None and current is not None:
        # R = P / I²
        result = power / (current ** 2)
    else:
        raise ValueError("لطفاً از بین ولتاژ، جریان، توان دو مقدار وارد کنید.")

    return f'{result} R' if e == 1 else result

def voltage(current=None, resistance=None, power=None):
    global e
    if current is not None and resistance is not None:
        result = current * resistance  # V = I * R
    elif power is not None and current is not None:
        result = power / current       # V = P / I
    elif power is not None and resistance is not None:
        result = math.sqrt(power * resistance)  # V = √(P * R)
    else:
        raise ValueError("لطفاً از بین جریان، مقاومت، توان دو مقدار وارد کنید.")

    return f'{result} V' if e == 1 else result

def init():
    root = tk.Tk()
    root.title("TElectric - Electrical Calculator")
    root.geometry("500x400")

    title_label = ttk.Label(root, text="TElectric Calculator", font=("Arial", 16))
    title_label.pack(pady=20)

    input_frame = ttk.Frame(root)
    input_frame.pack(pady=10)

    current_label = ttk.Label(input_frame, text="Current (I) [A]:")
    current_label.grid(row=0, column=0)
    current_entry = ttk.Entry(input_frame)
    current_entry.grid(row=0, column=1)

    resistance_label = ttk.Label(input_frame, text="Resistance (R) [Ω]:")
    resistance_label.grid(row=1, column=0)
    resistance_entry = ttk.Entry(input_frame)
    resistance_entry.grid(row=1, column=1)

    power_label = ttk.Label(input_frame, text="Power (P) [W]:")
    power_label.grid(row=2, column=0)
    power_entry = ttk.Entry(input_frame)
    power_entry.grid(row=2, column=1)

    result_label = ttk.Label(root, text="Result: ", font=("Arial", 12))
    result_label.pack(pady=20)

    def calculate():
        try:
            I = float(current_entry.get()) if current_entry.get() else None
            R = float(resistance_entry.get()) if resistance_entry.get() else None
            P = float(power_entry.get()) if power_entry.get() else None

            if P is None and I is not None and R is not None:
                P = power(current=I, resistance=R)
                result_label.config(text=f"Power (P): {P:.2f} W")

            elif I is None and P is not None and R is not None:
                I = current(power=P, resistance=R)
                result_label.config(text=f"Current (I): {I:.2f} A")

            elif R is None and P is not None and I is not None:
                R = resistance(power=P, current=I)
                result_label.config(text=f"Resistance (R): {R:.2f} Ω")
            else:
                result_label.config(text="Error: Please enter two values for calculation.")

        except Exception as e:
            result_label.config(text=f"Error: {e}")

    calc_btn = ttk.Button(root, text="Calculate", command=calculate)
    calc_btn.pack(pady=10)

    root.mainloop()
def energy_label_w(power = None):
    if power < 100:
        return "A+++"
    elif power < 150:
        return "A++"
    elif power < 200:
        return "A+"
    elif power < 250:
        return "A"
    elif power < 300:
        return "B"
    elif power < 400:
        return "C"
    elif power < 500:
        return "D"
    else:
        return "E"
def energy_label_c(current = None):
    if current < 0.1:
        return "Ultra Low (C+++)"
    elif current < 0.5:
        return "Low (C++)"
    elif current < 2:
        return "Moderate (C+)"
    elif current < 5:
        return "High (C)"
    elif current < 10:
        return "Very High (C-)"
    else:
        return "Extreme (C--)"
def energy_label_r(resistance = None):
    if resistance < 1:
        return "Ultra Low (R+++)"
    elif resistance < 10:
        return "Low (R++)"
    elif resistance < 100:
        return "Standard (R+)"
    elif resistance < 1000:
        return "High (R)"
    elif resistance < 10000:
        return "Very High (R-)"
    else:
        return "Extreme (R--)"
