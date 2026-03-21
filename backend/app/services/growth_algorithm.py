import math
import random
from datetime import datetime, timedelta
from typing import List, Tuple
from app.core.database import redis_client

class CrookedGraphAlgorithm:
    """The 'Crooked Graph' algorithm for organic growth simulation"""
    
    @staticmethod
    def _get_configured_timezone() -> str:
        """Get configured timezone from Redis settings"""
        try:
            config = redis_client.hgetall("admin:timezone_config")
            return config.get("timezone", "GMT+7")
        except Exception:
            return "GMT+7"
    
    @staticmethod
    def _apply_timezone_offset(utc_time: datetime) -> datetime:
        """Apply timezone offset to UTC time"""
        timezone = CrookedGraphAlgorithm._get_configured_timezone()
        
        if timezone == "UTC":
            return utc_time
        
        try:
            # Parse GMT offset (e.g., "GMT+7" -> +7)
            if timezone.startswith("GMT"):
                offset_hours = int(timezone.replace("GMT", ""))
                return utc_time + timedelta(hours=offset_hours)
        except (ValueError, AttributeError):
            pass
        
        return utc_time
    
    @staticmethod
    def calculate_schedule(
        total_quantity: int,
        duration_minutes: int,
        step_interval: int,
        graph_type: str,
        tolerance_percent: int = 10,
        seed: int = None,
        start_time: datetime = None
    ) -> List[Tuple[datetime, int]]:
        """
        Calculate schedule for sub-orders
        
        Args:
            total_quantity: Total quantity to deliver
            duration_minutes: Total duration in minutes
            step_interval: Interval between steps in minutes
            graph_type: Type of growth curve ('Organic', 'Viral', 'Steady', 'Burst')
            tolerance_percent: Random noise percentage
            seed: Optional seed for reproducible results
            start_time: Optional start time (defaults to tomorrow 12:00 AM if not provided)
            
        Returns:
            List of (scheduled_time, quantity) tuples
        """
        
        if seed:
            random.seed(seed)
        
        # Use provided start_time or default with configured timezone
        if start_time is None:
            # Default to tomorrow 12:00 AM in configured timezone
            utc_now = datetime.utcnow()
            local_time = CrookedGraphAlgorithm._apply_timezone_offset(utc_now)
            start_time = local_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            # Apply configured timezone to provided start_time
            start_time = CrookedGraphAlgorithm._apply_timezone_offset(start_time)
        
        # Calculate number of steps
        num_steps = max(1, duration_minutes // step_interval)
        
        # Generate base curve
        base_quantities = CrookedGraphAlgorithm._generate_base_curve(
            total_quantity, num_steps, graph_type
        )
        
        # Apply tolerance noise
        noisy_quantities = CrookedGraphAlgorithm._apply_tolerance_noise(
            base_quantities, tolerance_percent
        )
        
        # Ensure minimum quantities (API minimum is usually 10)
        final_quantities = CrookedGraphAlgorithm._ensure_minimum_quantities(
            noisy_quantities, min_quantity=10
        )
        
        # Adjust to match total quantity within tolerance
        final_quantities = CrookedGraphAlgorithm._adjust_to_total(
            final_quantities, total_quantity, tolerance_percent
        )
        
        # Generate schedule with timestamps
        schedule = []
        current_time = start_time
        
        for i, quantity in enumerate(final_quantities):
            schedule.append((current_time, quantity))
            current_time += timedelta(minutes=step_interval)
        
        return schedule
    
    @staticmethod
    def _generate_base_curve(total_quantity: int, num_steps: int, graph_type: str) -> List[float]:
        """Generate the base growth curve"""
        
        if num_steps <= 0:
            return [float(total_quantity)]
        
        base_curve = []
        
        if graph_type == 'Steady':
            # Linear growth: y = mx
            step_quantity = total_quantity / num_steps
            base_curve = [step_quantity] * num_steps
            
        elif graph_type == 'Viral':
            # Exponential growth: y = e^x (normalized)
            exp_values = [math.exp(i / num_steps * 3) for i in range(num_steps)]
            total_exp = sum(exp_values)
            base_curve = [total_quantity * (val / total_exp) for val in exp_values]
            
        elif graph_type == 'Organic':
            # Sigmoid S-curve: natural growth pattern
            sigmoid_values = []
            for i in range(num_steps):
                x = (i / num_steps) * 6 - 3  # Scale to -3 to 3
                sigmoid = 1 / (1 + math.exp(-x))
                sigmoid_values.append(sigmoid)
            
            total_sigmoid = sum(sigmoid_values)
            base_curve = [total_quantity * (val / total_sigmoid) for val in sigmoid_values]
            
        elif graph_type == 'Burst':
            # Logarithmic decay with random bursts
            log_values = []
            for i in range(num_steps):
                # Base logarithmic decay
                if i == 0:
                    log_val = 1.0
                else:
                    log_val = math.log(num_steps) / math.log(i + 1)
                
                # Add burst probability
                if i > 0 and i < num_steps - 1 and random.random() < 0.2:  # 20% burst chance
                    log_val *= random.uniform(1.5, 3.0)
                
                log_values.append(log_val)
            
            total_log = sum(log_values)
            base_curve = [total_quantity * (val / total_log) for val in log_values]
            
        else:
            # Default to steady
            step_quantity = total_quantity / num_steps
            base_curve = [step_quantity] * num_steps
        
        return base_curve
    
    @staticmethod
    def _apply_tolerance_noise(quantities: List[float], tolerance_percent: int) -> List[float]:
        """Apply random walk noise to simulate organic variation"""
        
        noisy_quantities = []
        tolerance_factor = tolerance_percent / 100.0
        
        for i, quantity in enumerate(quantities):
            if i == 0:
                # First step gets base quantity
                noisy_quantities.append(quantity)
            else:
                # Random walk with tolerance bounds
                max_change = quantity * tolerance_factor
                change = random.uniform(-max_change, max_change)
                noisy_quantity = max(0, quantity + change)
                noisy_quantities.append(noisy_quantity)
        
        return noisy_quantities
    
    @staticmethod
    def _ensure_minimum_quantities(quantities: List[float], min_quantity: int = 10) -> List[float]:
        """Ensure no quantity is below the minimum API requirement"""
        
        # Find quantities below minimum
        below_min = [i for i, q in enumerate(quantities) if q < min_quantity]
        
        if not below_min:
            return quantities
        
        # Redistribute from larger quantities
        total_deficit = sum(min_quantity - quantities[i] for i in below_min)
        total_surplus = sum(max(0, quantities[i] - min_quantity * 2) for i in range(len(quantities)) if i not in below_min)
        
        if total_surplus >= total_deficit:
            # Redistribute surplus
            surplus_indices = [i for i in range(len(quantities)) if quantities[i] > min_quantity * 2]
            
            for i in below_min:
                quantities[i] = min_quantity
            
            for i in surplus_indices:
                if total_deficit <= 0:
                    break
                available = quantities[i] - min_quantity * 2
                reduction = min(available, total_deficit / len(surplus_indices))
                quantities[i] -= reduction
                total_deficit -= reduction
        
        else:
            # Set all to minimum and adjust total
            for i in range(len(quantities)):
                quantities[i] = max(min_quantity, quantities[i])
        
        return quantities
    
    @staticmethod
    def _adjust_to_total(quantities: List[float], target_total: int, tolerance_percent: int) -> List[int]:
        """Adjust quantities to match target total within tolerance"""
        
        current_total = sum(quantities)
        
        if abs(current_total - target_total) / target_total <= (tolerance_percent / 100):
            # Already within tolerance
            return [int(round(q)) for q in quantities]
        
        # Scale to match target
        scale_factor = target_total / current_total
        scaled_quantities = [q * scale_factor for q in quantities]
        
        # Round to integers
        int_quantities = [int(round(q)) for q in scaled_quantities]
        
        # Adjust for rounding errors
        rounding_error = target_total - sum(int_quantities)
        
        if rounding_error != 0:
            # Distribute error to largest quantities
            sorted_indices = sorted(range(len(int_quantities)), key=lambda i: int_quantities[i], reverse=True)
            
            for i in range(abs(rounding_error)):
                idx = sorted_indices[i % len(sorted_indices)]
                if rounding_error > 0:
                    int_quantities[idx] += 1
                else:
                    int_quantities[idx] = max(1, int_quantities[idx] - 1)
        
        return int_quantities
    
    @staticmethod
    def generate_preview_data(
        total_quantity: int,
        duration_minutes: int,
        step_interval: int,
        graph_type: str,
        tolerance_percent: int = 10,
        seed: int = None
    ) -> dict:
        """Generate data for graph preview"""
        
        schedule = CrookedGraphAlgorithm.calculate_schedule(
            total_quantity, duration_minutes, step_interval, graph_type, tolerance_percent, seed
        )
        
        # Convert to chart-friendly format
        timestamps = [time.isoformat() for time, _ in schedule]
        quantities = [quantity for _, quantity in schedule]
        
        # Calculate cumulative totals
        cumulative = []
        running_total = 0
        for quantity in quantities:
            running_total += quantity
            cumulative.append(running_total)
        
        return {
            'timestamps': timestamps,
            'quantities': quantities,
            'cumulative': cumulative,
            'total_steps': len(schedule),
            'total_quantity': sum(quantities),
            'start_time': schedule[0][0].isoformat() if schedule else None,
            'end_time': schedule[-1][0].isoformat() if schedule else None
        }
