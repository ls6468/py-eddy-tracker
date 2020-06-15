"""
Propagation Histogram
===================

"""
from matplotlib import pyplot as plt
from py_eddy_tracker.observations.tracking import TrackEddiesObservations
from py_eddy_tracker.generic import distance
import py_eddy_tracker_sample
from numpy import arange, empty
from numba import njit


@njit(cache=True)
def cum_distance_by_track(distance, track):
    tr_previous = 0
    d_cum = 0
    new_distance = empty(track.shape, dtype=distance.dtype)
    for i in range(distance.shape[0]):
        tr = track[i]
        if i != 0 and tr != tr_previous:
            d_cum = 0
        new_distance[i] = d_cum
        d_cum += distance[i]
        tr_previous = tr
    new_distance[i + 1] = d_cum
    return new_distance

a = TrackEddiesObservations.load_file(
    py_eddy_tracker_sample.get_path("eddies_med_adt_allsat_dt2018/Anticyclonic.zarr")
)
c = TrackEddiesObservations.load_file(
    py_eddy_tracker_sample.get_path("eddies_med_adt_allsat_dt2018/Cyclonic.zarr")
)
d_a = distance(a.longitude[:-1], a.latitude[:-1], a.longitude[1:], a.latitude[1:])
d_c = distance(c.longitude[:-1], c.latitude[:-1], c.longitude[1:], c.latitude[1:])
d_a = cum_distance_by_track(d_a, a["track"]) / 1000.
d_c = cum_distance_by_track(d_c, c["track"]) / 1000.

# Plot
fig = plt.figure()
ax_propagation = fig.add_axes([0.05, 0.55, 0.4, 0.4])
ax_cum_propagation = fig.add_axes([0.55, 0.55, 0.4, 0.4])
ax_ratio_propagation = fig.add_axes([0.05, 0.05, 0.4, 0.4])
ax_ratio_cum_propagation = fig.add_axes([0.55, 0.05, 0.4, 0.4])


bins = arange(0, 1500, 25)
cum_a, bins, _ = ax_cum_propagation.hist(
    d_a, histtype="step", bins=bins, label="Anticyclonic", color="b"
)
cum_c, bins, _ = ax_cum_propagation.hist(
    d_c, histtype="step", bins=bins, label="Cyclonic", color="r"
)

x = (bins[1:] + bins[:-1]) / 2.0
ax_ratio_cum_propagation.plot(x, cum_c / cum_a)

nb_a, nb_c = cum_a[:-1] - cum_a[1:], cum_c[:-1] - cum_c[1:]
ax_propagation.plot(x[1:], nb_a, label="Anticyclonic", color="b")
ax_propagation.plot(x[1:], nb_c, label="Cyclonic", color="r")

ax_ratio_propagation.plot(x[1:], nb_c / nb_a)


for ax in (ax_propagation, ax_cum_propagation, ax_ratio_cum_propagation, ax_ratio_propagation):
    ax.set_xlim(0, 1000)
    if ax in (ax_propagation, ax_cum_propagation):
        ax.set_ylim(1, None)
        ax.set_yscale("log")
        ax.legend()
    else:
        ax.set_ylim(0, 2)
        ax.set_ylabel("Ratio Cyclonic/Anticyclonic")
    ax.set_xlabel("Propagation (km)")
    ax.grid()