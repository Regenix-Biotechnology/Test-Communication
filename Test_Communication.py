import serial 

commande = "#LOGO\r"
#commande = "MEA 4 3\r"
ser = serial.Serial('COM3',baudrate=115200, timeout=2)
print("Creer")
ser.write(commande.encode())

print("enoyer")


try: 
    try:
        bs = ser.readline()
        print(bs)
    except serial.SerialException as e:
        print(e)
        
except KeyboardInterrupt:
    print("exit")

finally:
    ser.close()
print("Finish")

