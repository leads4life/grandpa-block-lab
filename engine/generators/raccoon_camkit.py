"""Camera sight-blockers for the Raccoon Lift scenes (west of the cabin): the waterwheel and the trip hammer (Episode 1's
machine, from make_ep01_s009), so no spinning spoke or swinging hammer ever crosses Grandpa's face."""
WHEEL_BOX = ((-5.12, 0.38, -0.05), (-4.88, 1.62, 1.18))
MACHINE = [((-4.47, 0.93, 0.62), (-4.33, 1.95, 0.92)),            # the helve (it rises with the cams)
           ((-4.57, 1.73, 0.0), (-4.23, 2.17, 0.75)),             # the anvil and the hammer head
           ((-4.57, 1.23, 0.0), (-4.43, 1.37, 0.82)),             # the pivot frame
           ((-4.95, 0.92, 0.48), (-4.05, 1.08, 0.62))]            # the axle and the cams
BLOCKERS = [WHEEL_BOX] + MACHINE
