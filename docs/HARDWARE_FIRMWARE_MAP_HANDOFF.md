# Hardware, navigation and map handoff — Mini-Waymo Micro

## Robot target

- **Primary:** self-contained driveable World's Littlest Waymo Jaguar I-PACE diecast model. Measure its *inside* dimensions before final motors, battery, driver board, wheelbase, shell modifications or printed chassis.
- **Main controller planned:** Seeed XIAO ESP32-S3 Sense (camera), local motor/sensor processing; Kratos assists high-level missions, map, telemetry and history.
- **Candidate components:** 2 ultra-small geared DC motors in differential-drive arrangement, compact DRV8835/DRV8833 dual driver (confirm voltage/current/pinout), VL53L7CX 8x8 ToF forward depth sensor, small IMU/wheel odometry, 1S LiPo + protected charge/power, amber turn indicators, tiny sounder, hardware motor power-cut.
- **Unverified:** exact shell scale/internal envelope, motor mounting space across axle, battery fit/discharge, camera window/metal shell antenna performance, cooling and current load. No purchased candidate implies fit.

## Safety invariants

1. **E-stop must be physical and independent** of Wi-Fi and Kratos: motor supply interruption and nonautomatic restart.
2. Local ESP32 watchdog and obstacle sensing must stop the car on stale commands, dropped link, sensor faults and uncertain pose.
3. Remote STOP is an additional command, **not a substitute** for hardware stop.
4. S3 firmware in `firmware/` is intentionally motor-disabled bench scaffolding; don't enable unverified motor wiring.
5. C3 receive-only code in `bench/esp32-c3/` tests command messages and ACK RTT, **no hardware GPIO outputs**. Test on trusted private LAN; report measured median, p95, max, losses and reconnect time only after running against real Kratos.

## Survey and floor plan

- Second floor of SJSU IS Building; C/U-shaped hallway estimated from user's hand sketch and iPhone Measure readings.
- **North hallway ~168 ft**, **south ~168 ft**, **east ~300 ft**; these are rough *travel lengths*, not verified architectural dimensions or accurately digitized waypoints.
- User validated the rough south room sequence **200–214**, with bottom right **214**, but the bitmap includes some duplicated/misread printed labels (e.g. 205, 223). Verify visible text before assigning coordinates.
- East rooms include **220, 221, 219C, 218B, 217, two 216 doors** (one double/one single), and an **Aviation Club Room below the 216 doors**, plus 245 near the lower junction. The elevator was shifted north by about one room interval in prior markup. Men's restroom near upper inner east wall; women's below elevator; an additional unisex restroom and stairs were marked on the user sketch; positions require verification against the latest image.
- The *visible* V1.008 map uses `maps/reference/is_building_user_map_2026-10-29.png` and `maps/reference/is_building_dark_presentation.png` — preserve geometry and label uncertainties; latest handwritten details may not all be reflected in the displayed bitmap.
- Existing browser route overlay is synthetic. Physical localization needs known room markers, wheel/sensor calibration and safe stop if confidence is low.

## Defer until after main car

Optional detachable FPV trailer may hold battery, compatible DJI O4 camera/air unit and fan. User has Goggles 3 and iPhone; proposed spectator feed is **DJI air unit -> Goggles 3 -> iPhone DJI Fly -> Discord screen share -> presentation PC**. Unverified compatibility/cooling/size/reception/latency; video is for spectators only, not driving.

## Immediate engineering checklist

Measure internal shell and axle/wheel wells; mock fit with paper/3D tray; bench motor driver (no car shell); flash C3 benchmark and measure RTT; verify C3 API vs backend; power design and battery safety; bench VL53L7CX; select pilot hallway route, measure doorway positions/markers; only then integrate the real diecast and run low-speed supervised trials.
