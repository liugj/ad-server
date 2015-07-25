#!/usr/bin/env
# -*- coding: utf-8 -*-
import re
a_str='[2015-07_15 14:11:01] charge.py[line:99] INFO COMMON:{"charge_type": "cpm", "idea_id": "19", "price": 0.0, "cost": 0.0, "impid": "ee846b69a9534479a74e08c31aa1062f"}'
pattern=re.compile(".*COMMON\:(.*)")
b=pattern.match(a_str)
print b.group(1)
