# -*- coding: utf-8 -*-

# Copyright 2023-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Run Python functions"""

from .common import PostProcessor
from .. import util


class PythonPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        mode = options.get("mode")
        if mode == "eval" or not mode and options.get("expression"):
            self.function = util.compile_expression(options["expression"])
        else:
            spec = options["function"]
            module_name, _, function_name = spec.rpartition(":")
            module = util.import_file(module_name)
            self.function = getattr(module, function_name)

        if archive := self._archive_init(job, options):
            self.run = self.run_archive

        events = options.get("event")
        if events is None:
            events = ("file",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: self.run for event in events}, options)

        if archive:
            self._archive_register(job)

    def run(self, pathfmt):
        self.function(pathfmt.kwdict)

    def run_archive(self, pathfmt):
        kwdict = pathfmt.kwdict
        if self.archive.check(kwdict):
            return
        self.function(kwdict)
        self.archive.add(kwdict)


__postprocessor__ = PythonPP
