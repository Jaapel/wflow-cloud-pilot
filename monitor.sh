sudo -v 

LOG_DIR="logs/"
rm -rf $LOG_DIR
mkdir $LOG_DIR
SAMPLE_RATE_S=1

./run_hydromt.sh large &
PID=$!

echo "attaching to PID: " $PID

while ps -p $PID >/dev/null; do
  sudo iftop -t -s $SAMPLE_RATE_S > $LOG_DIR/$(date --date=now +'%H-%M-%S.%N').log 
done;

echo "exiting harness"
