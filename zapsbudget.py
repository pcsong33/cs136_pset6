#!/usr/bin/env python

import sys
import random

from gsp import GSP
from util import argmax_index

class ZapsBudget:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return 0


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = [a_id_b for a_id_b in prev_round.bids if a_id_b[0] != self.id]

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = list(map(compute, list(range(len(clicks)))))
#        sys.stdout.write("slot info: %s\n" % info)
        return info


    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # TODO: Fill this in
        utilities = []
        clicks = history.round(t-1).clicks
        num_slots = len(clicks)

        slot_infos = self.slot_info(t, history, reserve)

        for i in range(num_slots):
            min_bid = slot_infos[i][1]
            utility = clicks[i] * (self.value - min_bid)
            utilities.append(utility)

        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i = len(history.round(t-1).clicks) - 1
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, _) = self.target_slot(t, history, reserve)

        # TODO: Fill this in.
        clicks = prev_round.clicks

        if slot == 0 or min_bid > self.value or t == 47:
            bid = self.value
        else:
            utility = clicks[slot] * (self.value - min_bid)
            bid = self.value - utility/clicks[slot - 1]

        budget_to_payment = 1
        if min_bid * clicks[slot] > 0 and 48 - t > 0 and t != 47:
            budget_per_period = (self.budget - history.agents_spent[self.id]) / (48 - t)
            expected_pay = min_bid * clicks[slot]
            budget_to_payment = budget_per_period / expected_pay

        will_bid = random.random() <= budget_to_payment

        return bid * will_bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


