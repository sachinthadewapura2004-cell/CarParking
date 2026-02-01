"""
Urban City Parking Management System - Enhanced Demonstration
This script simulates realistic scenarios with proper time durations
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict
import uuid


# ============== VEHICLE CLASSES ==============

class Vehicle(ABC):
    """Abstract Base Class for all vehicle types."""
    
    def __init__(self, registration_number: str):
        self._registration_number = registration_number
    
    @abstractmethod
    def get_space_requirement(self) -> int:
        pass
    
    @abstractmethod
    def get_vehicle_type(self) -> str:
        pass
    
    def get_registration(self) -> str:
        return self._registration_number


class Car(Vehicle):
    def get_space_requirement(self) -> int:
        return 1
    
    def get_vehicle_type(self) -> str:
        return "Car"


class Motorcycle(Vehicle):
    def get_space_requirement(self) -> int:
        return 1
    
    def get_vehicle_type(self) -> str:
        return "Motorcycle"


class Truck(Vehicle):
    def get_space_requirement(self) -> int:
        return 2
    
    def get_vehicle_type(self) -> str:
        return "Truck"


# ============== PARKING PASS CLASSES ==============

class ParkingPass(ABC):
    """Abstract Base Class for parking passes."""
    
    def __init__(self, pass_id: str, holder_name: str, vehicle_registration: str):
        self._pass_id = pass_id
        self._holder_name = holder_name
        self._vehicle_registration = vehicle_registration
        self._issue_date = datetime.now()
    
    @abstractmethod
    def is_valid(self) -> bool:
        pass
    
    @abstractmethod
    def get_pass_type(self) -> str:
        pass
    
    def use_pass(self) -> bool:
        return True
    
    @property
    def pass_id(self) -> str:
        return self._pass_id
    
    @property
    def holder_name(self) -> str:
        return self._holder_name
    
    @property
    def vehicle_registration(self) -> str:
        return self._vehicle_registration


class MonthlyPass(ParkingPass):
    def __init__(self, pass_id: str, holder_name: str, 
                 vehicle_registration: str, expiry_date: datetime):
        super().__init__(pass_id, holder_name, vehicle_registration)
        self._expiry_date = expiry_date
    
    def is_valid(self) -> bool:
        return datetime.now() < self._expiry_date
    
    def get_pass_type(self) -> str:
        return "Monthly Pass"
    
    def days_remaining(self) -> int:
        if not self.is_valid():
            return 0
        delta = self._expiry_date - datetime.now()
        return delta.days
    
    @property
    def expiry_date(self) -> datetime:
        return self._expiry_date


class SingleEntryPass(ParkingPass):
    FLAT_RATE = 10.00
    
    def __init__(self, pass_id: str, holder_name: str, vehicle_registration: str):
        super().__init__(pass_id, holder_name, vehicle_registration)
        self._is_used = False
    
    def is_valid(self) -> bool:
        return not self._is_used
    
    def get_pass_type(self) -> str:
        return "Single Entry Pass"
    
    def use_pass(self) -> bool:
        if self._is_used:
            return False
        self._is_used = True
        return True


# ============== PRICING STRATEGY CLASSES ==============

class PricingStrategy(ABC):
    """Abstract Base Class for pricing strategies."""
    
    def __init__(self):
        self._base_rates = {}
    
    @abstractmethod
    def get_hourly_rate(self, vehicle_type: str) -> float:
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        pass
    
    def calculate_fee(self, vehicle_type: str, duration_hours: float) -> float:
        hourly_rate = self.get_hourly_rate(vehicle_type)
        return round(hourly_rate * duration_hours, 2)


class StandardPricing(PricingStrategy):
    def __init__(self):
        super().__init__()
        self._base_rates = {"Car": 2.00, "Motorcycle": 1.00, "Truck": 3.00}
    
    def get_hourly_rate(self, vehicle_type: str) -> float:
        return self._base_rates.get(vehicle_type, 2.00)
    
    def get_strategy_name(self) -> str:
        return "Standard"


class PeakPricing(PricingStrategy):
    def __init__(self):
        super().__init__()
        self._base_rates = {"Car": 4.00, "Motorcycle": 2.00, "Truck": 6.00}
    
    def get_hourly_rate(self, vehicle_type: str) -> float:
        return self._base_rates.get(vehicle_type, 4.00)
    
    def get_strategy_name(self) -> str:
        return "Peak Hours"


class WeekendPricing(PricingStrategy):
    def __init__(self):
        super().__init__()
        self._base_rates = {"Car": 1.50, "Motorcycle": 0.75, "Truck": 2.25}
    
    def get_hourly_rate(self, vehicle_type: str) -> float:
        return self._base_rates.get(vehicle_type, 1.50)
    
    def get_strategy_name(self) -> str:
        return "Weekend"


# ============== PARKING TICKET CLASS ==============

class ParkingTicket:
    """Represents a parking session from entry to exit."""
    
    def __init__(self, ticket_id: str, vehicle: Vehicle, entry_time: datetime):
        self._ticket_id = ticket_id
        self._vehicle = vehicle
        self._entry_time = entry_time
        self._exit_time: Optional[datetime] = None
        self._parking_pass: Optional[ParkingPass] = None
        self._fee_charged: float = 0.0
        self._spaces_used: int = vehicle.get_space_requirement()
    
    def get_duration_hours(self, custom_exit_time: datetime = None) -> float:
        end_time = custom_exit_time or self._exit_time or datetime.now()
        duration = end_time - self._entry_time
        hours = duration.total_seconds() / 3600
        return round(hours, 2)
    
    def set_exit_time(self, exit_time: datetime) -> None:
        self._exit_time = exit_time
    
    def apply_pass(self, parking_pass: ParkingPass) -> bool:
        if parking_pass.vehicle_registration != self._vehicle.get_registration():
            return False
        self._parking_pass = parking_pass
        return True
    
    def calculate_fee(self, strategy: PricingStrategy, duration_hours: float = None) -> float:
        if self._parking_pass and isinstance(self._parking_pass, MonthlyPass):
            if self._parking_pass.is_valid():
                self._fee_charged = 0.0
                return self._fee_charged
        
        if self._parking_pass and isinstance(self._parking_pass, SingleEntryPass):
            if self._parking_pass.is_valid():
                self._parking_pass.use_pass()
                self._fee_charged = SingleEntryPass.FLAT_RATE
                return self._fee_charged
        
        duration = duration_hours if duration_hours else self.get_duration_hours()
        vehicle_type = self._vehicle.get_vehicle_type()
        self._fee_charged = strategy.calculate_fee(vehicle_type, duration)
        return self._fee_charged
    
    @property
    def ticket_id(self) -> str:
        return self._ticket_id
    
    @property
    def vehicle(self) -> Vehicle:
        return self._vehicle
    
    @property
    def entry_time(self) -> datetime:
        return self._entry_time
    
    @property
    def exit_time(self) -> Optional[datetime]:
        return self._exit_time
    
    @property
    def parking_pass(self) -> Optional[ParkingPass]:
        return self._parking_pass
    
    @property
    def fee_charged(self) -> float:
        return self._fee_charged
    
    @property
    def spaces_used(self) -> int:
        return self._spaces_used


# ============== PARKING LOT CLASS ==============

class ParkingLot:
    """Main controller class for the parking management system."""
    
    def __init__(self, total_spaces: int = 300):
        self.__total_spaces = total_spaces
        self.__occupied_spaces = 0
        self.__active_tickets: Dict[str, ParkingTicket] = {}
        self.__passes: Dict[str, ParkingPass] = {}
        self.__pricing_strategy: PricingStrategy = StandardPricing()
        self.__ticket_counter = 0
        self.__pass_counter = {"monthly": 0, "single": 0}
    
    def _generate_ticket_id(self) -> str:
        self.__ticket_counter += 1
        return f"TKT-{self.__ticket_counter:04d}"
    
    def _generate_pass_id(self, pass_type: str) -> str:
        if pass_type == "monthly":
            self.__pass_counter["monthly"] += 1
            return f"MP-{self.__pass_counter['monthly']:04d}"
        else:
            self.__pass_counter["single"] += 1
            return f"SP-{self.__pass_counter['single']:04d}"
    
    def get_available_spaces(self) -> int:
        return self.__total_spaces - self.__occupied_spaces
    
    def set_occupied_spaces(self, count: int) -> None:
        """For simulation purposes - set occupied spaces directly."""
        self.__occupied_spaces = min(count, self.__total_spaces)
    
    def vehicle_entry(self, vehicle: Vehicle, pass_id: Optional[str] = None,
                      entry_time: datetime = None, pricing_strategy: PricingStrategy = None) -> Optional[ParkingTicket]:
        """Processes vehicle entry with optional custom entry time for simulation."""
        
        spaces_needed = vehicle.get_space_requirement()
        
        if self.get_available_spaces() < spaces_needed:
            print(f"\n{'='*45}")
            print("            ENTRY DENIED")
            print(f"{'='*45}")
            print(f"Vehicle: {vehicle.get_registration()} ({vehicle.get_vehicle_type()})")
            print("Reason: PARKING LOT FULL")
            print(f"Required Spaces: {spaces_needed}")
            print(f"Available Spaces: {self.get_available_spaces()}")
            print("-" * 45)
            print("Please try again later.")
            print(f"{'='*45}\n")
            return None
        
        ticket_id = self._generate_ticket_id()
        actual_entry_time = entry_time if entry_time else datetime.now()
        ticket = ParkingTicket(ticket_id, vehicle, actual_entry_time)
        
        pass_applied = False
        parking_pass = None
        if pass_id and pass_id in self.__passes:
            parking_pass = self.__passes[pass_id]
            if parking_pass.is_valid():
                if ticket.apply_pass(parking_pass):
                    pass_applied = True
        
        self.__occupied_spaces += spaces_needed
        self.__active_tickets[ticket_id] = ticket
        
        strategy = pricing_strategy if pricing_strategy else self.__pricing_strategy
        
        print(f"\n{'='*45}")
        print("            PARKING TICKET")
        print(f"{'='*45}")
        print(f"Ticket ID: {ticket_id}")
        print(f"Vehicle: {vehicle.get_registration()} ({vehicle.get_vehicle_type()})")
        print(f"Entry Time: {actual_entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Spaces Allocated: {spaces_needed}")
        print(f"Available Spaces: {self.get_available_spaces()}")
        
        if pass_applied and parking_pass:
            print("-" * 45)
            print(f"Pass Applied: {parking_pass.get_pass_type()} ({pass_id})")
            print(f"Pass Holder: {parking_pass.holder_name}")
            if isinstance(parking_pass, MonthlyPass):
                print(f"Days Remaining: {parking_pass.days_remaining()}")
                print("FEE WAIVED - Monthly Pass Holder")
            elif isinstance(parking_pass, SingleEntryPass):
                print(f"Flat Rate: ${SingleEntryPass.FLAT_RATE:.2f}")
        elif pass_id:
            print("-" * 45)
            print(f"WARNING: Pass ID '{pass_id}' not found")
            print("         or invalid. Standard rates apply.")
        
        print("-" * 45)
        print(f"Pricing: {strategy.get_strategy_name()} Rate")
        print(f"{'='*45}\n")
        
        return ticket
    
    def vehicle_exit(self, ticket_id: str, exit_time: datetime = None,
                     pricing_strategy: PricingStrategy = None, 
                     simulated_duration: float = None) -> Optional[Dict]:
        """Processes vehicle exit with optional custom exit time for simulation."""
        
        if ticket_id not in self.__active_tickets:
            print(f"\nError: Ticket '{ticket_id}' not found.")
            return None
        
        ticket = self.__active_tickets[ticket_id]
        actual_exit_time = exit_time if exit_time else datetime.now()
        ticket.set_exit_time(actual_exit_time)
        
        strategy = pricing_strategy if pricing_strategy else self.__pricing_strategy
        
        # Use simulated duration if provided
        if simulated_duration:
            duration = simulated_duration
        else:
            duration = ticket.get_duration_hours(actual_exit_time)
        
        fee = ticket.calculate_fee(strategy, duration)
        
        self.__occupied_spaces -= ticket.spaces_used
        del self.__active_tickets[ticket_id]
        
        exit_details = {
            "ticket_id": ticket_id,
            "vehicle_reg": ticket.vehicle.get_registration(),
            "vehicle_type": ticket.vehicle.get_vehicle_type(),
            "entry_time": ticket.entry_time,
            "exit_time": actual_exit_time,
            "duration_hours": duration,
            "pricing_strategy": strategy.get_strategy_name(),
            "hourly_rate": strategy.get_hourly_rate(ticket.vehicle.get_vehicle_type()),
            "total_fee": fee,
            "pass_type": ticket.parking_pass.get_pass_type() if ticket.parking_pass else None,
            "pass_id": ticket.parking_pass.pass_id if ticket.parking_pass else None
        }
        
        print(f"\n{'='*45}")
        print("            EXIT RECEIPT")
        print(f"{'='*45}")
        print(f"Ticket ID: {ticket_id}")
        print(f"Vehicle: {exit_details['vehicle_reg']} ({exit_details['vehicle_type']})")
        print(f"Entry Time: {exit_details['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Exit Time: {exit_details['exit_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {exit_details['duration_hours']} hours")
        print("-" * 45)
        
        if ticket.parking_pass:
            print(f"Pass Type: {exit_details['pass_type']}")
            print(f"Pass ID: {exit_details['pass_id']}")
            if isinstance(ticket.parking_pass, SingleEntryPass):
                print("Pass Status: CONSUMED")
            print("-" * 45)
            if isinstance(ticket.parking_pass, MonthlyPass):
                print(f"TOTAL FEE: $0.00 (Pass Holder)")
            else:
                print(f"TOTAL FEE: ${fee:.2f} (Flat Rate)")
        else:
            print(f"Pricing Strategy: {exit_details['pricing_strategy']}")
            print(f"Hourly Rate: ${exit_details['hourly_rate']:.2f}")
            print("-" * 45)
            print(f"TOTAL FEE: ${fee:.2f}")
        
        print(f"{'='*45}")
        print(f"Spaces Released: {ticket.spaces_used}")
        print(f"Current Availability: {self.get_available_spaces()}/{self.__total_spaces}")
        print(f"{'='*45}\n")
        
        return exit_details
    
    def issue_monthly_pass(self, holder_name: str, vehicle_registration: str, 
                           months: int = 1) -> MonthlyPass:
        pass_id = self._generate_pass_id("monthly")
        expiry_date = datetime.now() + timedelta(days=30 * months)
        
        monthly_pass = MonthlyPass(pass_id, holder_name, vehicle_registration, expiry_date)
        self.__passes[pass_id] = monthly_pass
        
        print(f"\n{'='*45}")
        print("        MONTHLY PASS ISSUED")
        print(f"{'='*45}")
        print(f"Pass ID: {pass_id}")
        print(f"Holder: {holder_name}")
        print(f"Vehicle: {vehicle_registration}")
        print(f"Issue Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"Expiry Date: {expiry_date.strftime('%Y-%m-%d')}")
        print(f"Days Valid: {monthly_pass.days_remaining()}")
        print("Status: ACTIVE")
        print(f"{'='*45}\n")
        
        return monthly_pass
    
    def issue_single_pass(self, holder_name: str, vehicle_registration: str) -> SingleEntryPass:
        pass_id = self._generate_pass_id("single")
        
        single_pass = SingleEntryPass(pass_id, holder_name, vehicle_registration)
        self.__passes[pass_id] = single_pass
        
        print(f"\n{'='*45}")
        print("       SINGLE ENTRY PASS ISSUED")
        print(f"{'='*45}")
        print(f"Pass ID: {pass_id}")
        print(f"Holder: {holder_name}")
        print(f"Vehicle: {vehicle_registration}")
        print("Status: VALID (Single Use)")
        print(f"Flat Rate: ${SingleEntryPass.FLAT_RATE:.2f}")
        print(f"{'='*45}\n")
        
        return single_pass
    
    def get_status(self) -> Dict:
        return {
            "total_spaces": self.__total_spaces,
            "occupied_spaces": self.__occupied_spaces,
            "available_spaces": self.get_available_spaces(),
            "active_tickets": len(self.__active_tickets),
            "registered_passes": len(self.__passes)
        }


# ============== ENHANCED DEMONSTRATION ==============

def main():
    print("\n" + "=" * 65)
    print("     URBAN CITY PARKING MANAGEMENT SYSTEM - DEMONSTRATION")
    print("              (Enhanced with Simulated Time Durations)")
    print("=" * 65)
    
    parking_lot = ParkingLot(300)
    
    status = parking_lot.get_status()
    print(f"\nInitial Status:")
    print(f"  Total Spaces: {status['total_spaces']}")
    print(f"  Available: {status['available_spaces']}")
    
    # ===== 5.1: Vehicle Entry (No Pass) =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.1: Vehicle Entry (No Pass)")
    print("-" * 65)
    
    car1 = Car("ABC-1234")
    entry_time_1 = datetime(2025, 1, 15, 9, 30, 0)  # Wednesday 9:30 AM
    ticket1 = parking_lot.vehicle_entry(car1, entry_time=entry_time_1, 
                                         pricing_strategy=StandardPricing())
    
    # ===== 5.2: Vehicle Exit with Fee Calculation =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.2: Vehicle Exit with Fee Calculation (3.5 hours)")
    print("-" * 65)
    
    exit_time_1 = datetime(2025, 1, 15, 13, 0, 0)  # Wednesday 1:00 PM
    parking_lot.vehicle_exit(ticket1.ticket_id, exit_time=exit_time_1,
                             pricing_strategy=StandardPricing(),
                             simulated_duration=3.5)
    
    # ===== 5.3: Monthly Pass Issuance =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.3: Monthly Pass Issuance")
    print("-" * 65)
    
    monthly_pass = parking_lot.issue_monthly_pass(
        holder_name="John Smith",
        vehicle_registration="XYZ-5678",
        months=1
    )
    
    # ===== 5.4: Entry with Monthly Pass =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.4: Entry with Monthly Pass")
    print("-" * 65)
    
    car2 = Car("XYZ-5678")
    entry_time_2 = datetime(2025, 1, 15, 14, 0, 0)
    ticket2 = parking_lot.vehicle_entry(car2, pass_id=monthly_pass.pass_id,
                                         entry_time=entry_time_2,
                                         pricing_strategy=StandardPricing())
    
    # ===== 5.5: Exit with Monthly Pass =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.5: Exit with Monthly Pass (4.5 hours - Fee Waived)")
    print("-" * 65)
    
    exit_time_2 = datetime(2025, 1, 15, 18, 30, 0)
    parking_lot.vehicle_exit(ticket2.ticket_id, exit_time=exit_time_2,
                             pricing_strategy=StandardPricing(),
                             simulated_duration=4.5)
    
    # ===== 5.6: Peak Hour Pricing =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.6: Peak Hour Pricing (Truck, 4 hours during peak)")
    print("-" * 65)
    
    truck = Truck("TRK-9999")
    entry_time_3 = datetime(2025, 1, 13, 10, 0, 0)  # Monday 10:00 AM (Peak)
    ticket3 = parking_lot.vehicle_entry(truck, entry_time=entry_time_3,
                                         pricing_strategy=PeakPricing())
    
    exit_time_3 = datetime(2025, 1, 13, 14, 0, 0)  # Monday 2:00 PM
    parking_lot.vehicle_exit(ticket3.ticket_id, exit_time=exit_time_3,
                             pricing_strategy=PeakPricing(),
                             simulated_duration=4.0)
    
    # ===== 5.7: Weekend Pricing =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.7: Weekend Pricing (Motorcycle, 5 hours)")
    print("-" * 65)
    
    motorcycle = Motorcycle("MTR-1111")
    entry_time_4 = datetime(2025, 1, 18, 11, 0, 0)  # Saturday 11:00 AM
    ticket4 = parking_lot.vehicle_entry(motorcycle, entry_time=entry_time_4,
                                         pricing_strategy=WeekendPricing())
    
    exit_time_4 = datetime(2025, 1, 18, 16, 0, 0)  # Saturday 4:00 PM
    parking_lot.vehicle_exit(ticket4.ticket_id, exit_time=exit_time_4,
                             pricing_strategy=WeekendPricing(),
                             simulated_duration=5.0)
    
    # ===== 5.8: Single Entry Pass Usage =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.8: Single Entry Pass Usage (6 hours - Flat Rate)")
    print("-" * 65)
    
    single_pass = parking_lot.issue_single_pass(
        holder_name="Jane Doe",
        vehicle_registration="SGL-2222"
    )
    
    car3 = Car("SGL-2222")
    entry_time_5 = datetime(2025, 1, 15, 8, 0, 0)
    ticket5 = parking_lot.vehicle_entry(car3, pass_id=single_pass.pass_id,
                                         entry_time=entry_time_5,
                                         pricing_strategy=StandardPricing())
    
    exit_time_5 = datetime(2025, 1, 15, 14, 0, 0)
    parking_lot.vehicle_exit(ticket5.ticket_id, exit_time=exit_time_5,
                             pricing_strategy=StandardPricing(),
                             simulated_duration=6.0)
    
    # ===== 5.9: Parking Lot Full Scenario =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.9: Parking Lot Full (Entry Denied)")
    print("-" * 65)
    
    # Simulate lot being full
    parking_lot.set_occupied_spaces(300)
    print(f"[Simulating full parking lot: {parking_lot.get_available_spaces()} spaces available]")
    
    car4 = Car("NEW-0001")
    parking_lot.vehicle_entry(car4, pricing_strategy=StandardPricing())
    
    # Reset for next demo
    parking_lot.set_occupied_spaces(0)
    
    # ===== 5.10: Invalid Pass Attempt =====
    print("\n" + "-" * 65)
    print("SCENARIO 5.10: Invalid Pass Attempt")
    print("-" * 65)
    
    car5 = Car("INV-0000")
    entry_time_6 = datetime(2025, 1, 15, 9, 0, 0)
    ticket6 = parking_lot.vehicle_entry(car5, pass_id="INVALID-001",
                                         entry_time=entry_time_6,
                                         pricing_strategy=StandardPricing())
    
    exit_time_6 = datetime(2025, 1, 15, 11, 0, 0)
    parking_lot.vehicle_exit(ticket6.ticket_id, exit_time=exit_time_6,
                             pricing_strategy=StandardPricing(),
                             simulated_duration=2.0)
    
    # ===== FINAL STATUS =====
    print("\n" + "-" * 65)
    print("FINAL STATUS")
    print("-" * 65)
    status = parking_lot.get_status()
    print(f"  Total Spaces: {status['total_spaces']}")
    print(f"  Occupied: {status['occupied_spaces']}")
    print(f"  Available: {status['available_spaces']}")
    print(f"  Active Tickets: {status['active_tickets']}")
    print(f"  Registered Passes: {status['registered_passes']}")
    
    print("\n" + "=" * 65)
    print("                   DEMONSTRATION COMPLETE")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()