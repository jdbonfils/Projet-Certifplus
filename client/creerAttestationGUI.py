from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
import subprocess
import os
#Permet de recuperer le dossier selectionné
def chooseDir():
	global dirPath, root
	dirPath =  filedialog.askdirectory()
	l = Label( root, text=str(dirPath),anchor="w")
	l.config(font=("Courier", 7))
	l.place(x = 10, y = 290 , width= 400, height=20)

#Recupere les informations et les soumette au serveur frontal 
def valider():
	global dirPath,root,entryNom,entryPrenom,entryIntitule

	#Si le path indiqué n'est pas valide alors on prend le repertoire courant 
	if(not os.path.isdir(dirPath)):
		dirPath = os.getcwd()
	filename = dirPath+"/"+"attestation_"+str(entryNom.get().replace(" ","_"))+".png"
	print("Téléchargement dans : "+filename)
	certPath = os.path.dirname(os.path.realpath(__file__))+"/root_certs_list/ca-root.cert.pem"
	subprocess.run("curl -v -X POST -d 'nom="+str(entryNom.get())+"' -d 'prenom="+str(entryPrenom.get())+"' --output "+ filename +" -d 'intitule="+str(entryIntitule.get())+"' --cacert "+certPath+" https://localhost:9000/creation",shell=True)

	#Si le fichier à bien été récupérer
	if( os.path.isfile(filename) and os.path.getsize(filename) != 0):
		messagebox.showinfo(title="Attestation générée", message="L'attestation a corectement été enregistré dans : "+ dirPath)
		root.destroy()
		return True
	messagebox.showinfo(title="Erreur", message="Une erreur s'est produite")
	root.destroy()
	return False

#Creation de la fenetre avec tkinter

dirPath = os.getcwd()
root = Tk()
root.title("Création Attestation")
root.geometry("500x450")

l = Label( root, text="Saisir les informations :",anchor="w")
l.config(font=("Courier", 12,"bold"))
l.place(x = 5, y = 10 , width= 370, height=40)

l = Label( root, text="Nom :",anchor="w")
l.config(font=("Courier", 9,"bold"))
l.place(x = 20, y = 50 , width= 100, height=20)
entryNom = Entry(root,fg='blue')
entryNom.config(highlightbackground='blue')
entryNom.place(x = 130,y = 50,width= 200,height= 30)

l = Label( root, text="Prenom :",anchor="w")
l.config(font=("Courier", 9,"bold"))
l.place(x = 20, y = 100 , width= 370, height=40)
entryPrenom = Entry(root,fg='blue')
entryPrenom.config(highlightbackground='blue')
entryPrenom.place(x = 130,y = 100,width= 200,height= 30)

l = Label( root, text="Intitulé :",anchor="w")
l.config(font=("Courier", 9,"bold"))
l.place(x = 20, y = 150 , width= 370, height=40)
entryIntitule = Entry(root,fg='blue')
entryIntitule.config(highlightbackground='blue')
entryIntitule.place(x = 130,y = 150,width= 200,height= 30)

l = Label( root, text="Selectionner un dossier dans lequel enrgistrer l'attestation :",anchor="w")
l.config(font=("Courier", 9,"bold"))
l.place(x = 20, y = 200 , width= 500, height=40)
B = Button(root, text ="Choisir repertoire", command =chooseDir)
B.place(x = 50, y = 240, width= 150, height=40)

B = Button(root, text ="Generer l'attestation", command = valider)
B.place(x = 150, y = 350, width= 200, height=50)
root.mainloop()



