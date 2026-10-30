# Colorway proposals — V1.003 draft

These are **three selectable design treatments of the same Mini-Waymo application**, not separate products. All existing app behavior and the pending V1.002 task-board API are preserved.

- **Ride Blue:** white map-first Waymo-app-inspired layout, dark blue header, electric blue actions, mint-green status. Best for public presentation.
- **Midnight Navigation:** ink/navy dark mode, bright blue route emphasis, seafoam highlights. Best for projected high-contrast demo.
- **Mint Circuit:** softer off-white and green/teal surfaces with pale mint highlights. Best for an approachable SME/student identity.

Switch using the header buttons; the choice persists locally per browser. Open `Mini_Waymo_V12_Demo.html` or `Mini_Waymo_V12_About.html` locally to preview. Add `?colorway=blue`, `?colorway=night` or `?colorway=mint` to select a theme from a URL. Theme switching does not send requests to the server.

**Scope:** Prototype only; actual deployment to Kratos not verified. Shared task changes require `/api/tasks` and server-side `WAYMO_TEAM_TASK_PASSWORD` as specified in `docs/TEAM_BOARD_DEPLOYMENT.md`. Never place the password in website HTML or Git.

**Version:** V1.003 is an unmerged draft; V1.000 remains the initial GitHub baseline until approved updates are merged in sequence. Historical simulator V12 naming retained for compatibility.
