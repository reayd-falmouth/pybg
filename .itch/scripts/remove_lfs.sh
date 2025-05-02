#!/bin/bash

git lfs install
git lfs fetch --all
git lfs checkout

lfs_dirs=()

echo "finding lfs files"
for lfs_file in $(git lfs ls-files | sed -r 's/^.{13}//'); do lfs_dirs+=($(dirname "$lfs_file")); done;

echo "found all lfs files"

unique_dirs=()
for unique_dir in ${lfs_dirs}; do unique_dirs+=("$unique_dir/*"); done;

count=${#unique_dirs[@]}

if (($count == 0))
then
echo "No lfs dirs"
exit 0
fi

echo "There are $count unique lfs dirs"

printf -v migrate_paths ',%s' "${unique_dirs[@]}"
migrate_paths=${migrate_paths:1}

echo "performing: git lfs migrate export --include='$migrate_paths' --yes --verbose --everything"
git lfs migrate export --include="$migrate_paths" --yes --verbose --everything
git lfs uninstall
