import sys

from ecole.core import RandomGenerator, seed, spawn_random_generator, MarkovError, Default

import ecole.version
import ecole.data
import ecole.observation
import ecole.reward
import ecole.information
import ecole.scip
import ecole.instance
import ecole.dynamics
import ecole.environment

__version__ = "{v.major}.{v.minor}.{v.patch}".format(v=ecole.version.get_ecole_lib_version())
