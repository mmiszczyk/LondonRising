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

import json
import sqlite3
import argparse
import fl_types

DECRYPTED_FILE = "decrypted.cblite"
GRAPH_FILE = "fallenlondon.gexf"


def main(input_file, graphfile, big_graph):
    if big_graph:
        fl_types.IGNORE_FIELDS = []
        fl_types.GameObject.ignore_refs = []

    graphdata = FLGraph(graphfile)

    db = sqlite3.connect(input_file)
    c = db.cursor()
    c.execute('select * from revs')

    for x in c.fetchall():
        graphdata.add_graph_node(db_row_to_dict(x))

    graphdata.write_to_file()


def db_row_to_dict(row):
    row_dict = {'sequence': row[0],
                'doc_id': row[1],
                'revid': row[2],
                'parent': row[3],
                'current': row[4],
                'deleted': row[5],
                'json': json.loads(decode_from_bytes(row[6])) if row[6] is not None else {},
                'no_attachments': row[7],
                'doc_type': row[8]}
    return row_dict


def decode_from_bytes(x):
    return x.decode('utf-8') if type(x) is bytes else x


def encode_to_bytes(x):
    return bytes(x, 'utf-8') if type(x) is str else x


class FLGraph(object):
    def __init__(self, graphfile):
        if graphfile is None:
            self._should_skip = True
            return
        import networkx
        import functools
        self._should_skip = False
        self._G = networkx.MultiDiGraph()
        self._write_func = functools.partial(networkx.write_gexf, self._G, graphfile,
                                             encoding='utf-8', prettyprint=True)

    def add_graph_node(self, row_dict):
        if self._should_skip:
            return
        row_dict = self._flatten_node(row_dict)
        node, edges = fl_types.parse_dict_to_game_object(row_dict, self.add_graph_node)
        if node is not None:
            self._G.add_node(node[0], **node[1])
            self._G.add_edges_from(edges)
            return node[0]
        return None

    def write_to_file(self):
        if self._should_skip:
            return
        self._write_func()

    @classmethod
    def _flatten_node(cls, node):

        cls._parametrized_flatten(node, 'json')
        cls._parametrized_flatten(node, 'body')
        return node

    @classmethod
    def _parametrized_flatten(cls, node, param):
        try:
            for key in node[param]:
                node[key] = node[param][key]
            del node[param]
        except KeyError:
            pass
        return node


if __name__ == "__main__":
    # text ASCII art generated with http://patorjk.com/software/taag (font: Georgia 11)
    # ASCII Fanghat by me
    # (but the output of https://manytools.org/hacker-tools/convert-images-to-ascii-art/ was used as reference)
    print("""
7MMF'                                 `7MM                        
  MM                                     MM                        
  MM         ,pW"Wq.  `7MMpMMMb.    ,M""bMM   ,pW"Wq.  `7MMpMMMb.  
  MM        6W'   `Wb   MM    MM  ,AP    MM  6W'   `Wb   MM    MM  
  MM      , 8M     M8   MM    MM  8MI    MM  8M     M8   MM    MM  
  MM     ,M YA.   ,A9   MM    MM  `Mb    MM  YA.   ,A9   MM    MM  
.JMMmmmmMMM  `Ybmd9'  .JMML  JMML. `Wbmd"MML. `Ybmd9'  .JMML  JMML.

             ----------------------
             |&&&&&&&&&&&&&&&&&&&&|
             |&&&&&&&&&&&&/.     *|
             |@@@&&&&&&&&&&@@@&*.%|
             |@@@@@@@@@@@@@@@@@@#.|
             |@@@@@@@@@@@@@@@@#.. |
             |@@@@@@@@@@@@@@@@#.. |
             |&@@@@@@@@@@@@@@@@@#.|
       /----&(&@@@@@@@@@@@@@@@@@,@&----\  
      @&&&&&&&&&&&& &&&&&&&& &&&&&&&&&&&@                         Fallen London
     (%&&&&&&&&&&& ' &&&&&& ' &&&&&&&&&&&)          Reverse Engineering Project
      @&&&&&&&&&&&   &&&&&&   &&&&&&&&&&@
       \-------------------------------/  
               \                */        
                \  / v v v v.\  /
                 \/           \/
                 
              ,,            ,,                  
`7MM\"""Mq.    db            db                                     
  MM   `MM.                                                        
  MM   ,M9  `7MM  ,pP"Ybd `7MM  `7MMpMMMb.   .P"Ybmmm              
  MMmmdM9     MM  8I   `"   MM    MM    MM  :MI  I8                
  MM  YM.     MM  `YMMMa.   MM    MM    MM   WmmmP"                
  MM   `Mb.   MM  L.   I8   MM    MM    MM  8M                     
.JMML. .JMM..JMML.M9mmmP' .JMML..JMML  JMML. YMMMMMb               
                                            6'     dP              
                                            Ybmmmd'     
    """)
    parser = argparse.ArgumentParser(description=
                                     "Tools for reverse engineering databases from the Fallen London mobile app")

    parser.add_argument("-i", "--infile", help=
                        "File to read from (default: " + DECRYPTED_FILE + ")")
    parser.add_argument("-o", "--outfile", help="File to write to (default: " + GRAPH_FILE + ")")
    parser.add_argument("--big-graph", help="If true, we don't try to limit the number of nodes/edges and generate" +
                                            "a big graph. This makes Gephi mad so this isn't the default.",
                        action='store_true')
    args = parser.parse_args()
    infile = args.infile if args.infile else DECRYPTED_FILE
    outfile = args.outfile if args.outfile else GRAPH_FILE
    big_graph_for_you = args.big_graph
    main(infile, outfile, big_graph_for_you)

