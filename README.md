# Padding log analyser for Tor

This project reads log files from a special mod of Tor and outputs graphs and
information about circuits and cells.

For this analyser to work you need to patch your Tor with the following commit:\
 https://github.com/asn-d6/tor/tree/bug28634_analysis_no_pad \
so that it outputs useful informatation about circuits and cells in its logs.

In particular the branch above adds the following logs to Tor:\
   `new-circ: <global-id> <purpose> <is_predicted_circuit>`\
   `outgoing-cell: <global_id> <purpose> <command> <state>`\
   `incoming-cell: <global_id> <command> <purpose> <state> <length>`\
You can see log_line.py for how these lines are parsed.

After you collect a big enough log file, just do this:\
     `$ python3 padanalyzer.py tbb.log`

I also added logs/0404_torbrowser_test.log as a sample log file you can try
out.

