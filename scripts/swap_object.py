#!/usr/bin/env python3
import sys
import os
import argparse
import re

# Mapping of standard COCO classes to locally cached or online Gazebo Models
COCO_TO_GAZEBO = {
    "person": "person_standing",
    "bottle": "beer",
    "car": "suv",
    "bus": "bus",
    "wheel": "car_wheel",
    "mailbox": "mailbox",
    "traffic light": "stop_light",
    "chair": "chair",
    "table": "cafe_table",
    "box": "cardboard_box",
    "cone": "construction_cone",
    "tree": "pine_tree"
}

def main():
    parser = argparse.ArgumentParser(description="Swap target COCO objects in Gazebo warehouse world")
    parser.add_argument("--object", type=str, help="Target COCO object name (e.g. person, chair, table, box, bottle, cone) or custom Gazebo model name")
    parser.add_argument("--x", type=float, default=1.8, help="X position to spawn the object (default: 1.8)")
    parser.add_argument("--y", type=float, default=5.0, help="Y position to spawn the object (default: 5.0)")
    parser.add_argument("--z", type=float, default=0.0, help="Z position to spawn the object (default: 0.0)")
    parser.add_argument("--remove", action="store_true", help="Remove the target object from the world file")
    
    args = parser.parse_args()
    
    world_path = "/home/alex/Documents/Omokai_Project/config/worlds/warehouse.world"
    if not os.path.exists(world_path):
        print(f"Error: World file not found at {world_path}")
        sys.exit(1)
        
    with open(world_path, "r") as f:
        content = f.read()
        
    # Check if a coco_target model already exists in the XML
    pattern = r"(\s*<model name=['\"]coco_target['\"]>.*?</model>)"
    has_target = re.search(pattern, content, re.DOTALL)
    
    if args.remove:
        if has_target:
            content = re.sub(pattern, "", content, flags=re.DOTALL)
            print("Removed 'coco_target' from warehouse.world")
        else:
            print("No existing 'coco_target' found to remove.")
    else:
        if not args.object:
            print("Error: --object is required unless --remove is set")
            sys.exit(1)
            
        # Determine Gazebo model name
        model_name = COCO_TO_GAZEBO.get(args.object.lower(), args.object)
        
        # Build the XML model block
        model_xml = f"""
    <model name="coco_target">
      <static>true</static>
      <include>
        <uri>model://{model_name}</uri>
      </include>
      <pose>{args.x} {args.y} {args.z} 0 0 0</pose>
    </model>"""
    
        if has_target:
            # Replace existing target model block
            content = re.sub(pattern, model_xml, content, flags=re.DOTALL)
            print(f"Swapped target object to '{model_name}' at ({args.x}, {args.y}, {args.z}) in warehouse.world")
        else:
            # Insert before the closing </world> tag
            world_close_idx = content.rfind("</world>")
            if world_close_idx == -1:
                print("Error: Could not find closing </world> tag in XML.")
                sys.exit(1)
            content = content[:world_close_idx] + model_xml + "\n  " + content[world_close_idx:]
            print(f"Spawning target object '{model_name}' at ({args.x}, {args.y}, {args.z}) in warehouse.world")
            
    with open(world_path, "w") as f:
        f.write(content)
        
if __name__ == "__main__":
    main()
