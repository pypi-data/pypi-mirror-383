import uuid
from typing import Union, Optional

class UUIDClass(bytes):
    def __new__(cls, input_uuid: Union[str, uuid.UUID, None] = None) -> bytes:
        if not input_uuid:
            return None

        if isinstance(input_uuid, uuid.UUID):
            return input_uuid.bytes
        elif isinstance(input_uuid, str):
            try:
                return uuid.UUID(input_uuid).bytes
            except ValueError:
                print(f"Validation Error: '{input_uuid}' is not a valid UUID format.")
                return None
        else:
            print(f"Validation Error: Input type {type(input_uuid)} not supported for UUID.")
            return None
# --- Examples ---

# Valid string UUID
#obj1 = UUIDClass("a1b2c3d4-e5f6-7890-1234-567890abcdef")
#print(f"Object 1 UUID (Bytes): {obj1}")
