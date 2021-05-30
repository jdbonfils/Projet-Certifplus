#!/usr/bin/python3
import subprocess
import base64
import os.path
import uuid
from bottle import route, run, template, request, response



@route('/genTimeStamp', method='POST')
def create_time_stamp():

	#Recuperation du fichier à timestamper
	fileToTS =  request.files.get('file')
	fileToTS.save("out/fileTMP")
	print("Génération d'un timestamp pour "+fileToTS.filename)
	
	#Generation du timestamp
	subprocess.run("openssl ts -query -config ../ca-root.cnf -data out/fileTMP -out out/request.tsq -sha384",shell=True)
	subprocess.run("openssl ts -reply -passin pass:Certiplus-TSA-CA87000 -config ../ca-root.cnf -queryfile out/request.tsq -out out/response.tsr",shell=True)
	
	response.set_header('Content-type', 'application/timestamp-query') 
	descripteur_fichier=open("out/response.tsr",'rb')
	tsaResp=descripteur_fichier.read()
	descripteur_fichier.close()

	#On supprime les fichiers TMP
	subprocess.run("rm out/*",shell=True)

	return tsaResp

if __name__ == '__main__':
	print("Time Stamp Webservice : En attente d'une connexion")
	run(host='0.0.0.0',port=8060,debug=True)


