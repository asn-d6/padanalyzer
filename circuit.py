import itertools

# Introduction circuit purposes
CIRCUIT_PURPOSE_C_INTRODUCING = 6
CIRCUIT_PURPOSE_C_INTRODUCE_ACK_WAIT = 7

# Rendezvous circuit purposes
CIRCUIT_PURPOSE_C_ESTABLISH_REND = 9
CIRCUIT_PURPOSE_C_REND_READY_INTRO_ACKED = 11
CIRCUIT_PURPOSE_C_REND_JOINED = 12

# HSDir fetch circuit purpose
CIRCUIT_PURPOSE_C_HSDIR_GET = 13


class Circuit(object):
    def __init__(self, global_id, purpose, is_predicted, timestamp):
        self.circ_type = "General"

        self.global_id = global_id
        self.is_predicted = is_predicted

        self.created_ts = timestamp
        self.ts_str = self.created_ts.strftime("%H:%M:%S.%f")[:-3]

        self.cells = []
        # A circuit changes multiple purposes through its lifetime.
        self.purposes = []
        self.purposes.append(int(purpose))

    def get_purpose_str(self):
        purpose = None

        # purposes 6 and 7 are intro purposes
        if any(x in (6,7) for x in self.purposes):
            purpose = "intro"

        if any(x in (9, 10, 11, 12) for x in self.purposes):
            assert(not purpose)
            purpose = "rend"

        if 13 in self.purposes:
            assert(not purpose)
            purpose = "hsdir_get"

        if 22 in self.purposes:
            assert(not purpose)
            purpose = "path_bias"

        # If we still have not found the purpose, it's general
        if not purpose:
            purpose = "general"

        return purpose

    def register_outgoing_cell(self, purpose, command, timestamp):
        self._register_cell(purpose, command, timestamp, True)

    def register_incoming_cell(self, purpose, command, timestamp):
        self._register_cell(purpose, command, timestamp, False)

    def _register_cell(self, purpose, command, timestamp, is_outgoing):
        cell = Cell(command, timestamp, is_outgoing)

        # Since we are reading logs from top to bottom, self.cells should
        # contain the cells in chronological order
        self.cells.append(cell)

        if int(purpose) not in self.purposes:
            self.purposes.append(int(purpose))

    def get_cells_directions(self):
        """Return the direction of the first 10 cells of this circuit"""
        cell_directions = ""
        cells_n = 0

        for i, cell in enumerate(self.cells):
            if i >= 10:
                break
            cell_directions += cell.get_direction() + " "
            cells_n += 1

        # Don't return preemptive circs that did not get used
        if (cells_n <= 4):
            return None

        return cell_directions

    def get_cells_commands(self):
        commands = []
        for i, cell in enumerate(self.cells):
            if i >= 10:
                break
            commands.append(cell.command)
        return commands

    def analyze_cells_verbose(self):
        """Print verbose cell details about this circuit (used in HS log)"""
        print("{} circuit {} was created at {}".format(self.circ_type, self.global_id, self.ts_str))
        print("Relay cells:")
        for i, cell in enumerate(self.cells):
            print("{}: {}".format(i, cell))

    def analyze_cells_groupby(self):
        """Print cell details about this circuit but group together similar cells (used in HS log)"""
        print("{} circuit {} was created at {}".format(self.circ_type, self.global_id, self.ts_str))
        print("Relay cells:")

        cells_no_ts = []
        for cell in self.cells:
            cells_no_ts.append(cell.str_no_ts())

        count_dups = [sum(1 for _ in group) for _, group in itertools.groupby(cells_no_ts)]
        for i, (cell_str, _) in enumerate(itertools.groupby(cells_no_ts)):
            print("{}: {} x{}".format(i, cell_str, count_dups[i]))

    def figure_out_circ_type(self):
        """
        Check if this is an HSDir/RP/IP circuit and return it if so.
        Also set the type of the circuit.
        """
        if CIRCUIT_PURPOSE_C_ESTABLISH_REND in self.purposes and \
           CIRCUIT_PURPOSE_C_REND_JOINED in self.purposes:
            self.circ_type = "RP"

        if CIRCUIT_PURPOSE_C_INTRODUCING in self.purposes and \
           CIRCUIT_PURPOSE_C_INTRODUCE_ACK_WAIT in self.purposes:
            assert(self.circ_type == "General")
            self.circ_type = "IP"

        if CIRCUIT_PURPOSE_C_HSDIR_GET in self.purposes:
            assert(self.circ_type == "General")
            self.circ_type = "HSDir"

        return self.circ_type

class Cell(object):
    def __init__(self, command, timestamp, is_outgoing):
        self.command = command
        self.is_outgoing = is_outgoing

        self.timestamp = timestamp
        self.ts_str = self.timestamp.strftime("%H:%M:%S.%f")[:-3]

    def __str__(self):
        return "{} {} {}".format(self.ts_str,
                                 "->" if self.is_outgoing else "<-",
                                 self.command)

    def str_no_ts(self):
        return "{} {}".format("->" if self.is_outgoing else "<-",
                              self.command)

    def get_direction(self):
        return "-1" if self.is_outgoing else "+1"

