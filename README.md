# CalmSpace

**A fullscreen space for the moment right after you get furious** — or right before you say something you'd have to clean up for months.

CalmSpace takes over your entire screen, breathes with you, and refuses to let you leave until you type a single word. That word is the speed bump between the impulse and the keyboard.

![CalmSpace](preview.png)

---

## What it does

- **Takes the whole screen.** Borderless, no address bar, no tabs, nothing to click away.
- **Breathes with you.** A 4-7-8 cycle (inhale 4s / hold 7s / exhale 8s) driven by a slowly expanding ring with a phase countdown. The long exhale is the part that actually tells your body it's safe.
- **Gives you something to think about.** 17 lines that rotate every 16 seconds — observations, then questions aimed inward. *"Is the thing you want to solve the problem, or to make them hurt too?"*
- **Waits out the chemistry.** At 90 seconds it says so out loud: the surge has usually crested by then. A concrete reason to stay one more minute.
- **Lets you write it down, then let it go.** Anything you type there fades into drifting light and is gone. Nothing is saved, anywhere.
- **Offers quiet.** Brown noise synthesized live in the browser — no audio files, and its volume swells and settles with your breath.
- **Only one way out.** `Esc`, `F11`, `F5`, `Ctrl+W` and friends are blocked, right-click is disabled, and there are no buttons to close. You have to type the leave word in the input at the bottom.

The interface is in Chinese; the leave word is `离开` (lí kāi). You only ever have to type it — never say it out loud.

## Quick start

Double-click **`start.bat`**.

Edge opens in kiosk mode at your screen's full resolution. Breathe. When you're done, type `离开` in the box at the bottom and press Enter — the screen fades out, the window closes itself, and you're back on your desktop.

## Requirements

- Windows 10 / 11
- Python 3 (already installed on most machines; `start.bat` looks for it and tells you if it can't find it)
- Microsoft Edge or Google Chrome

## How it works

```
start.bat
  └─ launcher.py
       ├─ serves index.html from a tiny server bound to 127.0.0.1 only
       ├─ launches Edge/Chrome with --kiosk --app=<url>?kiosk=1
       │    (with a throwaway --user-data-dir, so it never touches your own browser session)
       └─ waits. On exit it runs taskkill /F /T on the browser process,
          shuts the server down, and deletes the throwaway profile.
```

The page calls `/__exit__` only after you type the leave word; that request is what triggers the shutdown. The port is random, the server binds to localhost only, and it lives exactly as long as the window does.

`index.html` also works standalone — open it directly and it asks for fullscreen itself (the exit falls back to `window.close()`).

## Honest limits

- `Alt+F4` still closes the window. No web page can stop the OS, and pretending otherwise would be a lie. It's a speed bump and a room, not a jail.
- If the very first launch ever shows an empty Edge window, close it and start again — a throwaway profile occasionally needs one warm-up. `error.log` appears in this folder if anything fails.
- Not therapy and not medical advice. If this kind of anger is a regular visitor, or if anyone is at risk, it deserves real help, not a script.

## Everything is local

The page makes no external requests, no telemetry, no accounts. Nothing is written to disk — the only exception is an `error.log` in this folder if something crashes. Your typed words exist in browser memory and vanish when you let them go, or when the window closes.

## License

No license file yet — all rights reserved by default.

---

*The name is the whole spec: a space that is calm.*
