#!/bin/bash
#dir="CA/intermediate/"
#echo "En attente d'une connexion sur le port 9000..."
#socat openssl-listen:9000,fork,cert=$dir/serveur_frontal/bundle_serveur.pem,cafile=$dir/certs/intermediate.cert.pem,verify=0 tcp:127.0.0.1:8080
#!/bin/bash
scriptDIR="$(cd "$(dirname "$0")" && pwd)"
dir="${scriptDIR}/CA/intermediate/"
echo "En attente d'une connexion sur le port 9000..."
socat openssl-listen:9000,fork,cert=$dir/serveur_frontal/bundle_serveur.pem,cafile=$dir/certs/intermediate.cert.pem,verify=0 tcp:127.0.0.1:8080
