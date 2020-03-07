import serial

ser = serial.Serial("/dev/ttyACM0")
trans = {"8":"6939", "4":"6039", "6":"6930", "5":"6030"}

while True:
    a = input("> ")
    if a in trans:
        ser.write(trans[a].encode())