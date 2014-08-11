#!/usr/bin/python

import pandas as pd

from thermal import Thermal, ThermalGovernor
from pid_controller import PIDController
from power import InPower, OutPower
import plot_utils

def _plot_power_hists(power_inst, map_label, what, title):
    """Helper function for plot_power_hists

    power_obj is either an InPower() or OutPower() instance.  what is
    a string: "in" or "out"

    """
    freqs = power_inst.get_all_freqs(map_label)
    for actor in freqs:
        this_title = "freq {} {}".format(what, actor)
        this_title = plot_utils.normalize_title(this_title, title)
        xlim = (0, freqs[actor].max())

        plot_utils.plot_hist(freqs[actor], this_title, 20, "Frequency (KHz)",
                             xlim, "default")

class Run(object):
    """A wrapper class that initializes all the classes of a given run"""

    classes = {"thermal": "Thermal",
               "thermal_governor": "ThermalGovernor",
               "pid_controller": "PIDController",
               "in_power": "InPower",
               "out_power": "OutPower",
    }

    def __init__(self, path=None):
        for name, class_name in self.classes.iteritems():
            setattr(self, name, globals()[class_name](path))

    def normalize_time(self, basetime):
        """Normalize the time of all the trace classes"""
        for attr in self.classes.iterkeys():
            getattr(self, attr).normalize_time(basetime)

    def get_all_freqs_data(self, map_label):
        """get a dict of DataFrames suitable for the allfreqs plot"""

        in_freqs = self.in_power.get_all_freqs(map_label)
        out_freqs = self.out_power.get_all_freqs(map_label)

        ret_dict = {}
        for label in map_label.values():
            in_label = label + "_freq_in"
            out_label = label + "_freq_out"

            inout_freq_dict = {in_label: in_freqs[label], out_label: out_freqs[label]}
            ret_dict[label] = pd.DataFrame(inout_freq_dict).fillna(method="pad")

        return ret_dict

    def plot_power_hists(self, map_label, title=""):
        """Plot histograms for each actor input and output power"""

        _plot_power_hists(self.out_power, map_label, "out", title)
        _plot_power_hists(self.in_power, map_label, "in", title)

    def plot_allfreqs(self, map_label, title="", width=None, height=None):
        """Do allfreqs plots similar to those of CompareRuns"""
        all_freqs = self.get_all_freqs_data(map_label)

        for label, dfr in all_freqs.iteritems():
            this_title = plot_utils.normalize_title("allfreqs " + label, title)

            ax = plot_utils.pre_plot_setup(width=width, height=height)
            dfr.plot(ax=ax)
            plot_utils.post_plot_setup(ax, title=this_title)
