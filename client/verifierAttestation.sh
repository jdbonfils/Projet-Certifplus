#/bin/bash
scriptDIR="$(cd "$(dirname "$0")" && pwd)"
certPath="${scriptDIR}/root_certs_list/ca-root.cert.pem"

#On verifie que l'utilisateur a bien saisie une option
if [ $# -eq 0 ]
then
    echo "Veuillez indiquer le chemin de l'attessation"
    exit 1
fi

#Si le fichier passe en argument existe
if [[ -f $1 ]]
then
    echo "Envoie de la requete de verification..."
    curl -F "image=@$1" --cacert $certPath https://localhost:9000/verification
else
    echo "Le fichier n'existe pas"
fi



