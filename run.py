from h2mony import H2mony
import sys

h2mony = H2mony()
if len(h2mony.device_list) > 0:
    device = h2mony.device_list[0]
    h2mony.explore_for_hopping(device)