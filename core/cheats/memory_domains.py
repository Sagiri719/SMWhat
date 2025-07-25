from enum import Enum

class Domains(str, Enum):

    CART_RAM = "CARTRAM",
    CART_ROM = "CARTROM",
    WORK_RAM = "WRAM",
    VIDEO_RAM = "VRAM";