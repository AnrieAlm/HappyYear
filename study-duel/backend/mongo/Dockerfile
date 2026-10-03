# Only needed if you choose to self-host MongoDB on Render instead of using
# Atlas. Referenced by the commented-out `study-duel-db` service in render.yaml.
#
# Set MONGO_INITDB_ROOT_USERNAME / MONGO_INITDB_ROOT_PASSWORD in Render, and
# point the API's MONGO_URI at:
#   mongodb://<user>:<pass>@study-duel-db:27017/study_duel?authSource=admin
FROM mongo:7

# Render mounts the persistent disk at /data/db; declare it in render.yaml too.
VOLUME ["/data/db"]
EXPOSE 27017
CMD ["mongod", "--bind_ip_all"]
