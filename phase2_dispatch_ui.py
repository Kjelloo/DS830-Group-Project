from __future__ import annotations

from typing import Optional, Dict, Callable, Any
from gui._engine import run_app
from phase2.RequestGenerator import RequestGenerator


def main(backend: Optional[Dict[str, Callable[..., Any]]] = None) -> None:
    if backend is not None:
        run_app(backend)
    else:
        run_app()


if __name__ == "__main__":

    from adapter.GUIAdapter import GUIAdapter
    import datetime
    from phase2.DeliverySimulation import DeliverySimulation
    from phase2.Driver import Driver
    from phase2.Request import Request
    from phase2.MutationRule import MutationRule
    from phase2.dispatch.GlobalGreedyPolicy import GlobalGreedyPolicy

    run_id = datetime.datetime.now().strftime("%H%M%S_%d%m%y")

    simulation = DeliverySimulation(
        time=0,
        width=50,
        height=30,
        drivers=list[Driver](),
        requests=list[Request](),
        mutation_rule=MutationRule(n_trips=5, threshold=0.7, run_id=run_id),
        dispatch_policy=GlobalGreedyPolicy(),
        run_id=run_id,
        timeout=30,
        statistics={},
        request_generator=RequestGenerator(start_id=1, rate=0.5, width=50, height=30, run_id=run_id) # Will be overwritten in the adapter init_state
    )

    adapter = GUIAdapter(
        run_id=run_id,
        delivery_simulation=simulation
    )

    _backend = {
        "load_drivers": adapter.load_drivers,
        "load_requests": adapter.load_requests,
        "generate_drivers": adapter.generate_drivers,
        "generate_requests": adapter.generate_requests,
        "init_state": adapter.init_state,
        "simulate_step": adapter.simulate_step,
        "get_plot_data": adapter.get_plot_data
    }

    main(_backend)
