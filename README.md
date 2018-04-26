#BrazilProject            

For the programe to start automaticly, you need to add the line : "sudo python3 \$WHEREYOUINSTALLEDTHECODE\BrazilProject\main.py config" at the end of the ".bashrc" situated in the user directory that automaticly is being log in at boot (by default "pi").

The programe is made to work in tendem with the Witty Pi, when installing the Witty Pi ("wget http://www.uugear.com/repo/WittyPi2/installWittyPi.sh" and "sudo sh installWittyPi.sh") the installer configure the i2c line by itself so no need to try to enable them.
