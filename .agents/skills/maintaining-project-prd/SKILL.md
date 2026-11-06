---
name: maintaining-project-prd
description: Use when project work changes code, configuration, documentation, assets, or data and before declaring that work complete.
---

# Maintaining the Project PRD

Keep `prd/v1.md` aligned with the implemented project. A project change is not complete until its PRD update is coherent with the existing catalog.

## Workflow

1. Before finishing work that changes project code, configuration, docs, assets, or data, inspect the actual changed files and read the current `prd/v1.md` in full. Find the affected product area and related entries; understand existing structure and status before editing.
2. Update the catalog in place: revise affected descriptions and status, remove or reconcile stale/conflicting entries, and add entries only for real project behavior or explicitly stated requirements. Preserve unrelated content and the document's useful organization. Do not turn the PRD into a dump of changed files or append an isolated note when an existing section should be updated.
3. Make status unambiguous. Mark delivered behavior implemented (`[x]` where the file uses checkboxes); keep future requirements planned (`[ ]`); identify genuinely unfinished work as in progress. Never describe planned or incomplete behavior as implemented, or infer requirements from implementation details.
4. Add a dated change-history entry using the file's existing date style, summarizing the user-visible capability or product area changed. Keep history concise and consistent with the catalog; do not duplicate the whole spec.
5. Review the resulting PRD against the diff: it should accurately cover the change, retain a coherent catalog of the whole project, distinguish implemented from planned/in-progress work, and contain no invented requirements. Then finish the project task.

Skip the PRD update for informational questions that do not change project files, and when the user explicitly says to skip the PRD. For mixed requests, update it if any requested work changes project files unless the user explicitly opts out.
