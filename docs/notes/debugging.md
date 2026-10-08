# Debugging Notes

## Map distortion during turns (Phase 3)

**Symptom.** The live `/map` degrades while driving, worst on long slow ~90°
turns: walls appear doubled, corners smear, the grid stretches or shifts, and
the robot occasionally appears to jump in RViz.

**Measurement.** `odom_yaw_test.py` commands a fixed yaw rate for a fixed
duration in simulation time and accumulates yaw from two independent sources:
`/odom` (what the DiffDrive plugin believes) and `gz model -m my_robot -p`
(what the physics engine actually did). Result:

| commanded yaw rate | nominal turn | odom yaw | true yaw | ratio |
|---|---|---|---|---|
| _fill in_ | | | | |

**Root cause.** _Write this in your own words once the number is in._

**Fix.** _One change, with the prediction you made before running it._

---

## Zero-byte maps

`map_saver_cli` produced 0-byte `.pgm`/`.yaml` files. _Record what the actual
cause turned out to be._ `scripts/save_map.sh` now refuses to exit 0 unless
both output files are non-empty.
