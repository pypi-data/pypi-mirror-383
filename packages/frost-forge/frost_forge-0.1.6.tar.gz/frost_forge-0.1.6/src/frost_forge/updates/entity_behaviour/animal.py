from .entity_movement import move_entity
from ...info import ATTRACTION


def animal(
    chunks,
    chunk,
    tile,
    current_tile,
    create_tiles,
    delete_tiles,
    location,
    inventory_key,
):
    if (
        max(
            abs(
                chunk[0] * 16 + tile[0] - location["tile"][0] * 16 - location["tile"][2]
            ),
            abs(
                chunk[1] * 16 + tile[1] - location["tile"][1] * 16 - location["tile"][3]
            ),
        )
        < 8
        and inventory_key == ATTRACTION[current_tile["kind"]]
    ):
        create_tiles, delete_tiles = move_entity(
            chunks, chunk, tile, current_tile, create_tiles, delete_tiles, 1, location
        )
    else:
        create_tiles, delete_tiles = move_entity(
            chunks, chunk, tile, current_tile, create_tiles, delete_tiles, 0, location
        )
    return create_tiles, delete_tiles
