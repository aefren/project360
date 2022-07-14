#!/usr/bin/env python
from cytolk import tolk
from datetime import datetime
from pdb import Pdb
import pickle
import socket

tolk.load()


class MyClient:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8050
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.cli:
            print(f"Connecting at {datetime.now().time()}.")
            self.cli.bind(("127.0.0.3", self.port))
            self.cli.connect((self.host, self.port))
            print(f"Connected at {datetime.now().time()}.")
            #Creamos un bucle para retener la conexion
            while True:
                #Instanciamos una entrada de datos para que el cliente pueda enviar mensajes
                mens = input("Mensaje desde Cliente a Servidor >> ")
                #Con el método send, enviamos el mensaje
                print(f"Sending message at {datetime.now().time()}.")
                self.cli.sendall(mens.encode("ascii"))
                print(f"Sent at {datetime.now().time()}.")
                
                print(f"Received at {datetime.now().time()}.")
                recibido = pickle.loads(recibido)
                print(f"Unload at {datetime.now().time()}.")
                print(f"{recibido[0]} {recibido[1]}.")
                if recibido[1] == "exit":
                    print(f"saliendo.")
                    break

MyClient().run()