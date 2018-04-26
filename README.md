 ,ggggggggggg,                                                  ,ggggggggggg,                                                  
dP"""88""""""Y8,                                         ,dPYb,dP"""88""""""Y8,                                           I8   
Yb,  88      `8b                                         IP'`YbYb,  88      `8b                                           I8   
 `"  88      ,8P                                    gg   I8  8I `"  88      ,8P                   gg                   88888888
     88aaaad8P"                                     ""   I8  8'     88aaaad8P"                    ""                      I8   
     88""""Y8ba   ,gggggg,    ,gggg,gg     ,gggg,   gg   I8 dP      88""""",gggggg,    ,ggggg,    gg   ,ggg,     ,gggg,   I8   
     88      `8b  dP""""8I   dP"  "Y8I    d8"  Yb   88   I8dP       88     dP""""8I   dP"  "Y8ggg 8I  i8" "8i   dP"  "Yb  I8   
     88      ,8P ,8'    8I  i8'    ,8I   dP    dP   88   I8P        88    ,8'    8I  i8'    ,8I  ,8I  I8, ,8I  i8'       ,I8,  
     88_____,d8',dP     Y8,,d8,   ,d8b,,dP  ,adP' _,88,_,d8b,_      88   ,dP     Y8,,d8,   ,d8'_,d8I  `YbadP' ,d8,_    _,d88b, 
    88888888P"  8P      `Y8P"Y8888P"`Y88"   ""Y8d88P""Y88P'"Y88     88   8P      `Y8P"Y8888P"888P"888888P"Y888P""Y8888PP8P""Y8 
                                             ,d8I'                                              ,d8I'                          
                                           ,dP'8I                                             ,dP'8I                           
                                          ,8"  8I                                            ,8"  8I                           
                                          I8   8I                                            I8   8I                           
                                          `8, ,8I                                            `8, ,8I                           
                                           `Y8P"                                              `Y8P"                            

For the programe to start automaticly, you need to add the line : "sudo python3 \$WHEREYOUINSTALLEDTHECODE\BresilProject\main.py config" at the end of the ".bashrc" situated in the user directory that automaticly is being log in at boot (by default "pi").

The programe is made to work in tendem with the Witty Pi, when installing the Witty Pi ("wget http://www.uugear.com/repo/WittyPi2/installWittyPi.sh" and "sudo sh installWittyPi.sh") the installer configure the i2c line by itself so no need to try to enable them.
