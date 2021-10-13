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
e3 = Node("E3", wait=0.7, left_edge="B2", left_max=23) #0
b2 = Node("B2", wait = 1.11, left_edge="F#5", left_max=15, right_edge="G5", right_min=5) #1
fs5 = Node("F#5", wait=0.51, dur=0.5, left_max=17, left_edge="E3", right_min=1, right_edge="G5")#2
g5 = Node("G5", wait=2.82, dur=2.2, left_max=16, left_edge="F#5", right_edge="G4", right_min=6)#3
a5 = Node("A5", wait = 7, dur=2.2, left_max=12, right_min=13, left_edge="A3", right_edge="D5")#4
d5 = Node("D5", wait=1, dur=4, left_max=23, right_min=18, left_edge="G4", right_edge="G5")#5
g4 = Node("G4", wait=1, dur=4, left_max=23, right_min=16, left_edge="G3", right_edge="F#5")#6
g3 = Node("G3", wait=5, dur=4, left_max=23, right_min=15, left_edge="G#6", right_edge="F#5")#7
g6 = Node("G6", wait=5, dur=4, left_max=20, right_min=8, left_edge="G4", right_edge="E2")#8
e2 = Node("E2", wait=6, dur=4, right_min=8, right_edge="A3")#9
a3 = Node("A3", wait=5, dur=4, left_max=23, left_edge="G#6")#10
gs6 = Node("G#6", wait=5, dur=4)#11

container.visualize()
while True:
    pass


