#!/usr/bin/env bash
# Publie une release Forgejo à partir d'un tag déjà poussé.
# Remplace "gh release create" (GitHub) avec les mêmes arguments :
#   release.sh TAG [fichiers...] [--title TITRE] [--notes-file FICHIER] [--generate-notes] [--verify-tag]
# Sans --notes-file, les notes listent les commits depuis le tag précédent.
set -euo pipefail

tag=$1; shift
title=$tag
notes_file=
files=()
while [ $# -gt 0 ]; do
  case $1 in
    --title) title=$2; shift 2 ;;
    --notes-file) notes_file=$2; shift 2 ;;
    --generate-notes|--verify-tag) shift ;;
    *) files+=("$1"); shift ;;
  esac
done

if [ -n "$notes_file" ]; then
  body=$(cat "$notes_file")
else
  prev=$(git tag -l 'v*' --sort=-v:refname | grep -vxF "$tag" | head -n1 || true)
  body=$(git log --no-merges --pretty='- %s' ${prev:+"$prev.."}"$tag" | grep -v '^- Release v' || true)
fi

api="${GITHUB_SERVER_URL}/api/v1/repos/${GITHUB_REPOSITORY}"
auth="Authorization: token ${FORGEJO_TOKEN:?FORGEJO_TOKEN manquant}"

id=$(jq -n --arg t "$tag" --arg n "$title" --arg b "$body" '{tag_name:$t,name:$n,body:$b}' \
  | curl -fsS -X POST "$api/releases" -H "$auth" -H 'Content-Type: application/json' -d @- \
  | jq -r .id)
echo "Release $tag créée (id $id)"

for f in "${files[@]}"; do
  curl -fsS -X POST "$api/releases/$id/assets?name=$(basename "$f")" -H "$auth" -F "attachment=@$f" >/dev/null
  echo "  + $(basename "$f")"
done
