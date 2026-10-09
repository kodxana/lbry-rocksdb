#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
if [ ! -f src/rocksdb/include/rocksdb/db.h ]; then
    echo 'Initialize the pinned source with: git submodule update --init' >&2
    exit 1
fi

output_dir=${TEST_OUTPUT_DIR:-ci-results}
mkdir -p "$output_dir"
image_file=$(mktemp)
container=
cleanup() {
    if [ -n "$container" ]; then
        docker rm -f "$container" >/dev/null
    fi
    rm -f "$image_file"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

docker build --progress=plain --iidfile "$image_file" \
    --build-arg JOBS="${JOBS:-2}" -f docker/Dockerfile.test .
container=$(docker create --network none --cpus 2 --memory 4g \
    "$(cat "$image_file")")
status=0
docker start -a "$container" || status=$?
if [ "$status" -eq 0 ]; then
    status=$(docker inspect --format '{{.State.ExitCode}}' "$container")
fi
docker logs "$container" > "$output_dir/tests.log" 2>&1
docker cp "$container:/results/." "$output_dir/"
exit "$status"
