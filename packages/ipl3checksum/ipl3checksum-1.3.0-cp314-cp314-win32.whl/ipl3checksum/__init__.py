#!/usr/bin/env python3

# SPDX-FileCopyrightText: © 2023-2024 Decompollaborate
# SPDX-License-Identifier: MIT

from __future__ import annotations

# Version should be synced with pyproject.toml, Cargo.toml and src/rs/version.rs
__version_info__: tuple[int, int, int] = (1, 3, 0)
__version__ = ".".join(map(str, __version_info__))  # + "-dev0"
__author__ = "Decompollaborate"

from .ipl3checksum import *  # noqa: F403

from . import frontends as frontends
