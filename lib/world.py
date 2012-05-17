"""
Game world for "mh"

this will create a pickle that can be read by the library
"""

from lib2d.server.area import AbstractArea, Area
from lib2d.common.avatar import Avatar, Animation, StaticAnimation
from lib2d.common.objects import AvatarObject
from lib2d.common import res
from lib.rpg import Hero, NPC
from lib.buildarea import fromTMX

from collections import defaultdict


def build():
    # build the initial environment
    uni = AbstractArea()
    uni.name = 'MH'
    uni.setGUID(0)

    # build our avatars and heros
    avatar = Avatar()
    ani = Animation("warrior-male-stand.png", "stand", 1, 4)
    avatar.add(ani)
    ani = Animation("warrior-male-walk.png", "walk", [0,1,2,1], 4)
    avatar.add(ani)
    ani = Animation("warrior-male-attack.png", "attack", 4, 4, 60)
    avatar.add(ani)
    avatar.play("walk")
    npc = Hero()
    npc.setName("Rat")
    npc.setAvatar(avatar)
    npc.setGUID(1)
    uni.add(npc)


    avatar = Avatar()
    ani = Animation("townfolk-male-walk.png", "walk", [0,1,2,1], 4)
    avatar.add(ani)
    npc = NPC()
    npc.setName("Mayor")
    npc.setAvatar(avatar)
    npc.setGUID(2)
    uni.add(npc)


    avatar = Avatar()
    ani = Animation("ranger-male-walk.png", "walk", [0,1,2,1], 4)
    avatar.add(ani)
    npc = NPC()
    npc.setName("Bolt")
    npc.setAvatar(avatar)
    npc.setGUID(3)
    uni.add(npc)


    avatar = Avatar()
    ani = Animation("healer-male-walk.png", "walk", [0,1,2,1], 4)
    avatar.add(ani)
    npc = NPC()
    npc.setName("Ax")
    npc.setAvatar(avatar)
    npc.setGUID(4)
    uni.add(npc)


    avatar = Avatar()
    ani = Animation("healer-female-walk.png", "walk", [0,1,2,1], 4)
    avatar.add(ani)
    npc = NPC()
    npc.setName("Tooth")
    npc.setAvatar(avatar)
    npc.setGUID(5)
    uni.add(npc)


    avatar = Avatar()
    ani = Animation("magician-male-walk.png", "walk", [0,1,2,1], 4)
    avatar.add(ani)
    npc = NPC()
    npc.setName("Nail")
    npc.setAvatar(avatar)
    npc.setGUID(6)
    uni.add(npc)


    avatar = Avatar()
    ani = StaticAnimation("16x16-forest-town.png", "barrel", (9,1), (16,16))
    avatar.add(ani)
    item = AvatarObject()
    item.pushable = True
    item.setName("Barrel")
    item.setAvatar(avatar)
    item.setGUID(513)
    uni.add(item)

    avatar = Avatar()
    ani = StaticAnimation("16x16-forest-town.png", "sign", (11,1), (16,16))
    avatar.add(ani)
    item = AvatarObject()
    item.pushable = False
    item.setName("Sign")
    item.setAvatar(avatar)
    item.setGUID(514)
    uni.add(item) 

    avatar = Avatar()
    ani = StaticAnimation("16x16-forest-town.png", "rock", (8,9), (16,16))
    avatar.add(ani)
    item = AvatarObject()
    item.pushable = True
    item.setName("Rock")
    item.setAvatar(avatar)
    item.setGUID(515)
    uni.add(item) 

    avatar = Avatar()
    ani = StaticAnimation("16x16-forest-town.png", "stump", (8,7), (16,16))
    avatar.add(ani)
    item = AvatarObject()
    item.pushable = False
    item.setName("Stump")
    item.setAvatar(avatar)
    item.setGUID(516)
    uni.add(item) 

    avatar = Avatar()
    ani = StaticAnimation("16x16-forest-town.png", "stump", (8,7), (16,16))
    avatar.add(ani)
    item = AvatarObject()
    item.pushable = False
    item.setName("Stump")
    item.setAvatar(avatar)
    item.setGUID(517)
    uni.add(item) 

    avatar = Avatar()
    ani = StaticAnimation("16x16-forest-town.png", "stump", (8,7), (16,16))
    avatar.add(ani)
    item = AvatarObject()
    item.pushable = False
    item.setName("Stump")
    item.setAvatar(avatar)
    item.setGUID(518)
    uni.add(item) 

    avatar = Avatar()
    ani = StaticAnimation("16x16-forest-town.png", "stump", (8,7), (16,16))
    avatar.add(ani)
    item = AvatarObject()
    item.pushable = False
    item.setName("Stump")
    item.setAvatar(avatar)
    item.setGUID(519)
    uni.add(item)

    avatar = Avatar()
    ani = StaticAnimation("16x16-forest-town.png", "stump", (8,7), (16,16))
    avatar.add(ani)
    item = AvatarObject()
    item.pushable = False
    item.setName("Stump")
    item.setAvatar(avatar)
    item.setGUID(520)
    uni.add(item)



    # build the areas to explore

    village = fromTMX(uni, "village.tmx")
    village.setName("Village")
    village.setGUID(5001)


    home = fromTMX(uni, "building0.tmx")
    home.setName("Building0")
    home.setGUID(5002)


    # finialize exits by adding the needed references

    allAreas = [ i for i in uni.getChildren() if isinstance(i, Area) ]
    allExits = defaultdict(list)

    # make table of all exits
    for area in allAreas:
        for guid in area.exits.keys():
            allExits[guid].append(area)

    # set the exits properly
    for guid, areaList in allExits.items():
        if len(areaList) == 2:
            areaList[0].exits[guid] = (areaList[0].exits[guid][0], areaList[1].guid)
            areaList[1].exits[guid] = (areaList[1].exits[guid][0], areaList[0].guid)


    return uni
