import carla
import py_trees

from scenario.atomic.behavior import ActorDestroy, ActorTransformSetter
from scenario.atomic.trigger import StandStill, TriggerTimer
from scenario.pattern.basic import BasicScenario, CarlaDataProvider
from scenario.configuration import SeedConfig
from .behavior import WalkerWaypointFollower

class WalkerScenario(BasicScenario):

    name = 'WalkerScenario'

    def __init__(
            self,
            config: SeedConfig,
            timeout=60,
            debug_mode=False,
            terminate_on_failure=True,
            criteria_enable: bool = False,
            fitness_enable: bool = False
    ):
        self.other_actors_config = list()

        super(WalkerScenario, self).__init__(
            self.name,
            config,
            timeout,
            terminate_on_failure=terminate_on_failure,
            debug_mode=debug_mode,
            criteria_enable=criteria_enable,
            fitness_enable=fitness_enable
        )

    def _initialize_actors(self):
        """
        Custom initialization
        """
        walker_section = self.config.scenario.walker_section
        walker_actors_config = walker_section.agents

        self.other_actors = list()
        self.other_actors_config = list()
        for actor_config in walker_actors_config:
            # initialize vehicles
            new_actor = CarlaDataProvider.request_new_actor_by_config(actor_config)
            if new_actor is None:
                continue
            new_actor.set_simulate_physics(enabled=True)
            self.other_actors.append(new_actor)
            self.other_actors_config.append(actor_config)

    def _create_behavior(self):
        actor_pool_tree = py_trees.composites.Parallel(
            name="WalkerPool",
            policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ALL
        )

        for i in range(len(self.other_actors_config)):
            actor_config = self.other_actors_config[i]
            actor = self.other_actors[i]

            py_trees_name = f"walker_behavior_{actor_config.id}"

            actor_tree = py_trees.composites.Sequence(name=py_trees_name)
            actor_start_wp = actor_config.route[0]
            actor_transform = carla.Transform(
                location=carla.Location(
                    x=actor_start_wp.x,
                    y=actor_start_wp.y,
                    z=0.5
                ),
                rotation=carla.Rotation(
                    pitch=actor_start_wp.pitch,
                    yaw=actor_start_wp.yaw,
                    roll=actor_start_wp.roll
                )
            )
            start_transform = ActorTransformSetter(actor, actor_transform)
            actor_tree.add_child(start_transform)
            actor_tree.add_child(
                TriggerTimer(actor, name=f"{py_trees_name}_behavior_trigger_time", duration=actor_config.trigger_time))

            actor_behavior = py_trees.composites.Parallel(
                name=f"{py_trees_name}_behavior",
                policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE
            )

            actor_behavior.add_child(WalkerWaypointFollower(
                actor,
                actor_config
            ))
            actor_behavior.add_child(StandStill(actor, name=f"{py_trees_name}_behavior_standstill", duration=60))

            actor_tree.add_child(actor_behavior)
            actor_tree.add_child(StandStill(actor, name=f"{py_trees_name}_behavior_standstill", duration=10))
            actor_tree.add_child(ActorDestroy(actor))

            actor_pool_tree.add_child(actor_tree)

        return actor_pool_tree
