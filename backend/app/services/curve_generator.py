import math
import random
from datetime import datetime, timedelta
from typing import List, Dict

class CurveGenerator:
    """Mathematical logic for generating sub-order distributions"""
    
    @staticmethod
    def generate_sub_orders(
        total_qty: int,
        total_time_mins: int,
        step_mins: int,
        graph_type: str,
        tolerance_pct: int = 10
    ) -> List[Dict]:
        """
        Generate a list of sub-order quantities and their relative scheduled times (in minutes).
        """
        if total_time_mins <= 0 or step_mins <= 0:
            return [{"qty": total_qty, "mins_offset": 0}]
            
        num_steps = max(1, total_time_mins // step_mins)
        if num_steps == 1:
             return [{"qty": total_qty, "mins_offset": 0}]

        dist = []
        if graph_type == 'Linear':
            dist = CurveGenerator._linear_dist(num_steps)
        elif graph_type == 'Exponential':
            dist = CurveGenerator._exponential_dist(num_steps)
        elif graph_type == 'Viral Bell Curve':
            dist = CurveGenerator._viral_bell_dist(num_steps)
        elif graph_type == 'Random':
            dist = CurveGenerator._random_burst_dist(num_steps)
        else:
            dist = CurveGenerator._linear_dist(num_steps)
            
        # Normalize distribution to match total_qty
        total_weights = sum(dist)
        sub_orders = []
        current_qty_sum = 0
        
        for i in range(num_steps):
            raw_qty = (dist[i] / total_weights) * total_qty
            
            # Apply Quantity Jitter
            jitter = (random.random() * 2 - 1) * (tolerance_pct / 100.0)
            qty = round(raw_qty * (1 + jitter))
            
            # Ensure at least 1 if the weight suggests it, but don't exceed total_qty
            if qty < 1 and dist[i] > 0:
                qty = 1
                
            # Relative offset
            mins_offset = i * step_mins
            
            # Apply Time Jitter (+/- step_mins / 4)
            time_jitter = random.randint(-step_mins // 4, step_mins // 4)
            mins_offset = max(0, mins_offset + time_jitter)
            
            sub_orders.append({
                "qty": qty,
                "mins_offset": mins_offset,
                "ordinal": i + 1
            })
            current_qty_sum += qty
            
        # Adjustment to match exact total_qty
        diff = total_qty - current_qty_sum
        if diff != 0 and sub_orders:
            # Add/subtract remainder to the last one or largest one
            sub_orders[-1]["qty"] = max(1, sub_orders[-1]["qty"] + diff)
            
        return sub_orders

    @staticmethod
    def _linear_dist(n: int) -> List[float]:
        return [1.0] * n

    @staticmethod
    def _exponential_dist(n: int) -> List[float]:
        # y = e^(x)
        return [math.exp(3 * (i / n)) for i in range(n)]

    @staticmethod
    def _viral_bell_dist(n: int) -> List[float]:
        # Gaussian distribution centered at 60% of the way
        center = n * 0.6
        sigma = n * 0.2
        return [math.exp(-((i - center)**2) / (2 * sigma**2)) for i in range(n)]

    @staticmethod
    def _random_burst_dist(n: int) -> List[float]:
        return [random.random() for _ in range(n)]
