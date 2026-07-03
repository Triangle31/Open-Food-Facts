#!/bin/bash
set -e

echo "Starting Neo4j initialization script..."

DB_PATH="/data/databases/neo4j"
DUMP_PATH="/dumps/neo4j.dump"

if [ ! -d "$DB_PATH" ] || [ -z "$(ls -A "$DB_PATH" 2>/dev/null)" ]; then
  echo "Neo4j database is empty."

  if [ -f "$DUMP_PATH" ]; then
    echo "Loading Neo4j dump..."
    neo4j-admin database load neo4j \
      --from-path=/dumps \
      --overwrite-destination=true
    echo "Neo4j dump loaded."
  else
    echo "No dump found, skipping restore."
  fi
else
  echo "Neo4j database already exists, skipping restore."
fi

echo "Starting Neo4j..."
exec /startup/docker-entrypoint.sh neo4j