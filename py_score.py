import networkx as nx
import matplotlib.pyplot as plt
from typing import List
from empty_gate_score import empty_gate_score
from main import webrtc_request, play_np, score_str3
from audiolazy import lazy_midi


class Node:
    container = None
    index = 0
    def __init__(self, pitch: str, wait: float = 1, dur: float = 1, left_max: int = 20,
                 left_edge = None, right_min: int = 1, right_edge = None):
        self.pitch = pitch
        self.wait = wait
        self.dur = dur
        self.left_max = left_max
        self.left_edge = left_edge
        self.right_min = right_min
        self.right_edge = right_edge
        self.i = Node.index
        Node.index += 1
        self.container.add_node(self)


class TreeContainer:
    def __init__(self, bpm: int = 120, maxdepth: int = 15):
        self.G = nx.DiGraph()
        self.bpm = bpm
        self.maxdepth = maxdepth
        self.nodes: List[Node]= []
        self.limit_depths = []

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
        #colors = [t / max_wait for t in wait_times]
        #colors = [0.5 for _ in wait_times]

        colors = ['yellow'] + ['pink' for _ in range(Node.index - 1)]

        self.G.add_edges_from(edges)
        nx.draw_networkx(self.G, arrows=True, cmap = plt.get_cmap('jet'), node_size=500, node_color = colors)
        plt.ion()
        plt.draw()
        plt.pause(0.001)

    def index_of_node(self, pitch: str):
        for n in self.nodes:
            if pitch == n.pitch:
                return n.i
        return -1

    def get_rtc_score(self):
        node_make_str = ""
        for n in self.nodes:
            midi_pitch = lazy_midi.str2midi(n.pitch)
            left_index = self.index_of_node(n.left_edge)
            right_index = self.index_of_node(n.right_edge)

            node_make_str += f"make_note_node({n.wait}, {n.dur}, {midi_pitch}, {n.left_max}, {left_index}, {n.right_min}, {right_index})\n"

        build_index = empty_gate_score.index("BUILD HERE") + 11
        rtc_score = empty_gate_score[:build_index] + node_make_str + empty_gate_score[build_index:]
        return rtc_score

    def listen(self):
        rtc_score = self.get_rtc_score()
        print(rtc_score)
        play_np(webrtc_request(rtc_score))


container = TreeContainer()
Node.container = container
a5 = Node("A5", left_edge="G4")
g4 = Node("G4", left_edge="F6")
f6 = Node("F6", left_edge="A5", right_edge="D2")
e3 = Node("E3", left_edge="G4")
d2 = Node("D2", left_edge="E3")
