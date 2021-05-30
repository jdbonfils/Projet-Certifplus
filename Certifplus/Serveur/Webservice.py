#!/usr/bin/python3
from bottle import route, run, template, request, response, error
from Steganography import *
import subprocess
#import pyqrcode
import qrcode,cv2
import pyqrcode
from pyzbar.pyzbar import decode
import zbarlight
import base64
import os.path
import uuid
from PIL import Image

@route('/creation', method='POST')
def creation_attestation():
	#Creation d'un repertoire temporaire permettant de stocker les différents fichiers
	tmpDir = "temp"+str(uuid.uuid4())[:7]
	subprocess.run("mkdir " + tmpDir, shell=True)

	#Definition des chemins vers les differents elements temporaire
	infosEtuPath = tmpDir+"/infosEtudiant.txt"
	signInfosEtuPath = tmpDir+"/signature.sigsha256"
	labelAttestationPath = tmpDir+"/texte.png"
	combinaisonPath = tmpDir+"/combinaison.png"
	qrcodePath = tmpDir+"/qrcode.png"
	attestationPath = tmpDir+"/attestation.png"
	attestationFinalePath = tmpDir+"/stegano_attestation.png"
	timestampRequestPath = tmpDir+"/timestamp.tsq"
	timestampReplyPath = tmpDir+"/timestamp.tsr"

	try:
		#Recuperation des information saisies
		prenomEtudiant =  request.forms.get('prenom')
		nomEtudiant =  request.forms.get('nom')
		intituleCertif =  request.forms.get('intitule')
		print('nom étudiant: ',nomEtudiant,' prénom étudiant :', prenomEtudiant, ' intitulé de la certification :',intituleCertif)

		#Récupération des données de l'etudiant et ecriture de celles-ci dans un fichier
		infosEtudiant = nomEtudiant+prenomEtudiant+intituleCertif
		file = open(infosEtuPath,"w")
		file.write(infosEtudiant)
		file.close()

		#Signature du bloc d'information avec la clé privée de CertifPlus
		subprocess.run("openssl dgst -sha256 -sign ../CA/intermediate/private/certifplus.key.pem -out "+signInfosEtuPath+" "+infosEtuPath, shell= True)
		
		#Génération du texte à combiner dans l'image finale à l'aide du webservice ChartAPI fournie par Google à l'aide d'une requete réalisée avec l'outil CURL
		texte_ligne= intituleCertif+" délivré|à|"+prenomEtudiant+" "+nomEtudiant
		
		#Generation du label au format png
		subprocess.run("curl -o "+labelAttestationPath+" 'http://chart.apis.google.com/chart' --data-urlencode 'chst=d_text_outline' --data-urlencode 'chld=000000|56|h|FFFFFF|b|%s'"%texte_ligne,shell=True)

		#Redimensionnement avec ImageMagick
		subprocess.run("mogrify -resize 1000x600 "+labelAttestationPath,shell=True)

		#Combinaison des images en l'image finale avec ImageMagick
		subprocess.run("composite -gravity center "+labelAttestationPath+" fond_attestation/fond_attestation.png "+combinaisonPath,shell=True)
		
		#Création du QRCode
		print ("Création du QRcode...\n")
		fichier=open(signInfosEtuPath,'rb')
		data=fichier.read()
		donneesqr=base64.b64encode(data).decode()
		qr=pyqrcode.create(donneesqr)
		qr.png(qrcodePath, scale=2)
		fichier.close()

		#Ajout du QRCode dans l'image finale
		subprocess.run("composite -geometry +1418+934 "+qrcodePath+" "+combinaisonPath+" "+attestationPath, shell=True)

		#concaténation du bloc d'informations et rajout des cararctères pour avoir une longueur de 64 
		while (len(infosEtudiant) < 64):
			infosEtudiant="*" + infosEtudiant

		#Commande pour recuperer un timestamp reply de la part du TimeStamp authority de certiplus
		subprocess.run("curl -v -F 'file=@"+infosEtuPath+"' --output "+timestampReplyPath+"  http://0.0.0.0:8060/genTimeStamp",shell=True)
		#Commande pour recuperer un timestamp reply de la part de freetsa
		#cmd = subprocess.run("openssl ts -query -data "+infosEtuPath+" -no_nonce -sha512 -cert -out "+timestampRequestPath, shell=True)
		#cmd = subprocess.run('curl -H "Content-Type: application/timestamp-query" '+"--data-binary '@"+timestampRequestPath+"' https://freetsa.org/tsr > "+timestampReplyPath,shell=True)

		#On recupere les données du timestamp
		fichier=open(timestampReplyPath,'rb')
		timestamp=fichier.read()
		fichier.close()

		#On ajoute les donnees du timestamp au données de l'etudiant
		msg=base64.b64encode(timestamp)
		infosEtudiant+=msg.decode('utf-8')
		imageAtt = Image.open(attestationPath)
		#On cache ces donnees par steganography dans l'image
		cacher(imageAtt,infosEtudiant)
		imageAtt.save(attestationFinalePath)
		imageAtt.close()

		#On recupere les donnes de l'image final
		response.set_header('Content-type', 'image/png') 
		descripFichier=open(attestationFinalePath,'rb')
		attestation=descripFichier.read()
		descripFichier.close()

	#Si une erreur survient on supprime le dossier temporaire créé et on retourne None
	except Exception:
		print("Erreur durant la generation de lattestation")
		subprocess.run("rm -r " + tmpDir, shell=True)
		return None

	#Supression du dossier temporaire et des éléments à l'interieur
	subprocess.run("rm -r " + tmpDir, shell=True)

	return attestation 
	
#enleverBourrage sépare les infos de la partie bourage puis stock les infos dans un fichier
def enleverBourrage(ch):
	infosEtu=""
	for x in range(0,len(ch)):
		if ch[x]!='*':
			infosEtu+=ch[x]
	return infosEtu


#Vérification du timestamp
def Timestamp_Verify(NomFichier, timestamp="timestamp.tsr"):
	#Commande pour verifier le TSA reply généré par freeTSA (nécessite la cle publique le certificat de free tsa)
	#output = subprocess.Popen("openssl ts -verify -data %s -in %s -CAfile TSA/freetsa.pem -untrusted TSA/freetsa.crt"%(NomFichier,timestamp), shell=True,stdout=subprocess.PIPE).communicate()[0].decode()
	#Verification du timestamp grace au certificat du TSA de Certifplus et de la cle du CA root
	output = subprocess.Popen("openssl ts -verify -config ../CA/ca-root.cnf -data "+NomFichier+" -in "+timestamp+" -CAfile ../CA/certs/ca-root.cert.pem -untrusted ../CA/TSA/tsa.crt", shell=True,stdout=subprocess.PIPE).communicate()[0].decode()
	print(output)
	if("Verification: OK" in output):
		return 1
	return 0
		
#Vérification de la signature
def Signature_Verify(InfoFichier,signature):
	#cmd = subprocess.run('openssl x509 -pubkey -noout -in ../CA/intermediate/certs/certifplus.cert.pem -out test.pem' , shell=True)
	output = subprocess.Popen("openssl dgst -sha256 -verify ../CA/intermediate/certifplus.pem -signature "+signature+" "+InfoFichier, shell=True,stdout=subprocess.PIPE).communicate()[0].decode()
	if ("OK" in output):
		return 1
	return  0

@route('/verification', method='POST')
def vérification_attestation():

	#Creation d'un repertoire temporaire permettant de stocker les différents fichiers
	tmpDir = "temp"+str(uuid.uuid4())[:7]
	subprocess.run("mkdir " + tmpDir, shell=True)

	#Paths dans lequel on stockera les elements temporaires
	attestationPath = tmpDir+'/attestation_a_verifier.png'
	qrCodeImgPath = tmpDir+"/qrcoderecupere.png"
	signatureFilePath=tmpDir+"/Signqrcode"
	timeStampReply = tmpDir+"/timestamp.tsr"
	infosEtudiantPath = tmpDir+"/verifInfosEtu.txt"

	try:
		#On l'attestation envoye par l'utilisateur
		contenu_image = request.files.get('image')
		contenu_image.save(attestationPath,overwrite=True)

		print("Extraction des informations...")
		#Récupération du contenu QRCode 
		imageAtt = Image.open(attestationPath)
		qrImage = imageAtt.crop((1418,934,1418+210,934+210))
		qrImage.save(qrCodeImgPath, "PNG")
		image=Image.open(qrCodeImgPath)
		d = decode(image)
		print(d[0].data.decode('ascii'))
		#Ecriture du contenu du qrcode (la signature) dans un fichier
		file=open(signatureFilePath,'wb')
		file.write(base64.b64decode(d[0].data.decode('ascii')))
		file.close()

		#Recuperation des infos de l'etudiant + du timestamp
		infosEtuRetrouve = recuperer(imageAtt, 15600)
		imageAtt.close()
		
		#Recuperation des informations de l'étudiant
		#les 64 premiers caractères retrouvés contiennent les informations de l'etudiant + du bourrage
		infosEtudiant = enleverBourrage(infosEtuRetrouve[:64])
		file=open(infosEtudiantPath,"w")
		file.write(infosEtudiant)
		file.close()

		#Recuperation du timestamp
		timestamp = infosEtuRetrouve[64:] 
		timestamp=bytes(timestamp,"utf-8")
		timestamp=base64.b64decode(timestamp)
		file=open(timeStampReply,"wb")
		file.write(timestamp)
		file.close()

		#Vérification du timestamp
		print("Vérification du timestamp...")
		v1=Timestamp_Verify(infosEtudiantPath,timeStampReply)
		
		#Verification de la signature
		print("Vérification de la signature...")
		v2=Signature_Verify(infosEtudiantPath,signatureFilePath)

	except Exception:
		v1,v2 = 0,0
	finally:
		#Supression du dossier temporaire
		subprocess.run("rm -r " + tmpDir, shell=True)
		response.set_header('Content-type', 'text/plain')
		
		#Si la signature et le timestamp sont corrects alors l'attestation est verifiee
		if(v1 and v2):
			print("Yeah ! Attestation certifiée!")
			return "OK : Attestation correcte "

		print("Oops ! Attestation non certifiée!")
		return "ERREUR : Attestation incorrecte "

@error(404)
def error404(error):
    return 'Erreur - /creation : Pour créer une attestation    /verification : Verifier une attestation'

if __name__ == '__main__':
	run(host='0.0.0.0',port=8080,debug=True)

