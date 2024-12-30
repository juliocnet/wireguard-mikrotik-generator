Con este script puedes crear los clientes o Peers Wireguard que necesites agregar a tu servidor (opción 2: solo peers). 
Si no tienes configurado tu servidor escoge la opción 1 que incluye la configuración de un servidor Wireguard para Mikrotik.

Salvo la dirección ip pública o FQDN, que es obligado escribir, todos los demás valores puedes dejarlo por defecto (dando enter) y se aplica una configuración que he preparado.

Entre los resultados del script se genera un código QR por cada uno de los peers creados, así es más facil de configurar el cliente en un móvil.
Asegurate de tener instalada la librería "qrcode" (pip install qrcode)

Al terminar de ejecutar el script se te habrá creado un directorio nuevo (wireguard-configs) y dentro tendrás:
- Un directorio (qrcodes) con las fotos de todos los clientes que decidiste crear.
- Un fichero (mikrotik_commands.rsc) con los comandos necesarios para la configuración en la parte del Mikrotik. (en caso de no tener ningún servidor te lo crea, incluyendo configuraciones como la dirección IP y las reglas del firewall.
- Tantos ficheros (peer_xx.conf) como clientes hayas decidido crear.

Espero que te ayude a ganar tiempo creando este tipo de configuraciones. 
