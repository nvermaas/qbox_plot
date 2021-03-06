# qbox_plot
Dit is een Python programma dat qbx bestanden in grafieken kan weergeven in een html pagina.

## Vereisten
Het programma draait zowel op windows als linux. Python en pip moeten wel zijn geinstalleerd. 
Als dat niet het geval is dan kun je hier wat instructies vinden:
* https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation

## Installatie

   ``pip install http://uilennest.net/repository/qbox_plot-1.2.0.tar.gz --upgrade``

## Gebruik
Zorg dat de qbx bestanden lokaal beschikbaar zijn. In de voorbeelden staan ze in een ``data`` directory.
Een enkele grafiek kan elk gewenst qbx bestand laten zien als 'bar' diagram of 'scatter' (lijn) diagram.

De gecombineerde grafiek gaat er vanuit dat er 2 ``consumption_files`` en 2 ``redelivery_files`` zijn, 
dat zijn respectievelijk de hoog/laag verbruik en hoog/laag teruglevering bestanden die oorspronkelijk door 'qurrent' de kanalen 181, 182, 281, 282 werden genoemd.
In het voorbeeld heb ik die 'kanalen' in de bestandsnaam opgenomen, maar dat is niet verplicht.

qbox_plot kan gestart worden met parameters op de commandline, maar het kan ook handig zijn om per weergave een 'parameter file' te maken die met de parameter --parfile kan worden geladen.

  `qbox_plot --parfile <my_parfile>`

Voor 'help' over welke parameters er beschikbaar zijn:

  `qbox_plot --h`

## Voorbeelden

### Laagverbruik (kanaal 181) op 11 jan 2019
  `qbox_plot --filename data\181.qbx --interval hour --starttime "2019-01-11 00:00" --endtime "2019-01-12 00:00" --output_html=stroom181.html --title "nachtstroom 12 jan 2019"`
`

### Hoogverbruik (kanaal 182) op 11 jan 2019
  `qbox_plot --filename data\182.qbx --interval hour --starttime "2019-01-11 00:00" --endtime "2019-01-12 00:00" --output_html=stroom182.html --title "dagstroom 12 jan 2019"`


### Enkele staafdiagram (gasverbruik) 
parameter file: `2018_gas_per_maand.par`
 
```
--filename=2421.qbx
--local_dir=data
--output_html=qbx2018_gas.html
--title=Gasverbruik 2018 per maand
--starttime=2018-01-01 00:00
--endtime=2019-01-01 01:00
--interval=month
--y_axis_title=verbruik in m
--type=bar
```
  `qbox_plot --parfile 2018_gas_per_maand.par`
  
<p align="center">
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/gas_plot.png"/>
</p>

### Gecombineerde electriciteit

parameter file: `2018_dec_stroom_per_dag.par`
```
--consumption_files=181.qbx,281.qbx
--redelivery_files=182.qbx,282.qbx
--local_dir=data
--output_html=qbx2018_stroom.html
--title=Stroom December 2018 - per dag
--starttime=2018-12-01 00:00
--endtime=2019-01-07 01:00
--interval=day
--y_axis_title=verbruik in kWh
```

  `qbox_plot --parfile 2018_dec_stroom_per_dag.par`

<p align="center">
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/stroom_plot.png"/>
</p>

## Using qbox_plot as 'Live Energy Monitor' 

qbox_plot can be used as a frontend monitor by letting it generate the html pages of the
current gas and electricity usage on a directory that can be served by a webserver.

This tutorial assumes that the Qserver and DumpQbx applicaties are already installed and working on the Raspberry Pi.
We are working towards the following situation:

<p align="center">
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/qbox_plot_as_frontend_basic.jpg"/>
</p>

   
### Install qbox_plot
It is advisable to use virtualenv to create a clean python environment that does not mix with the existing environment.
 
 ``sudo pip install virtualenv``
 
 ``virtualenv env``
 
 ``source env/bin/activate``
 
 ``pip install http://uilennest.net/repository/qbox_plot-1.0.0.tar.gz --upgrade``

Test if the qbox_plot installation has worked by typing: ``qbox_plot --version``. You should see output like this:

--- qbx_plot.py - version 1.0.0 - 16 jan 2019 ---
Copyright (C) 2019 - Nico Vermaas. This program comes with ABSOLUTELY NO WARRANTY;

### Creating the graphs
Create the following script in the data directory, it will execute the dump script and qbox_plot every 5 minutes to create 4 different presentations.

> make_qbox_graphs.sh
```
#!/bin/bash
source env/bin/activate
while [ 1 ]
do
  ./dump_all.sh	
  qbox_plot --parfile stroom_per_hour_today.par
  qbox_plot --parfile gas_per_hour_today.par
  qbox_plot --parfile stroom_this_month.par
  qbox_plot --parfile gas_this_month.par
  echo sleep for 5 minutes
  sleep 300
done
```

Make the script executable:
  ``chmod +x make_qbox_graphs.sh``
  
# The presentation files
Create the following parameter files for the 4 different presentations:
  First create the output directory: 
  
  ``cd html``

  Create the following files:
  
>  gas_per_hour_today.par
```  
--filename=2421.qbx
--output_html=html/gas.html
--title=Gas per uur - Vandaag
--mode=today
--interval=hour
--y_axis_title=verbruik in m3
```
  
> gas_this_month.par
```
--filename=2421.qbx
--output_html=html/gas_month.html
--title=Gas per dag - Deze Maand
--mode=this_month
--interval=day
--y_axis_title=verbruik in m3
```

> stroom_per_hour_today.par
```
--consumption_files=181.qbx,182.qbx
--redelivery_files=281.qbx,282.qbx
--mode=today
--legends=verbruik,teruglevering,netto
--output_html=html/stroom.html
--title=Stroom per uur - Vandaag
--interval=hour
--y_axis_title=verbruik in Wh
```

> stroom_this_month.par
```
--consumption_files=181.qbx,182.qbx
--redelivery_files=281.qbx,282.qbx
--mode=this_month
--legends=verbruik,teruglevering,netto
--output_html=html/stroom_month.html
--title=Stroom per dag - Deze Maand
--interval=day
--y_axis_title=verbruik in Wh
```

Create the main html file that contains the presentation:
> qbox.html

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="refresh" content="300">
    <meta charset="UTF-8">
    <title>Qbox - Live Energy Monitor</title>
</head>
<body>
<table>
<tr>
    <td>
    <div>
        <iframe src="http://localhost/gas.html" name="targetframe" allowTransparency="true" scrolling="no" frameborder="0" width="700" height="400"></iframe>
    </div>
    </td>
    <td>
    <div>
        <iframe src="http://localhost/stroom.html" name="targetframe" allowTransparency="true" scrolling="no" frameborder="0" width="700" height="400"></iframe>
    </div>
    </td>
</tr>
<tr>
    <td>
    <div>
        <iframe src="http://localhost/gas_month.html" name="Gas deze maand" allowTransparency="true" scrolling="no" frameborder="0" width="700" height="400"></iframe>
    </div>
    </td>
    <td>

    <div>
        <iframe src="http://localhost/stroom_month.html" name="Stroom deze maand" allowTransparency="true" scrolling="no" frameborder="0" width="700" height="400"></iframe>
    </div>
    </td>
</tr>
</table>
</body>
</html>
```

Your data directory should now look like this (the number of txt and qbx files may differ)
<p align="center">
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/pi_qbox_dir.png"/>
</p>


## automation
Running the script ``make_qbox_graphs.sh`` should now produce all the graphs as webpages.
To automate that process and keep it running in the background you should start that script with the following command.

  ``nohup ./make_qbox_graphs.sh &``
    
    
## showing it on a webserver
Since port 80 is already reserved for the Qserver, we need to define a new port of this website. Like 81.

Change that (as root) in the nginx configuration file:
  ''pico /etc/nginx/sites-enabled/default''

Add the following server section:
```
server {
        listen 81;
        listen [::]:81;

        server_name example.com;

        root /var/www/html;
        index index.html;
}
```

Restart nginx:
  ``service nginx restart``

create a symbolic link from the qbox html page to the /var/www/html directory.
  
  ``cd /var/www/html``

  ``ln -s /var/qboxnextdata/Qbox_15-49-002-081/html/qbox.html qbox.html``
  
  ``ln -s /var/qboxnextdata/Qbox_15-49-002-081/html/stroom.html stroom.html``
  
  ``ln -s /var/qboxnextdata/Qbox_15-49-002-081/html/gas.html gas.html``
  
  ``ln -s /var/qboxnextdata/Qbox_15-49-002-081/html/stroom_month.html stroom_month.html``
  
  ``ln -s /var/qboxnextdata/Qbox_15-49-002-081/html/gas_month.html gas_month.html``
  
Now the following URL to the local Raspberry Pi on port 81 shows the energy data every 5 minutes automatically:

> http://192.168.178.62:81/qbox.html
  
<p align="center">
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/qbox_gas_stroom.png"/>
</p>

## Changelist
### versie 1.2.0 (6 feb 2019)
  * qbox_plot kan nu behalve txt bestanden ook qbx bestanden gebruiken. 
    Die zijn een stuk sneller en de DumpQbx applicatie is niet meer nodig. 
    Vervang in de parameter files simpelweg de extentie .txt door .qbx.
    (de txt bestanden kunnen ook nog steeds gebruikt worden).
  * Er wordt nu ook een 'qbox_read' programma mee geinstalleerd dat gebruikt kan worden voor queries op de binaire qbx bestanden.
    type 'qbox_read -h' voor meer informatie.   
  
### versie 1.1.0 (19 jan 2019)
``pip install http://uilennest.net/repository/qbox_plot-1.1.0.tar.gz --upgrade``
  * Link met qservice backend kan nu gemaakt worden door de '--qbackend' parameter te zetten. 
    Hiervoor moet ook de '--qbox_sn' parameter worden gezet (type 'qbox_plot -h' voor meer details)
  * '-- presentation' parameter om te kiezen tussen 'single' en 'electricity' plot
  
### versie 1.0.0 (16 jan 2019)
``pip install http://uilennest.net/repository/qbox_plot-1.0.0.tar.gz --upgrade``