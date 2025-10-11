# This file is part of Plotlines.

# Plotlines is free software: You can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

# Plotlines is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the
# GNU General Public License along with Plotlines.
# If not, see <https://www.gnu.org/licenses/>.


from decimal import Decimal
from fractions import Fraction
import textwrap
import tkinter as tk
import tomllib
import turtle
import unittest

from plotlines.board import Board
from plotlines.board import Edge
from plotlines.board import Node
from plotlines.board import Port
from plotlines.coordinates import Coordinates as C


class BoardTests(unittest.TestCase):

    def test_edge_init(self):
        edge = Edge((1, 3), (19, 12))
        self.assertEqual(len(edge.ports), 2)
        self.assertTrue(all(isinstance(p.pos, C) for p in edge.ports), edge.ports)
        self.assertEqual(edge.ports[0].pos, (1, 3))
        self.assertEqual(edge.ports[1].pos, (19, 12))

    def test_node_init(self):
        node = Node((13, 14))
        self.assertIsInstance(node.pos, C)
        self.assertEqual(node.pos, (13, 14))

    def test_node_connect(self):
        nodes = [Node(), Node()]
        edge = nodes[0].connect(nodes[1])
        self.assertIsInstance(edge, Edge)
        self.assertEqual(edge.ports[0].joins, {edge.uid, nodes[0].uid})
        self.assertEqual(edge.ports[1].joins, {edge.uid, nodes[1].uid})
        self.assertEqual(nodes[0].ports["00"].joins, {edge.uid, nodes[0].uid})
        self.assertEqual(nodes[1].ports["00"].joins, {edge.uid, nodes[1].uid})

    def test_node_nearby(self):
        Node.store.clear()
        nodes = [Node(), Node()]
        edge = nodes[0].connect(nodes[1])
        self.assertIn(nodes[1], nodes[0].nearby)
        self.assertNotIn(nodes[0], nodes[0].nearby)
        self.assertIn(nodes[0], nodes[1].nearby)
        self.assertNotIn(nodes[1], nodes[1].nearby)

    def test_node_edges(self):
        nodes = [Node(), Node()]
        edge = nodes[0].connect(nodes[1])

        for node in nodes:
            with self.subTest(node=node):
                self.assertIsInstance(node.edges, list)
                self.assertIn(edge, node.edges)
                self.assertEqual(len(node.edges), 1)

    def test_node_spacing_node_self(self):
        node = Node((1, 3))

        spacing = node.spacing(node)
        self.assertEqual(len(spacing), 1)
        space = min(spacing.values())
        self.assertEqual(space, 0)

    def test_node_spacing_node_other(self):
        nodes = [Node((1, 3)), Node((19, 12))]

        spacing = nodes[0].spacing(nodes[1])
        self.assertEqual(len(spacing), 1)
        space = min(spacing.values())
        self.assertAlmostEqual(space, 20, places=0)

    def test_node_spacing_edge(self):
        edge = Edge((1, 3), (19, 12))
        node = Node((13, 4))

        spacing = node.spacing(edge)
        self.assertEqual(len(spacing), 3, spacing)
        space = min(spacing.values())
        self.assertAlmostEqual(space, 4.5, places=1)

    def test_frame(self):
        points = (C(0, 0), C(10, 10))
        check = (C(-0.5, -0.5), C(10.5, 10.5))
        self.assertEqual(Board.frame(*points), check)

        points = (C(0, 0), C(0, 10))
        check = (C(-0.5, -0.5), C(0.5, 10.5))
        self.assertEqual(Board.frame(*points), check)

    def test_scale_factor(self):
        geom = (400, 300)
        frame = (C(1.50, 1.50, coerce=Decimal), C(12.50, 2.50, coerce=Decimal))
        scale = Board.scale_factor(geom, frame)
        check = Fraction(909, 25)
        self.assertEqual(scale, check)

    def test_style_graph(self):
        nodes = [
            Node((1, 8)),
            Node((6, 3)),
            Node((6, 6)),
            Node((6, 9)),
            Node((6, 12)),
            Node((11, 4), area=16),
            Node((10, 8)),
            Node((12.5, 11.5), area=9),
            Node((17, 1)),
            Node((17, 4)),
            Node((17, 7)),
            Node((17, 10)),
            Node((17, 13)),
        ]
        edges = [
            nodes[0].connect(nodes[3], C(2, 8), C(5, 9)),
            nodes[3].connect(nodes[2], C(6, 5), C(6, 4)),
            nodes[2].connect(nodes[1], C(6, 8), C(6, 7)),
            nodes[3].connect(nodes[4], C(6, 10), C(6, 11)),
            nodes[1].connect(nodes[5], C(7, 3), C(9, 3)),
            nodes[2].connect(nodes[5], C(7, 6), C(9, 5)),
            nodes[3].connect(nodes[6], C(7, 9), C(9, 8)),
            nodes[4].connect(nodes[7], C(7, 12), C(11, 12)),
            nodes[5].connect(nodes[8], C(13, 3), C(16, 1)),
            nodes[5].connect(nodes[9], C(13, 4), C(16, 4)),
            nodes[5].connect(nodes[10], C(13, 5), C(16, 7)),
            nodes[6].connect(nodes[10], C(11, 8), C(16, 7)),
            nodes[7].connect(nodes[11], C(14, 11), C(16, 10)),
            nodes[7].connect(nodes[12], C(14, 12), C(16, 13)),
        ]

        t = turtle.Turtle()
        board = Board(t, title="Multigraph")
        rv = board.style_graph(nodes + edges)
        rv = board.draw_graph(nodes + edges, debug=True, delay=0)
        t.screen.mainloop()
        self.assertEqual(len(board.shapes), 3, board.shapes)
        self.assertEqual(len(board.stamps), len(nodes), board.stamps)
