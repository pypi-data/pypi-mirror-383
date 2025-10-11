#! /usr/bin/env python3
# encoding: UTF-8

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

import dataclasses
from decimal import Decimal
from fractions import Fraction
import functools
import itertools
import textwrap
import tkinter as tk
import tomllib
import turtle
from types import SimpleNamespace as NS
import unittest.mock
import uuid
import xml.etree.ElementTree as ET

from plotlines.board import Board
from plotlines.board import Edge
from plotlines.board import Node
from plotlines.board import Pin
from plotlines.board import Port
from plotlines.board import RGB
from plotlines.board import Style
from plotlines.coordinates import Coordinates as C


class EdgeTests(unittest.TestCase):

    def test_uid_int(self):
        edge = Edge(uid=1)
        self.assertTrue(edge)
        self.assertEqual(edge.uid, 1)

    def test_init_from_toml_full(self):
        toml = textwrap.dedent("""
        uid = "e7ed29c8-f718-488c-9b3b-adf1f881f6a2"
        trail = "main"

        [style]
        stroke = [127, 127, 127]
        fill = [32, 32, 32]
        weight = 6

        [[ports]]
        pos = [0, 1]
        joins = []

        [[ports]]
        pos = [2, 3]
        joins = [77096613620228011470678743578062052921, "NODE_1"]

        [[contents]]
        """)
        data = tomllib.loads(toml)
        edge = Edge.build(**data)
        self.assertTrue(edge)
        self.assertIsInstance(edge.uid, uuid.UUID)
        self.assertIsInstance(edge.ports[0].joins, set)
        self.assertIsInstance(edge.ports[0].pos, C)
        self.assertIsInstance(edge.ports[1].joins, set)
        self.assertIsInstance(edge.ports[1].pos, C)

        self.assertEqual(len(edge.ports[0].joins), 1, edge.ports[0].joins)
        self.assertEqual(len(edge.ports[1].joins), 3, edge.ports[1].joins)
        self.assertIn(uuid.UUID(int=list(data["ports"][1]["joins"])[0]), edge.ports[1].joins)
        self.assertNotIn(list(data["ports"][1]["joins"])[0], edge.ports[1].joins)
        self.assertIn("NODE_1", edge.ports[1].joins)

        self.assertIsInstance(edge.style, Style)


class NodeTests(unittest.TestCase):

    def test_uid_int(self):
        node = Node(uid=1)
        self.assertTrue(node)
        self.assertEqual(node.uid, 1)
        self.assertEqual(node.handle(), "00")

    def test_init_from_toml_full(self):
        toml = textwrap.dedent("""
        uid = "e7ed29c8-f718-488c-9b3b-adf1f881f6a2"
        pos = [0, 0]

        [style]
        stroke = [127, 127, 127]
        fill = [32, 32, 32]
        weight = 6

        [ports.E]
        pos = [0, 1]
        joins = []

        [ports.W]
        pos = [0, -1]
        joins = [77096613620228011470678743578062052921, "EDGE_1"]

        [[contents]]
        """)
        data = tomllib.loads(toml)
        node = Node.build(**data)
        self.assertTrue(node)

        self.assertIsInstance(node.uid, uuid.UUID)
        self.assertIsInstance(node.ports["E"].joins, set)
        self.assertIsInstance(node.ports["E"].pos, C)
        self.assertIsInstance(node.ports["W"].joins, set)
        self.assertIsInstance(node.ports["W"].pos, C)

        self.assertEqual(len(node.ports["E"].joins), 0, node.ports["E"].joins)
        self.assertEqual(len(node.ports["W"].joins), 2, node.ports["W"].joins)
        self.assertTrue(any(isinstance(i, uuid.UUID) for i in node.ports["W"].joins), node.ports["W"].joins)
        self.assertFalse(any(isinstance(i, int) for i in node.ports["W"].joins), node.ports["W"].joins)
        self.assertIn("EDGE_1", node.ports["W"].joins)

        self.assertIsInstance(node.style, Style)


class SVGTests(unittest.TestCase):

    @staticmethod
    def build_screen(size: tuple = (400, 300)):
        mock_image = unittest.mock.Mock(spec=tk.PhotoImage)
        mock_image._type = "image"
        mock_image._data = None

        rv = unittest.mock.MagicMock(spec=turtle.TurtleScreen)
        rv._tracing = 0
        rv._turtles = []
        rv._blankimage.return_value = mock_image
        rv._shapes = dict(blank=mock_image, classic=mock_image)
        rv._write.return_value = (None, None)

        rv.register_shape.side_effect = lambda name, shape: rv._shapes.setdefault(name, shape)
        rv.getshapes.side_effect = lambda: list(rv._shapes)
        rv._createpoly.side_effect = itertools.count()
        rv.xscale = 1.0
        rv.yscale = 1.0
        rv.mode.return_value = "world"
        rv.screensize.return_value = size
        return rv

    @staticmethod
    def build_3_nodes():
        nodes = [
            Node((2, 2)),
            Node((7, 2), style=Style(stroke=RGB(127, 127, 127), fill=RGB(32, 32, 32), weight=10)),
            Node((12, 2))
        ]
        edges = [
            nodes[0].connect(nodes[1], C(3, 2), C(6, 2)),
            nodes[0].connect(nodes[2], C(8, 2), C(11, 2)),
        ]
        return nodes, edges

    def test_3_nodes_draw(self):
        nodes, edges = self.build_3_nodes()
        mock_screen = self.build_screen()
        with unittest.mock.patch.object(turtle.Turtle, "_screen", mock_screen):
            t = turtle.Turtle()
            board = Board(t)
            rv = board.style_graph(nodes + edges)
            rv = board.draw_graph(nodes + edges)
            self.assertEqual(len(board.shapes), 1, board.shapes)
            self.assertEqual(len(board.stamps), len(nodes), board.stamps)

    def test_3_nodes_toml(self):
        nodes, edges = self.build_3_nodes()
        for node in nodes:
            toml = "\n".join(node.toml())
            try:
                data = tomllib.loads(toml)
                check = Node.build(**data)
            except Exception:
                self.fail("\n" + toml)

            self.assertEqual(node.uid, check.uid)
            for field in dataclasses.fields(Node):
                with self.subTest(field=field):
                    try:
                        self.assertEqual(sorted(getattr(node, field.name)), sorted(getattr(check, field.name)), "\n" + toml)
                    except TypeError:
                        self.assertEqual(getattr(node, field.name), getattr(check, field.name), "\n" + toml)

            self.assertEqual(node, check)

    def test_2_edges_toml(self):
        nodes, edges = self.build_3_nodes()
        for edge in edges:
            toml = "\n".join(edge.toml())
            try:
                data = tomllib.loads(toml)
                check = Edge.build(**data)
            except Exception:
                self.fail("\n" + toml)

            self.assertEqual(edge.uid, check.uid)
            for field in dataclasses.fields(Edge):
                with self.subTest(field=field):
                    self.assertEqual(getattr(edge, field.name), getattr(check, field.name), "\n" + toml)

            self.assertEqual(edge, check)

    def test_3_nodes_svg(self):
        nodes, edges = self.build_3_nodes()
        mock_screen = self.build_screen()
        with unittest.mock.patch.object(turtle.Turtle, "_screen", mock_screen):
            t = turtle.Turtle()
            board = Board(t, title="3 Node test")
            rv = board.style_graph(nodes + edges)
            items = board.draw_graph(nodes + edges)

            frame = board.frame(*board.extent(nodes + edges), square=True)
            size = t.screen.screensize()

            svg = board.svg(items)
            root = ET.fromstring(svg)

            ns = NS(svg="http://www.w3.org/2000/svg", xlink="http://www.w3.org/1999/xlink")
            self.assertEqual(root.tag, ET.QName(ns.svg, "svg"))
            self.assertIn('xmlns:xlink="http://www.w3.org/1999/xlink"', svg)
            self.assertEqual(root.attrib.get("width"), str(t.screen.screensize()[0]), root.attrib)
            self.assertEqual(root.attrib.get("height"), str(t.screen.screensize()[1]), root.attrib)

            self.assertIn("viewBox", root.attrib)
            self.assertIn("preserveAspectRatio", root.attrib)

            title = root.find(f"svg:title", vars(ns))
            self.assertTrue(title.text)
