#!/bin/sh
# Delete a (regenerable) path. Used between size groups in merge->eval chains to
# keep at most one large FP16 merged checkpoint on work3 at a time (pool6 quota).
# Usage: TARGET=/abs/path bsub < scripts/hpc/cleanup_path.sh
#BSUB -J cleanup_path
#BSUB -q hpc
#BSUB -n 1
#BSUB -R "rusage[mem=2GB]"
#BSUB -W 00:10
#BSUB -o logs/cleanup_path_%J.out
#BSUB -eo logs/cleanup_path_%J.err

set -e
if [ -z "${TARGET:-}" ]; then echo "ERROR: TARGET unset"; exit 1; fi
case "$TARGET" in
    /work3/s242779/models/models/merged/*) ;;  # only ever delete regenerable merged checkpoints
    *) echo "ERROR: refusing to delete '$TARGET' (not a work3 merged checkpoint)"; exit 1 ;;
esac
echo "Removing $TARGET"
rm -rf "$TARGET"
echo "Done. Remaining merged dirs:"
ls -d /work3/s242779/models/models/merged/* 2>/dev/null || true
