#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Svara app icons from the user's actual Svara icon (lossless PNG embedded)."""
from PIL import Image
import os, io, base64

# Lossless 192x192 RGBA PNG of the user's Svara icon, embedded as base64
ICON_B64 = "
