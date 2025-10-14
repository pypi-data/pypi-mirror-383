Data:
    Velocity max(x_vel = 1, y_vel = 1, z_vel = 1, angular_vel = 1)
    Location wy (latitude: 40.4137286054638, longitude: -79.9489233699767, altitude: 10, heading: 0)


Actions:
    TakeOff t1(take_off_altitude: 10)
    SetGlobalPosition goto_wy(location = wy, heading_mode = _, altitude_mode = _, max_velocity = max)

Mission:
    Start t1
    During t1:
        done -> goto_wy
        