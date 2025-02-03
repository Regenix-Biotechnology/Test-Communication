import serial 
import time
import csv
from datetime import datetime
import os

"""
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
"""

# Configuration de la communication série
SERIAL_PORT = 'COM3'  
BAUD_RATE = 115200  
DATA_TIMEOUT = 2


CSV_FILE = "firesting_data_log.csv"  # Fichier de stockage des données
DURATION_SECONDS = 30
#DURATION_SECONDS = 7 * 24 * 60 * 60  # Durée de l'acquisition: 7 jours
SAMPLING_INTERVAL = 1.0                # Fréquence d'échantillonnage en secondes

print("Chemin du fichier CSV :", os.path.abspath(CSV_FILE))



# Initialisation du port série
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=DATA_TIMEOUT)
    print("Connexion série établie avec FireSting")
except serial.SerialException as e:
    print(f"Erreur de connexion : {e}")
    exit()

# Fonction pour envoyer une commande au module FireSting
def send_command(command):
    ser.write((f"{command}\r\n").encode()) #Envoie la commande série au module FireSting, La commande est complétée par \r\n (retour à la ligne + saut de ligne),convertit la chaîne en format binaire UTF-8
    time.sleep(0.1)
    response = ser.readline().decode().strip() #transforme les données binaires en chaîne de texte,supprime les espaces et les retours à la ligne 
    return response

# Fonction pour lire les mesures de température, DO et pH
def read_measurements():
    command = "MEA 1 47"  # Canal 1 et tous les capteurs disponibles (47)
    response = send_command(command) #Envoie la commande et reçoit la réponse du FireSting
    
    if not response.startswith("MEA"):
        print("Erreur de lecture des mesures")
        return None

    try:
        parts = response.split(" ")
        status = int(parts[2])
        if status != 0:
            print("Mesure invalide ou erreur")
           #return None

        # Extraction des valeurs clés selon les indices documentés
        temp_sample = float(parts[8]) / 1000.0 
        DO = float(parts[4]) / 1000.0 
        ph_value = float(parts[15]) / 100.0

        print(response)


        return temp_sample, DO, ph_value
    except (ValueError, IndexError) as e:   #Si une conversion en entier échoue,Si un indice (parts[5]) dépasse la taille de la liste 
        print(f"Erreur lors du parsing des données : {e}")
        return None

# Création ou ouverture du fichier CSV
with open(CSV_FILE, mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Horodatage", "Température (°C)", "DO (µmol/L)", "pH"])

    start_time = time.time()

    while time.time() - start_time < DURATION_SECONDS:
        measurements = read_measurements()      #Si la mesure est valide, les valeurs sont extraites et enregistrés
        if measurements:
            temp, do, ph = measurements
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #YYYY-MM-DD HH:MM:SS
            csv_writer.writerow([timestamp, temp, do, ph])
            print(f"{timestamp} | Temp: {temp} °C | DO: {do} µmol/L | pH: {ph}")

        time.sleep(SAMPLING_INTERVAL)

print("Acquisition terminée. Données enregistrées dans firesting_data_log.csv")

# Fermeture de la connexion série
ser.close()
