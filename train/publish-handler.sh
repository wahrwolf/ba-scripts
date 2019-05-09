#!/bin/bash
action=$1
corpus=$2

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
	echo  "Downloading new corpora..." | tee "$tmpfile"
	echo "------------------------" | tee "$tmpfile"
	"$SCRIPT_DIR/train/get-corpora.sh" "$corpus"| tee "$tmpfile"
	corpora_return=$?
	echo "Finished with [$corpora_return]"
	echo "------------------------" | tee "$tmpfile"
else
	echo "Found config file!"
fi

echo -n "Creating lockfile in $DATA_DIR/$corpus/$action.lock..."
if [ -f -"$DATA_DIR/$corpus/$action.lock" ]
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
"$action_script" "$corpus" 2>>"$tmpfile"
action_return=$?
echo "Finished with [$action_return]"
# }}}
echo "Printing log for $action"
echo "------------------------"
cat "$tmpfile"
echo "------------------------"
# Error Handling # {{{
if [ $action_return -eq 0 ]
then
	sendmail "$DEBUG_MAIL" \
	<<-EOF
	Subject:[BA][$corpus]: $action success
	--------------------------------------
	$(cat "$tmpfile")
	--------------------------------------
	EOF
else 
	echo "Job failed! Waiting for next one..."
fi
# }}}
rm "$tmpfile"
echo -n "Removing lock..."
rm "$DATA_DIR/$corpus/$action.lock"
echo "Done"
set -o errexit # }}}
echo "========================"
