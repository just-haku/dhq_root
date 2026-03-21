import re
import os

router_path = "/home/haku/projects/DHQ_Root/frontend/src/router/index.js"

with open(router_path, "r") as f:
    content = f.read()

# Make sure we don't apply it twice
if "DashboardLayout" not in content:
    # Add import
    content = content.replace("import Funny404 from '../views/Funny404.vue'\n", 
                              "import Funny404 from '../views/Funny404.vue'\nimport DashboardLayout from '../layouts/DashboardLayout.vue'\n")
    
    # We want to wrap routes that use () => import('../views/...') inside DashboardLayout
    # Let's find the `const routes = [`
    
    # Split the content
    routes_start = content.find("const routes = [\n") + len("const routes = [\n")
    routes_end = content.rfind("]\n\nconst router = createRouter")
    
    routes_str = content[routes_start:routes_end]
    
    # Let's extract the first few routes that don't need layout: 
    # '/', '/login', '/shadow-garden/login', '/shadow-garden/apply', '/*'
    
    # Actually, it's easier to just do string substitution for the whole array
    # We will build a new routes array.
    
    # Anything from line 27 to 519 (Dashboard to Collaboration) will be under DashboardLayout
    # Wait, in the output, Dashboard is at line 27.
    # '/shadow-garden/apply' ends around line 26.
    
    # Let's split by regex or just do it by finding `/dashboard`
    parts = content.split("  {\n    path: '/dashboard',\n")
    
    if len(parts) == 2:
        top_half = parts[0]
        # the rest is the second half
        # but '/*' is at the end.
        
        # let's find the last route '/*'
        bottom_parts = parts[1].split("  {\n    path: '/*',\n")
        
        if len(bottom_parts) == 2:
            middle = "  {\n    path: '/dashboard',\n" + bottom_parts[0]
            bottom = "  {\n    path: '/*',\n" + bottom_parts[1]
            
            # wrap the middle
            wrapped_middle = "  {\n    path: '',\n    component: DashboardLayout,\n    children: [\n      " + middle.replace("\n  {", "\n      {") + "    ]\n  },\n"
            
            new_content = top_half + wrapped_middle + bottom
            
            with open(router_path, "w") as f:
                f.write(new_content)
            print("Successfully updated router/index.js")
        else:
            print("Could not find line /*")
    else:
        print("Could not find line /dashboard")
else:
    print("DashboardLayout already in router")
