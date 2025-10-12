# 🔢 decitobin WebStyle 🧒🔢

**decitobin** is a versatile Python tool that converts between number systems and text — now with a web-style user interface and enhanced features.

Whether you're converting decimal to binary, exploring ASCII encoding, or transforming hexadecimal strings, decitobin offers an interactive and beginner-friendly experience.

---

## 🌟 Features

🧠 Support for multiple conversions:
Decimal → Binary  Binary → Decimal  ASCII → Binary  Binary → ASCII  Hex → Binary  Binary → Hex  Binary → Octal  Octal → Binary  

🖥️ Graphical interface with dropdown selection (Tkinter-based)  
🚀 Instant results with detailed formatting  
📋 Copy output to clipboard  
📦 Easy to install and run on any platform  

---

## 💻 Installation  

```sh
pip install decitobin
```

## Launching the App  
Run the converter using:  
```sh
python -m decitobin
```
Or run your own launcher script using:  
```python
import decitobin

print(decitobin.dec2bin("12"))        # Output: 1100
print(decitobin.ascii2bin("A"))       # Output: 01000001
print(decitobin.bin2hex("1011"))      # Output: B
print(decitobin.bin2oct("101110"))    # Output: 56
print(decitobin.oct2bin("56"))        # Output: 101110
```
## License
Licensed under the MIT License.
