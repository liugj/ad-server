#!/usr/bin/env
# -*- coding: utf-8 -*-

import logging
import datetime
class rank_bid_t:
    def __init__(self):
        pass
    
    def rank_bid(self,idea_list,idea_idx_dict):
        second=int(datetime.datetime.now().strftime("%S"))
        length=len(idea_list)
        if length==0:
            return (-1,0)
        random_i=second%length
        win_idea_id=idea_list[random_i]
        bid=3000
        return (win_idea_id,bid)
        
