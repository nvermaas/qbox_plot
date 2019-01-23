# qbox_plot
Dit is een Python programma dat QBox text bestanden in grafieken kan weergeven in een html pagina.

De text bestanden kunnen worden gemaakt met het DumpQbx programma. Dat valt buiten de scope van qpbox_plot, zie daarvoor:
* https://bitbucket.org/qboxnext/dotnetcore-minimal/src/master/

## Vereisten
Het programma draait zowel op windows als linux. Python en pip moeten wel zijn geinstalleerd. 
Als dat niet het geval is dan kun je hier wat instructies vinden:
* https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation

## Installatie

   ``pip install http://uilennest.net/repository/qbox_plot-1.0.0.tar.gz --upgrade``

## Gebruik
Zorg dat de qbox text bestanden lokaal beschikbaar zijn. In de voorbeelden staan ze in een ``data`` directory.
Een enkele grafiek kan elk gewenst qbox text bestand laten zien als 'bar' diagram of 'scatter' (lijn) diagram.

De gecombineerde grafiek gaat er vanuit dat er 2 ``consumption_files`` en 2 ``redelivery_files`` zijn, 
dat zijn respectievelijk de hoog/laag verbruik en hoog/laag teruglevering bestanden die oorspronkelijk door 'qurrent' de kanalen 181, 182, 281, 282 werden genoemd.
In het voorbeeld heb ik die 'kanalen' in de bestandsnaam opgenomen, maar dat is niet verplicht.

qbox_plot kan gestart worden met parameters op de commandline, maar het kan ook handig zijn om per weergave een 'parameter file' te maken die met de parameter --parfile kan worden geladen.

  `qbox_plot --parfile <my_parfile>`

Voor 'help' over welke parameters er beschikbaar zijn:

  `qbox_plot --h`

## Voorbeelden

### Nachtverbruik (kanaal 181) op 11 jan 2019
  `qbox_plot --filename data\181.txt --interval hour --starttime "2019-01-11 00:00" --endtime "2019-01-12 00:00" --output_html=stroom181.html --title "nachtstroom 12 jan 2019"`
`

### Dagverbruik (kanaal 182) op 11 jan 2019
  `qbox_plot --filename data\182.txt --interval hour --starttime "2019-01-11 00:00" --endtime "2019-01-12 00:00" --output_html=stroom182.html --title "dagstroom 12 jan 2019"`


### Enkele staafdiagram (gasverbruik) 
parameter file: `2018_gas_per_maand.par`
 
```
--filename=qbx2018_2421.txt
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
--consumption_files=qbx2018_181.txt,qbx2018_182.txt
--redelivery_files=qbx2018_182.txt,qbx2018_282.txt
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

### Dumping the data.

Make sure that you have DumpQbx installed. See the Qserver instructions for details, but it involves the following steps:
  - go to your ``local dotnetcore-minimal\QboxNext.DumpQbx`` directory
  - compile the code for linux with the following command: ``dotnet publish -c Release -r linux-arm``
  - copy the contents of ``dotnetcore-minimal\QboxNext.DumpQbx\bin\Release\netcoreapp2.1\linux-arm\publish`` to the ``/home/pi/DumpQbx`` directory on the Pi.
  
Go to your data directory (you will have a different serialnumber): 
  ``cd /var/qboxnextdata/<Qbox_15-49-002-081/``
 
And make a symbolic link to the DumpQbx application:
  ``ln -s /home/pi/DumpQbx/QboxNext.DumpQbx dumpqbx``
  
Create the 'dump_all.sh' script that will execute the conversion. It should have the following contents (but with your own serialnumber)

> dump_all.sh
```  
  cd /var/qboxnextdata/Qbox_15-49-002-081
  ./dumpqbx --qbx=/var/qboxnextdata/Qbox_15-49-002-081/15-49-002-081_00000181.qbx --values > 181.txt
  ./dumpqbx --qbx=/var/qboxnextdata/Qbox_15-49-002-081/15-49-002-081_00000182.qbx --values > 182.txt
  ./dumpqbx --qbx=/var/qboxnextdata/Qbox_15-49-002-081/15-49-002-081_00000281.qbx --values > 281.txt
  ./dumpqbx --qbx=/var/qboxnextdata/Qbox_15-49-002-081/15-49-002-081_00000282.qbx --values > 282.txt
  ./dumpqbx --qbx=/var/qboxnextdata/Qbox_15-49-002-081/15-49-002-081_00002421.qbx --values > 2421.txt
```
   
Make it executable:
   ``chmod +x dump_all.sh``
  
Test the script by executing and check if the txt files are created.
   ``./dump_all.sh``
   
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
--filename=2421.txt
--output_html=html/gas.html
--title=Gas per uur - Vandaag
--mode=today
--interval=hour
--y_axis_title=verbruik in m3
```
  
> gas_this_month.par
```
--filename=2421.txt
--output_html=html/gas_month.html
--title=Gas per dag - Deze Maand
--mode=this_month
--interval=day
--y_axis_title=verbruik in m3
```

> stroom_per_hour_today.par
```
--consumption_files=181.txt,182.txt
--redelivery_files=281.txt,282.txt
--mode=today
--legends=verbruik,teruglevering,netto
--output_html=html/stroom.html
--title=Stroom per uur - Vandaag
--interval=hour
--y_axis_title=verbruik in Wh
```

> stroom_this_month.par
```
--consumption_files=181.txt,182.txt
--redelivery_files=281.txt,282.txt
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
        <iframe src="http://localhost/qbox/gas.html" name="targetframe" allowTransparency="true" scrolling="no" frameborder="0" width="700" height="400"></iframe>
    </div>
    </td>
    <td>
    <div>
        <iframe src="http://localhost/qbox/stroom.html" name="targetframe" allowTransparency="true" scrolling="no" frameborder="0" width="700" height="400"></iframe>
    </div>
    </td>
</tr>
<tr>
    <td>
    <div>
        <iframe src="http://localhost/qbox/gas_month.html" name="Gas deze maand" allowTransparency="true" scrolling="no" frameborder="0" width="700" height="400"></iframe>
    </div>
    </td>
    <td>

    <div>
        <iframe src="http://localhost/qbox/stroom_month.html" name="Stroom deze maand" allowTransparency="true" scrolling="no" frameborder="0" width="700" height="400"></iframe>
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
  
Now the following URL to the local Raspberry Pi on port 81 shows the energy data every 5 minutes automatically:

> http://192.168.178.62:81/qbox.html
  
<p align="center">
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/qbox_gas_stroom.png"/>
</p>

## Changelist
### versie 1.1.0 (19 jan 2019)
``pip install http://uilennest.net/repository/qbox_plot-1.1.0.tar.gz --upgrade``
  * Link met qservice backend kan nu gemaakt worden door de '--qbackend' parameter te zetten. 
    Hiervoor moet ook de '--qbox_sn' parameter worden gezet (type 'qbox_plot -h' voor meer details)
  * '-- presentation' parameter om te kiezen tussen 'single' en 'electricity' plot
  
### versie 1.0.0 (16 jan 2019)
``pip install http://uilennest.net/repository/qbox_plot-1.0.0.tar.gz --upgrade``