import random

# === CONFIGURABLE SIMULATION PARAMETERS ===
GOODS = {
    "water": 1,
    "wheat": 2,
    "fruit": 3,
    "vegetables": 3,
    "electricity": 5
}

INITIAL_AGENTS = 5
INITIAL_WEALTH = 100
MAX_AGE = 70
DAYS_WITHOUT_NEEDS = 10
EDUCATION_RANGE = (1, 10)
NEEDS_RANGE = {
    "water": (1, 3),
    "wheat": (0, 2),
    "fruit": (1, 3),
    "vegetables": (1, 2),
    "electricity": (1, 3)
}
PRODUCTION_GOODS_RANGE = (1, 5)
PRODUCTION_MU_RANGE = (1, 150)
PRODUCTION_FAIL_CHANCE = 0.1
MAX_YIELD = 20
SPECIALIZATION_PENALTY = 0.1
TAX_RATE = 0.001
SIMULATION_DAYS = 15
POPULATION_GROWTH_RATE = 0.3
OFFSPRING_WEALTH_FRACTION = 0.25

# Government Service Parameters
SERVICE_AGENTS = {
    "Police+Military": {"boost_factor": 0.1, "allocation": 0.2},  # Boosts all goods slightly
    "Education": {"boost_factor": 0.3, "allocation": 0.3},       # Stronger boost tied to education
    "Infrastructure+Transportation": {"boost_factor": 0.2, "allocation": 0.3},  # Moderate boost
    "Healthcare": {"boost_factor": 0.15, "allocation": 0.2}      # Boosts survival and production
}

# Derived Constants
inverse_difficulty = {good: 1 / diff for good, diff in GOODS.items()}
total_weight = sum(inverse_difficulty.values())
production_weights = {good: weight / total_weight for good, weight in inverse_difficulty.items()}

import random
from math import floor

# [CONFIGURABLE PARAMETERS AND DERIVED CONSTANTS UNCHANGED]

# === CLASSES ===
class Government:
    def __init__(self):
        self.wealth = 0
        self.money_unit = "$"

    def collect_taxes(self, agents):
        total_tax = 0
        for agent in agents:
            if agent.alive:
                tax = round(agent.wealth * TAX_RATE, 2)
                agent.wealth = round(max(0, agent.wealth - tax), 2)
                total_tax += tax
        self.wealth = round(self.wealth + total_tax, 2)
        return total_tax

    def receive_dead_agent_wealth(self, agent):
        inherited_wealth = agent.wealth
        self.wealth = round(self.wealth + inherited_wealth, 2)
        agent.wealth = 0
        return inherited_wealth

    def distribute_funds(self, service_agents):
        if self.wealth <= 0:
            return 0
        total_spent = 0
        allocations = {}
        for service, params in SERVICE_AGENTS.items():
            if service == list(SERVICE_AGENTS.keys())[-1]:  # Last agent gets remainder
                allocation = self.wealth - total_spent
            else:
                allocation = round(self.wealth * params["allocation"], 2)
            allocations[service] = allocation
            total_spent += allocation
        for service, amount in allocations.items():
            service_agents[service].wealth = round(service_agents[service].wealth + amount, 2)
        spent_amount = self.wealth
        self.wealth = 0  # Fully deplete government wealth
        return spent_amount

    def __str__(self):
        return f"Government | Wealth: ${self.wealth:.2f}"

class ServiceAgent:
    def __init__(self, name, boost_factor):
        self.name = name
        self.wealth = 0
        self.boost_factor = boost_factor
        self.money_unit = "$"

    def provide_boost(self, agents):
        if self.wealth <= 0:
            return
        boost_amount = self.wealth * self.boost_factor / 1000
        if self.name == "Police+Military":
            for agent in agents:
                if agent.alive:
                    agent.gov_efficiency_boost["general"] += boost_amount
        elif self.name == "Education":
            for agent in agents:
                if agent.alive:
                    agent.gov_efficiency_boost["education"] += boost_amount * (agent.education_level / EDUCATION_RANGE[1])
        elif self.name == "Infrastructure+Transportation":
            for agent in agents:
                if agent.alive:
                    agent.gov_efficiency_boost["infra"] += boost_amount
        elif self.name == "Healthcare":
            for agent in agents:
                if agent.alive:
                    agent.gov_efficiency_boost["health"] += boost_amount
                    agent.days_without_fulfilled_need = max(0, agent.days_without_fulfilled_need - 1)
        self.wealth = 0  # Spend all wealth

    def __str__(self):
        return f"{self.name} | Wealth: ${self.wealth:.2f}"

class Agent:
    def __init__(self, id, education_level, initial_wealth, parent_id=None):
        self.id = id
        self.education_level = education_level
        self.wealth = initial_wealth
        self.parent_id = parent_id
        self.days_elapsed = 0
        self.days_without_fulfilled_need = 0
        self.alive = True
        self.death_reason = ""
        self.money_unit = "$"
        self.gov_efficiency_boost = {"general": 0, "education": 0, "infra": 0, "health": 0}

        num_goods = random.randint(*PRODUCTION_GOODS_RANGE)
        self.produced_goods = {good: 0 for good in random.sample(list(GOODS.keys()), min(num_goods, len(GOODS)))}
        self.specialization_factor = max(0.5, 1 - len(self.produced_goods) * SPECIALIZATION_PENALTY)

        self.needs = {good: random.randint(*range_) for good, range_ in NEEDS_RANGE.items()}
        self.mu = random.randint(*PRODUCTION_MU_RANGE)
        self.sigma = self.specialization_factor * 3

    def trade(self, agents):
        unmet_needs = 0
        for good, amount in self.needs.items():
            if amount > 0:
                remaining_need = amount - self.produced_goods.get(good, 0)
                if remaining_need > 0:
                    seller = self.choose_seller(agents, good)
                    if seller:
                        price = seller.set_prices().get(good, float('inf'))
                        if price != float('inf'):
                            amount_bought = self.buy_from_seller(seller, good, price, remaining_need)
                            self.produced_goods[good] = self.produced_goods.get(good, 0) + amount_bought
                            remaining_need -= amount_bought
                    if remaining_need > 0:
                        unmet_needs += 1
        self.days_without_fulfilled_need = self.days_without_fulfilled_need + 1 if unmet_needs > 0 else 0

    def buy_from_seller(self, seller, good, price, amount_needed):
        available_amount = min(amount_needed, seller.produced_goods.get(good, 0))
        affordable_amount = min(available_amount, floor(self.wealth / price)) if price > 0 else 0
        if affordable_amount > 0:
            cost = round(affordable_amount * price, 2)
            self.wealth = round(max(0, self.wealth - cost), 2)
            seller.wealth = round(seller.wealth + cost, 2)
            seller.produced_goods[good] = max(0, seller.produced_goods[good] - affordable_amount)
            return affordable_amount
        return 0

    def generate_yield(self, good):
        if good not in self.produced_goods or random.random() < PRODUCTION_FAIL_CHANCE:
            return 0
        yield_value = random.gauss(self.mu, self.sigma)
        education_boost = 1.0 + (self.education_level - EDUCATION_RANGE[0]) * 0.1
        total_boost = (1 + self.gov_efficiency_boost["general"] + 
                       self.gov_efficiency_boost["education"] + 
                       self.gov_efficiency_boost["infra"] + 
                       self.gov_efficiency_boost["health"])
        boosted_yield = yield_value * education_boost * total_boost
        return max(0, min(MAX_YIELD, round(boosted_yield)))

    def set_prices(self):
        return {good: float('inf') if qty <= 0 else max(1, 10 / qty) 
                for good, qty in self.produced_goods.items()}

    def choose_seller(self, agents, good):
        possible_sellers = [a for a in agents if a != self and a.alive and 
                          good in a.produced_goods and a.produced_goods[good] > 0]
        if not possible_sellers:
            return None
        sellers_with_prices = [(s, s.set_prices().get(good, float('inf'))) for s in possible_sellers]
        valid_sellers = [(s, p) for s, p in sellers_with_prices if p != float('inf')]
        if not valid_sellers:
            return None
        total_prob = sum(1 / (p + 0.01) for _, p in valid_sellers)
        if total_prob == 0:
            return None
        rand_choice = random.random() * total_prob
        cumulative = 0
        for seller, price in valid_sellers:
            cumulative += 1 / (price + 0.01)
            if rand_choice <= cumulative:
                return seller
        return valid_sellers[-1][0]

    def tick(self, agents):
        if not self.alive:
            return
        self.days_elapsed += 1
        for good in self.produced_goods:
            self.produced_goods[good] = self.generate_yield(good)
        self.trade(agents)
        if self.days_without_fulfilled_need >= DAYS_WITHOUT_NEEDS:
            self.alive = False
            self.death_reason = "unmet needs"
        elif self.days_elapsed >= MAX_AGE:
            self.alive = False
            self.death_reason = "old age"

    def __str__(self):
        parent_str = f" (offspring of {self.parent_id})" if self.parent_id is not None else ""
        return (f"Agent {self.id}{parent_str} | Wealth: ${self.wealth:.2f} | "
                f"Alive: {self.alive} | Age: {self.days_elapsed}")

def create_offspring(dead_agent, new_id):
    education = max(EDUCATION_RANGE[0], 
                   min(EDUCATION_RANGE[1], int(random.gauss(dead_agent.education_level, 1))))
    initial_wealth = round(dead_agent.original_wealth * OFFSPRING_WEALTH_FRACTION, 2)
    return Agent(new_id, education, initial_wealth, parent_id=dead_agent.id)

# === SIMULATION ===
government = Government()
service_agents = {name: ServiceAgent(name, params["boost_factor"]) 
                  for name, params in SERVICE_AGENTS.items()}
agents = [Agent(id=i, education_level=random.randint(*EDUCATION_RANGE), initial_wealth=INITIAL_WEALTH) 
          for i in range(INITIAL_AGENTS)]
for agent in agents:
    agent.original_wealth = agent.wealth
dead_agents = []
next_agent_id = INITIAL_AGENTS

initial_total_wealth = round(sum(agent.wealth for agent in agents) + government.wealth + 
                            sum(sa.wealth for sa in service_agents.values()), 2)
print(f"\n=== Initial Total Wealth: ${initial_total_wealth:.2f} ===")

for day in range(SIMULATION_DAYS):
    print(f"\n=== Day {day + 1} ===")
    
    tax_collected = government.collect_taxes(agents)
    print(f"Government collected ${tax_collected:.2f} in taxes")
    spent_amount = government.distribute_funds(service_agents)
    if spent_amount > 0:
        print(f"Government distributed ${spent_amount:.2f} to service agents")
    print(government)
    
    for service_agent in service_agents.values():
        service_agent.provide_boost(agents)
        print(service_agent)
    
    for agent in agents[:]:
        if agent.alive:
            agent.tick(agents)
            if not agent.alive:
                print(f"Agent {agent.id} died due to {agent.death_reason}")
                inherited = government.receive_dead_agent_wealth(agent)
                print(f"Government inherited ${inherited:.2f} from Agent {agent.id}")
                dead_agents.append(agent)
                agents.remove(agent)
                if random.random() < POPULATION_GROWTH_RATE:
                    new_agent = create_offspring(agent, next_agent_id)
                    new_agent.original_wealth = new_agent.wealth
                    agents.append(new_agent)
                    print(f"New Agent {new_agent.id} born as offspring of Agent {agent.id}")
                    next_agent_id += 1
    
    for agent in agents:
        print(agent)
    
    # Debug: Check total wealth each day
    daily_total = round(sum(agent.wealth for agent in agents) + government.wealth + 
                        sum(sa.wealth for sa in service_agents.values()), 2)
    print(f"Daily Total Wealth: ${daily_total:.2f}")

final_total_wealth = round(sum(agent.wealth for agent in agents) + government.wealth + 
                          sum(sa.wealth for sa in service_agents.values()), 2)
print(f"\n=== Final Total Wealth: ${final_total_wealth:.2f} ===")
wealth_diff = round(final_total_wealth - initial_total_wealth, 2)
print(f"Wealth Difference: ${wealth_diff:.2f}")
if abs(wealth_diff) > 0.01:
    print("WARNING: Wealth not conserved!")

print("\n=== Simulation Summary ===")
print(f"Initial agents: {INITIAL_AGENTS}")
print(f"Dead agents: {len(dead_agents)}")
print(f"Final agents: {len(agents)}")
print(f"Total agents created: {next_agent_id}")
avg_age = sum(a.days_elapsed for a in dead_agents) / len(dead_agents) if dead_agents else 0
print(f"Average age at death: {avg_age:.2f} days")