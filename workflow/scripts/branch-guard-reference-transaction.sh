#!/bin/sh
# branch-guard: reference-transaction hook (installed by workflow/scripts/branch_guard.py)
#
# A Claude session may not create a branch. Rick's ruling, 2026-09-29 (row 0a9b1d68):
# trust WHO is asking, not what the branch is called — a name allowlist is one any
# worker can forge by typing a plausible `wip-v…` name.
#
#   Who                                   Result
#   a human terminal (no CLAUDECODE)       allowed, recorded in the ledger as "human"
#   a Claude session (CLAUDECODE=1)        REFUSED, whatever the name
#   ... with BRANCH_GUARD_ALLOW=<reason>   allowed, recorded as "allow:<reason>"
#                                          (the spawner's seat branch, the reaper's rescue branch)
#
# Only the CREATION of refs/heads/* is judged. Commits to an existing branch, deletions,
# tags, remote-tracking refs, stash and HEAD all pass untouched.
#
# SELF-CONTAINED POSIX sh on purpose: the containers run git against the same .git, and a
# hook that calls out to a script by host path would fail there and block every commit.
#
# This is the BACKSTOP. An agent with a shell can still get around a local hook
# (core.hooksPath, editing .git/hooks, unsetting CLAUDECODE). The PreToolUse guard denies
# those, and the census flags any branch the ledger does not know.
#
# Known hole, measured on git 2.34: `git branch -m` renames without a ref transaction, so
# this hook never sees it. The census catches the new name.

[ "$1" = "prepared" ] || exit 0

common_dir=$( git rev-parse --git-common-dir 2>/dev/null ) || exit 0
ledger="$common_dir/branch-ledger.tsv"
stamp=$( date -u +%Y-%m-%dT%H:%M:%SZ )
status=0

while read -r old new ref; do
    case "$ref" in refs/heads/*) ;; *) continue ;; esac
    case "$new" in *[!0]*) ;; *) continue ;; esac                  # a deletion
    git rev-parse --verify --quiet "$ref" >/dev/null && continue  # already exists: an update

    if [ "$CLAUDECODE" = "1" ] && [ -z "$BRANCH_GUARD_ALLOW" ]; then
        echo "branch-guard: refusing to create ${ref#refs/heads/}: Claude sessions may not create branches." >&2
        echo "branch-guard: commit in your seat's tree; the manager lands your work by merge." >&2
        status=1
        continue
    fi

    who="human"
    [ -n "$BRANCH_GUARD_ALLOW" ] && who="allow:$BRANCH_GUARD_ALLOW"
    printf '%s\t%s\t%s\t%s\n' "$stamp" "$who" "$ref" "$new" >> "$ledger" 2>/dev/null
done

exit $status
