import datetime

import circuit

class LogLine(object):
    def __init__(self, line_str, hs_log):
        """Can raise ValueError exception"""
        self.timestamp = None
        self.hs_log = hs_log

        self.parse_whole_log_line(line_str)

    def parse_new_circ_line(self, new_circ_line_list):
        """new-circ: global-id purpose is_predicted_circuit"""
        assert(len(new_circ_line_list) == 4)
        assert(new_circ_line_list[0] == "new-circ:")

        global_id, purpose = new_circ_line_list[1], new_circ_line_list[2]
        is_predicted = new_circ_line_list[3]

        new_circ = circuit.Circuit(global_id, purpose, is_predicted, self.timestamp)
        self.hs_log.register_circuit(new_circ)

    def parse_outgoing_cell_line(self, outgoing_cell_list):
        """outgoing-cell: global_id purpose command state"""
        assert(len(outgoing_cell_list) == 5)
        assert(outgoing_cell_list[0] == "outgoing-cell:")

        # Parse log line
        global_id, purpose = outgoing_cell_list[1], outgoing_cell_list[2]
        command = outgoing_cell_list[3]
        _ = outgoing_cell_list[4]

        # Get the circuit corresponding to this cell
        circuit = self.hs_log.get_circuit(global_id)
        assert(circuit)

        circuit.register_outgoing_cell(purpose, command, self.timestamp)

    def parse_incoming_cell_line(self, incoming_cell_list):
        """incoming-cell: global_id command purpose state length"""
        assert(len(incoming_cell_list) == 6)
        assert(incoming_cell_list[0] == "incoming-cell:")

        # Parse log line
        global_id, purpose = incoming_cell_list[1], incoming_cell_list[2]
        command = incoming_cell_list[3]
        _ = incoming_cell_list[4]
        _ = incoming_cell_list[5]

        # Get the circuit corresponding to this cell
        circuit = self.hs_log.get_circuit(global_id)
        assert(circuit)

        circuit.register_incoming_cell(purpose, command, self.timestamp)

    def parse_log_body(self, log_body_list):
        """
        Parse the body of a log line, presented as a list of space-delimited strings.
           e.g. ['Tor', '0.4.1.0-alpha-dev', '(git-d2714f2322530147)', 'opening', 'log', 'file.']
                ['incoming-cell:', '1', 'DATA', '5', 'open', '498']
        """
        assert(len(log_body_list) > 1)

        if log_body_list[0] == "new-circ:":
            self.parse_new_circ_line(log_body_list)
        elif log_body_list[0] == "outgoing-cell:":
            self.parse_outgoing_cell_line(log_body_list)
        elif log_body_list[0] == "incoming-cell:":
            self.parse_incoming_cell_line(log_body_list)
        elif log_body_list[0] == "found-circ:":
            pass
        else:
            pass

    def parse_whole_log_line(self, line_str):
        """Parse log line and raise ValueError if fail"""
        split_line = line_str.split(" ")

        if (len(split_line) < 5):
            raise ValueError('Too small log line {}'.format(line_str))

        self.timestamp = self._parse_timestamp(split_line[:3])
        log_severity = split_line[3]
        log_body = split_line[4:]

        self.parse_log_body(log_body)

    def _parse_timestamp(self, timestamp_list):
        timestamp_str = " ".join(timestamp_list)
        return datetime.datetime.strptime(timestamp_str, "%b %d %H:%M:%S.%f")

######################################################################

def parse_log_line(line_str, hs_log):
    """
    Parse a log line. Check if it's relevant to us, and if so register it to
    the HS log.
    """
    try:
        log_line = LogLine(line_str, hs_log)
    except ValueError:
        pass

