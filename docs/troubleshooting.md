# Troubleshooting

## "An error occurred. Please check the log"
Check the latest file under `logs/run_<timestamp>.log`.

## Crossref disabled
If you skipped Crossref polite setup, it will be disabled. Run `papyr init` to configure it.

## SSRN disabled
SSRN is disabled by default. Only enable if you have explicit permission.

## No results
- Try broader keywords
- Remove filters
- Increase limit

## Downloads fail
- Papyr only downloads legitimate PDFs.
- Check that the record has an official PDF URL.

## Control file not working
- Ensure `.papyr_control` is in the output directory
- Commands are case-insensitive: PAUSE/RESUME/STOP
