import reapy
import logging
from typing import Union, Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_item_by_id_or_index(track: reapy.Track, item_id: Union[int, str]) -> Optional[reapy.Item]:
    """
    Get an item from a track by its ID or index.
    
    Args:
        track (reapy.Track): The track to search in
        item_id (Union[int, str]): The item ID or index
        
    Returns:
        Optional[reapy.Item]: The found item or None if not found
    """
    try:
        # Try to use item_id as an index
        item_index = int(item_id)
        if 0 <= item_index < len(track.items):
            item = track.items[item_index]
            logger.debug(f"Found item at index: {item_index}")
            return item
    except ValueError:
        # If conversion fails, try to match by string ID
        str_item_id = str(item_id)
        for i in track.items:
            if str(i.id) == str_item_id:
                logger.debug(f"Found item with ID: {item_id}")
                return i
    
    logger.error(f"Item with ID {item_id} not found")
    return None

def get_item_properties(item: reapy.Item) -> Dict[str, Any]:
    """
    Get properties of a media item.
    
    Args:
        item (reapy.Item): The item to get properties from
        
    Returns:
        Dict[str, Any]: Dictionary of item properties
    """
    try:
        # Get basic properties
        position = item.position
        length = item.length
        name = item.active_take.name if item.active_take else ""
        
        # Determine if it's an audio item
        is_audio = False
        source_file = ""
        take = item.active_take
        if take and not take.is_midi:
            is_audio = True
            try:
                source_file = take.source.filename if hasattr(take, 'source') and hasattr(take.source, 'filename') else ""
            except Exception as e:
                logger.warning(f"Failed to get source filename: {e}")
        
        # Get muted and selected state
        is_muted = item.muted if hasattr(item, 'muted') else False
        is_selected = item.selected if hasattr(item, 'selected') else False
        
        return {
            'position': position,
            'length': length,
            'name': name,
            'is_audio': is_audio,
            'file_path': source_file,
            'muted': is_muted,
            'selected': is_selected
        }
    except Exception as e:
        logger.error(f"Failed to get item properties: {e}")
        return {}

def select_item(item: reapy.Item) -> bool:
    """
    Select a media item.
    
    Args:
        item (reapy.Item): The item to select
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Always use the ReaScript API directly
        from reapy import reascript_api as RPR
        
        # First clear all selections
        RPR.SelectAllMediaItems(0, False)
        
        # Then select this item
        RPR.SetMediaItemSelected(item.id, True)
        return True
    except Exception as e:
        logger.error(f"Failed to select item: {e}")
        return False

def delete_item(item: reapy.Item) -> bool:
    """
    Delete a media item.
    
    Args:
        item (reapy.Item): The item to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use reapy's native API to delete the item
        item.delete()
        
        # Verify the item was deleted
        try:
            # Try to find the item again - it should be gone
            for i in item.track.items:
                if str(i.id) == str(item.id):
                    logger.error("Item still exists after deletion")
                    return False
        except Exception as e:
            # If we get an error trying to access the item, it probably means it was deleted
            pass
        
        logger.info(f"Deleted item with ID: {item.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete item: {e}")
        return False 