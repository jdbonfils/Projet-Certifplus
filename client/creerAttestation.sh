#/bin/bash
scriptDIR="$(cd "$(dirname "$0")" && pwd)"
certPath="${scriptDIR}/root_certs_list/ca-root.cert.pem"

#On traite les parametres saisis
while getopts p:n:i:o: flag
do
    case "${flag}" in
        p) prenom=${OPTARG};;
        n) nom=${OPTARG};;
        i) intitule=${OPTARG};;
	o) output=${OPTARG};;
    esac
done

#Si les parametre en entré du programme n'ont pas été saisi, alors on demande à l'utilisateur de les saisir
if [ -z ${prenom} ]; then read -p 'Sasir le prenom: ' prenom ;fi
if [ -z ${nom} ]; then read -p 'Sasir le nom: ' nom ;fi
if [ -z ${intitule} ]; then read -p 'Sasir l intitule: ' intitule ;fi
filename="/attestation_${nom// /_}.png"
if [ -z ${output} ]; then output=$scriptDIR$filename ;else  output="$(cd "$(dirname "$output")"; pwd)/$(basename "$output")"$filename ;fi

echo "Envoie de la requete..."
curl -v -X POST -d "nom=$nom" -d "prenom=$prenom" --output $output -d "intitule=$intitule" --cacert $certPath https://localhost:9000/creation

if [ -s $output ]; then
	echo "Attestation recue "$output;
else 
	echo "Echec de la reception de l'attestation";
fi
	
