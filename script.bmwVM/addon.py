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
VM_DB_FILE		= os.path.join(ADDON_USERPATH, 'VM_Database.log')
deliminator 	= ' '
TankVolumen		= ADDON_SETTINGS.getSetting("Tankvol")
#Notifikationen, standard texte fuer Dialogbfenster
lineyesno = "Möchten Sie diesen Wert wirklich zurückstellen?"

#Aus dem Kombi holen, send_tcp_command gibt: "return answer" Testzwecke:136000
#aktKilometer 	= get_odometer()


#------------------Funktionen------------------#

#Nur Zahlen Eingeben
def numerischeEingabe(title):
	dialog = xbmcgui.Dialog()
	d = dialog.numeric(0, title)
	#Variable darf keinesfalls Leer übergeben werden, daher wird das Fenster wieder aufgerufen
	while d=="":
		d = dialog.numeric(0, title)
	return d
		
#Vollwertige Tastatur
def TastaturEingabe(title):
	ts = xbmc.Keyboard('default', 'heading')
	ts.setDefault("")
	ts.setHeading(title)
	ts.setHiddenInput(False)
	ts.doModal()
	
	if(ts.isConfirmed()):
		ausgabe_wert = ts.getText()
		return(ausgabe_wert)
	else:
		return(title)

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
        xbmc.executebuiltin('Notification(ERROR:, TCP returns: %s)' % (odometer)) #ok
		
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
	
		#Ist keine Datei vorhanden so soll direkt die Dialogbox erscheinen für den ersten Eintrag
		#dialog = VMDialog("skin.xml", ADDON_PATH, 'Default', '720p')
		#dialog.doModal()
		#del dialog
	
	#Datenbank auslesen
	with open(VM_DB_FILE, 'r') as DB_FILE_LESEN:
		inhaltSpeichern = DB_FILE_LESEN.read()
		
	DB_FILE_LESEN.close()
	
	ItemList = filter(lambda a: a!='', inhaltSpeichern.split('\n'))
	global Items
	Items = [{
		"Datum":x.split(deliminator)[0],
		"Tacho":x.split(deliminator)[1],
		"Verbrauch":x.split(deliminator)[2],
		"Distanz":x.split(deliminator)[3],
		"Menge":x.split(deliminator)[4],
		"Kosten":x.split(deliminator)[5],
		"Sorte":x.split(deliminator)[6],
		"Betankung":x.split(deliminator)[7],
		}for x in ItemList]
		#GEHT!
	#xbmcgui.Dialog().ok(ADDON_NAME, str(Items[0].get('Tacho')))
	
	#VM_DB_FILE EXPORTFUNKTION zum HOME verzeichnis
	
	#inhaltSchreiben = open(VM_DB_FILE, 'w')
	#inhaltSchreiben.write(str(Items))
	#inhaltSchreiben.write("\n")
	#inhaltSchreiben.close()

def WriteNewFile(Menge, Kosten, Sorte, Betankung):
	#VM_DB_FILE EXPORTFUNKTION zum HOME verzeichnis
	ListParameter = list()
	
	ListParameter.append("Datum")
	ListParameter.append("Tacho")
	ListParameter.append("Verbrauch")
	ListParameter.append("Distanz")
	ListParameter.append("Menge")
	ListParameter.append("Kosten")
	ListParameter.append("Sorte")
	ListParameter.append("Betankung")
		
	#Distance = Items[0].get("Tacho")) - get_odometer()
	
	try:
		Items[0].get(ListParameter[1])
		
		Distance = int(get_odometer()) - int(Items[0].get(ListParameter[1]))
		
		if(Distance == 0):
			Distance = numerischeEingabe("Erstbetankung Distanz:") # Erste Distanz haendisch eintragen bei "Neuwagen"
			
			while(Distance == "0"):
				Distance = numerischeEingabe("Erstbetankung Distanz:") # Erste Distanz haendisch eintragen bei "Neuwagen"
	except:
		Distance = numerischeEingabe("Erstbetankung Distanz:") #Distanz haendisch nachtragen wenn erste Betankung
		
		while(Distance == "0"):
				Distance = numerischeEingabe("Erstbetankung Distanz:") # Erste Distanz haendisch eintragen bei "Neuwagen"
	
	Verbrauch = 0
	allKilo = 0
	allMenge = 0.0
	cpyDist = Distance
	cpyMenge = Menge
	Counter = 0
	
	if (Betankung == 0):
		try:
			if (int(Items[0].get(ListParameter[7])) == 1):
				for Item in Items:
					if (int(Items[Counter].get(ListParameter[7])) == 1):
						allKilo = allKilo + int(Items[Counter].get(ListParameter[3]))
						allMenge = allMenge + float(Items[Counter].get(ListParameter[4]))
					Counter = Counter + 1
				
					if(int(Items[Counter].get(ListParameter[7])) == 0):
						break
				
			cpyDist = int(cpyDist) + int(allKilo)
			cpyMenge = float(cpyMenge) + float(allMenge)
			
			Verbrauch 	= (float(cpyMenge) * 100) / int(cpyDist)
		except:
			Verbrauch 	= (float(Menge) * 100) / int(Distance)
			
		
				
		
	
	d = datetime.today()
	
	inhaltSchreiben = open(VM_DB_FILE, 'w')
	
	inhaltSchreiben.write(str(d.strftime('%d.%m.%y'))) #str(d.day) + "." + str(d.month) + "." + str(d.year)) #Datum
	inhaltSchreiben.write(" ")
	inhaltSchreiben.write(str(get_odometer())) #get_odometer()
	inhaltSchreiben.write(" ")
	if (Betankung == 0):
		inhaltSchreiben.write(str(round(Verbrauch, 2)))
	if (Betankung == 1):
		inhaltSchreiben.write("-")
	inhaltSchreiben.write(" ")
	inhaltSchreiben.write(str(Distance))
	inhaltSchreiben.write(" ")
	inhaltSchreiben.write(str(Menge))
	inhaltSchreiben.write(" ")
	inhaltSchreiben.write(str(Kosten))
	inhaltSchreiben.write(" ")
	inhaltSchreiben.write(str(Sorte))
	inhaltSchreiben.write(" ")
	inhaltSchreiben.write(str(Betankung))
	inhaltSchreiben.write("\n")
	
	Count 	= 0
	Count2 	= 0
	
	for Item in Items:
		for Count2 in range(8):
			inhaltSchreiben.write(str(Items[Count].get(ListParameter[Count2])))
			inhaltSchreiben.write(" ")
		inhaltSchreiben.write("\n")
		Count = Count + 1
		
	inhaltSchreiben.close()
	
#----------------------MAIN---------------------#

def main(): 
	checkFileandRead()
	
	#Es werden erstmal nur die letzten 10 Einträge angezeigt, später soll man durch alle scrollen können
	
	#-> welcher Button zuerst den Fokus hat ist von den IDs abhängig
	
class FensterXML(xbmcgui.WindowXML):
	
	def onInit(self):
		#self.Konfig = self.getControl(201)
		
		
		#Buttons Navigation, label links/mittig
		self.BtnKonfig		= self.getControl(201)
		self.BtnKonfig.setLabel("Konfiguration")
		self.BtnHinzufuegen	= self.getControl(202)
		self.BtnHinzufuegen.setLabel("Hinzufügen")
		
		self.Gr1	= self.getControl(666)
		self.Gr2	= self.getControl(667)
		self.Gr3	= self.getControl(668)
		self.Gr4	= self.getControl(669)
		self.Gr5	= self.getControl(670)
		self.Gr6	= self.getControl(671)
		self.Gr7	= self.getControl(672)
		self.Gr8	= self.getControl(673)
		self.Gr9	= self.getControl(674)
		self.Gr10	= self.getControl(675)
		
		self.DictionaryListParameter = list()
		self.DictionaryListParameter.append("Datum")
		self.DictionaryListParameter.append("Tacho")
		self.DictionaryListParameter.append("Verbrauch")
		self.DictionaryListParameter.append("Distanz")
		self.DictionaryListParameter.append("Menge")
		self.DictionaryListParameter.append("Kosten")
		self.DictionaryListParameter.append("Sorte")
		
		self.DictionaryListEndPara = list()
		self.DictionaryListEndPara.append(" km")
		self.DictionaryListEndPara.append(" L")
		self.DictionaryListEndPara.append(" L")
		self.DictionaryListEndPara.append(" €")
		
		#Umbau auf einer Liste
		self.Line_1 	= list()
		self.Line_2 	= list()
		self.Line_3 	= list()
		self.Line_4 	= list()
		self.Line_5 	= list()
		self.Line_6 	= list()
		self.Line_7 	= list()
		self.Line_8 	= list()
		self.Line_9 	= list()
		self.Line_10 	= list()
		
		self.Line_1.append(self.getControl(111)) # Erster Button
		
		iLineNr = 211
		
		while (iLineNr < 217):
			self.Line_1.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
		
		while (iLineNr < 224):
			self.Line_2.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
		
		while (iLineNr < 231):
			self.Line_3.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
		
		while (iLineNr < 238):
			self.Line_4.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
		
		while (iLineNr < 245):
			self.Line_5.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
		
		while (iLineNr < 252):
			self.Line_6.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
		
		while (iLineNr < 259):
			self.Line_7.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
		
		while (iLineNr < 266):
			self.Line_8.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
		
		while (iLineNr < 273):
			self.Line_9.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
			
		while (iLineNr < 280):
			self.Line_10.append(self.getControl(iLineNr))
			iLineNr = iLineNr + 1
		
		LineNullOrDone 	= True
		ItemCount 		= 0
		LineAParaCount 	= 0
		
		while (LineNullOrDone == True):
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr1.setVisible(False)
				#LineNullOrDone = False
			
			ItemCount = ItemCount + 1
			
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr2.setVisible(False)
				#LineNullOrDone = False
			
			ItemCount = ItemCount + 1
			
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr3.setVisible(False)
				#LineNullOrDone = False
			
			ItemCount = ItemCount + 1
			
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr4.setVisible(False)
				#LineNullOrDone = False
			
			ItemCount = ItemCount + 1
			
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr5.setVisible(False)
				#LineNullOrDone = False
			
			ItemCount = ItemCount + 1
			
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr6.setVisible(False)
				#LineNullOrDone = False
			
			ItemCount = ItemCount + 1
			
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr7.setVisible(False)
				#LineNullOrDone = False
			
			ItemCount = ItemCount + 1
			
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr8.setVisible(False)
				#LineNullOrDone = False
			
			
			ItemCount = ItemCount + 1
			
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr9.setVisible(False)
				#LineNullOrDone = False
			
			ItemCount = ItemCount + 1
			
			try:
				Items[ItemCount]
				
				for LineAParaCount in range(7):
					if(LineAParaCount == 1 or LineAParaCount == 3):
						self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
					if(LineAParaCount == 2):
						self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
					if(LineAParaCount == 4):
						self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
					if(LineAParaCount == 5):
						self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
					if(LineAParaCount == 0 or LineAParaCount == 6):
						self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
			except:
				self.Gr10.setVisible(False)
				#LineNullOrDone = False
			
			LineNullOrDone = False
		
		
		#Navigation
		self.BtnKonfig.setNavigation(self.Line_1[0],self.Line_1[0],self.Line_1[0],self.BtnHinzufuegen)
		self.BtnHinzufuegen.setNavigation(self.Line_1[0],self.Line_1[0],self.BtnKonfig,self.Line_1[0])
		self.Line_1[0].setNavigation(self.Line_10[0],self.Line_2[0],self.BtnKonfig,self.BtnHinzufuegen)
		self.Line_2[0].setNavigation(self.Line_1[0],self.Line_3[0],self.BtnKonfig,self.BtnHinzufuegen)
		self.Line_3[0].setNavigation(self.Line_2[0],self.Line_4[0],self.BtnKonfig,self.BtnHinzufuegen)
		self.Line_4[0].setNavigation(self.Line_3[0],self.Line_5[0],self.BtnKonfig,self.BtnHinzufuegen)
		self.Line_5[0].setNavigation(self.Line_4[0],self.Line_6[0],self.BtnKonfig,self.BtnHinzufuegen)
		self.Line_6[0].setNavigation(self.Line_5[0],self.Line_7[0],self.BtnKonfig,self.BtnHinzufuegen)
		self.Line_7[0].setNavigation(self.Line_6[0],self.Line_8[0],self.BtnKonfig,self.BtnHinzufuegen)
		self.Line_8[0].setNavigation(self.Line_7[0],self.Line_9[0],self.BtnKonfig,self.BtnHinzufuegen)
		self.Line_9[0].setNavigation(self.Line_8[0],self.Line_10[0],self.BtnKonfig,self.BtnHinzufuegen)
		self.Line_10[0].setNavigation(self.Line_9[0],self.Line_1[0],self.BtnKonfig,self.BtnHinzufuegen)
		
			
	def onClick(self, controlID):
	
		def reloadWindowXML(self):
		
			checkFileandRead()
			
			LineNullOrDone 	= True
			ItemCount 		= 0
			LineAParaCount 	= 0
		
			while (LineNullOrDone == True):
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_1[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
					
					self.Gr1.setVisible(True)
				except:
					self.Gr1.setVisible(False)
				#LineNullOrDone = False
			
				ItemCount = ItemCount + 1
			
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_2[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
						
					self.Gr2.setVisible(True)
				except:
					self.Gr2.setVisible(False)
					#LineNullOrDone = False
			
				ItemCount = ItemCount + 1
			
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_3[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
					
					self.Gr3.setVisible(True)
				except:
					self.Gr3.setVisible(False)
					#LineNullOrDone = False
			
				ItemCount = ItemCount + 1
				
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_4[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
					
					self.Gr4.setVisible(True)
				except:
					self.Gr4.setVisible(False)
					#LineNullOrDone = False
			
				ItemCount = ItemCount + 1
			
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_5[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
					
					self.Gr5.setVisible(True)
				except:
					self.Gr5.setVisible(False)
					#LineNullOrDone = False
			
				ItemCount = ItemCount + 1
			
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_6[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
					self.Gr6.setVisible(True)
				except:
					self.Gr6.setVisible(False)
					#LineNullOrDone = False
			
				ItemCount = ItemCount + 1
			
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_7[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
			
					self.Gr7.setVisible(True)
				except:
					self.Gr7.setVisible(False)
					#LineNullOrDone = False
			
				ItemCount = ItemCount + 1
			
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_8[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
					
					self.Gr8.setVisible(True)
				except:
					self.Gr8.setVisible(False)
				#LineNullOrDone = False
			
			
				ItemCount = ItemCount + 1
			
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_9[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
					
					self.Gr9.setVisible(True)
				except:
					self.Gr9.setVisible(False)
					#LineNullOrDone = False
			
				ItemCount = ItemCount + 1
			
				try:
					Items[ItemCount]
				
					for LineAParaCount in range(7):
						if(LineAParaCount == 1 or LineAParaCount == 3):
							self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[0]))
						if(LineAParaCount == 2):
							self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[1]))
						if(LineAParaCount == 4):
							self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[2]))
						if(LineAParaCount == 5):
							self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount]) + self.DictionaryListEndPara[3]))
						if(LineAParaCount == 0 or LineAParaCount == 6):
							self.Line_10[LineAParaCount].setLabel(str(Items[ItemCount].get(self.DictionaryListParameter[LineAParaCount])))
					
					self.Gr10.setVisible(True)
				except:
					self.Gr10.setVisible(False)
					
				LineNullOrDone = False
				
		if (controlID == 201): #Konfigurations Buttons
			ok = xbmcaddon.Addon().openSettings()
			self.close()
			
			#dialog = VMDialog("skin.xml", ADDON_PATH, 'Default', '720p')
			#dialog.doModal()
			#del dialog
		
		if (controlID == 202): #Wert hinzufügen
			dialog = VMDialog("verbrauchsmonitor_2.xml", ADDON_PATH, 'Default', '720p')
			dialog.doModal()
			del dialog
			reloadWindowXML(self)
			
	
		if (controlID == 111): #BUTTONID #RESETFUNKTION 
			ok = xbmcgui.Dialog().yesno(ADDON_NAME, lineyesno)
			#if ok==1:
				#xbmc.executebuiltin("XBMC.ReloadSkin()")
				#resetPointDSANeuschreiben(0) 	#resetfunktion ausfuehren
				#faelligkeitAusfuehren()			#faelligkeit neu berechnen
				#self.Inspektion1.setLabel(str(aktFaelligkeit[0])+" km") #label setzen
				#self.InspektionIGelb.setVisible(False)
				#self.InspektionIRot.setVisible(False)
				#self.InspektionIGruen.setVisible(True) #Gruenes icon anzeigen und Rot und Gelb unsichtbar machen
			
				#xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%("Service",lineZurueck, time, iconInsp))
				
	#def onFocus(self, controlID):
	#	if (controlID == 111):
	#		self.BtnLine_1.setVisible(True) 
	#	else:
	#		self.BtnLine_1.setVisible(False)
			
	
class VMDialog(xbmcgui.WindowXMLDialog):			

	def onInit(self):
		
		self.MAIN = self.getControl(200)
		self.MAIN.setLabel("Verbrauchsmonitor")
		
		self.DescFuellMenge = self.getControl(800)
		self.DescKosten 	= self.getControl(801)
		self.DescSorte 		= self.getControl(802)
		self.DescBetankung 	= self.getControl(803)
		
		self.DescKosten.setVisible(False)
		self.DescSorte.setVisible(False)
		self.DescBetankung.setVisible(False)
		
		#Buttons
		self.BttnFuellMenge = self.getControl(111)
		self.BttnKosten 	= self.getControl(112)
		self.BttnSorte 		= self.getControl(113)
		self.BttnBetankung	= self.getControl(114)
		self.BtnHinzufuegen	= self.getControl(202)
		
		self.LblFuellMenge 	= self.getControl(122)
		self.LblKosten 		= self.getControl(123)
		self.LblSorte		= self.getControl(124)
		self.LblBetankungen = self.getControl(125)
		
		self.LblFuellMenge.setLabel("? L / " + str(TankVolumen) + " L")
		
		#Navigation
		self.BtnHinzufuegen.setNavigation(self.BttnFuellMenge,self.BttnFuellMenge,self.BttnFuellMenge,self.BttnFuellMenge)
		self.BttnFuellMenge.setNavigation(self.BttnBetankung,self.BttnKosten,self.BtnHinzufuegen,self.BtnHinzufuegen)
		self.BttnKosten.setNavigation(self.BttnFuellMenge,self.BttnSorte,self.BtnHinzufuegen,self.BtnHinzufuegen)
		self.BttnSorte.setNavigation(self.BttnKosten,self.BttnBetankung,self.BtnHinzufuegen,self.BtnHinzufuegen)
		self.BttnBetankung.setNavigation(self.BttnSorte,self.BttnFuellMenge,self.BtnHinzufuegen,self.BtnHinzufuegen)
	
	def onClick(self, controlID):
			
		global EingabeKraftstoffmenge
		global EingabeKraftstoffkosten
		global EingabeKraftstoffart
		
		global Betankungsart
		
		global VorKomma
		global NachKomma
			
		#Krafstoffmenge
		if (controlID == 111):
			VorKomma = numerischeEingabe("Krafstoffmenge Vorkommazahl:")
			NachKomma = numerischeEingabe("Krafstoffmenge Nachkommazahl:")
		
			EingabeKraftstoffmenge = str(str(VorKomma) + "." + str(NachKomma))
			self.LblFuellMenge.setLabel(str(EingabeKraftstoffmenge) + " L / " + str(TankVolumen) + " L")
			
		#Gesamtkosten
		if (controlID == 112):
			VorKomma = numerischeEingabe("Kraftstoffkosten Vorkommazahl:")
			NachKomma = numerischeEingabe("Krafstoffkosten Nachkommazahl:")
		
			EingabeKraftstoffkosten = str(str(VorKomma) + "." + str(NachKomma))
			self.LblKosten.setLabel(str(EingabeKraftstoffkosten) + " €")
			
		#Kraftstoffart
		if (controlID == 113):
			NormalBenzin = "S"
			Hochoktan = "S+"
			Diesel = "D"
			PowerDiesel = "D+"
			
			EingabeKraftstoffart = xbmcgui.Dialog().select("Krafstoffart:", [NormalBenzin, Hochoktan, Diesel, PowerDiesel])
			
			if (EingabeKraftstoffart == 0):
				self.LblSorte.setLabel(str(NormalBenzin))
				EingabeKraftstoffart = str(NormalBenzin)
			elif (EingabeKraftstoffart == 1):
				self.LblSorte.setLabel(str(Hochoktan))
				EingabeKraftstoffart = str(Hochoktan)
			elif (EingabeKraftstoffart == 2):
				self.LblSorte.setLabel(str(Diesel))
				EingabeKraftstoffart = str(Diesel)
			elif (EingabeKraftstoffart == 3):
				self.LblSorte.setLabel(str(PowerDiesel))
				EingabeKraftstoffart = str(PowerDiesel)
			elif (EingabeKraftstoffart == -1):
				self.LblSorte.setLabel("-")
				EingabeKraftstoffart = "-"
				
		if (controlID == 114):
			Voll = "Vollbetankung"
			Teil = "Teilbetankung"
			
			Betankungsart = xbmcgui.Dialog().select("Betankungsart:", [Voll, Teil])
			
			if (Betankungsart == 0):
				self.LblBetankungen.setLabel(str(Voll))
			elif (Betankungsart == 1):
				self.LblBetankungen.setLabel(str(Teil))
			elif (Betankungsart == -1):
				if(self.LblBetankungen.getLabel() == str(Voll)):
					Betankungsart = 0
					self.LblBetankungen.setLabel(str(Voll))
				if(self.LblBetankungen.getLabel() == str(Teil)):
					Betankungsart = 1
					self.LblBetankungen.setLabel(str(Teil))
				
			#EingabeKraftstoffart = TastaturEingabe("Krafstoffart:")
			
			#while(len(EingabeKraftstoffart) > 2):
			#	EingabeKraftstoffart = TastaturEingabe("Krafstoffart:")
					
			
		
		if (controlID == 202): #Konfigurations Buttons
		
			if((len(EingabeKraftstoffmenge) != 0)):
				
				try:
					EingabeKraftstoffkosten
				except:
					EingabeKraftstoffkosten = "-"
					
				try:
					EingabeKraftstoffart
				except:
					EingabeKraftstoffart = "-"
				try:
					Betankungsart
				except:
					Betankungsart = 0
					
				WriteNewFile(EingabeKraftstoffmenge, EingabeKraftstoffkosten, EingabeKraftstoffart, Betankungsart)
				
				#Reset
				EingabeKraftstoffmenge = 0
				EingabeKraftstoffkosten = "-"
				EingabeKraftstoffart = "-"
				Betankungsart = 0
				
			self.close()
		
	def onFocus(self, controlID):
		if (controlID == 111):
			self.DescFuellMenge.setVisible(True) 
		else:
			self.DescFuellMenge.setVisible(False)
			
		if (controlID == 112):
			self.DescKosten.setVisible(True) 
		else:
			self.DescKosten.setVisible(False)
			
		if (controlID == 113):
			self.DescSorte.setVisible(True) 
		else:
			self.DescSorte.setVisible(False)
			
		if (controlID == 114):
			self.DescBetankung.setVisible(True) 
		else:
			self.DescBetankung.setVisible(False)

			
if __name__ == '__main__':
	main() #ok
	w = FensterXML("verbrauchsmonitor.xml", ADDON_PATH, 'Default', '720p') #ok
	w.doModal() #ok
	del w #ok