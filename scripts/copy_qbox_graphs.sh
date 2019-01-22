while [ 1 ]
do
  scp pi@192.168.178.62://var/qboxnextdata/Qbox_15-49-002-081/html/* .
  echo sleep for 5 minutes
  sleep 300
done
