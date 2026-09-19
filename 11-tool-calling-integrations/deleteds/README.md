# deleteds/

Parked, not deleted. None of these is needed to set up or run the assistant
(`main.py` + `personal_assistant/`), and nothing in the project imports them.
Each is a one-topic lesson demo whose code is already printed in the matching
file under `docs/`. Delete the whole folder when you're sure you don't want
them (`git rm -r deleteds/`).

| File | What it was | Why it's parked |
|---|---|---|
| `00_setup.py` | Built a Gemini client and read `.env` | Nothing used its client; `personal_assistant/config.py` + `llm.py` do this. Its smoke test is now a one-liner in the README |
| `01_function_calling_recap.py` | `add_numbers` toy tool | Unrelated to the assistant |
| `02_rest_apis.py` | Random-fact API as a tool | Unrelated to the assistant |
| `04_gmail_tool.py` | Raw Gmail read/send | Same logic lives in `personal_assistant/gmail_tool.py` |
| `05_calendar_tool.py` | Raw free/busy + create event | Same logic lives in `personal_assistant/calendar_tool.py` |
| `06_maps_tool.py` | Raw geocode + directions | Same logic lives in `personal_assistant/maps_tool.py` |
| `07_authentication_demo.py` | Prints the three auth patterns | Demo only |

## Running one anyway

They import `personal_assistant`, which resolves from the module root, so run
them from there with `PYTHONPATH=.`:

```bash
PYTHONPATH=. ./.venv/bin/python deleteds/06_maps_tool.py
```

`04_gmail_tool.py` sends a real email and prints snippets of your inbox, and
`05_calendar_tool.py` creates a real calendar event.
