"""Alembic Migration DAG & Continuity Tests.

Verifies using Alembic's ScriptDirectory that:
1. Exactly one head exists and it is '0012'.
2. No branching exists in the migration history.
3. Continuity from '0012' down to '0001' is complete and unbroken.
4. Every revision is resolvable and has consistent down_revision pointers.
"""

import os
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory


@pytest.fixture(scope="module")
def alembic_script_directory() -> ScriptDirectory:
    """Provides the Alembic ScriptDirectory parsed from alembic.ini."""
    # Find alembic.ini relative to this test file or /app in container
    possible_ini_paths = [
        os.path.join(os.path.dirname(__file__), "..", "alembic.ini"),
        "/app/alembic.ini",
    ]
    ini_path = next((p for p in possible_ini_paths if os.path.exists(p)), None)
    assert ini_path is not None, "alembic.ini not found"
    cfg = Config(ini_path)
    return ScriptDirectory.from_config(cfg)


def test_migration_dag_single_head(alembic_script_directory: ScriptDirectory):
    """Verifies that there is exactly one head in the migration graph, and it is 0012."""
    heads = alembic_script_directory.get_heads()
    assert len(heads) == 1, f"Expected exactly 1 migration head, found {len(heads)}: {heads}"
    assert heads[0] == "0012", f"Expected migration head to be '0012', got '{heads[0]}'"


def test_migration_dag_single_base(alembic_script_directory: ScriptDirectory):
    """Verifies that there is exactly one base migration in the graph ('0001')."""
    bases = alembic_script_directory.get_bases()
    assert len(bases) == 1, f"Expected exactly 1 migration base, found {len(bases)}: {bases}"
    assert bases[0] == "0001", f"Expected migration base to be '0001', got '{bases[0]}'"


def test_migration_dag_unbroken_continuity(alembic_script_directory: ScriptDirectory):
    """Verifies complete, linear continuity from head ('0012') to base ('0001')."""
    revisions = list(alembic_script_directory.walk_revisions(base="base", head="0012"))
    rev_ids = [r.revision for r in revisions]

    expected_revisions = [
        "0012",
        "0011",
        "0010",
        "0009",
        "0008",
        "0007",
        "0006",
        "0005",
        "0004",
        "0003",
        "0002_add_email_verification",
        "0001",
    ]
    assert rev_ids == expected_revisions, f"Migration chain mismatch:\nGot: {rev_ids}\nExpected: {expected_revisions}"

    # Verify each revision's down_revision matches the next element in the chain
    for i, rev in enumerate(revisions):
        if i < len(revisions) - 1:
            expected_down = revisions[i + 1].revision
            assert rev.down_revision == expected_down, (
                f"Revision '{rev.revision}' expected down_revision '{expected_down}', "
                f"got '{rev.down_revision}'"
            )
        else:
            assert rev.down_revision is None, (
                f"Base revision '{rev.revision}' must have down_revision=None, got '{rev.down_revision}'"
            )


def test_migration_dag_no_branches_or_merge_points(alembic_script_directory: ScriptDirectory):
    """Verifies that no revision defines branch labels or depends_on merges."""
    for rev in alembic_script_directory.walk_revisions():
        assert not rev.branch_labels, f"Revision '{rev.revision}' has unexpected branch labels: {rev.branch_labels}"
        assert not rev.dependencies, f"Revision '{rev.revision}' has unexpected multi-dependency: {rev.dependencies}"


