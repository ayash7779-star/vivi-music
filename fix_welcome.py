#!/usr/bin/env python3
"""Fix WelcomeActivity: change developer name, remove community/features pages."""
import re

path = 'app/src/main/kotlin/com/music/vivi/WelcomeActivity.kt'
with open(path) as f:
    content = f.read()

# 1. Change developer name
content = content.replace('By vividh p ashokan', 'By Yash Agrawal')

# 2. Fix finishing transition text
content = content.replace('"ViviMusic\u2026"', '"Svara\u2026"')

# 3. Remove Community and Features onboarding pages
join_idx = content.find('"Join our"')
if join_idx > 0:
    ob_start = content.rfind('        OnboardingPageInfo(', 0, join_idx)
    if ob_start > 0:
        feat_idx = content.find('feat_discover', join_idx)
        if feat_idx > 0:
            list_end = content.find('\n        )\n    )\n', feat_idx)
            if list_end > 0:
                list_end_full = list_end + len('\n        )\n    )\n')
                before = content[:ob_start]
                after = content[list_end_full:]
                last_comma = before.rfind('        ),\n')
                if last_comma > 0:
                    before = before[:last_comma] + '        )\n    )\n'
                content = before + after
                print("Removed Community and Features pages")
            else:
                print("WARNING: Could not find listOf closing")
        else:
            print("WARNING: Could not find feat_discover")
    else:
        print("WARNING: Could not find OnboardingPageInfo before Join our")
else:
    print("WARNING: Could not find Join our")

with open(path, 'w') as f:
    f.write(content)

print("WelcomeActivity.kt fixed")
