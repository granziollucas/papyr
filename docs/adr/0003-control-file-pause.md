Title: Control-file pause/resume mechanism
Date: 2026-01-22
Status: Accepted

Context
- Cross-platform keyboard capture is unreliable.
- Papyr requires pause, resume, and stop controls during long searches.

Decision
- Use a control file `.papyr_control` in the run folder.
- Commands: PAUSE, RESUME, STOP.

Alternatives considered
- Global keyboard hooks (OS-specific and brittle).
- TCP control socket (adds complexity and firewall issues).

Consequences / trade-offs
- User must create/edit a file to control runs.
- Simple and reliable across platforms.
