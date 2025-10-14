#   
#   This file is part of HILO-MPC
#
#   HILO-MPC is a toolbox for easy, flexible and fast development of machine-learning-supported
#   optimal control and estimation problems
#
#   Copyright (c) 2021 Johannes Pohlodek, Bruno Morabito, Rolf Findeisen
#                      All rights reserved
#
#   HILO-MPC is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as
#   published by the Free Software Foundation, either version 3
#   of the License, or (at your option) any later version.
#
#   HILO-MPC is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with HILO-MPC. If not, see <http://www.gnu.org/licenses/>.
#

# NOTE: Adapted from pandas plotting functionality

from .plot import *
from ...util.util import is_list_like


PLOT_CLASSES = {
    'line': LinePlot,
    'dashed': DashedPlot,
    'dotted': DottedPlot,
    'dashdot': DashDotPlot,
    'step': StepPlot,
    'scatter': ScatterPlot
}


def plot(data, kind, **kwargs):
    """

    :param data:
    :param kind:
    :param kwargs:
    :return:
    """
    if is_list_like(kind):
        plot_obj = MultiPlot(data, kind, **kwargs)
    else:
        plot_obj = PLOT_CLASSES[kind](data, **kwargs)
    plot_obj.generate()
    plot_obj.draw()
    return plot_obj.result


__all__ = []
