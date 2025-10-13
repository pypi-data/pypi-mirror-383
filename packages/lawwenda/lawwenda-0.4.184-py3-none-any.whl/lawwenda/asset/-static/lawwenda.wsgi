# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only

import os
import sys


# Set this to the path of the 'lawwenda' module (so it must end with
# "/lawwenda"). This directory contains "server.py" and some others.
lawwenda_dir = {lawwenda_dir}

# Set this to the path of the Lawwenda configuration directory, or `None` if you
# want to use the default location.
config_dir = {config_dir}

os.chdir(lawwenda_dir)  # not required but security paranoia :)
sys.path.append(os.path.dirname(lawwenda_dir))
import lawwenda.app.main_app
import lawwenda.config
application = lawwenda.app.main_app.MainApp(configuration=lawwenda.config.Configuration(config_dir))
