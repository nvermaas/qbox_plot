# qbox_plot
Dit is een Python programma dat QBox text bestanden in grafieken kan weergeven.

De text bestanden kunnen worden gemaakt met het DumpQbx programma. Dat valt buiten de scope van qpbox_plot, die daarvoor:
* https://bitbucket.org/qboxnext/dotnetcore-minimal/src/master/

## Vereisten
Het programma draait zowel op windows als linux. Python en pip moeten wel zijn geinstalleerd. 
Als dat niet het geval is dan kun je hier wat instructies vinden:
* https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation

## Installatie

   pip install http://uilennest.net/repository/qbox_plot-1.0.0.tar.gz --upgrade

## Gebruik

qbox_plot kan gestart worden met parameters op de commandline, maar het kan ook handig zijn om per weergave een 'parameter file' te maken die met de parameter --parfile kan worden geladen.

   qbox_plot --parfile <my_parfile>

## Examples

--- 2018_gas_permaand.par ---  
--filename=data\qbx2018_2421.txt
--output_html=qbx2018_gas.html
--title=Gasverbruik 2018 per maand
--starttime=2018-01-01 00:00
--endtime=2019-01-01 01:00
--interval=month
--y_axis_title=verbruik in m3


<p align="center">
  <img src="https://github.com/nvermaas/qbox_plot/blob/master/images/gas_plot.png"/>
</p>
