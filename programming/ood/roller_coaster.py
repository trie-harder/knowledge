"""
OOD: Roller Coaster System with Extensible Score Calculation
=============================================================

Design goals
------------
1. Multiple coaster *types* that share a common interface but carry
   type-specific attributes (Wooden, Steel, Launch).
2. Multiple *scoring strategies* that can be swapped at runtime without
   touching the coaster classes (Strategy pattern).
3. Extending either axis — new coaster type OR new scoring formula —
   requires adding a class, not editing existing ones (Open/Closed).

Structure
---------
  ScoringStrategy  (ABC)               ← strategy interface
    ├─ ThrillScoring                   ← weights speed + inversions
    ├─ FamilyScoring                   ← weights accessibility
    └─ SafetyScoring                   ← penalises age + inversions

  RollerCoaster    (ABC)               ← base coaster
    ├─ WoodenCoaster                   ← adds wood_type
    ├─ SteelCoaster                    ← adds is_inverted flag
    └─ LaunchCoaster                   ← adds launch_force_g

Composition: every RollerCoaster holds a ScoringStrategy reference.
Calling coaster.score() delegates entirely to the injected strategy.
Swapping the strategy (coaster.scorer = FamilyScoring()) is the ONLY
change needed to switch formulas — no coaster logic is touched.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ──────────────────────────────────────────────
# STRATEGY INTERFACE
# ──────────────────────────────────────────────

class ScoringStrategy(ABC):
    """
    Abstract base for all scoring algorithms.

    Receives the coaster object so strategies can read any attribute they
    need without coupling the base class to any particular formula.
    """

    @abstractmethod
    def compute(self, coaster: RollerCoaster) -> float:
        """Return a numeric score for the given coaster."""
        ...


# ──────────────────────────────────────────────
# CONCRETE STRATEGIES
# ──────────────────────────────────────────────

class ThrillScoring(ScoringStrategy):
    """
    Scores a coaster on raw excitement.
    Formula: speed * 0.5 + inversions * 10 + height * 0.1
    Each weight reflects perceived rider adrenaline contribution.
    """

    def compute(self, coaster: RollerCoaster) -> float:
        return (
            coaster.speed_mph   * 0.5
            + coaster.num_inversions * 10.0
            + coaster.height_ft * 0.1
        )


class FamilyScoring(ScoringStrategy):
    """
    Scores a coaster on accessibility for mixed-age groups.
    Rewards moderate height/speed; heavily penalises inversions
    (many families avoid them) and extremely high speeds.
    Formula: 100 - |speed - 40| * 0.3 - |height - 80| * 0.2 - inversions * 15
    """

    def compute(self, coaster: RollerCoaster) -> float:
        speed_penalty   = abs(coaster.speed_mph - 40) * 0.3   # sweet spot ≈ 40 mph
        height_penalty  = abs(coaster.height_ft - 80) * 0.2   # sweet spot ≈ 80 ft
        inversion_penalty = coaster.num_inversions * 15.0
        return 100.0 - speed_penalty - height_penalty - inversion_penalty


class SafetyScoring(ScoringStrategy):
    """
    Scores a coaster on perceived structural/operational safety.
    Penalises older rides and rides with many inversions (more stress on track).
    Formula: 100 - age * 1.5 - inversions * 5
    """

    def compute(self, coaster: RollerCoaster) -> float:
        return 100.0 - coaster.age_years * 1.5 - coaster.num_inversions * 5.0


# ──────────────────────────────────────────────
# BASE COASTER  (abstract)
# ──────────────────────────────────────────────

class RollerCoaster(ABC):
    """
    Abstract base for all coaster types.

    Shared attributes live here; type-specific attributes live in
    subclasses.  The `scorer` field is a ScoringStrategy — injected at
    construction time and replaceable at any point (dependency injection).

    Why ABC here?
    - Forces subclasses to implement `describe()` (each type has unique copy).
    - Prevents instantiating a bare RollerCoaster with no meaningful type.
    """

    def __init__(
        self,
        name: str,
        height_ft: float,
        speed_mph: float,
        num_inversions: int,
        age_years: int,
        scorer: ScoringStrategy,
    ) -> None:
        self.name            = name
        self.height_ft       = height_ft
        self.speed_mph       = speed_mph
        self.num_inversions  = num_inversions
        self.age_years       = age_years
        self.scorer          = scorer          # ← strategy held by composition

    def score(self) -> float:
        """Delegate entirely to the injected strategy. No formula here."""
        return self.scorer.compute(self)

    @abstractmethod
    def describe(self) -> str:
        """Return a human-readable summary including type-specific details."""
        ...

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.name!r}, "
            f"{self.speed_mph} mph, {self.height_ft} ft, "
            f"{self.num_inversions} inv, {self.age_years} yrs)"
        )


# ──────────────────────────────────────────────
# CONCRETE COASTER TYPES
# ──────────────────────────────────────────────

class WoodenCoaster(RollerCoaster):
    """
    A traditional wooden coaster.
    Extra attribute: wood_type (e.g. "pine", "laminated").
    Wooden coasters typically have zero inversions and rougher rides.
    """

    def __init__(self, wood_type: str, **kwargs) -> None:
        # wood_type is WoodenCoaster-specific; everything else goes up to base
        super().__init__(**kwargs)
        self.wood_type = wood_type

    def describe(self) -> str:
        return (
            f"[Wooden] {self.name} — built from {self.wood_type} wood, "
            f"{self.height_ft} ft tall, {self.speed_mph} mph top speed."
        )


class SteelCoaster(RollerCoaster):
    """
    A modern steel coaster.
    Extra attribute: is_inverted — whether riders hang below the track.
    Steel construction allows tighter loops and more inversions.
    """

    def __init__(self, is_inverted: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.is_inverted = is_inverted

    def describe(self) -> str:
        inverted_label = "inverted " if self.is_inverted else ""
        return (
            f"[Steel] {self.name} — {inverted_label}steel coaster, "
            f"{self.num_inversions} inversions, {self.speed_mph} mph top speed."
        )


class LaunchCoaster(RollerCoaster):
    """
    A hydraulic/magnetic launch coaster.
    Extra attribute: launch_force_g — peak acceleration in g-forces.
    Launch coasters reach top speed almost instantly (no chain lift).
    """

    def __init__(self, launch_force_g: float, **kwargs) -> None:
        super().__init__(**kwargs)
        self.launch_force_g = launch_force_g

    def describe(self) -> str:
        return (
            f"[Launch] {self.name} — {self.launch_force_g}g launch force, "
            f"{self.speed_mph} mph top speed, {self.height_ft} ft peak height."
        )


# ──────────────────────────────────────────────
# USAGE EXAMPLE
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # --- Instantiate two scoring strategies ---
    thrill = ThrillScoring()
    family = FamilyScoring()
    safety = SafetyScoring()

    # --- Instantiate two coaster types, each injected with a default scorer ---
    cyclone = WoodenCoaster(
        name="The Cyclone",
        height_ft=85,
        speed_mph=60,
        num_inversions=0,
        age_years=30,
        wood_type="laminated",
        scorer=thrill,            # default: score for thrill
    )

    viper = SteelCoaster(
        name="Viper",
        height_ft=140,
        speed_mph=100,
        num_inversions=7,
        age_years=10,
        is_inverted=True,
        scorer=thrill,
    )

    nitro = LaunchCoaster(
        name="Nitro",
        height_ft=120,
        speed_mph=90,
        num_inversions=3,
        age_years=5,
        launch_force_g=1.8,
        scorer=family,
    )

    coasters = [cyclone, viper, nitro]

    # --- Print descriptions ---
    print("=== Coaster Descriptions ===")
    for c in coasters:
        print(c.describe())

    # --- Score with default (injected) strategy ---
    print("\n=== Scores (default strategies) ===")
    for c in coasters:
        print(f"  {c.name:12s} [{c.scorer.__class__.__name__:14s}] → {c.score():.1f}")

    # --- Swap Cyclone's scorer to FamilyScoring at runtime ---
    # No changes to WoodenCoaster class needed — just reassign the field.
    print("\n=== Cyclone re-scored under all three strategies ===")
    for strat in [thrill, family, safety]:
        cyclone.scorer = strat
        print(f"  {strat.__class__.__name__:14s} → {cyclone.score():.1f}")

    # --- Swap Viper to SafetyScoring to show penalty for age+inversions ---
    viper.scorer = safety
    print(f"\n  Viper under SafetyScoring → {viper.score():.1f}  "
          f"(penalised: {viper.age_years} yrs × 1.5 + {viper.num_inversions} inv × 5)")
