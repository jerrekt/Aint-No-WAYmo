# Pre-deployment, handoff and release checklist

This check must be performed on the actual GitHub/Kratos systems by a teammate with authorized access; a checked box in this local ZIP does not constitute verification.

- [ ] Inspect actual Git remote and current `main`; resolve diverged versions before pushing.
- [ ] Review all six roster names and ask for unconfirmed roles before publishing job titles.
- [ ] Confirm `VERSION` from the branch being merged, and bump exactly one suffix relative to current `main`.
- [ ] Confirm logo appearance, mobile layout, map rendering and About navigation on the *served* application.
- [ ] Confirm displayed vehicle status says SIM ONLY unless backed by real telemetry.
- [ ] Verify actual target LXC and unique cloudflared instance/token without reading secrets into logs.
- [ ] Verify only the intended hostname route exists, pointed to container-local origin; no MQTT/SSH/Proxmox public exposure.
- [ ] Verify public GET task list works and anonymous/wrong-password mutations fail.
- [ ] Replace prototype shared password with an individual identity model for production/public task mutation.
- [ ] Verify team task claims persist across sessions/browsers after deployment and status conflicts are handled.
- [ ] Verify task DB backups and restore path.
- [ ] Verify website maps/rooms are treated as provisional and route overlay does not drive physical motors.
- [ ] Verify real ESP32-C3 MQTT ACK latency before suggesting network is robust.
- [ ] Confirm the independent physical E-stop and link-loss safety before enabling S3 motor GPIO.
- [ ] Record deployment, versions, actual working URLs, tests and ownership in Mnemosyne.
- [ ] Keep the stand-alone V1.008 source as a rollback artifact.
