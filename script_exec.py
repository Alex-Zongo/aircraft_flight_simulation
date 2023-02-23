import jsbsim
import time

### Simulation Properties
sleep_period = 0.1
realtime = True
nice = False
suspend = False
end = 1E99


fdm = jsbsim.FGFDMExec("./jsbsim_data")
fdm.load_model("787-8")
# fdm.load_ic("787-8_init_pos.xml", True)
fdm.load_script('scripts/787-8_bj_xian.xml')

fdm.run_ic()
fdm.print_simulation_configuration()

frame_duration = fdm.get_delta_t()
sleep_nseconds = (frame_duration if realtime else sleep_period) * 1E9
current_seconds = initial_seconds = time.time()
result = fdm.run()

if suspend:
    fdm.hold()

while result and fdm.get_sim_time() <= end:
    fdm.check_incremental_hold()
    if fdm.holding():
        suspend = True
        paused_seconds = time.time() - current_seconds
        result = fdm.run()
    else:
        if realtime:
            if suspend:
                initial_seconds += paused_seconds
                suspend = False
            current_seconds = time.time()
            actual_elapsed_time = current_seconds - initial_seconds
            sim_lag_time = actual_elapsed_time - fdm.get_sim_time()

            for _ in range(int(sim_lag_time / frame_duration)):
                result = fdm.run()
                current_seconds = time.time()
                if fdm.holding():
                    break
        else:
            result = fdm.run()

    if nice:
        time.sleep(sleep_nseconds / 1000000.0)