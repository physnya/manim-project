#!/usr/bin/env fish
# Activate manimGL virtualenv and add this workspace to PYTHONPATH
if test -f manimGL/bin/activate.fish
    source manimGL/bin/activate.fish
else
    printf "Error: manimGL/bin/activate.fish not found\n" >&2
    return 1
end

set -x PYTHONPATH (pwd) $PYTHONPATH
