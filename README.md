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
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/electra_plot.png"/>
</p>
