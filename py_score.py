import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Union
from empty_gate_score import empty_gate_score
from main import webrtc_request, play_np
from audiolazy import lazy_midi
from random import randrange, getrandbits, uniform, choice

with open("blank_all_features.sco") as f:
    empty_score = f.read()


def insert_param(score: str, index_string: str, insert_string: str):
    index_string += " ="
    i = score.index(index_string) + len(index_string)
    return score[:i] + insert_string + score[i:]

def insert_under_comment(score: str, comment_string: str, insert_string: str):
    i = score.index(comment_string) + len(comment_string) + 2
    return score[:i] + insert_string + score[i:]

class Node:
    container = None
    def __init__(self, pitch: Union[str, float], wait: float = 1, dur: float = 1, left_max: int = 20,
                 left_edge = None, right_min: int = 0, right_edge = None):
        self.pitch = pitch
        self.wait = wait
        self.dur = dur
        self.left_max = left_max
        self.left_edge = left_edge
        self.right_min = right_min
        self.right_edge = right_edge
        #self.container.add_node(self)


class TreeContainer:
    def __init__(self, bpm: int = 120, maxdepth: int = 15):
        self.G = nx.DiGraph()
        self.bpm = bpm
        self.maxdepth = maxdepth
        self.nodes: List[Node]= []
        self.limit_depths = []

        self.params = {
        "max_dur": 30,
        "tempo": 100,
        "max_depth": 19,
        "max_curs": 1000,
        "init_curs": 1,
        "limit_depths": {},
        "limit_max_cursor_nums": {},
        "hardness": 8,
        "upper_decay": 1,
        "gliss_mode": "'uncoor'",
        "coor_stop_time": 20
        }

    def rand_graph(self, start_intensity=0, end_intensity=5, slide=False, num_nodes: int = 7, pitches=("A5",)):
        container = TreeContainer()
        Node.index = 0
        Node.container = container
        more_pitches = []

        while len(more_pitches) < num_nodes:  # make more pitches the whole family can enjoy
            for pitch in pitches:
                m = lazy_midi.str2midi(pitch)
                if not pitch in more_pitches:
                    more_pitches.append(pitch)
                else:
                    add = 6
                    if randrange(4) == 0:
                        add += randrange(-3, 2)
                    p = lazy_midi.midi2str(m + add)
                    if not p in more_pitches:
                        more_pitches.append(p)

                fifth = 7
                if getrandbits(1):
                    fifth = 14
                if getrandbits(1):
                    new_note = lazy_midi.midi2str(m + fifth)
                else:
                    new_note = lazy_midi.midi2str(m - fifth)
                if not new_note in more_pitches:
                    more_pitches.append(new_note)
        for p in more_pitches:
            possible_edges = [pitch for pitch in more_pitches if pitch != p]
            le = choice(possible_edges) if getrandbits(1) else None
            re = choice(possible_edges) if getrandbits(1) else None
            self.nodes.append(Node(p, wait=uniform(0.5, 5), dur=uniform(1, 4), left_edge=le, right_edge=re))


    def add_node(self, node: Node):
        self.nodes.append(node)

    def visualize(self):
        edges = []
        for n in self.nodes:
            if n.left_edge:
                edges.append((n.pitch, n.left_edge))
            if n.right_edge:
                edges.append((n.pitch, n.right_edge))

        wait_times = [n.wait for n in self.nodes]
        max_wait = max(wait_times)
        colors = [t / max_wait for t in wait_times]
        colors = [0.5 for _ in wait_times]


        self.G.add_edges_from(edges)
        colors = ['yellow'] + ['pink' for _ in range(len(self.G.nodes) - 1)]

        pos = nx.circular_layout(self.G)
        nx.draw_networkx(self.G, pos, arrows=True, cmap = plt.get_cmap('jet'), node_size=500, node_color = colors)
        plt.ion()
        plt.draw()
        plt.pause(0.001)

    def check_all_connected(self) -> List[Node]:
        connected_nodes = []

        def traverse_tree(n: Node):
            if n in connected_nodes:
                return
            connected_nodes.append(n)
            if n.left_edge:
                traverse_tree(self.get_node_by_pitch(n.left_edge))
            if n.right_edge:
                traverse_tree(self.get_node_by_pitch(n.right_edge))

        traverse_tree(self.nodes[0])

        connected_pitches = [n.pitch for n in connected_nodes]
        print(connected_pitches)
        return connected_nodes

    def make_all_connected(self):
        already_connected = self.check_all_connected()
        all_nodes = set(self.nodes)

        unconnected = all_nodes.difference(set(already_connected))

        for unc_node in unconnected:
            for con_node in already_connected:
                if not con_node.left_edge:
                    con_node.left_edge = unc_node.pitch
                    break
                if not con_node.right_edge:
                    con_node.right_edge = unc_node.pitch
                    break


    def get_node_by_pitch(self, pitch: Union[str, float]):
        for n in self.nodes:
            if n.pitch == pitch:
                return n

    def index_of_node(self, pitch: Union[str, float]):
        for n in self.nodes:
            if pitch == n.pitch:
                return self.nodes.index(n)
        return -1

    def get_rtc_score(self):
        node_make_str = ""
        for n in self.nodes:
            midi_pitch = lazy_midi.str2midi(n.pitch)
            left_index = self.index_of_node(n.left_edge)
            right_index = self.index_of_node(n.right_edge)

            node_make_str += f"make_note_node({n.wait}, {n.dur}, {midi_pitch}, {n.left_max}, {left_index}, {n.right_min}, {right_index})\n"

        rtc_score = insert_under_comment(empty_score, "BUILD HERE", node_make_str)
        for param, val in self.params.items():
            rtc_score = insert_param(rtc_score, param, str(val))

        #print(rtc_score)

        return rtc_score

    def listen(self):
        rtc_score = self.get_rtc_score()
        play_np(webrtc_request(rtc_score))





def test_rand():
    print("Testing random graph")
    container = TreeContainer()
    Node.container = container
    container.rand_graph(num_nodes=9)
    container.make_all_connected()
    container.visualize()
    container.listen()


def test_preset():
    container = TreeContainer()
    Node.container = container
    e3 = Node("D3", wait=0.7, dur=1, left_edge="B2", left_max=23)  # 0
    b2 = Node("B2", wait=1.11, left_edge="F#5", left_max=15, right_edge="G5", right_min=5)  # 1
    fs5 = Node("F#5", wait=0.51, dur=0.5, left_max=17, left_edge="D3", right_min=1, right_edge="G5")  # 2
    g5 = Node("G5", wait=2.82, dur=2.2, left_max=16, left_edge="F#5", right_edge="G4", right_min=6)  # 3
    a5 = Node("A5", wait=7, dur=2.2, left_max=12, right_min=13, left_edge="A3", right_edge="D5")  # 4
    d5 = Node("D5", wait=1, dur=4, left_max=23, right_min=18, left_edge="G4", right_edge="G5")  # 5
    g4 = Node("G4", wait=1, dur=4, left_max=23, right_min=16, left_edge="G3", right_edge="F#5")  # 6
    g3 = Node("G3", wait=5, dur=4, left_max=23, right_min=15, left_edge="G6", right_edge="G#6")  # 7
    g6 = Node("G6", wait=5, dur=4, left_max=20, right_min=8, left_edge="G4", right_edge="E2")  # 8
    e2 = Node("E2", wait=6, dur=4, right_min=8, right_edge="A3")  # 9
    a3 = Node("A3", wait=5, dur=4, left_max=23, left_edge="G#6")  # 10
    gs6 = Node("G#6", wait=5, dur=4)  # 11

    container.visualize()
    container.listen()


if __name__ == "__main__":
    test_rand()


