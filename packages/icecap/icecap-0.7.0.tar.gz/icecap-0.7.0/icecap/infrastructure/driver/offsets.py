#### Global Offsets ####
CLIENT_CONNECTION_OFFSET = 0x00C79CE0
LOCAL_PLAYER_GUID_STATIC_OFFSET = 0x00CA1238

#### Object Manager Offsets ####
# Relative to the client connection address.
OBJECT_MANAGER_OFFSET = 0x2ED0

# Relative to object manager address.
FIRST_OBJECT_OFFSET = 0xAC
LOCAL_PLAYER_GUID_OFFSET = 0xC0

#### Object Offsets ####
# Relative to the object address.
OBJECT_TYPE_OFFSET = 0x14
OBJECT_GUID_OFFSET = 0x30
NEXT_OBJECT_OFFSET = 0x3C
UNIT_X_POSITION_OFFSET = 0x798
GAME_OBJECT_X_POSITION_OFFSET = 0xE8
OBJECT_FIELDS_OFFSET = 0x8

# Relative to the object address.
UNIT_NAMEBLOCK_OFFSET = 0x964
UNIT_NAMEBLOCK_NAME_OFFSET = 0x5C


#### Name Store Offsets ####
NAME_STORE_BASE = 0x00C5D938 + 0x8
NAME_MASK_OFFSET = 0x24
NAME_TABLE_ADDRESS_OFFSET = 0x1C
NAME_NODE_NAME_OFFSET = 0x20

#### Map Offsets ####
# Relative to the object manager address.
MAP_ID_OFFSET = 0xCC
