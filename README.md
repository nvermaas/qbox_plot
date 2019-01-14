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

### Enkele grafiek
 
parameter file: `2018_gas_per_maand.par`
 
```
--filename=data\qbx2018_2421.txt
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
--consumption_files=data\qbx2018_181.txt,data\qbx2018_182.txt
--redelivery_files=data\qbx2018_182.txt,data\qbx2018_282.txt
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
