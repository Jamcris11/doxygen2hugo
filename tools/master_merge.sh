git checkout dev

previous_build=$(git log --oneline | grep -m 1 -o 'build v[0-9]\+.[0-9]\+.[0-9]\+' | awk '{print $2}')

major=$(grep 'MAJOR_BUILD' .ENV | awk '{print $NF}')
previous_major="$(echo $previous_build | cut -d '.' -f1)"
previous_minor="$(echo $previous_build | cut -d '.' -f2)"

if test "$1" = "--new-minor" && test "$major" = "$previous_major"; then
	minor=$((previous_minor+1))
elif test "$major" = "$previous_major"; then
	minor=$previous_minor
else
	minor=0
fi

if test "$1" != "--new-minor"; then
	last_commits_since_last_merge=$(echo $previous_build | sed 's/\./ /g' | awk '{ print $NF }')
	commits_since_last_merge=$(($last_commits_since_last_merge + $(git log --oneline --decorate | sed '/build v/q' | wc -l)))
else
	commits_since_last_merge=$(git log --oneline --decorate | sed '/build v/q' | wc -l)
fi

new_build="build $major.$minor.$commits_since_last_merge"

echo -e "\n--Your new build number (check this is correct!)--"
echo "$previous_build -> $new_build"
echo -e "--------------------------------------------------\n"

read -p "Are you ready to merge into the master branch? (y/n): " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi

git checkout master
git pull
git merge --squash dev
git commit -m "$new_build"
git checkout dev
git merge master
