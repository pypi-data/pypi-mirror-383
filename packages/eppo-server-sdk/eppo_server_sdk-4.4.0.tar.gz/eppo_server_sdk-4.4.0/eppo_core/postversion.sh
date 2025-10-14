#!/usr/bin/env sh
set -eux

VERSION="$(jq -r .version ./package.json)"

cargo set-version -p eppo_core "$VERSION"

# ruby-sdk is in a separate workspace, so we need to update it independently
cargo upgrade --manifest-path ../ruby-sdk/ext/eppo_client/Cargo.toml --pinned -p eppo_core@="$VERSION"

# Elixir
cargo upgrade --manifest-path ../elixir-sdk/native/sdk_core/Cargo.toml --pinned -p eppo_core@="$VERSION"
