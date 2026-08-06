# Roblox Game 1

A clean Luau and Rojo starter repository for a new Roblox game.

## Project structure

```text
src/
├── client/   Client-only startup code and systems
├── server/   Server-authoritative gameplay code
└── shared/   Modules shared by the client and server
```

Rojo maps these folders into:

```text
ReplicatedStorage/Shared
ServerScriptService/Server
StarterPlayer/StarterPlayerScripts/Client
```

## Start developing

1. Open a terminal in the repository.
2. Install the pinned tools:

```powershell
rokit install
```

3. Start Rojo:

```powershell
rojo serve
```

4. Open a Roblox Studio place.
5. Open the Rojo plugin and connect to the running server.
6. Press **Play**.

The Output window should show:

```text
[Server] Roblox Game 1 initialized
[Client] Roblox Game 1 initialized
```

## Development rules

- Keep important gameplay decisions and validation on the server.
- Treat all client requests as untrusted.
- Put reusable configuration and shared modules in `src/shared`.
- Add systems only when the game concept needs them; keep the starter small.
- Do not commit generated Roblox place files or exported 3D assets.

## Previous asset workspace

The old Blender mannequin generators and documentation were removed from the current working tree so this repository can serve as a clean game project. They remain recoverable from the Git commit history.
