#!/bin/env bash
Version=$1
Message="$2"

if [ "$Version" == '' ]; then
    echo "Please provide version number"
    exit 1
fi
if [ "$Message" == '' ]; then
    echo "Please provide commit message"
    exit 1
fi
source .venv/bin/activate
uv build
rename 'linux_x86_64' 'manylinux1_x86_64' dist/*.whl
git add -f dist/*.whl
git add src/
git commit -am "$Message"
git push
twine upload dist/whitepossum-"${Version}"*