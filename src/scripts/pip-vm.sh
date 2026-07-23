#!/usr/bin/env bash
#
# pip-vm.sh — git-bundle SYNC of planning-is-prompting to the cloud-test VM (lupin-host-test).
#
# Purpose: make PIP a REAL git checkout on the VM (a browsable/trackable clone), sibling of lupin,
# via the same bundle mechanism lupin uses. PIP has NO running service — so this is the SYNC HALF
# ONLY (bundle -> scp -> fetch/clone -> checkout). There is nothing to restart, no `deploy`.
#
# Why a bundle (not push-repo): push-repo archives tracked files @ HEAD and STRIPS .git, giving a
# flat copy. Rick wants a git-trackable checkout on the VM, so we ship a `git bundle` (a portable,
# offline stand-in for a remote) and clone/fetch from it. The VM has no GitHub creds, so the bundle
# file IS its origin remote.
#
# COMMITTED WORK ONLY: `git bundle create <file> <branch>` packs the branch's committed tip.
# Working-tree edits, staged-but-uncommitted changes, and untracked files are EXCLUDED by
# construction. ⇒ commit before you sync, or the VM gets the branch's LAST COMMIT, not your editor.
#
# Reference pattern: lupin/src/scripts/lupin-vm.sh @ da64318e, do_push_bundle() + the push-bundle
# case (Mr Radio 🦉). This variant drops the server-restart/deploy half and adds a first-run
# BOOTSTRAP (lupin's do_push_bundle assumes the VM checkout already exists to `git fetch` into;
# PIP's first sync has no checkout yet, so it clones from the bundle instead).
#
# Usage:
#   src/scripts/pip-vm.sh push-bundle [branch]              # sync code (bootstrap clone OR fetch+checkout)
#   src/scripts/pip-vm.sh --dry-run push-bundle [branch]    # echo the plan, run nothing
#
# Env:
#   LUPIN_GCP_PROJECT_ID   REQUIRED — GCP project id (no default; abort if unset).
#   LUPIN_VM_NAME          optional — instance name (default: lupin-host-test)
#   LUPIN_VM_ZONE          optional — zone          (default: us-central1-a)
#
# Self-contained: no repo dependencies — copy this one file anywhere with gcloud + IAP access.

set -euo pipefail

# ---- config (overridable via env) ----------------------------------------
VM_NAME="${LUPIN_VM_NAME:-lupin-host-test}"
VM_ZONE="${LUPIN_VM_ZONE:-us-central1-a}"
VM_ROOT="/mnt/lupin-data/planning-is-prompting"                 # on-VM checkout, sibling of lupin
VM_BUNDLE="/mnt/lupin-data/planning-is-prompting-wip.bundle"    # PIP's own bundle (its VM "origin")
VM_OWNER="1001:1001"                                            # UID-1001-owned (matches lupin deploy)

DRY_RUN=0

log() { echo "[pip-vm] $*"; }
die() { echo "[pip-vm] FATAL: $*" >&2; exit 1; }

usage() {
    cat >&2 <<EOF
pip-vm.sh — git-bundle sync of planning-is-prompting to $VM_NAME ($VM_ZONE)

Usage: pip-vm.sh [--dry-run] push-bundle [branch]

  push-bundle [branch]   sync THIS repo's <branch> (default: current branch) to the VM as a real
                         git checkout at $VM_ROOT.
                         First run: clones from the bundle (bootstrap). Later runs: fetch + checkout.
                         COMMITTED work only — commit before you sync. No server restart (PIP has none).

Env: LUPIN_GCP_PROJECT_ID (required), LUPIN_VM_NAME, LUPIN_VM_ZONE
EOF
}

# ---- flags ---------------------------------------------------------------
if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN=1
    shift
fi

SUBCMD="${1:-}"
[ -n "$SUBCMD" ] || { usage; exit 2; }
shift || true

# ---- project id (fail loud — a silent default can act on the wrong project) ----
require_project() {
    : "${LUPIN_GCP_PROJECT_ID:?Set LUPIN_GCP_PROJECT_ID (e.g. export LUPIN_GCP_PROJECT_ID=hello-world-foo-423219)}"
}

# ---- bundle + (clone|fetch) + checkout — the sync primitive ---------------
# Bundles THIS repo's <branch>, ships it, and on the VM either clones it (first run) or fetches +
# checks it out (subsequent runs). The overwritten bundle file stays as the checkout's origin, so a
# plain `git fetch`/`pull` on the VM keeps working after this script hands off.
#   $1 branch   (empty ⇒ this repo's current branch)
do_push_bundle() {
    local branch="$1"
    require_project
    local repo_root
    repo_root="$( git -C "$( dirname "${BASH_SOURCE[0]}" )" rev-parse --show-toplevel 2>/dev/null )" \
        || die "must run from inside the planning-is-prompting git checkout (the bundle is built here)"
    [ -n "$branch" ] || branch="$( git -C "$repo_root" rev-parse --abbrev-ref HEAD )"
    local safe="-c safe.directory=$VM_ROOT"        # root's gitconfig lacks the 1001-owned-repo exception

    # Remote plan: cp the bundle into place, then bootstrap-clone if there's no checkout yet, else
    # fetch + checkout. Ownership is restored to 1001 after every root-side git op.
    local rcmd="set -e
cp /tmp/pip-wip.bundle $VM_BUNDLE && rm -f /tmp/pip-wip.bundle
if [ ! -d $VM_ROOT/.git ]; then
  echo '== bootstrap: cloning from bundle =='
  sudo rm -rf $VM_ROOT
  sudo git clone -b $branch $VM_BUNDLE $VM_ROOT
  sudo chown -R $VM_OWNER $VM_ROOT
  echo CLONED
else
  echo '== refresh: fetch + checkout =='
  cd $VM_ROOT
  sudo git $safe fetch origin $branch
  sudo git $safe checkout -B $branch FETCH_HEAD
  sudo chown -R $VM_OWNER .
  echo CHECKED_OUT
fi
git $safe -C $VM_ROOT log --oneline -1
git $safe -C $VM_ROOT rev-parse --abbrev-ref HEAD"

    log "bundling branch '$branch' from $repo_root"
    if [ "$DRY_RUN" -eq 1 ]; then
        log "(dry-run) git bundle create <tmp> $branch; scp -> $VM_NAME:/tmp/pip-wip.bundle; then on VM:"
        printf '%s\n' "$rcmd" >&2
        return 0
    fi

    local bundle_tmp
    bundle_tmp="$( mktemp -t pip-bundle-XXXXXX.bundle )"
    git -C "$repo_root" bundle create "$bundle_tmp" "$branch" || die "git bundle failed"
    log "scp bundle -> $VM_NAME:/tmp/pip-wip.bundle"
    gcloud compute scp "$bundle_tmp" "$VM_NAME:/tmp/pip-wip.bundle" \
        --zone="$VM_ZONE" --project="$LUPIN_GCP_PROJECT_ID" --tunnel-through-iap
    rm -f "$bundle_tmp"
    log "syncing bundle -> $VM_ROOT on $VM_NAME"
    gcloud compute ssh "$VM_NAME" \
        --zone="$VM_ZONE" --project="$LUPIN_GCP_PROJECT_ID" --tunnel-through-iap \
        --command "$rcmd"
}

# ---- dispatch ------------------------------------------------------------
case "$SUBCMD" in
    push-bundle)
        BRANCH=""
        for a in "$@"; do
            case "$a" in
                --*) die "push-bundle: unknown flag $a" ;;
                *)   [ -z "$BRANCH" ] && BRANCH="$a" ;;
            esac
        done
        do_push_bundle "$BRANCH"
        ;;

    -h|--help|help)
        usage
        ;;

    *)
        die "unknown subcommand: $SUBCMD  (try: pip-vm.sh --help)"
        ;;
esac
