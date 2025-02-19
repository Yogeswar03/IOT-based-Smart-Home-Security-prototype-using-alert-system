pip install twilio pybluez RPi.GPIO



import RPi.GPIO as GPIO
import time
import bluetooth
from twilio.rest import Client


TWILIO_ACCOUNT_SID = "AC20eaa6f03636b759368c605440f063"
TWILIO_AUTH_TOKEN = "bb7be5ae8de14e7cda433593dd7af"
TWILIO_PHONE_NUMBER = "+18649739495"
OWNER_PHONE_NUMBER = "+916305568170"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

PIR_SENSOR_PIN = 4        
DOOR_SENSOR_PIN = 17      
BUZZER_PIN = 27           

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_SENSOR_PIN, GPIO.IN)
GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def send_sms_alert(message):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=OWNER_PHONE_NUMBER
        )
        print("SMS alert sent successfully!")
    except Exception as e:
        print("Error sending SMS:", e)


def motion_detected(channel):
    print("Motion detected!")
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    send_sms_alert("ALERT: SomeOne enetered the house!")
    time.sleep(2)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def door_opened(channel):
    print("Door opened!")
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    send_sms_alert("ALERT: Someone Entered the House!")
    time.sleep(2)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def bluetooth_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", 1))
    server_sock.listen(1)
    print("Waiting for Bluetooth connection...")

    client_sock, address = server_sock.accept()
    print(f"Connected to {address}")

    try:
        while True:
            data = client_sock.recv(1024).decode("utf-8").strip()
            if data == "ARM":
                print("System Armed")
                send_sms_alert("Home Security System Armed.")
            elif data == "DISARM":
                print("System Disarmed")
                send_sms_alert("Home Security System Disarmed.")
            elif data == "EXIT":
                break
    except Exception as e:
        print("Bluetooth Error:", e)
    finally:
        client_sock.close()
        server_sock.close()



import threading
bluetooth_thread = threading.Thread(target=bluetooth_server)
bluetooth_thread.start()

try:
    while True:
        time.sleep(1) 
except KeyboardInterrupt:
    print("Exiting program...")
    GPIO.cleanup()
