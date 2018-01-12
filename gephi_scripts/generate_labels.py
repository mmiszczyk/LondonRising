#################################
#                               #
#         LONDON RISING         #
#   The Fallen London Reverse   #
#      Enginerring Project      #
#                               #
# This program is free and open #
#    source software released   #
#   GNU GPL 3 (see LICENCE for  #
#       further details).       #
#                               #
#################################

# to run this script, enter 'execfile(/absolute/path/to/LondonRising/gephi_scripts/generate_labels.py)' in gephi
# scripting console (with '/absolute/path/to' replaced with an actual path, obviously)

# this makes the graph labels based on Name instead of id;
# according to tutorials, it should be as simple as 'n.label = n.Name' within the foreach loop -
# but this doesn't work for some reason so there's this hack

idx = -1
for n in g.nodes:
    if idx == -1:
        idx = [str(x)[:4] for x in n.node.attributeColumns.toArray()].index('Name')
    n.label = n.node.attributes[idx]
