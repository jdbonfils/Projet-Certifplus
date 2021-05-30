from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
import subprocess
import os

def choisirFic():
	global rslt
	#On affiche une boite de dialogue permettant de selectionner un fichier
	filePath = filedialog.askopenfilename()
	if(os.path.isfile(filePath)):
		#On recupere le chemin du certificat pour la communication SSL
		certPath = os.path.dirname(os.path.realpath(__file__))+"/root_certs_list/ca-root.cert.pem"
		#On envoie l'attestation a verifier via le serveur frontal et on recupere la reponse
		output = subprocess.Popen("curl -F 'image=@"+filePath+"' --cacert "+certPath+" https://localhost:9000/verification", shell=True,stdout=subprocess.PIPE).communicate()[0].decode()
		rslt = Label( root, text=output,anchor="w")
		rslt.config(font=("Courier", 12,"bold"))
		rslt.place(x = 50, y = 150 , width= 370, height=40)
	else:
		rslt = Label( root, text="Le fichier n'existe pas",anchor="w")
		rslt.config(font=("Courier", 12,"bold"))
		rslt.place(x = 50, y = 150 , width= 370, height=40)


root = Tk()
root.title("Verifier une attestation")
root.geometry("450x250")

l = Label( root, text="Telecharger une attestation à verifier",anchor="w")
l.config(font=("Courier", 12,"bold"))
l.place(x = 10, y = 10 , width= 400, height=40)

B = Button(root, text ="Choisir un fichier", command =choisirFic)
B.place(x = 50, y = 70, width= 150, height=40)

root.mainloop()


