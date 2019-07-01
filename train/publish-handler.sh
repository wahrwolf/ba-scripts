#!/bin/bash
action=$1
corpus=$2
export TIME="$(date --iso-8601=hours)"

echo "Running handler on [$action] for $corpus"
echo "========================"
echo -n 'Creating logfile...'
tmpfile=$(mktemp)
echo "using ${tmpfile}!"

set +o errexit # {{{
if [ ! -f "$CONFIG_DIR/$corpus/$action.config" ]
then
	echo "Config '$CONFIG_DIR/$corpus/$action.config' not found!"
	echo "Updating files..."
	echo "------------------------"
	"$SCRIPT_DIR/train/update.sh" "$CONFIG_DIR"
	echo  "Downloading new corpora..." 
	echo "------------------------" 
	"$SCRIPT_DIR/train/get-corpora.sh" "$corpus" 2>&1 | tee --append "$tmpfile"
	corpora_return=${PIPESTATUS[0]}
	echo "Finished with [$corpora_return]"
	echo "------------------------" 
else
	echo "Found config file!"
fi

echo -n "Creating lockfile in $DATA_DIR/$corpus/$action.lock..."
if [ -f "$DATA_DIR/$corpus/$action.lock" ]
then
	echo "Failed!"
	echo "Job already in progress! Waiting for next one..."
	echo "========================"
	exit 1 
else
	touch "$DATA_DIR/$corpus/$action.lock" 
	echo "Done"
fi
# Exectuing action #{{{
action_script="$SCRIPT_DIR/train/$action.sh" 
echo -n "Running $action_script..."
"$action_script" "$corpus" 2>&1 | tee --append "$tmpfile"
action_return=${PIPESTATUS[0]}
echo "Finished with [$action_return]"
# }}}
echo "Printing log for $action"
echo "------------------------"
cat "$tmpfile"
echo "------------------------"
# Error Handling # {{{
if [ "$action_return" -eq 0 ]
then
	sendmail "$DEBUG_MAIL" 1>&2 \
	<<-EOF
	Subject:[BA][$corpus]: $action success
	--------------------------------------
	$(cat "$tmpfile")
	--------------------------------------
	EOF
else 
	sendmail "$DEBUG_MAIL" 1>&2 \
	<<-EOF
	Subject:[BA][$corpus]: $action failure!
	--------------------------------------
	$(cat "$tmpfile")
	--------------------------------------
	$(cat "$CONFIG_DIR/$corpus/$action.config")
	--------------------------------------
	$(df --human)
	--------------------------------------
	$(printenv)
	--------------------------------------
	EOF
fi
# }}}
mkdir --parent "$DATA_DIR/$corpus/logs"
mv "$tmpfile" "$DATA_DIR/$corpus/logs/${action}-${TIME}.log"
echo -n "Removing lock..."
rm "$DATA_DIR/$corpus/$action.lock"
echo "Done"
set -o errexit # }}}
echo "========================"
