from bitarray import bitarray


def shape_bit_mask(size: int, active_bits) -> bitarray:
    bit_mask = bitarray(size)
    bit_mask.setall(False)
    for i in active_bits:
        bit_mask[i] = True
    return bit_mask


def extract_bit_indices(bits: bitarray) -> set:
    return {idx for idx, bit in enumerate(bits) if bit}

