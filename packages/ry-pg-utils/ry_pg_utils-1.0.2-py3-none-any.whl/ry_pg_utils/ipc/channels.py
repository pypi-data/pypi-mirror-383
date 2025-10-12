from ry_redis_bus.channels import Channel

from ry_pg_utils.pb_types.database_pb2 import DatabaseConfigPb  # pylint: disable=no-name-in-module
from ry_pg_utils.pb_types.database_pb2 import (  # pylint: disable=no-name-in-module
    DatabaseNotificationPb,
)
from ry_pg_utils.pb_types.database_pb2 import (  # pylint: disable=no-name-in-module
    DatabaseSettingsPb,
)

# Channels
DATABASE_CHANNEL = Channel("DATABASE_CHANNEL", DatabaseConfigPb)
DATABASE_CONFIG_CHANNEL = Channel("DATABASE_CONFIG_CHANNEL", DatabaseSettingsPb)
DATABASE_NOTIFY_CHANNEL = Channel("DATABASE_NOTIFY_CHANNEL", DatabaseNotificationPb)
