"""
Ark Item Library - Contains definitions for Ark Survival Ascended items
"""

import json
import logging
from typing import Dict, List, Optional

class ItemLibrary:
    """Library of Ark Survival Ascended items with blueprints and metadata"""
    
    def __init__(self):
        """Initialize the item library"""
        self.items = self._load_item_data()
        self.categories = self._build_categories()
    
    def _load_item_data(self) -> List[Dict]:
        """Load item data - in a full implementation this would load from files or API"""
        return [
            # Weapons
            {
                "id": "rifle",
                "name": "Assault Rifle",
                "category": "Weapons",
                "type": "Weapon",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Weapons/PrimalItem_WeaponRifle.PrimalItem_WeaponRifle",
                "description": "A powerful assault rifle for ranged combat",
                "level_requirement": 55,
                "suggested_price": 150,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi AssaultRifle 1 100 false"
            },
            {
                "id": "longneck",
                "name": "Longneck Rifle",
                "category": "Weapons", 
                "type": "Weapon",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Weapons/PrimalItem_WeaponOneShotRifle.PrimalItem_WeaponOneShotRifle",
                "description": "High-damage sniper rifle for long-range combat",
                "level_requirement": 35,
                "suggested_price": 100,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi LongneckRifle 1 100 false"
            },
            {
                "id": "shotgun",
                "name": "Pump-Action Shotgun",
                "category": "Weapons",
                "type": "Weapon", 
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Weapons/PrimalItem_WeaponShotgun.PrimalItem_WeaponShotgun",
                "description": "Close-range shotgun with devastating damage",
                "level_requirement": 39,
                "suggested_price": 120,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi Shotgun 1 100 false"
            },
            {
                "id": "fabricatedpistol",
                "name": "Fabricated Pistol",
                "category": "Weapons",
                "type": "Weapon",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Weapons/PrimalItem_WeaponMachinedPistol.PrimalItem_WeaponMachinedPistol",
                "description": "Advanced semi-automatic pistol",
                "level_requirement": 45,
                "suggested_price": 80,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi MachinedPistol 1 100 false"
            },
            
            # Armor
            {
                "id": "riothelmet",
                "name": "Riot Helmet",
                "category": "Armor",
                "type": "Armor",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Riot/PrimalItemArmor_RiotHelmet.PrimalItemArmor_RiotHelmet",
                "description": "Heavy-duty riot helmet with excellent protection",
                "level_requirement": 52,
                "suggested_price": 100,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi RiotHelmet 1 100 false"
            },
            {
                "id": "riotchest",
                "name": "Riot Chestpiece",
                "category": "Armor",
                "type": "Armor",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Riot/PrimalItemArmor_RiotShirt.PrimalItemArmor_RiotShirt",
                "description": "Heavy riot armor chestpiece",
                "level_requirement": 52,
                "suggested_price": 150,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi RiotShirt 1 100 false"
            },
            {
                "id": "riotgloves",
                "name": "Riot Gloves",
                "category": "Armor",
                "type": "Armor",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Riot/PrimalItemArmor_RiotGloves.PrimalItemArmor_RiotGloves",
                "description": "Protective riot gloves",
                "level_requirement": 52,
                "suggested_price": 75,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi RiotGloves 1 100 false"
            },
            {
                "id": "riotboots",
                "name": "Riot Boots",
                "category": "Armor",
                "type": "Armor",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Riot/PrimalItemArmor_RiotBoots.PrimalItemArmor_RiotBoots",
                "description": "Heavy-duty riot boots",
                "level_requirement": 52,
                "suggested_price": 75,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi RiotBoots 1 100 false"
            },
            {
                "id": "riotpants",
                "name": "Riot Leggings",
                "category": "Armor",
                "type": "Armor",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Riot/PrimalItemArmor_RiotPants.PrimalItemArmor_RiotPants",
                "description": "Protective riot leggings",
                "level_requirement": 52,
                "suggested_price": 100,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi RiotPants 1 100 false"
            },
            
            # Tools
            {
                "id": "chainsawBP",
                "name": "Chainsaw",
                "category": "Tools",
                "type": "Tool",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Tools/PrimalItem_ChainSaw.PrimalItem_ChainSaw",
                "description": "Powerful chainsaw for harvesting wood and thatch",
                "level_requirement": 60,
                "suggested_price": 200,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi Chainsaw 1 100 false"
            },
            {
                "id": "metalaxe",
                "name": "Metal Hatchet",
                "category": "Tools",
                "type": "Tool",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Tools/PrimalItem_WeaponMetalHatchet.PrimalItem_WeaponMetalHatchet",
                "description": "High-quality metal hatchet for harvesting",
                "level_requirement": 25,
                "suggested_price": 50,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi MetalHatchet 1 100 false"
            },
            {
                "id": "metalpick",
                "name": "Metal Pick",
                "category": "Tools",
                "type": "Tool",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Tools/PrimalItem_WeaponMetalPick.PrimalItem_WeaponMetalPick",
                "description": "High-quality metal pickaxe for mining",
                "level_requirement": 25,
                "suggested_price": 50,
                "quality_range": [1, 100],
                "spawn_command": "cheat gfi MetalPick 1 100 false"
            },
            
            # Resources
            {
                "id": "metal",
                "name": "Metal Ingot",
                "category": "Resources",
                "type": "Resource",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_MetalIngot.PrimalItemResource_MetalIngot",
                "description": "Refined metal ingot used in advanced crafting",
                "level_requirement": 1,
                "suggested_price": 2,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi MetalIngot 1 1 false"
            },
            {
                "id": "polymer",
                "name": "Polymer",
                "category": "Resources",
                "type": "Resource",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_Polymer.PrimalItemResource_Polymer",
                "description": "Advanced polymer material for high-tech items",
                "level_requirement": 1,
                "suggested_price": 5,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi Polymer 1 1 false"
            },
            {
                "id": "electronics",
                "name": "Electronics",
                "category": "Resources",
                "type": "Resource",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_Electronics.PrimalItemResource_Electronics",
                "description": "Complex electronics for advanced technology",
                "level_requirement": 1,
                "suggested_price": 8,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi Electronics 1 1 false"
            },
            {
                "id": "element",
                "name": "Element",
                "category": "Resources",
                "type": "Resource",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Resources/PrimalItemResource_Element.PrimalItemResource_Element",
                "description": "Rare element used for tek-tier items",
                "level_requirement": 1,
                "suggested_price": 50,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi Element 1 1 false"
            },
            
            # Structures
            {
                "id": "metalfoundation",
                "name": "Metal Foundation",
                "category": "Structures",
                "type": "Structure",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalFoundation.PrimalItemStructure_MetalFoundation",
                "description": "Strong metal foundation for building",
                "level_requirement": 25,
                "suggested_price": 30,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi MetalFoundation 1 1 false"
            },
            {
                "id": "metalwall",
                "name": "Metal Wall",
                "category": "Structures",
                "type": "Structure",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalWall.PrimalItemStructure_MetalWall",
                "description": "Durable metal wall",
                "level_requirement": 25,
                "suggested_price": 25,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi MetalWall 1 1 false"
            },
            {
                "id": "metalgate",
                "name": "Metal Behemoth Gateway",
                "category": "Structures",
                "type": "Structure",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalGate_Large.PrimalItemStructure_MetalGate_Large",
                "description": "Large metal gateway for big dinosaurs",
                "level_requirement": 25,
                "suggested_price": 150,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi MetalGate_Large 1 1 false"
            },
            
            # Consumables
            {
                "id": "stimulant",
                "name": "Stimulant",
                "category": "Consumables",
                "type": "Consumable",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemConsumable_Stimulant.PrimalItemConsumable_Stimulant",
                "description": "Increases movement speed and stamina",
                "level_requirement": 20,
                "suggested_price": 15,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi Stimulant 1 1 false"
            },
            {
                "id": "bloodpack",
                "name": "Blood Pack",
                "category": "Consumables",
                "type": "Consumable",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemConsumable_BloodPack.PrimalItemConsumable_BloodPack",
                "description": "Restores health over time",
                "level_requirement": 30,
                "suggested_price": 20,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi BloodPack 1 1 false"
            },
            {
                "id": "medicalbrewbp",
                "name": "Medical Brew",
                "category": "Consumables", 
                "type": "Consumable",
                "blueprint": "/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemConsumable_HealSoup.PrimalItemConsumable_HealSoup",
                "description": "Powerful healing consumable",
                "level_requirement": 45,
                "suggested_price": 25,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi MedicalBrew 1 1 false"
            },
            
            # Tames & Eggs
            {
                "id": "rexegg",
                "name": "Rex Egg",
                "category": "Tames",
                "type": "Egg",
                "blueprint": "/Game/PrimalEarth/Test/PrimalItemConsumable_Egg_Rex.PrimalItemConsumable_Egg_Rex",
                "description": "Fertilized Rex egg for breeding",
                "level_requirement": 60,
                "suggested_price": 500,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi Egg_Rex 1 1 false"
            },
            {
                "id": "argentavisegg",
                "name": "Argentavis Egg",
                "category": "Tames",
                "type": "Egg", 
                "blueprint": "/Game/PrimalEarth/Test/PrimalItemConsumable_Egg_Argentavis.PrimalItemConsumable_Egg_Argentavis",
                "description": "Fertilized Argentavis egg for breeding",
                "level_requirement": 40,
                "suggested_price": 300,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi Egg_Argentavis 1 1 false"
            },
            {
                "id": "ankyloegg",
                "name": "Ankylosaurus Egg", 
                "category": "Tames",
                "type": "Egg",
                "blueprint": "/Game/PrimalEarth/Test/PrimalItemConsumable_Egg_Ankylo.PrimalItemConsumable_Egg_Ankylo",
                "description": "Fertilized Ankylosaurus egg for breeding",
                "level_requirement": 30,
                "suggested_price": 200,
                "quality_range": [1, 1],
                "spawn_command": "cheat gfi Egg_Ankylo 1 1 false"
            }
        ]
    
    def _build_categories(self) -> List[str]:
        """Build list of available categories"""
        categories = set()
        for item in self.items:
            categories.add(item.get('category', 'Other'))
        return sorted(list(categories))
    
    def get_all_items(self) -> List[Dict]:
        """Get all items in the library"""
        return self.items.copy()
    
    def get_items_by_category(self, category: str) -> List[Dict]:
        """Get items by category"""
        try:
            return [item for item in self.items if item.get('category', '').lower() == category.lower()]
        except Exception as e:
            logging.error(f"Failed to get items by category {category}: {e}")
            return []
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get item by ID"""
        try:
            for item in self.items:
                if item.get('id', '').lower() == item_id.lower():
                    return item.copy()
            return None
        except Exception as e:
            logging.error(f"Failed to get item by ID {item_id}: {e}")
            return None
    
    def get_item_by_name(self, name: str) -> Optional[Dict]:
        """Get item by name"""
        try:
            for item in self.items:
                if item.get('name', '').lower() == name.lower():
                    return item.copy()
            return None
        except Exception as e:
            logging.error(f"Failed to get item by name {name}: {e}")
            return None
    
    def search_items(self, query: str) -> List[Dict]:
        """Search items by name or description"""
        try:
            query_lower = query.lower()
            results = []
            
            for item in self.items:
                # Check name
                if query_lower in item.get('name', '').lower():
                    results.append(item.copy())
                    continue
                
                # Check description
                if query_lower in item.get('description', '').lower():
                    results.append(item.copy())
                    continue
                
                # Check ID
                if query_lower in item.get('id', '').lower():
                    results.append(item.copy())
            
            return results
        except Exception as e:
            logging.error(f"Failed to search items: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        return self.categories.copy()
    
    def get_items_by_level_range(self, min_level: int, max_level: int) -> List[Dict]:
        """Get items within level range"""
        try:
            return [
                item for item in self.items 
                if min_level <= item.get('level_requirement', 1) <= max_level
            ]
        except Exception as e:
            logging.error(f"Failed to get items by level range: {e}")
            return []
    
    def get_items_by_price_range(self, min_price: int, max_price: int) -> List[Dict]:
        """Get items within price range"""
        try:
            return [
                item for item in self.items 
                if min_price <= item.get('suggested_price', 0) <= max_price
            ]
        except Exception as e:
            logging.error(f"Failed to get items by price range: {e}")
            return []
    
    def get_library_stats(self) -> Dict[str, any]:
        """Get library statistics"""
        try:
            stats = {
                'total_items': len(self.items),
                'categories': len(self.categories),
                'items_by_category': {},
                'average_suggested_price': 0,
                'level_range': {'min': 999, 'max': 0}
            }
            
            total_price = 0
            price_count = 0
            
            # Count items by category and calculate stats
            for item in self.items:
                category = item.get('category', 'Other')
                if category not in stats['items_by_category']:
                    stats['items_by_category'][category] = 0
                stats['items_by_category'][category] += 1
                
                # Price stats
                price = item.get('suggested_price', 0)
                if price > 0:
                    total_price += price
                    price_count += 1
                
                # Level stats
                level = item.get('level_requirement', 1)
                stats['level_range']['min'] = min(stats['level_range']['min'], level)
                stats['level_range']['max'] = max(stats['level_range']['max'], level)
            
            # Calculate average price
            if price_count > 0:
                stats['average_suggested_price'] = round(total_price / price_count, 2)
            
            return stats
            
        except Exception as e:
            logging.error(f"Failed to get library stats: {e}")
            return {}
    
    def validate_item_blueprint(self, blueprint: str) -> bool:
        """Validate if blueprint path looks correct"""
        try:
            if not blueprint:
                return False
            
            # Basic validation - should start with /Game/ and contain PrimalItem
            if blueprint.startswith('/Game/') and 'PrimalItem' in blueprint:
                return True
            
            return False
        except:
            return False
    
    def get_similar_items(self, item_id: str, limit: int = 5) -> List[Dict]:
        """Get items similar to the specified item"""
        try:
            base_item = self.get_item_by_id(item_id)
            if not base_item:
                return []
            
            similar_items = []
            base_category = base_item.get('category', '')
            base_level = base_item.get('level_requirement', 1)
            base_price = base_item.get('suggested_price', 0)
            
            for item in self.items:
                if item['id'] == item_id:
                    continue  # Skip the same item
                
                # Calculate similarity score
                score = 0
                
                # Same category gets high score
                if item.get('category', '') == base_category:
                    score += 50
                
                # Similar level requirement
                level_diff = abs(item.get('level_requirement', 1) - base_level)
                if level_diff <= 5:
                    score += 30 - (level_diff * 5)
                
                # Similar price
                if base_price > 0:
                    price_ratio = item.get('suggested_price', 0) / base_price
                    if 0.5 <= price_ratio <= 2.0:
                        score += 20
                
                if score > 0:
                    item_copy = item.copy()
                    item_copy['similarity_score'] = score
                    similar_items.append(item_copy)
            
            # Sort by similarity score and return top results
            similar_items.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_items[:limit]
            
        except Exception as e:
            logging.error(f"Failed to get similar items: {e}")
            return []
    
    def export_items_json(self, file_path: str) -> bool:
        """Export items to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Exported {len(self.items)} items to {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to export items to {file_path}: {e}")
            return False
    
    def import_items_json(self, file_path: str) -> bool:
        """Import items from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_items = json.load(f)
            
            if not isinstance(imported_items, list):
                logging.error("Imported data must be a list")
                return False
            
            # Validate imported items
            valid_items = []
            for item in imported_items:
                if self._validate_item_structure(item):
                    valid_items.append(item)
                else:
                    logging.warning(f"Skipping invalid item: {item.get('name', 'Unknown')}")
            
            if valid_items:
                self.items.extend(valid_items)
                self.categories = self._build_categories()
                logging.info(f"Imported {len(valid_items)} items from {file_path}")
                return True
            else:
                logging.error("No valid items found in import file")
                return False
                
        except Exception as e:
            logging.error(f"Failed to import items from {file_path}: {e}")
            return False
    
    def _validate_item_structure(self, item: Dict) -> bool:
        """Validate item structure"""
        try:
            required_fields = ['id', 'name', 'category']
            
            for field in required_fields:
                if field not in item or not item[field]:
                    return False
            
            # Check for duplicate ID
            for existing_item in self.items:
                if existing_item['id'] == item['id']:
                    return False  # Duplicate ID
            
            return True
            
        except:
            return False

