import grapher

class HSLog(object):
    """Represents a log of an onion service connection"""
    def __init__(self):
        # Necessary circuits for HS log
        self.hsdir_circs = []
        self.ip_circs = []
        self.rp_circs = []

        # Dictionary { <global_id> : <circuit> }
        self.circuits = {}

    def get_circuit(self, global_id):
        """Get circuit based on a global id"""
        if global_id in self.circuits:
            return self.circuits[global_id]

        print("Did not find circ {}".format(global_id))
        return None

    def register_circuit(self, circuit):
        """Register circuit to the HS log"""
        assert(circuit.global_id)
        assert(circuit.global_id not in self.circuits)

        self.circuits[circuit.global_id] = circuit

    def finalize_global_log(self):
        """We have read all the log lines. Print info about ALL the cells"""
        grapher.graph_circuits(self.circuits)

    def finalize_hs_log(self):
        """
        We have read all the log lines. Now finalize the whole thing:
        - Figure out which are the client-side HS circuits from the log
        - Print information about them
        """
        assert(self.circuits)
        assert(not self.hsdir_circs)
        assert(not self.ip_circs)
        assert(not self.rp_circs)

        # Find HS circs in the log
        self._find_hs_circuits()
        # Make sure we found them
        assert(self.rp_circs and self.ip_circs and self.hsdir_circs)

        self.hsdir_circs[0].analyze_cells_verbose()
        self.ip_circs[0].analyze_cells_verbose()
        self.rp_circs[0].analyze_cells_verbose()


    def _find_hs_circuits(self):
        """
        Find the HSDir/IP/RP circs if they exist
        """
        # Loop over all circuits and tag HS circuits
        for global_id, circ in self.circuits.items():
            circ_type = circ.figure_out_circ_type()
            if circ_type == "RP":
                self.rp_circs.append(circ)
            if circ_type == "IP":
                self.ip_circs.append(circ)
            if circ_type == "HSDir":
                self.hsdir_circs.append(circ)

        # Sanity check: We found at least one complete HS connection
        if not self.rp_circs:
            print("We did not find an RP circ")
        if not self.ip_circs:
            print("We did not find an IP circ")
        if not self.hsdir_circs:
            print("We did not find an HSDir circ")

        # Sanity check: These lists should be disjoint. An RP circ must not be
        # an IP circ or an HSDir circ.
        all_together_now = self.rp_circs + self.ip_circs + self.hsdir_circs
        assert(len(set(all_together_now)) == len(all_together_now))

