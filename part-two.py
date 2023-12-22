#!/usr/bin/env python3

import os
from time import perf_counter_ns
from string import ascii_uppercase

id = (f'{id1}{id2}{id3}' for id1 in ascii_uppercase for id2 in ascii_uppercase for id3 in ascii_uppercase)

class Block:
    Layers = {}

    def __init__(self, position, slab):
        self.x, self.y, self.z = position
        self.slab = slab
        if self.z not in Block.Layers:
            Block.Layers[self.z] = {}
        Block.Layers[self.z][(self.x, self.y)] = self
    
    def can_fall(self):
        if self.z == 1:
            return False
        if self.z - 1 in Block.Layers and (self.x, self.y) in Block.Layers[self.z - 1]:
            block_below = Block.Layers[self.z - 1][(self.x, self.y)]
            if block_below.slab.id != self.slab.id:
                block_below.slab.supports.add(self.slab.id)
                self.slab.supported_by.add(block_below.slab.id)
                return False
        return True

    def fall(self):
        Block.Layers[self.z].pop((self.x, self.y))
        self.z -= 1
        if self.z not in Block.Layers:
            Block.Layers[self.z] = {}
        Block.Layers[self.z][(self.x, self.y)] = self

class Slab:
    Collection = {}

    def __init__(self, coords):
        self.id = next(id)
        Slab.Collection[self.id] = self
        dirs = (1 if (coords[1][0] - coords[0][0]) >= 0 else -1, 1 if (coords[1][1] - coords[0][1])>= 0 else -1, 1 if (coords[1][2] - coords[0][2]) >= 0 else -1)
        self.blocks = [
            Block((ix, iy, iz), self)
            for ix in range(coords[0][0], coords[1][0] + 1, dirs[0])
            for iy in range(coords[0][1], coords[1][1] + 1, dirs[1])
            for iz in range(coords[0][2], coords[1][2] + 1, dirs[2])
        ]
        self.supports = set()
        self.lowest_point = min(map(lambda b: b.z, self.blocks))
    
    def fall(self):
        self.supports = set()
        self.supported_by = set()
        can_fall = True
        for block in self.blocks:
            can_fall = block.can_fall() and can_fall
        if not can_fall:
            return False
        blocks_bottom_to_top = sorted(self.blocks, key = lambda b: b.z)
        for block in blocks_bottom_to_top:
            block.fall()
        return True

def answer(input_file):
    start = perf_counter_ns()
    with open(input_file, 'r') as input:
        slabs = [Slab(tuple(map(lambda x: tuple(map(int,x.split(','))), slab.split('~')))) for slab in input.read().split('\n')]

    keep_falling = True
    while keep_falling:
        keep_falling = False
        slabs_bottom_to_top = sorted(slabs, key = lambda s: s.lowest_point)
        for slab in slabs_bottom_to_top:
            keep_falling = slab.fall() or keep_falling

    candidates_for_demolition = set()
    for slab in slabs:
        if len(slab.supports) != 0:
            for supported_slab in slab.supports:
                if len(Slab.Collection[supported_slab].supported_by) == 1:
                    candidates_for_demolition.add(slab)

    answer = 0
    for slab in candidates_for_demolition:
        demolished_slabs = set()
        slabs_to_check = {slab_id for slab_id in slab.supports}
        while supported_slab_id := slabs_to_check.pop() if slabs_to_check else False:
            supported_slab = Slab.Collection[supported_slab_id]
            remaining_supports = supported_slab.supported_by - {slab.id} - demolished_slabs
            if len(remaining_supports) == 0:
                demolished_slabs.add(supported_slab_id)
                slabs_to_check.update(supported_slab.supports)
        answer += len(demolished_slabs)

    end = perf_counter_ns()

    print(f'The answer is: {answer}')
    print(f'{((end-start)/1000000):.2f} milliseconds')

input_file = os.path.join(os.path.dirname(__file__), 'input')
answer(input_file)
