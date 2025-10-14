import abc
from typing import Self

import morphio
import pandas  # noqa: ICN001
from pydantic import Field, model_validator

from obi_one.core.block import Block
from obi_one.scientific.library.morphology_locations import (
    _CEN_IDX,
    generate_neurite_locations_on,
)

_MIN_PD_SD = 0.1


class MorphologyLocationsBlock(Block, abc.ABC):
    """Base class representing parameterized locations on morphology skeletons."""

    random_seed: int | list[int] = Field(
        default=0, name="Random seed", description="Seed for the random generation of locations"
    )
    number_of_locations: int | list[int] = Field(
        default=1,
        name="Number of locations",
        description="Number of locations to generate on morphology",
    )
    section_types: tuple[int, ...] | list[tuple[int, ...]] | None = Field(
        default=None,
        name="Section types",
        description="Types of sections to generate locations on. 2: axon, 3: basal, 4: apical",
    )

    @abc.abstractmethod
    def _make_points(self, morphology: morphio.Morphology) -> pandas.DataFrame:
        """Returns a generated list of points for the morphology."""

    @abc.abstractmethod
    def _check_parameter_values(self) -> None:
        """Do specific checks on the validity of parameters."""

    @model_validator(mode="after")
    def check_parameter_values(self) -> Self:
        # Only check whenever list are resolved to individual objects
        self._check_parameter_values()
        return self

    def points_on(self, morphology: morphio.Morphology) -> pandas.DataFrame:
        self.enforce_no_multi_param()
        return self._make_points(morphology)


class RandomMorphologyLocations(MorphologyLocationsBlock):
    """Completely random locations without constraint."""

    def _make_points(self, morphology: morphio.Morphology) -> pandas.DataFrame:
        locs = generate_neurite_locations_on(
            morphology,
            n_centers=1,
            n_per_center=self.number_of_locations,
            srcs_per_center=1,
            center_path_distances_mean=0.0,
            center_path_distances_sd=0.0,
            max_dist_from_center=None,
            lst_section_types=self.section_types,
            seed=self.random_seed,
        ).drop(columns=[_CEN_IDX])
        return locs

    def _check_parameter_values(self) -> None:
        # Only check whenever list are resolved to individual objects
        if not isinstance(self.number_of_locations, list):  # noqa: SIM102
            if self.number_of_locations <= 0:
                msg = f"Number of locations: {self.number_of_locations} <= 0"
                raise ValueError(msg)


class RandomGroupedMorphologyLocations(MorphologyLocationsBlock):
    """Completely random locations, but grouped into abstract groups."""

    n_groups: int | list[int] = Field(
        default=1,
        name="Number of groups",
        description="Number of groups of locations to \
            generate",
    )

    def _make_points(self, morphology: morphio.Morphology) -> pandas.DataFrame:
        locs = generate_neurite_locations_on(
            morphology,
            n_centers=1,
            n_per_center=self.number_of_locations,
            srcs_per_center=self.n_groups,
            center_path_distances_mean=0.0,
            center_path_distances_sd=0.0,
            max_dist_from_center=None,
            lst_section_types=self.section_types,
            seed=self.random_seed,
        ).drop(columns=[_CEN_IDX])
        return locs

    def _check_parameter_values(self) -> None:
        # Only check whenever list are resolved to individual objects
        if not isinstance(self.n_groups, list):  # noqa: SIM102
            if self.n_groups <= 0:
                msg = f"Number of groups: {self.n_groups} <= 0"
                raise ValueError(msg)


class PathDistanceMorphologyLocations(MorphologyLocationsBlock):
    """Locations around a specified path distance."""

    path_dist_mean: float | list[float] = Field(
        name="Path distance mean",
        description="Mean of a Gaussian, defined on soma path distance in um. Used to determine \
            locations.",
    )
    path_dist_tolerance: float | list[float] = Field(
        name="Path distance tolerance",
        description="Amount of deviation in um from mean path distance that is tolerated. Must be \
            > 1.0",
    )

    def _make_points(self, morphology: morphio.Morphology) -> pandas.DataFrame:
        locs = generate_neurite_locations_on(
            morphology,
            n_centers=self.number_of_locations,
            n_per_center=1,
            srcs_per_center=1,
            center_path_distances_mean=self.path_dist_mean,
            center_path_distances_sd=0.1 * self.path_dist_tolerance,
            max_dist_from_center=0.9 * self.path_dist_tolerance,
            lst_section_types=self.section_types,
            seed=self.random_seed,
        ).drop(columns=[_CEN_IDX])
        return locs

    def _check_parameter_values(self) -> None:
        # Only check whenever list are resolved to individual objects
        if not isinstance(self.path_dist_mean, list):  # noqa: SIM102
            if self.path_dist_mean < 0:
                msg = f"Path distance mean: {self.path_dist_mean} < 0"
                raise ValueError(msg)

        if not isinstance(self.path_dist_tolerance, list):  # noqa: SIM102
            if self.path_dist_tolerance < 1.0:
                msg = f"Path dist tolerance: {self.path_dist_tolerance} < 1.0 (numerical stability)"
                raise ValueError(msg)


class ClusteredMorphologyLocations(MorphologyLocationsBlock):
    """Clustered random locations."""

    n_clusters: int | list[int] = Field(
        name="Number of clusters", description="Number of location clusters to generate"
    )
    cluster_max_distance: float | list[float] = Field(
        name="Cluster maximum distance",
        description="Maximum distance in um of generated locations from the center of their \
            cluster",
    )

    def _make_points(self, morphology: morphio.Morphology) -> pandas.DataFrame:
        # TODO: This rounds down. Could make missing points
        # in a second call to generate_neurite_locations_on
        n_per_cluster = int(self.number_of_locations / self.n_clusters)
        locs = generate_neurite_locations_on(
            morphology,
            n_centers=self.n_clusters,
            n_per_center=n_per_cluster,
            srcs_per_center=1,
            center_path_distances_mean=0.0,
            center_path_distances_sd=1e20,
            max_dist_from_center=self.cluster_max_distance,
            lst_section_types=self.section_types,
            seed=self.random_seed,
        ).drop(columns=[_CEN_IDX])
        return locs

    def _check_parameter_values(self) -> None:
        # Only check whenever list are resolved to individual objects
        if not isinstance(self.n_clusters, list):
            if self.n_clusters < 1:
                msg = f"Number of clusters {self.n_clusters} < 1"
                raise ValueError(msg)
            if not isinstance(self.number_of_locations, list):  # noqa: SIM102
                if self.number_of_locations < self.n_clusters:
                    msg = f"Number of locations: {self.number_of_locations} \
                        < number of clusters: {self.n_clusters}"
                    raise ValueError(msg)


class ClusteredGroupedMorphologyLocations(
    ClusteredMorphologyLocations, RandomGroupedMorphologyLocations
):
    """Clustered random locations, grouped in to conceptual groups."""

    def _make_points(self, morphology: morphio.Morphology) -> pandas.DataFrame:
        # TODO: This rounds down. Could make missing points
        # in a second call to generate_neurite_locations_on
        n_per_cluster = int(self.number_of_locations / self.n_clusters)
        locs = generate_neurite_locations_on(
            morphology,
            n_centers=self.n_clusters,
            n_per_center=n_per_cluster,
            srcs_per_center=self.n_groups,
            center_path_distances_mean=0.0,
            center_path_distances_sd=1e20,
            max_dist_from_center=self.cluster_max_distance,
            lst_section_types=self.section_types,
            seed=self.random_seed,
        ).drop(columns=[_CEN_IDX])
        return locs

    def _check_parameter_values(self) -> None:
        super(ClusteredMorphologyLocations, self)._check_parameter_values()
        super(RandomGroupedMorphologyLocations, self)._check_parameter_values()


class ClusteredPathDistanceMorphologyLocations(ClusteredMorphologyLocations):
    """Clustered random locations around a specified path distance. Also creates
    groups within each cluster. This exposes the full possible complexity.
    """

    path_dist_mean: float | list[float] = Field(
        name="Path distance mean",
        description="Mean of a Gaussian, defined on soma path distance in um. Used to determine \
            locations.",
    )
    path_dist_sd: float | list[float] = Field(
        name="Path distance mean",
        description="SD of a Gaussian, defined on soma path distance in um. Used to determine \
            locations.",
    )
    n_groups_per_cluster: int | list[int] = Field(
        default=1,
        name="Number of groups per cluster",
        description="Number of conceptual groups per location cluster to generate",
    )

    def _make_points(self, morphology: morphio.Morphology) -> pandas.DataFrame:
        # TODO: This rounds down. Could make missing points
        # in a second call to generate_neurite_locations_on
        n_per_cluster = int(self.number_of_locations / self.n_clusters)
        locs = generate_neurite_locations_on(
            morphology,
            n_centers=self.n_clusters,
            n_per_center=n_per_cluster,
            srcs_per_center=self.n_groups_per_cluster,
            center_path_distances_mean=self.path_dist_mean,
            center_path_distances_sd=self.path_dist_sd,
            max_dist_from_center=self.cluster_max_distance,
            lst_section_types=self.section_types,
            seed=self.random_seed,
        )
        return locs

    def _check_parameter_values(self) -> None:
        super()._check_parameter_values()
        # Only check whenever list are resolved to individual objects
        if not isinstance(self.path_dist_mean, list):  # noqa: SIM102
            if self.path_dist_mean < 0:
                msg = f"Path distance mean: {self.path_dist_mean} < 0"
                raise ValueError(msg)

        if not isinstance(self.path_dist_sd, list):  # noqa: SIM102
            if self.path_dist_sd < _MIN_PD_SD:
                msg = f"Path distance std: {self.path_dist_sd} < {_MIN_PD_SD} (numerical stability)"
                raise ValueError(msg)

        if not isinstance(self.n_groups_per_cluster, list):  # noqa: SIM102
            if self.n_groups_per_cluster < 1:
                msg = f"Number of groups per cluster: {self.n_groups_per_cluster} < 1"
                raise ValueError(msg)
