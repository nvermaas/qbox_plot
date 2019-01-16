# qbox_plot
Dit is een Python programma dat QBox text bestanden in grafieken kan weergeven in een html pagina.

De text bestanden kunnen worden gemaakt met het DumpQbx programma. Dat valt buiten de scope van qpbox_plot, die daarvoor:
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

## Geavanceerd gebruik.
Het is mogelijk om qbox_plot zijn data files van een andere computer te laten lezen, 
bij voorkeur van de Raspberry Pi waar ze gecreeerd worden. 
En het is mogelijk om zowel voor als na de dataverwerking een extern commando uit te voeren, 
bijvoorbeeld een scp commando om die data files te kopieren.

Dit maakt het mogelijk om 'qbox_plot' op een webserver te draaien, 
waarbij hij eerst de QboxNext software de Raspberry Pi opdracht geeft om de data te exporteren naar de gewenste txt bestanden 
alvorens ze te downloaden en te visualiseren.

Dit gaat het vanuit dat de Qserver en DumpQbx applicaties al zijn geinstalleerd op de Raspberry Pi.

<p align="center">
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/qbox_plot_as_frontend.jpg"/>
</p>

'dump_stroom.sh' is een shell script dat de DumpQbx applicatie start voor elk 'kanaal' zodat de txt bestanden worden gegenereerd.
Dit script kan met de hand worden uitgevoerd, maar ook automatisch door 'qbox_plot' met het commando dat met de '--remote_pre_command' wordt meegegeven. (zie de parameter file)

'dump_stroom.sh':
```
cd /var/qboxnextdata/Qbox_15-49-002-081 
./dumpqbx --qbx=/var/qboxnextdata/Qbox_15-49-002-081/15-49-002-081_00000181.qbx --values > 181.txt
./dumpqbx --qbx=/var/qboxnextdata/Qbox_15-49-002-081/15-49-002-081_00000182.qbx --values > 182.txt
./dumpqbx --qbx=/var/qboxnextdata/Qbox_15-49-002-081/15-49-002-081_00000281.qbx --values > 281.txt
./dumpqbx --qbx=/var/qboxnextdata/Qbox_15-49-002-081/15-49-002-081_00000282.qbx --values > 282.txt
```

'stroom.par' (parameter file)
```
--filename=181.txt
--consumption_files=181.txt,182.txt
--redelivery_files=281.txt,282.txt
--remote_host=pi@192.168.?.?
--remote_dir=/var/qboxnextdata/Qbox_15-49-002-081
--remote_pre_command=/var/qboxnextdata/Qbox_15-49-002-081/dump_stroom.sh
--local_dir=data
--legends=verbruik,teruglevering,netto
--output_html=/www/stroom.html
--title=Stroom per uur - Januari 2019
--starttime=2019-01-16 00:00
--endtime=2019-01-17 01:00
--interval=hour
--y_axis_title=verbruik in Wh
```

'reload_qbx.sh'
Dit script start de `qbox_plot' applicatie elke 600 seconden (10 minuten). 
Dit voorbeeld laat zien dat er meerdere presentaties tegelijk kunnen worden gemaakt.

```
source ./env/bin/activate
while [ 1 ]
do
  qbox_plot --parfile stroom.par
  qbox_plot --parfile gas.par
  
  echo sleep for 10 minutes
  sleep 600
done
```

De '--output_html=www/stroom.html' zorgt ervoor dat de html pagina op een plek terecht komt die door een webserver kan worden getoont.
Het resultaat is deze web pagina die om de 10 minuten kan worden ververst. (de pagina ververst niet automatisch, maar met F5 wordt hij opnieuw geladen met nieuwe gegevens)

<p align="center">
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/www_gas_plot.jpg"/>
</p>