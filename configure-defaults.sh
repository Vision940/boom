#!/usr/bin/env bash

#TODO: run this in server install

template="install-config.json-template"
genCfg="${template%-template}"
idx=0

echo "{" > "$genCfg"
while IFS= read cfgItem; do
  if (( idx > 0 )); then
    echo "," >> "$genCfg"
  fi
  path="$(jq -r '.path[]' <<<"$cfgItem")"
  value="$(jq -r '.value' <<<"$cfgItem")"
  if [[ "$value" =~ "$" ]]; then
    value="$(eval echo "$value")"
  fi
  echo -n "  \"$path\": \"$value\"" >> "$genCfg"
  ((idx++))
done < <(jq -c 'paths(scalars) as $p | {path:$p, value:getpath($p)}' install-config.json-template)
echo -e "\n}" >> "$genCfg"

