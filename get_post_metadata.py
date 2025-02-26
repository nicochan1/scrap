from instaloader import Instaloader, Post
import json
from typing import Dict, Any
from datetime import datetime

def get_post_metadata(shortcode: str) -> Dict[str, Any]:
    """
    Get metadata for an Instagram post using its shortcode
    
    Args:
        shortcode: The Instagram post shortcode (e.g., 'B_K4CykAOtf')
        
    Returns:
        Dictionary containing post metadata
    """
    # Create Instaloader instance
    L = Instaloader()
    
    try:
        # Get post from shortcode
        post = Post.from_shortcode(L.context, shortcode)
        
        # Create metadata dictionary with key information
        metadata = {
            "shortcode": post.shortcode,
            "type": post.typename,
            "timestamp": post.date_local.strftime("%Y-%m-%d %H:%M:%S"),
            "caption": post.caption,
            "likes": post.likes,
            "comments": post.comments,
            "location": str(post.location) if post.location else None,
            "is_video": post.is_video,
            "owner": {
                "username": post.owner_username,
                "profile_id": post.owner_id,
            }
        }
        print('metadata: ', metadata)
        
        # Add media URLs based on post type
        if post.typename == "GraphImage":
            metadata["media_items"] = []
            item = {
                "is_video": post.is_video,
                "display_url": post.url,
            }                        
            metadata["media_items"].append(item)
        elif post.typename == "GraphVideo":
            metadata["media_items"] = []
            item = {
                "is_video": post.is_video,
                "display_url": post.video_url,
            }                        
            metadata["media_items"].append(item)
        elif post.typename == "GraphSidecar":
            metadata["media_items"] = []
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    item = {
                        "is_video": node.is_video,
                        "display_url": node.video_url
                    }
                else: 
                    item = {
                        "is_video": node.is_video,
                        "display_url": node.display_url,
                }

                metadata["media_items"].append(item)

        print('metadata after adding media items: ', metadata)
        
        return metadata
        
    except Exception as e:
        return {"error": str(e)}

def main():
    # Get shortcode from user
    shortcode = input("Enter Instagram post shortcode: ").strip()
    
    # Remove URL if full URL was pasted
    if "instagram.com/p/" in shortcode:
        shortcode = shortcode.split("/p/")[1].split("/")[0]
    
    # Get metadata
    metadata = get_post_metadata(shortcode)

    for item in metadata["media_items"]:
        print('url: ', item["display_url"])
        print('date: ', metadata["timestamp"])
    
    # Print formatted JSON
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main() 