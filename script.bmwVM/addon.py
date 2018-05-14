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
		}for x in ItemList]
		#GEHT!
	xbmcgui.Dialog().ok(ADDON_NAME, str(Items[0].get('Tacho')))
	
	#VM_DB_FILE EXPORTFUNKTION zum HOME verzeichnis
	
	#inhaltSchreiben = open(VM_DB_FILE, 'w')
	#inhaltSchreiben.write(str(Items))
	#inhaltSchreiben.write("\n")
	#inhaltSchreiben.close()
	
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
		
		self.BtnLine_1 	= self.getControl(111)
		self.BtnLine_2 	= self.getControl(217)
		self.BtnLine_3 	= self.getControl(224)
		self.BtnLine_4	= self.getControl(231)
		self.BtnLine_5 	= self.getControl(238)
		self.BtnLine_6	= self.getControl(245)		
		self.BtnLine_7 	= self.getControl(252)
		self.BtnLine_8 	= self.getControl(259)
		self.BtnLine_9 	= self.getControl(266)
		self.BtnLine_10	= self.getControl(273)
		
		
		#Navigation
		self.BtnKonfig.setNavigation(self.BtnLine_1,self.BtnLine_1,self.BtnLine_1,self.BtnHinzufuegen)
		self.BtnHinzufuegen.setNavigation(self.BtnLine_1,self.BtnLine_1,self.BtnKonfig,self.BtnLine_1)
		self.BtnLine_1.setNavigation(self.BtnLine_10,self.BtnLine_2,self.BtnKonfig,self.BtnHinzufuegen)
		self.BtnLine_2.setNavigation(self.BtnLine_1,self.BtnLine_3,self.BtnKonfig,self.BtnHinzufuegen)
		self.BtnLine_3.setNavigation(self.BtnLine_2,self.BtnLine_4,self.BtnKonfig,self.BtnHinzufuegen)
		self.BtnLine_4.setNavigation(self.BtnLine_3,self.BtnLine_5,self.BtnKonfig,self.BtnHinzufuegen)
		self.BtnLine_5.setNavigation(self.BtnLine_4,self.BtnLine_6,self.BtnKonfig,self.BtnHinzufuegen)
		self.BtnLine_6.setNavigation(self.BtnLine_5,self.BtnLine_7,self.BtnKonfig,self.BtnHinzufuegen)
		self.BtnLine_7.setNavigation(self.BtnLine_6,self.BtnLine_8,self.BtnKonfig,self.BtnHinzufuegen)
		self.BtnLine_8.setNavigation(self.BtnLine_7,self.BtnLine_9,self.BtnKonfig,self.BtnHinzufuegen)
		self.BtnLine_9.setNavigation(self.BtnLine_8,self.BtnLine_10,self.BtnKonfig,self.BtnHinzufuegen)
		self.BtnLine_10.setNavigation(self.BtnLine_9,self.BtnLine_1,self.BtnKonfig,self.BtnHinzufuegen)
		
		#Alle Label befüllen
		self.Line_1_Tacho 		= self.getControl(211)
		self.Line_1_Verbrauch 	= self.getControl(212)
		self.Line_1_Distanz		= self.getControl(213)
		self.Line_1_Menge		= self.getControl(214)
		self.Line_1_Kosten		= self.getControl(215)
		self.Line_1_Sorte 		= self.getControl(216)
		
		self.Line_2_Tacho		= self.getControl(218)
		self.Line_2_Verbrauch	= self.getControl(219)
		self.Line_2_Distanz		= self.getControl(220)
		self.Line_2_Menge		= self.getControl(221)
		self.Line_2_Kosten 		= self.getControl(222)
		self.Line_2_Sorte		= self.getControl(223)	
		
		
		self.BtnLine_1.setLabel(str(Items[0].get('Datum')))
		self.Line_1_Tacho.setLabel(str(Items[0].get('Tacho') + " km"))
		self.Line_1_Verbrauch.setLabel(str(Items[0].get('Verbrauch')+ " L/km"))
		self.Line_1_Distanz.setLabel(str(Items[0].get('Distanz')+ " km"))
		self.Line_1_Menge.setLabel(str(Items[0].get('Menge')+ " L / 63 L"))
		self.Line_1_Kosten.setLabel(str(Items[0].get('Kosten')+ " €"))
		self.Line_1_Sorte.setLabel(str(Items[0].get('Sorte')))
		
		self.BtnLine_2.setLabel(str(Items[1].get('Datum')))
		self.Line_2_Tacho.setLabel(str(Items[1].get('Tacho')+ " km"))
		self.Line_2_Verbrauch.setLabel(str(Items[1].get('Verbrauch')+ " L/km"))
		self.Line_2_Distanz.setLabel(str(Items[1].get('Distanz')+ " km"))
		self.Line_2_Menge.setLabel(str(Items[1].get('Menge')+ " L / 63 L"))
		self.Line_2_Kosten.setLabel(str(Items[1].get('Kosten')+ " €"))
		self.Line_2_Sorte.setLabel(str(Items[1].get('Sorte')))
		
		
		
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
				
	#def onFocus(self, controlID):
	#	if (controlID == 111):
	#		self.BtnLine_1.setVisible(True) 
	#	else:
	#		self.BtnLine_1.setVisible(False)
			
	
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