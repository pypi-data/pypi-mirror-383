from .point import left, up
from ..entity_behaviour.animal import animal
from ..entity_behaviour.enemy import enemy
from .machine import machine
from .growth import grow
from ...info import ATTRIBUTES, GROW_TILES, FPS


def update_tile(
    current_tile,
    chunks,
    chunk,
    tile,
    delete_tiles,
    create_tiles,
    tick,
    location,
    inventory_key,
    health,
):
    if current_tile["kind"] in GROW_TILES:
        chunks[chunk][tile] = grow(current_tile)
        if chunks[chunk][tile] == {}:
            delete_tiles.append((chunk, tile))
    elif current_tile["kind"] == "left":
        chunks, delete_tiles = left(chunks, chunk, tile, delete_tiles)
    elif current_tile["kind"] == "up":
        chunks, delete_tiles = up(chunks, chunk, tile, delete_tiles)
    elif "machine" in ATTRIBUTES.get(current_tile["kind"], ()):
        chunks = machine(chunks, chunk, tile, current_tile, tick)
    elif tick % (FPS // 6) == 0:
        if "animal" in ATTRIBUTES.get(current_tile["kind"], ()):
            create_tiles, delete_tiles = animal(
                chunks,
                chunk,
                tile,
                current_tile,
                create_tiles,
                delete_tiles,
                location,
                inventory_key,
            )
        elif "enemy" in ATTRIBUTES.get(current_tile["kind"], ()):
            create_tiles, delete_tiles, health = enemy(
                chunks,
                chunk,
                tile,
                current_tile,
                create_tiles,
                delete_tiles,
                location,
                health,
            )
    return chunks, create_tiles, delete_tiles, health
