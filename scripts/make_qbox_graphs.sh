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

