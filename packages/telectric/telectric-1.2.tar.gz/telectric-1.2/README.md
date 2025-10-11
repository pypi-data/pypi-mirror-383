# ⚡️ TElectric: Electrical Calculations Made Easy

TElectric  is a lightweight Python library for performing essential electrical engineering calculations. Whether you're a student, hobbyist, or professional engineer, TElectric helps you compute power, current, resistance, voltage, and more — quickly and accurately.

---

## 📦 Installation
``` bash 
pip install telectric

## 🚀 Features

* ✅ Calculate Power, Current, Resistance, and Voltage

* ✅ Support for Ohm’s Law and Power Law

* ✅ Compute Series and Parallel combinations of resistors and capacitors

* ✅ Convert between units (e.g., mA ↔ A, W ↔ kW)

* ✅ Validate Ohm’s Law for given values

* ✅ Optional symbolic output (e.g., R = 10 Ω) using eleman() mode

## 🧪 Usage Examples

from telectric import power, current, resistance, voltage, eleman

// Basic calculation
print(power(current=2, voltage=5))  # Output: 10

// Symbolic mode
eleman()
print(resistance(voltage=10, current=2))  # Output: '5.0 R'

## 📊 Downloads

Over 500+ downloads and growing!
Check out https://pepy.tech/projects/telectric for live stats. 