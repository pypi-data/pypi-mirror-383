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

import argparse
import datetime
import logging
import pprint
import string
import sys
import tkinter as tk
import tkinter.font
from turtle import Turtle
from turtle import Shape

from plotlines.board import Board


def setup_logger(level=logging.INFO):
    logging.basicConfig(level=level)
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(
            logging.Formatter(
                fmt="{asctime}|{levelname:>8}|{phase.name:^8}| {name:<16}| {path!s:<72}| {message}",
                datefmt=None, style='{',
                # defaults=dict(phase=Phase.CONFIG, path="")
            )
        )


def main(args):
    level = logging.DEBUG if args.debug else logging.INFO
    # setup_logger(level=level)
    logging.basicConfig(level=level)
    logger = logging.getLogger("plotlines")

    args.trails = args.trails or len(args.ending)
    logger.info(f"Start")
    logger.debug(f"{args=}")

    graph = dict(Board.build_graph(**vars(args)))

    if args.format == "plot":
        t = Turtle()
        stamps = []
        stamps.append(t.stamp())

        graph = Board.style_graph(graph)
        graph = Board.layout_graph(graph)
        print(string.ascii_uppercase, file=sys.stderr)
        print(f"{t.screen.getshapes()=}", file=sys.stderr)
        print(f"{stamps=}", file=sys.stderr)

        logger.debug(tk.font.families())
        Board.draw_graph(t, graph, debug=args.debug)
        t.screen.mainloop()
    elif args.format == "svg":
        # TODO: implement Renderer
        logger.warning("SVG output not yet implemented")
    elif args.format == "text":
        pprint.pprint(graph, depth=3)
    elif args.format == "toml":
        print(*Board.toml_graph(graph), sep="\n", file=sys.stdout)

    return 0


class InlineValues:

    def __init__(self, type_=str):
        self.type = type_

    def __call__(self, text, sep=","):
        return [self.type(i.strip()) for i in text.split(sep)]


def parser():
    rv = argparse.ArgumentParser(usage=__doc__, fromfile_prefix_chars="=")
    rv.add_argument("--debug", action="store_true", default=False, help="Display debug information")
    rv.add_argument(
        "--ending", type=InlineValues(str), default=["A"], help="Declare named endings"
    )
    rv.add_argument(
        "--loading", type=InlineValues(int), default=[10, 100],
        help="Define limits for the number of nodes of the story graph"
    )
    rv.add_argument(
        "--trails", type=int, default=None,
        help="Define the number of trails through the story graph"
    )
    rv.add_argument(
        "--format", choices=["plot", "svg", "text", "toml"], default="text",
        help="Specify format of output [text]"
    )
    rv.convert_arg_line_to_args = lambda x: x.split()
    return rv


def run():
    ts = datetime.datetime.now(tz=datetime.timezone.utc)
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
