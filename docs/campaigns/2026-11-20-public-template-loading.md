# Public translation page verification

The retired app's landing page and upload dashboard can now load on a case-sensitive filesystem. Django searched for `templates`, while the repository ships `Templates`. A single letter in the settings file changed. The HTML files are identical to the base revision.

| Revision | Commit |
| --- | --- |
| Original main and comparison base | `4e1c8d09e5e836dac78a9ec78a21feae5e7c38a2` |
| First implementation | `ec7af0ff3c8692b23f1298af1b32e2ec47062bfc` |
| Reviewed code | `62c6727573ebe1b30c11f4e593898f7da24383ff` |

## What was tested

| Check | Original | Reviewed |
| --- | --- | --- |
| GET / and /dashboard/ on a case-sensitive HFS+ volume | Both raised TemplateDoesNotExist | Both returned HTTP 200 |
| GET / and /dashboard/ on a case-insensitive volume | Both returned HTTP 200 | Both returned HTTP 200 |
| Original five tests using unittest and Django | Five passed with each runner on each filesystem | All five still passed |
| New test for both pages using unittest and Django | Failed on both filesystems after copying just the new test onto the base | Passed with each runner on each filesystem, six tests total per run |
| Django system check | Passed | Passed on both filesystems |

The regression requests both real routes and checks the expected page content. On case-insensitive systems it also compares the resolved template directory's spelling with its parent directory's entries. The independently compared responses matched the working base response after normalizing the random CSRF tokens.

A generated Word document was uploaded through the Django client using a temporary migrated database and upload directory. Two simulated HTTP replies exercised extraction, comparison and response rendering. The check verified the original file's saved bytes, submitted an edited translation to the download endpoint, reopened the generated Word file and verified its heading and edited paragraph. GET on the download endpoint returned HTTP 405. This journey passed on the working base filesystem and on both candidate filesystems. The provider was simulated throughout.

The campaign's native browser opened the candidate from the case-sensitive volume. The landing page displayed "Hello this is my app". The dashboard displayed "Upload File", "Document Translation Comparison", and the empty upload state. The server returned 200 for both pages and was stopped after inspection. The browser check covered those two pages. The upload and download checks used Django's client.

## Review and acceptance

A fresh implementation worker changed `translation/settings.py` and added `tests/test_public_pages.py`. An independent reviewer examined both files, the callers, the two test runners and the comparison data. The reviewer found that the first candidate could fail during Django test discovery. The worker fixed setup timing, and the reviewer accepted the corrected commit for behavior and engineering standards. The project owner verified the base, committed two-file diff, routes, tests and fictional document round trip.

The in-repository tests can be rerun from the reviewed checkout with its pinned requirements and a fictional local signing key:

~~~sh
DJANGO_SECRET_KEY=local-verification-only python -m unittest discover -s tests
DJANGO_SECRET_KEY=local-verification-only python manage.py test tests
~~~

The October retirement decision in `SECURITY_CLEANUP.md` still governs this application. This finding concerns local use. The fixtures used a new database and generated document. Live provider behavior and a production installation were outside the exercise.
