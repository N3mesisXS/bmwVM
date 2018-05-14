#!/usr/bin/env python
# -*- coding: utf-8 -*-

#14.5.2018 - Steven M. Schacht - Verbrauchsmonitor fuer BMW Ausf. A 
#Fuer BMW e46 und e39


import xbmcaddon
import xbmcvfs
import xbmcgui
import xbmc
import os
import sys
import time
import socket
from datetime import datetime
from time import sleep


#-------------------------Variablen & Spezialvariablen----------------------#
AUTHOR 			= 'Steven'
ADDON      		= xbmcaddon.Addon()
ADDON_ID 		= ADDON.getAddonInfo('id')
ADDON_NAME		= ADDON.getAddonInfo('name')
ADDON_PATH 		= ADDON.getAddonInfo('path')
ADDON_SETTINGS	= xbmcaddon.Addon(id="script.bmwVM") #ADDON_ID geht auch
ADDON_USERPATH 	= os.path.join(xbmc.translatePath('special://userdata'), 'addon_data', ADDON_ID)

#Variablen
JahrMonat		= datetime.now() #Uhrzeit, Jahr und Monat, Tag fehlt
VM_DB_FILE		=	os.path.join(ADDON_USERPATH, 'VM_Database.log')
deliminator 	= ' '

#Notifikationen, standard texte fuer Dialogbfenster
lineyesno = "Möchten Sie diesen Wert wirklich zurückstellen?"

#Aus dem Kombi holen, send_tcp_command gibt: "return answer" Testzwecke:136000
#aktKilometer 	= get_odometer()


#------------------Funktionen------------------#

#Kilometerstand aus dem Kombi abfragen mit TCP, wird in der Funktion "get_odometer()" aufgerufen
def send_tcp_command(message):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ok
    clientsocket.settimeout(0.1)  # ok
	
    port = 8089
    try:
        clientsocket.connect(('localhost', port))  # 127.0.0.1 ok
    except:
        raise ValueError

    clientsocket.send(message)  # obc;get;odometer #ok
    # time.sleep(0.2)

    clientsocket.settimeout(0.2)  # auf antwort warten ok

    # time.sleep(0.2)

    clientsocket.settimeout(0.2)  # ok
    clientsocket.shutdown(True)  # ok

    data = clientsocket.recv(50).replace('\n', '')  # antwort nicht groesser 50 nicht weniger 50 ok
    return data

#Ruft Kilometerstand ab
def get_odometer():
    try:
        odometer = int(send_tcp_command('obc;get;odometer')) #ok
    except ValueError:
        odometer = -1

    if odometer < 0:
        xbmc.executebuiltin('Notification(ERROR:, TCP returns: %s, %d)' % (odometer, time)) #ok
        return 0 # Um zu verhindern das er Quatsch in die variable schreibt, dummywert
    else:
        return odometer #ok	

		
def checkFileandRead():
	#Pfade und Dateien erstellen wenn nicht vorhanden.
	if not xbmcvfs.exists(ADDON_USERPATH):
		xbmcvfs.mkdir(ADDON_USERPATH)
		
	if os.path.isfile(VM_DB_FILE) == False:
		xbmcgui.Dialog().ok(ADDON_NAME, "'VM_Database.log' nicht gefunden!", "Datei oder Inhalt wird neu erstellt.", "Sie koennen jederzeit ein Backup im Addonverzeichnis ablegen.")
		with open(VM_DB_FILE, 'w') as neueDatei:
			neueDatei.close()
	
	#Datenbank auslesen
	with open(VM_DB_FILE, 'r') as DB_FILE_LESEN:
		inhaltSpeichern = DB_FILE_LESEN.read()
		
	DB_FILE_LESEN.close()
	
	ItemList = filter(lambda a: a!='', inhaltSpeichern.split('\n'))
	
	Items = [{
		"Datum":x.split(deliminator)[0],
		"Tacho":x.split(deliminator)[1],
		"Verbrauch":x.split(deliminator)[2],
		"Distanz":x.split(deliminator)[3],
		"Menge":x.split(deliminator)[4],
		"Kosten":x.split(deliminator)[5],
		"Sorte":x.split(deliminator)[6],
		}for x in ItemList]
		#GEHT!
	xbmcgui.Dialog().ok(ADDON_NAME, str(Items[0].get('Datum')))
	
	#inhaltSchreiben = open(VM_DB_FILE, 'w')
	#inhaltSchreiben.write(str(Items))
	#inhaltSchreiben.write("\n")
	#inhaltSchreiben.close()
	
#----------------------MAIN---------------------#

def main(): 
	checkFileandRead()
	
	
	
	
class FensterXML(xbmcgui.WindowXML):
	
	def onInit(self):
		
		
		self.Konfig = self.getControl(201)
		self.Konfig.setLabel("Konfiguration")
		
		#Buttons Navigation, label links/mittig
		self.BtnKonfig		= self.getControl(201)
		self.BtnInspektion1 = self.getControl(111)
		self.BtnInspektion2 = self.getControl(112)
		self.BtnOil 		= self.getControl(113)
		self.BtnZK 			= self.getControl(114)
		self.BtnMF 			= self.getControl(115)
		self.BtnLF	 		= self.getControl(116)		
		self.BtnBV 			= self.getControl(117)
		self.BtnBH 			= self.getControl(118)
		self.BtnBF 			= self.getControl(119)
		self.BtnHU 			= self.getControl(120)
		self.BtnAU 			= self.getControl(121)
		
		#Navigation
		self.BtnKonfig.setNavigation(self.BtnInspektion1,self.BtnInspektion1,self.BtnInspektion1,self.BtnInspektion1)
		self.BtnInspektion1.setNavigation(self.BtnAU,self.BtnInspektion2,self.BtnKonfig,self.BtnInspektion1)
		self.BtnInspektion2.setNavigation(self.BtnInspektion1,self.BtnOil,self.BtnKonfig,self.BtnInspektion2)
		self.BtnOil.setNavigation(self.BtnInspektion2,self.BtnZK,self.BtnKonfig,self.BtnOil)
		self.BtnZK.setNavigation(self.BtnOil,self.BtnMF,self.BtnKonfig,self.BtnZK)
		self.BtnMF.setNavigation(self.BtnZK,self.BtnLF,self.BtnKonfig,self.BtnMF)
		self.BtnLF.setNavigation(self.BtnMF,self.BtnBV,self.BtnKonfig,self.BtnLF)
		self.BtnBV.setNavigation(self.BtnLF,self.BtnBH,self.BtnKonfig,self.BtnBV)
		self.BtnBH.setNavigation(self.BtnBV,self.BtnBF,self.BtnKonfig,self.BtnBH)
		self.BtnBF.setNavigation(self.BtnBH,self.BtnHU,self.BtnKonfig,self.BtnBF)
		self.BtnHU.setNavigation(self.BtnBF,self.BtnAU,self.BtnKonfig,self.BtnHU)
		self.BtnAU.setNavigation(self.BtnHU,self.BtnInspektion1,self.BtnKonfig,self.BtnAU)
		
		
	def onClick(self, controlID):
		if (controlID == 201): #Konfigurations Buttons
			#ok = xbmcaddon.Addon().openSettings()
			#self.close()
			dialog = VMDialog("skin.xml", ADDON_PATH, 'Default', '720p')
			dialog.doModal()
			del dialog
	
		if (controlID == 111): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(addonname, lineyesno)
			if ok==1:
				resetPointDSANeuschreiben(0) 	#resetfunktion ausfuehren
				faelligkeitAusfuehren()			#faelligkeit neu berechnen
				self.Inspektion1.setLabel(str(aktFaelligkeit[0])+" km") #label setzen
				self.InspektionIGelb.setVisible(False)
				self.InspektionIRot.setVisible(False)
				self.InspektionIGruen.setVisible(True) #Gruenes icon anzeigen und Rot und Gelb unsichtbar machen
			
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconInsp))
			
	
class VMDialog(xbmcgui.WindowXMLDialog):			

	def onInit(self):
		self.MAIN = self.getControl(200)
		self.MAIN.setLabel("Service")
	
	
	def onClick(self, controlID):
		#if (controlID == 201): #Konfigurations Buttons
		ok = xbmcaddon.Addon().openSettings()
		self.close()

		
if __name__ == '__main__':
	main() #ok
	w = FensterXML("verbrauchsmonitor.xml", ADDON_PATH, 'Default', '720p') #ok
	w.doModal() #ok
	del w #ok