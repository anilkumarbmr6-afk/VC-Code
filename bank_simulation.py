from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List

import simpy

ARRIVAL_MEAN_MINUTES = 3.0
SERVICE_MEAN_MINUTES = 4.0
NUM_TELLERS = 2
DAY_LENGTH_MINUTES = 480.0
SIMULATION_HORIZON_MINUTES = DAY_LENGTH_MINUTES + 120.0


@dataclass
class SimulationSummary:
    avg_wait: float
    worst_wait: float
    p95_wait: float
    teller_busy_pct: float
    total_customers: int
    wait_times: List[float] = field(default_factory=list)
    busy_rates: List[float] = field(default_factory=list)


def _simulate_single_day(rng: random.Random) -> tuple[list[float], list[float]]:
    env = simpy.Environment()
    teller_pool = simpy.Resource(env, capacity=NUM_TELLERS)
    wait_times: list[float] = []
    busy_times: list[float] = []

    def customer() -> None:
        arrival_time = env.now
        with teller_pool.request() as request:
            yield request
            wait = env.now - arrival_time
            wait_times.append(wait)
            service_start = env.now
            service_time = rng.expovariate(1.0 / SERVICE_MEAN_MINUTES)
            yield env.timeout(service_time)
            busy_times.append(env.now - service_start)

    def arrivals() -> None:
        while True:
            yield env.timeout(rng.expovariate(1.0 / ARRIVAL_MEAN_MINUTES))
            if env.now >= DAY_LENGTH_MINUTES:
                break
            env.process(customer())

    env.process(arrivals())
    env.run(until=SIMULATION_HORIZON_MINUTES)
    return wait_times, busy_times


def simulate_bank_day(runs: int = 500, seed: int = 42) -> SimulationSummary:
    if runs <= 0:
        raise ValueError("runs must be positive")

    all_waits: list[float] = []
    busy_rates: list[float] = []
    total_customers = 0

    for run_index in range(runs):
        rng = random.Random(seed + run_index)
        wait_times, busy_times = _simulate_single_day(rng)
        all_waits.extend(wait_times)
        total_customers += len(wait_times)
        if busy_times:
            busy_rates.append((sum(busy_times) / (NUM_TELLERS * DAY_LENGTH_MINUTES)) * 100.0)

    avg_wait = sum(all_waits) / len(all_waits) if all_waits else 0.0
    worst_wait = max(all_waits, default=0.0)
    if all_waits:
        ordered = sorted(all_waits)
        p95_index = max(0, min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1))
        p95_wait = ordered[p95_index]
    else:
        p95_wait = 0.0

    teller_busy_pct = sum(busy_rates) / len(busy_rates) if busy_rates else 0.0

    return SimulationSummary(
        avg_wait=avg_wait,
        worst_wait=worst_wait,
        p95_wait=p95_wait,
        teller_busy_pct=teller_busy_pct,
        total_customers=total_customers,
        wait_times=all_waits,
        busy_rates=busy_rates,
    )
