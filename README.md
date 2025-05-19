# Agent-Based Economic Simulation

## Overview

This is a simple agent-based economic simulation where agents produce goods, trade with each other, and attempt to meet their daily needs. The simulation runs over a specified number of days, and agents can die if they fail to meet their needs for a certain number of consecutive days or if they reach the maximum age.

## Key Concepts

- **Agents**: Each agent is an entity that produces goods, has daily needs, and trades with other agents to fulfill those needs.
- **Goods**: There are five types of goods in the simulation: `WATER`, `WHEAT`, `FRUIT`, `VEGETABLES`, and `ELECTRICITY`.
- **Production Difficulty**: Each good has a production difficulty level. Higher difficulty means it is harder to produce.
- **Needs**: Each agent has daily needs for each type of good. If an agent cannot meet its needs for a certain number of consecutive days, it will die.
- **Wealth**: Agents have wealth in dollars, which they use to buy goods from other agents.
- **Trade**: Agents trade goods with each other based on availability, price, and probability.

## Code Structure

### Constants

- `WATER`, `WHEAT`, `FRUIT`, `VEGETABLES`, `ELECTRICITY`: Types of goods.
- `NUMBER_OF_DAYS_SURVIVING_WITHOUT_NEEDS`: Number of consecutive days an agent can survive without meeting its needs.
- `MAX_AGE_OF_AGENT`: Maximum age an agent can reach before dying.

### Production Difficulty

- `production_difficulty`: A dictionary that maps each good to its production difficulty.
- `inverse_difficulty`: A dictionary that maps each good to the inverse of its production difficulty.
- `total_weight`: The sum of the inverse difficulties.
- `production_weights`: A dictionary that maps each good to its production weight, which is used to determine the probability of producing each good.

### Agent Class

- **Attributes**:
  - `id`: Unique identifier for the agent.
  - `education_level`: Education level of the agent (not currently used in the simulation).
  - `wealth`: Wealth of the agent in dollars.
  - `savings`: Savings of the agent (not currently used in the simulation).
  - `debt`: Debt of the agent (not currently used in the simulation).
  - `consumption`: Consumption of the agent (not currently used in the simulation).
  - `days_elapsed`: Number of days the agent has been alive.
  - `days_without_fulfilled_need`: Number of consecutive days the agent has failed to meet its needs.
  - `alive`: Whether the agent is alive or dead.
  - `produced_goods`: A dictionary that maps each good the agent produces to the quantity produced.
  - `specialization_factor`: A factor that determines how efficiently the agent can produce goods.
  - `needs`: A dictionary that maps each good to the quantity the agent needs daily.
  - `mu`: Mean production quantity for Gaussian distribution.
  - `sigma`: Standard deviation for Gaussian distribution, adjusted by the specialization factor.

- **Methods**:
  - `trade(agents)`: Attempts to trade with other agents to fulfill needs.
  - `buy_from_seller(seller, good_needed, price, amount_needed)`: Attempts to buy a good from a seller.
  - `generate_yield(good)`: Generates a new daily yield for a good.
  - `set_prices()`: Sets the prices for the goods the agent produces.
  - `choose_seller(agents, good_needed)`: Chooses a seller to buy a good from based on availability, price, and probability.
  - `tick(agents)`: Simulates one day for the agent, including trading and generating new production.
  - `__str__()`: Returns a string representation of the agent.

### Simulation

- **Initialization**:
  - `num_agents`: Number of agents to create.
  - `agents`: A list of agents.
  - `dead_agents`: A list to keep track of agents that have died.

- **Simulation Loop**:
  - The simulation runs for a specified number of days.
  - Each day, each agent performs a `tick`, which includes trading and generating new production.
  - Agents that die are removed from the active agents list and added to the `dead_agents` list.

