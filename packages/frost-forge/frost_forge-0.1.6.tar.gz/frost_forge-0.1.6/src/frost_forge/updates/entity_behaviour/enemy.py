from .entity_movement import move_entity


def enemy(
    chunks, chunk, tile, current_tile, create_tiles, delete_tiles, location, health
):
    if (
        abs(chunk[0] * 16 + tile[0] - location["tile"][0] * 16 - location["tile"][2])
        + abs(chunk[1] * 16 + tile[1] - location["tile"][1] * 16 - location["tile"][3])
        == 1
    ):
        health -= 1
    elif (
        max(
            abs(
                chunk[0] * 16 + tile[0] - location["tile"][0] * 16 - location["tile"][2]
            ),
            abs(
                chunk[1] * 16 + tile[1] - location["tile"][1] * 16 - location["tile"][3]
            ),
        )
        < 8
    ):
        create_tiles, delete_tiles = move_entity(
            chunks, chunk, tile, current_tile, create_tiles, delete_tiles, 1, location
        )
    else:
        create_tiles, delete_tiles = move_entity(
            chunks, chunk, tile, current_tile, create_tiles, delete_tiles, 0, location
        )
    return create_tiles, delete_tiles, health
