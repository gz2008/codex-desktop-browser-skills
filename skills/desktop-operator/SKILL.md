---
name: desktop-operator
description: Control the local Windows desktop and Chromium browsers through a persistent Desktop Operator. Use for repeated browser/console actions, native window automation, window capture or OCR, and multi-step UI workflows where starting a new Playwright process for every action would be slow.
---

# Desktop Operator

Use the persistent operator for multi-step UI work. It keeps Playwright, Windows UI Automation, window capture, and Windows OCR in one process. Ordinary browser commands typically return in 10-150 ms instead of restarting a Playwright CLI for each action.

## Locate the runtime

Use `$env:DESKTOP_OPERATOR_HOME` when set; otherwise use
`$HOME\.codex\tools\desktop-operator`:

```powershell
$operatorHome = if ($env:DESKTOP_OPERATOR_HOME) {
    $env:DESKTOP_OPERATOR_HOME
} else {
    Join-Path $HOME '.codex\tools\desktop-operator'
}
$op = Join-Path $operatorHome 'op.ps1'

if (-not (Test-Path -LiteralPath $op)) {
    throw "Desktop Operator not found. Set DESKTOP_OPERATOR_HOME or install https://github.com/gz2008/desktop-operator"
}
```

Read `README.md` in that runtime before using an unfamiliar command. The runtime
deploys its Python environment with `setup.ps1`.

## Fast path

```powershell
& $op system.info
& $op browser.launch_cdp "port=9223" "profile=$HOME\.codex\tmp\cdp-profile" "url=https://example.com"
& $op browser.query "selector=button" "limit=10"
& $op browser.find_text "text=登录"
& $op browser.click "selectors=[\".login-btn\",\"text=登录\"]"
& $op browser.fill "selector=input[name=user]" "value=example"
& $op browser.fill_label "label=云服务器名称" "value=ecs-demo"
& $op browser.pick "label=镜像" "option=Ubuntu" "exact=true"
& $op browser.set_input_files "selector=input[type=file]" "file=D:\path\to\file.zip"
& $op win.list
& $op win.tree "title=记事本" "depth=4" "limit=120"
& $op win.click "title=记事本" "name=保存"
& $op win.capture "title=记事本"
```

The first call starts the daemon automatically. `system.shutdown` stops it; the next call restarts it with current code.

## Operating rules

- Prefer `browser.query` and `browser.find_text`; do not dump a full page snapshot when the target is known.
- For browser work, use CDP first: `browser.launch_cdp` or `browser.attach`, then DOM selectors, `fill`, and `set_input_files`. Do not use OCR + coordinates on a normal web page.
- Never activate, raise, or steal focus from a user's existing app without explicit permission for the current turn. Do not use `win.activate`, `win.topmost`, `mouse.click_capture` with `topmost=true`, or `screen.capture` as routine automation steps. Prefer background CDP/DOM/UIA; if the task cannot proceed without foregrounding the window, stop and ask first.
- For a window covered by another app, use `win.capture` (PrintWindow) instead of screen capture.
- Give click/fill 2-3 candidate selectors and keep the timeout at 3-5 seconds. The operator tries them in order and returns diagnostics on failure.
- Use `batch` for consecutive form actions so one HTTP round trip executes the whole sequence.
- Use `browser.capture_response` for click-triggered APIs, including experiment report checkpoints.
- Prefer `browser.api_get` for report endpoints so the call does not depend on tab state or a UI click.
- Use `browser.fill_label` / `browser.pick` on Chinese console forms; they resolve fields by nearby visible labels and avoid text collisions such as a hidden "密码" nav item.
- Pass `verify=<selector>` when clicking a primary CTA; the operator waits for the post-condition instead of clicking twice.
- The operator clears guide/anti-spam dialogs and retries intercepted clicks. If a modal still blocks, close it explicitly.
- Use `ssh.exec` with a `secret=` name; never put a password in the command line.
- If the CDP page closes, the next browser call re-attaches automatically; `browser.tabs` lists live pages only.
- For a canvas or remote desktop, request permission before screen capture, then use `screen.ocr/find_text/click_text`; coordinates are physical pixels.
- Use `secret.ps1 set/get` for credentials. Never print the value or put it in a tool call.
- Use a separate CDP profile for automation. Do not copy a daily browser profile.
- If the daemon fails, read `operator.log` in `$operatorHome`, run
  `system.shutdown`, then retry.

## Boundaries

- Local machine only; bind stays on `127.0.0.1`.
- Do not use synthetic clicks to bypass a user confirmation or a platform authorization step.
- Ask before destructive clicks, bulk deletes, purchases, or actions affecting an account outside the requested scope.
