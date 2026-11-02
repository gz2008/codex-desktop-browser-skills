---
name: chaoxing-coursework
description: Complete Chaoxing/Xuexitong/Learning通 coursework safely through an existing login profile and a headless Edge CDP session. Use when the user asks to open, answer, run, save, or diagnose a Chaoxing assignment without stealing focus or submitting unless explicitly requested.
---

# Chaoxing Coursework

Operate the assignment in the background through Playwright and CDP. Preserve the user's login profile, never handle credentials, and stop before submission unless the user explicitly asks to submit.

## Non-negotiable operating rules

- Do not use `win.activate`, `win.topmost`, coordinate clicks, `mouse.click_capture`, or UIA to drive ordinary web controls. They can raise or scroll the user's Edge and interrupt their foreground work.
- Use a headless Edge process and DOM automation. Do not repeatedly capture screenshots.
- Never ask for, print, extract, copy, or store passwords, cookies, tokens, or session values.
- Automate only assignments the user is authorized to work on and the platform permits automating; do not bypass login, CAPTCHA, or platform controls.
- Read the assignment from the live page. Do not reuse a stale hard-coded assignment URL.
- A request to do homework defaults to **temporary save only**. Never click `提交`, `completeBtn`, `submitValidate()`, or `submitWork()` without explicit submission permission.
- If the requested action cannot be completed headlessly, stop and explain the blocker instead of bringing the browser to the foreground.
- Read [references/headless-cdp.md](references/headless-cdp.md) before starting a new browser session.

## Workflow

1. Use the `c-coursework-verify` skill when the assignment contains C code. Extract every exact prompt and output requirement before editing.
2. Identify the current Edge login profile. The normal Windows profile is:
   `Join-Path $env:LOCALAPPDATA 'Microsoft\Edge\User Data'`
3. Edge rejects remote debugging when `--user-data-dir` points to its default directory. Create a directory junction to the same profile under a dedicated directory in `$env:TEMP`, launch Edge headlessly with the junction path, and remove only the junction during cleanup. Do not copy the profile.
4. If the regular Edge process still holds the profile, close only its verified main window gracefully after checking for unsaved user work. Do not terminate unrelated Edge processes.
5. Launch headless Edge on a verified free local debugging port, connect with Playwright, and navigate to the current course or assignment entry. If authentication is required, expose a single QR screenshot to the user for local scanning and delete it after login.
6. Locate `div.questionLi` elements and extract the prompt, hidden answer type, code editor value, and control IDs from the DOM.
7. Write code with `setCodeContentByBusinessId(id, code)` and immediately verify it with `getCodeContentByBusinessId(id)`.
8. Click each question's `#runBtn`, poll `.runResult`, and require all platform cases to report `Accepted` or `运行结果正确`. If output formatting fails, inspect the run response and change the code; do not guess from screenshots.
9. Synchronize answers through the page's normal save function, exactly once:
   `saveWork({silentSuccess:true, success, failure})`
   Require a response with `status: true` and `msg: "保存成功！"`.
10. Reload the page and compare every persisted editor value with the verified source after normalizing only trailing CR/LF. Confirm `a.completeBtn` still exists, which proves the page remains in the answering state rather than submitted.
11. Close the headless browser using its exact process ID, delete the temporary junction and QR image, and verify the port and process are gone.

Use a temporary directory under `$env:TEMP` for the junction and QR artifact.
Keep the existing Edge profile as the junction target; never copy its contents.

## Assignment DOM

The tested Chaoxing `dowork` page exposes:

- Questions: `div.questionLi`
- Code editors: `textarea.code-editor[data-business-id]`
- Editor API: `setCodeContentByBusinessId(id, code)` and `getCodeContentByBusinessId(id)`
- Run control: `#runBtn`
- Run result textareas: `textarea.runResult`
- Temporary save action: `saveWork(options)`

For exact Playwright snippets, run-response inspection, login handling, and cleanup commands, read [references/headless-cdp.md](references/headless-cdp.md).

## Completion criteria

Do not call the task complete until:

- Every code editor contains the locally verified source.
- Every platform run passes, or the user has been told exactly which case still fails and why.
- The server reports the temporary save succeeded.
- A reload confirms the source persisted.
- The page is still in the answering state and has not been submitted.
- The headless browser, debugging port, junction, and QR artifact are cleaned up.
