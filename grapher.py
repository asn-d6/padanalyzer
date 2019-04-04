from matplotlib import pyplot as plt

import circuit

def get_color_sequence_from_str(cell_sequence_str):
    cell_sequence = cell_sequence_str.split(" ")
    color_sequence = ['black' if x=="-1" else 'red' for x in cell_sequence]
    return color_sequence

def graph_circuits(circuits_list):
    """Dictionary: {cell_sequence : (purposes_list, seen_count, commands_list)}"""
    cell_sequence_dict = {}

    ordered_circuits = []

    ordered_circuits = sorted(circuits_list.values(), key=lambda x: x.get_purpose_str(), reverse=True)

    for circ in ordered_circuits:
        cell_sequence_str = circ.get_cells_directions()
        if not cell_sequence_str:
            continue

        cell_commands_list = circ.get_cells_commands()

        print(cell_sequence_str, circ.global_id)

        # If this cell sequence has not been seen before, register it.
        if cell_sequence_str not in cell_sequence_dict:
            cell_sequence_dict[cell_sequence_str] = [[circ.get_purpose_str()], 1, cell_commands_list]
            continue

        # If we get here, we have seen this before. Register it: add purposes
        # and increase seen_count
        prev_entry = cell_sequence_dict[cell_sequence_str]
        prev_purposes = prev_entry[0]
        prev_seen_count = prev_entry[1]
        prev_commands = prev_entry[2]

#        assert(prev_commands == circ.get_cells_commands())

        if circ.get_purpose_str() not in prev_purposes:
            prev_purposes.append(circ.get_purpose_str())
        cell_sequence_dict[cell_sequence_str] = [prev_purposes, prev_entry[1]+1, prev_commands]

    _graph(cell_sequence_dict)

def _graph(cell_sequence_dict):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = fig.add_subplot(111, sharex=ax1, frameon=False)

    i = 0
    max_x = 0
    max_y = 0

    y1_values = []
    y2_values = []

    for cell_sequence_str, (purposes_list, seen_count, commands_list) in cell_sequence_dict.items():
        color_sequence = get_color_sequence_from_str(cell_sequence_str)
        sequence_len = len(color_sequence)

        # x coord puts them in a line
        x = range(sequence_len)
        # change y coord relative to the circuit number
        y = [i]*sequence_len
        # add purposes to the y labels
        y1_values.append("circuits seen: " + str(seen_count))
        y2_values.append(str(purposes_list))

        ax1.scatter(x,y, color=color_sequence)
        ax2.scatter(x,y, color=color_sequence)

        for c, command in enumerate(commands_list):
            ax1.annotate(command, (c,i), fontsize="x-small")

        # Silly horizontal lines
        ax1.axhline(y=i, color='grey', linestyle='--', alpha=0.08)

        if sequence_len > max_x:
            max_x = sequence_len
        max_y = i
        i += 1

    # Print ticks
    ax1.set_xticks(range(0, max_x, 1))
    ax1.set_yticks(range(0, max_y+1, 1))
    ax1.set_yticklabels(y1_values)

    # Print right-aligned ticks
    ax2.set_yticks(range(0, max_y+1, 1))
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    ax2.set_yticklabels(y2_values, fontsize="small")

    ax1.set_xlabel('cells')

    #ax.annotate('lol', (-0.25, 0), textcoords='axes fraction', size=20)

    plt.show()
