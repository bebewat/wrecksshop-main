"""
Ark Survival: Ascended item library
Contains item definitions for the shop system
"""

# Comprehensive item library for Ark Survival: Ascended
ITEM_LIBRARY = [
    # Weapons - Melee
    {
        'name': 'Metal Hatchet',
        'category': 'Weapons',
        'description': 'A sturdy metal hatchet for gathering wood and thatch efficiently.',
        'default_price': 150,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponMetalHatchet.PrimalItem_WeaponMetalHatchet\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponMetalHatchet.PrimalItem_WeaponMetalHatchet',
        'item_id': 'PrimalItem_WeaponMetalHatchet',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Metal Pick',
        'category': 'Weapons',
        'description': 'A metal pickaxe for efficient stone and metal gathering.',
        'default_price': 150,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponMetalPick.PrimalItem_WeaponMetalPick\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponMetalPick.PrimalItem_WeaponMetalPick',
        'item_id': 'PrimalItem_WeaponMetalPick',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Metal Sword',
        'category': 'Weapons',
        'description': 'A sharp metal sword for close combat.',
        'default_price': 200,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponSword.PrimalItem_WeaponSword\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponSword.PrimalItem_WeaponSword',
        'item_id': 'PrimalItem_WeaponSword',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Pike',
        'category': 'Weapons',
        'description': 'A long-reach melee weapon, effective against larger creatures.',
        'default_price': 180,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponPike.PrimalItem_WeaponPike\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponPike.PrimalItem_WeaponPike',
        'item_id': 'PrimalItem_WeaponPike',
        'quality': 'Normal',
        'stackable': False
    },
    
    # Weapons - Ranged
    {
        'name': 'Crossbow',
        'category': 'Weapons',
        'description': 'A powerful ranged weapon that fires bolts.',
        'default_price': 250,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponCrossbow.PrimalItem_WeaponCrossbow\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponCrossbow.PrimalItem_WeaponCrossbow',
        'item_id': 'PrimalItem_WeaponCrossbow',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Longneck Rifle',
        'category': 'Weapons',
        'description': 'A long-range rifle with high damage and accuracy.',
        'default_price': 500,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponOneShotRifle.PrimalItem_WeaponOneShotRifle\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponOneShotRifle.PrimalItem_WeaponOneShotRifle',
        'item_id': 'PrimalItem_WeaponOneShotRifle',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Fabricated Pistol',
        'category': 'Weapons',
        'description': 'A semi-automatic pistol with moderate damage.',
        'default_price': 300,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponGun.PrimalItem_WeaponGun\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponGun.PrimalItem_WeaponGun',
        'item_id': 'PrimalItem_WeaponGun',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Assault Rifle',
        'category': 'Weapons',
        'description': 'A fully automatic rifle with high rate of fire.',
        'default_price': 800,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponMachineGun.PrimalItem_WeaponMachineGun\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItem_WeaponMachineGun.PrimalItem_WeaponMachineGun',
        'item_id': 'PrimalItem_WeaponMachineGun',
        'quality': 'Normal',
        'stackable': False
    },
    
    # Armor Sets
    {
        'name': 'Metal Helmet',
        'category': 'Armor',
        'description': 'Heavy metal helmet providing excellent protection.',
        'default_price': 200,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalHelmet.PrimalItemArmor_MetalHelmet\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalHelmet.PrimalItemArmor_MetalHelmet',
        'item_id': 'PrimalItemArmor_MetalHelmet',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Metal Chestpiece',
        'category': 'Armor',
        'description': 'Heavy metal chestpiece for maximum torso protection.',
        'default_price': 300,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalShirt.PrimalItemArmor_MetalShirt\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalShirt.PrimalItemArmor_MetalShirt',
        'item_id': 'PrimalItemArmor_MetalShirt',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Metal Leggings',
        'category': 'Armor',
        'description': 'Heavy metal leggings for leg protection.',
        'default_price': 250,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalPants.PrimalItemArmor_MetalPants\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalPants.PrimalItemArmor_MetalPants',
        'item_id': 'PrimalItemArmor_MetalPants',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Metal Gauntlets',
        'category': 'Armor',
        'description': 'Heavy metal gauntlets for hand protection.',
        'default_price': 150,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalGloves.PrimalItemArmor_MetalGloves\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalGloves.PrimalItemArmor_MetalGloves',
        'item_id': 'PrimalItemArmor_MetalGloves',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Metal Boots',
        'category': 'Armor',
        'description': 'Heavy metal boots for foot protection.',
        'default_price': 150,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalBoots.PrimalItemArmor_MetalBoots\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Armor/Metal/PrimalItemArmor_MetalBoots.PrimalItemArmor_MetalBoots',
        'item_id': 'PrimalItemArmor_MetalBoots',
        'quality': 'Normal',
        'stackable': False
    },
    
    # Resources
    {
        'name': 'Metal Ingot',
        'category': 'Resources',
        'description': 'Refined metal ingot used in advanced crafting.',
        'default_price': 10,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_MetalIngot.PrimalItemResource_MetalIngot\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_MetalIngot.PrimalItemResource_MetalIngot',
        'item_id': 'PrimalItemResource_MetalIngot',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Polymer',
        'category': 'Resources',
        'description': 'Advanced synthetic material for high-tech crafting.',
        'default_price': 25,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_Polymer.PrimalItemResource_Polymer\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_Polymer.PrimalItemResource_Polymer',
        'item_id': 'PrimalItemResource_Polymer',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Crystal',
        'category': 'Resources',
        'description': 'Rare crystal used in electronics and advanced items.',
        'default_price': 15,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_Crystal.PrimalItemResource_Crystal\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_Crystal.PrimalItemResource_Crystal',
        'item_id': 'PrimalItemResource_Crystal',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Black Pearl',
        'category': 'Resources',
        'description': 'Extremely rare resource obtained from dangerous creatures.',
        'default_price': 100,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_BlackPearl.PrimalItemResource_BlackPearl\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_BlackPearl.PrimalItemResource_BlackPearl',
        'item_id': 'PrimalItemResource_BlackPearl',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Element',
        'category': 'Resources',
        'description': 'The most valuable resource, used for tek-tier items.',
        'default_price': 1000,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_Element.PrimalItemResource_Element\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_Element.PrimalItemResource_Element',
        'item_id': 'PrimalItemResource_Element',
        'quality': 'Normal',
        'stackable': True
    },
    
    # Tools
    {
        'name': 'Spyglass',
        'category': 'Tools',
        'description': 'Allows you to see distant objects and creature levels.',
        'default_price': 120,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Tools/PrimalItem_WeaponSpyglass.PrimalItem_WeaponSpyglass\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Tools/PrimalItem_WeaponSpyglass.PrimalItem_WeaponSpyglass',
        'item_id': 'PrimalItem_WeaponSpyglass',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'GPS',
        'category': 'Tools',
        'description': 'Shows your exact coordinates and location.',
        'default_price': 200,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Tools/PrimalItem_WeaponGPS.PrimalItem_WeaponGPS\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Tools/PrimalItem_WeaponGPS.PrimalItem_WeaponGPS',
        'item_id': 'PrimalItem_WeaponGPS',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Parachute',
        'category': 'Tools',
        'description': 'Single-use parachute for safe falls from great heights.',
        'default_price': 50,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Tools/PrimalItem_WeaponParachute.PrimalItem_WeaponParachute\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Tools/PrimalItem_WeaponParachute.PrimalItem_WeaponParachute',
        'item_id': 'PrimalItem_WeaponParachute',
        'quality': 'Normal',
        'stackable': True
    },
    
    # Consumables
    {
        'name': 'Medical Brew',
        'category': 'Consumables',
        'description': 'Restores a large amount of health over time.',
        'default_price': 30,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemConsumable_HealSoup.PrimalItemConsumable_HealSoup\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemConsumable_HealSoup.PrimalItemConsumable_HealSoup',
        'item_id': 'PrimalItemConsumable_HealSoup',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Energy Brew',
        'category': 'Consumables',
        'description': 'Restores stamina and provides temporary stamina regeneration boost.',
        'default_price': 25,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemConsumable_StaminaSoup.PrimalItemConsumable_StaminaSoup\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemConsumable_StaminaSoup.PrimalItemConsumable_StaminaSoup',
        'item_id': 'PrimalItemConsumable_StaminaSoup',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Lazarus Chowder',
        'category': 'Consumables',
        'description': 'Provides oxygen underwater and improves swimming speed.',
        'default_price': 40,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemConsumable_SwimSoup.PrimalItemConsumable_SwimSoup\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemConsumable_SwimSoup.PrimalItemConsumable_SwimSoup',
        'item_id': 'PrimalItemConsumable_SwimSoup',
        'quality': 'Normal',
        'stackable': True
    },
    
    # Structures
    {
        'name': 'Metal Foundation',
        'category': 'Structures',
        'description': 'Strong metal foundation for advanced building.',
        'default_price': 80,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalFloor.PrimalItemStructure_MetalFloor\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalFloor.PrimalItemStructure_MetalFloor',
        'item_id': 'PrimalItemStructure_MetalFloor',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Metal Wall',
        'category': 'Structures',
        'description': 'Durable metal wall for secure building.',
        'default_price': 60,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalWall.PrimalItemStructure_MetalWall\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalWall.PrimalItemStructure_MetalWall',
        'item_id': 'PrimalItemStructure_MetalWall',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Metal Door',
        'category': 'Structures',
        'description': 'Secure metal door with lock capability.',
        'default_price': 100,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalDoor.PrimalItemStructure_MetalDoor\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalDoor.PrimalItemStructure_MetalDoor',
        'item_id': 'PrimalItemStructure_MetalDoor',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Generator',
        'category': 'Structures',
        'description': 'Electrical generator that runs on gasoline.',
        'default_price': 400,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_PowerGenerator.PrimalItemStructure_PowerGenerator\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_PowerGenerator.PrimalItemStructure_PowerGenerator',
        'item_id': 'PrimalItemStructure_PowerGenerator',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Fabricator',
        'category': 'Structures',
        'description': 'Advanced crafting station for electronics and weapons.',
        'default_price': 600,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Fabricator.PrimalItemStructure_Fabricator\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Fabricator.PrimalItemStructure_Fabricator',
        'item_id': 'PrimalItemStructure_Fabricator',
        'quality': 'Normal',
        'stackable': True
    },
    
    # Saddles
    {
        'name': 'Rex Saddle',
        'category': 'Saddles',
        'description': 'Saddle for the mighty Tyrannosaurus Rex.',
        'default_price': 800,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Armor/Saddles/PrimalItemArmor_RexSaddle.PrimalItemArmor_RexSaddle\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Armor/Saddles/PrimalItemArmor_RexSaddle.PrimalItemArmor_RexSaddle',
        'item_id': 'PrimalItemArmor_RexSaddle',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Argentavis Saddle',
        'category': 'Saddles',
        'description': 'Saddle for the giant Argentavis bird.',
        'default_price': 600,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Armor/Saddles/PrimalItemArmor_ArgentavisSaddle.PrimalItemArmor_ArgentavisSaddle\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Armor/Saddles/PrimalItemArmor_ArgentavisSaddle.PrimalItemArmor_ArgentavisSaddle',
        'item_id': 'PrimalItemArmor_ArgentavisSaddle',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Pteranodon Saddle',
        'category': 'Saddles',
        'description': 'Saddle for the fast-flying Pteranodon.',
        'default_price': 300,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Armor/Saddles/PrimalItemArmor_PteroSaddle.PrimalItemArmor_PteroSaddle\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Armor/Saddles/PrimalItemArmor_PteroSaddle.PrimalItemArmor_PteroSaddle',
        'item_id': 'PrimalItemArmor_PteroSaddle',
        'quality': 'Normal',
        'stackable': False
    },
    {
        'name': 'Trike Saddle',
        'category': 'Saddles',
        'description': 'Saddle for the herbivorous Triceratops.',
        'default_price': 200,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Armor/Saddles/PrimalItemArmor_TrikeSaddle.PrimalItemArmor_TrikeSaddle\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Armor/Saddles/PrimalItemArmor_TrikeSaddle.PrimalItemArmor_TrikeSaddle',
        'item_id': 'PrimalItemArmor_TrikeSaddle',
        'quality': 'Normal',
        'stackable': False
    },
    
    # Ammunition
    {
        'name': 'Advanced Rifle Bullet',
        'category': 'Weapons',
        'description': 'High-damage ammunition for longneck rifles.',
        'default_price': 5,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItemAmmo_AdvancedRifleBullet.PrimalItemAmmo_AdvancedRifleBullet\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItemAmmo_AdvancedRifleBullet.PrimalItemAmmo_AdvancedRifleBullet',
        'item_id': 'PrimalItemAmmo_AdvancedRifleBullet',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Tranquilizer Arrow',
        'category': 'Weapons',
        'description': 'Arrow that inflicts torpor for taming creatures.',
        'default_price': 8,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItemAmmo_ArrowTranq.PrimalItemAmmo_ArrowTranq\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItemAmmo_ArrowTranq.PrimalItemAmmo_ArrowTranq',
        'item_id': 'PrimalItemAmmo_ArrowTranq',
        'quality': 'Normal',
        'stackable': True
    },
    {
        'name': 'Rocket Propelled Grenade',
        'category': 'Weapons',
        'description': 'Explosive ammunition for rocket launchers.',
        'default_price': 100,
        'command': 'GiveItemToPlayer {steam_id} "Blueprint\'/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItemAmmo_Rocket.PrimalItemAmmo_Rocket\'" {quantity} 1 0',
        'blueprint_path': '/Game/PrimalEarth/CoreBlueprints/Items/Weapons/PrimalItemAmmo_Rocket.PrimalItemAmmo_Rocket',
        'item_id': 'PrimalItemAmmo_Rocket',
        'quality': 'Normal',
        'stackable': True
    }
]

# Category definitions for easy filtering
CATEGORIES = [
    'Weapons',
    'Armor',
    'Resources',
    'Tools',
    'Consumables',
    'Structures',
    'Saddles'
]

# Quality levels available
QUALITY_LEVELS = [
    'Primitive',
    'Ramshackle',
    'Apprentice', 
    'Journeyman',
    'Mastercraft',
    'Ascendant',
    'Normal'
]

def get_items_by_category(category: str) -> list:
    """Get all items in a specific category"""
    return [item for item in ITEM_LIBRARY if item['category'] == category]

def get_item_by_name(name: str) -> dict:
    """Get item by name"""
    for item in ITEM_LIBRARY:
        if item['name'].lower() == name.lower():
            return item
    return None

def search_items(query: str) -> list:
    """Search items by name or description"""
    query = query.lower()
    results = []
    
    for item in ITEM_LIBRARY:
        if (query in item['name'].lower() or 
            query in item['description'].lower()):
            results.append(item)
    
    return results

def get_items_by_price_range(min_price: int, max_price: int) -> list:
    """Get items within price range"""
    return [item for item in ITEM_LIBRARY 
            if min_price <= item['default_price'] <= max_price]

def get_most_expensive_items(limit: int = 10) -> list:
    """Get most expensive items"""
    sorted_items = sorted(ITEM_LIBRARY, key=lambda x: x['default_price'], reverse=True)
    return sorted_items[:limit]

def get_cheapest_items(limit: int = 10) -> list:
    """Get cheapest items"""
    sorted_items = sorted(ITEM_LIBRARY, key=lambda x: x['default_price'])
    return sorted_items[:limit]
