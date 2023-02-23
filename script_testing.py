import numpy as np

from xml.dom import minidom
import pandas as pd


if __name__ == '__main__':
    fpath = '../BaseEnvironment/jsbsim/jsbsim'
    # fdm = jsbsim.FGFDMExec(fpath, None)
    # fdm.set_debug_level(0)
    #
    # fdm.print_simulation_configuration()
    #
    # fdm.set_output_directive('./data_output/flightgear.xml')
    #
    # fdm.load_script('./scripts/c172_elevation_test.xml')
    # fdm.run_ic()
    #
    # while fdm.run():
    #     pass
    # [lat, lon], alt

    flight_path = pd.read_excel('flight_data_B787.xlsx')
    mToFeet = 3.28084
    waypoints = flight_path.loc[:, ["lat", "lon", "altitude_m", "air_speed_m_per_s"]].values
    # print(waypoints[1])
    locations = []
    for lat, lon, alt, airspeed in waypoints:
        locations.append([np.deg2rad(lat), np.deg2rad(lon), alt*mToFeet, airspeed*mToFeet])

    print(locations[0])
    locs = locations[1:]
    # print(locs)

    wp = {
        "description": None,
        "wp_distance": None,
        "pre_active_wp": None,
        "long": None,
        "lat": None,
        "next_active_wp": None,
        "altitude_setpoint": None,
        "airspeed_setpoint": None,
    }

    w_pts = []
    for idx, pt in enumerate(locs):
        wp = {"description": idx + 1, "wp_distance": 700, "pre_active_wp": idx , "long": pt[1], "lat": pt[0],
              "next_active_wp": idx + 1, "altitude_setpoint": pt[2], "airspeed_setpoint": pt[3]}
        # print(idx, pt)
        w_pts.append(wp)

    print(w_pts)

    print()

    """
    <event name="Set fourth waypoint">
      <description>
        When the distance to the third waypoint is less than 800 feet,
        then set the fourth waypoint.
      </description>
      <condition>
        guidance/wp-distance lt 600
        ap/active-waypoint eq 3
      </condition>
      <set name="guidance/target_wp_latitude_rad" value="0.69921031"/>
      <set name="guidance/target_wp_longitude_rad" value="2.03503645"/>
      <set name="ap/active-waypoint" value="4"/>
      <set name="ap/altitude_setpoint" action="FG_EXP" value="1000.0" tc="1.0"/>
      <set name="ap/airspeed_setpoint" action="FG_EXP" value="" tc="1.0"/>
      <set name="simulation/notify-trigger" value="1"/>
      <notify>
        <property caption="Distance to WP  "> guidance/wp-distance  </property>
       </notify>
    </event>
    """


    events = []
    wp_events = minidom.parseString("<waypoints/>")
    for pt in reversed(w_pts):
        root = wp_events.documentElement

        event = wp_events.createElement('event')
        root.appendChild(event)

        event.setAttribute("name", "Set Waypoint Num: " + str(pt["description"]))

        description = wp_events.createElement('description')
        txt = wp_events.createTextNode("When the distance to waypoint " + str(pt["pre_active_wp"]) + " is less than " + str(pt["wp_distance"]) + " feet, then set the "
                                       + str(pt["next_active_wp"]) + " waypoint.")
        description.appendChild(txt)

        condition = wp_events.createElement('condition')
        condition.setAttribute("logic", "AND")
        txt_cond1 = wp_events.createTextNode("guidance/wp-distance lt " + str(pt["wp_distance"]))
        txt_cond2 = wp_events.createTextNode("ap/active-waypoint eq " + str(pt["pre_active_wp"]))
        condition.appendChild(txt_cond1)
        condition.appendChild(txt_cond2)

        set1 = wp_events.createElement('set')
        set1.setAttribute("name", "guidance/target_wp_latitude_rad")
        set1.setAttribute("value", str(pt["lat"]))

        set2 = wp_events.createElement('set')
        set2.setAttribute("name", "guidance/target_wp_longitude_rad")
        set2.setAttribute("value", str(pt["long"]))

        set3 = wp_events.createElement('set')
        set3.setAttribute("name", "ap/active-waypoint")
        set3.setAttribute("value", str(pt["next_active_wp"]))

        set4 = wp_events.createElement('set')
        set4.setAttribute("name", "simulation/notify-trigger")
        set4.setAttribute("value", "1")

        set5 = wp_events.createElement('set')
        set5.setAttribute("name", "ap/altitude_setpoint")
        set5.setAttribute("type", "value")
        set5.setAttribute("value", str(pt["altitude_setpoint"]))
        # set5.setAttribute("tc", "2.0")
        # set5.setAttribute("action", "FG_EXP")

        set6 = wp_events.createElement('set')
        set6.setAttribute("name", "ap/airspeed_setpoint")
        # set6.setAttribute("type", "value")
        set6.setAttribute("tc", "1.0")
        set6.setAttribute("action", "FG_EXP")
        set6.setAttribute("value", str(pt["airspeed_setpoint"]))

        notify = wp_events.createElement('notify')
        property_not = wp_events.createElement('property')
        property_not.setAttribute("caption", "Distance to WP  ")
        property_not.appendChild(wp_events.createTextNode("guidance/wp-distance"))
        notify.appendChild(property_not)

        event.appendChild(description)
        event.appendChild(condition)
        event.appendChild(set1)
        event.appendChild(set2)
        event.appendChild(set3)
        event.appendChild(set4)
        event.appendChild(set5)
        event.appendChild(set6)
        event.appendChild(notify)

    print(wp_events.toprettyxml())
    path_file = "waypoints.xml"
    with open(path_file, "w") as f:
        f.write(wp_events.toprettyxml())





