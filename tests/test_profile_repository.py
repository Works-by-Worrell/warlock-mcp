
# We expect these imports to fail initially (Red TDD phase)
from worksbyworrell.warlock.repository.profile import (
    LocalUserProfileRepository,
    _merge,
)

# ============================================================================
# 1. MERGE LOGIC TESTS
# ============================================================================

def test_profile_merge_preserves_both_prompts():
    """
    Verify profile merge retains both public and private prompt contents
    rather than letting the private system_prompt overwrite the public one.
    """
    public = {"role": "Senior Engineer", "system_prompt": "Public Lore & Profile"}
    private = {"alias": "Warlock", "system_prompt": "Private Alignment Constraints"}
    
    merged = _merge("raworre", public, private)
    
    assert merged["username"] == "raworre"
    assert merged["role"] == "Senior Engineer"
    assert merged["alias"] == "Warlock"
    assert merged["public_prompt"] == "Public Lore & Profile"
    assert merged["private_prompt"] == "Private Alignment Constraints"


# ============================================================================
# 2. LOCAL USER PROFILE REPOSITORY TESTS
# ============================================================================

def test_local_profile_repository_reads_and_merges_symmetrically(tmp_path):
    """
    Verify LocalUserProfileRepository parses public/private directories
    symmetrically and compiles metadata and prompts.
    """
    # Arrange folders
    public_dir = tmp_path / "public"
    private_dir = tmp_path / "private"
    public_dir.mkdir()
    private_dir.mkdir()
    
    # Write public profile file
    public_file = public_dir / "raworre.md"
    public_file.write_text(
        "---\n"
        "name: Roger\n"
        "---\n"
        "Public profile content."
    )
    
    # Write private override file (symmetrically named)
    private_file = private_dir / "raworre.md"
    private_file.write_text(
        "---\n"
        "alignment: strict-sse\n"
        "---\n"
        "Private profile constraints."
    )
    
    # Act
    repo = LocalUserProfileRepository(public_dir=str(public_dir), private_dir=str(private_dir))
    data = repo.get_profile("raworre")
    
    # Assert
    assert data["username"] == "raworre"
    assert data["name"] == "Roger"
    assert data["alignment"] == "alignment" or data.get("alignment") == "strict-sse"
    assert data["public_prompt"] == "Public profile content."
    assert data["private_prompt"] == "Private profile constraints."


def test_local_profile_repository_missing_files_fallback(tmp_path):
    """Verify local profile repo falls back to empty strings when files do not exist."""
    public_dir = tmp_path / "public"
    private_dir = tmp_path / "private"
    public_dir.mkdir()
    private_dir.mkdir()
    
    repo = LocalUserProfileRepository(public_dir=str(public_dir), private_dir=str(private_dir))
    data = repo.get_profile("unknown-user")
    
    assert data["username"] == "unknown-user"
    assert data["public_prompt"] == ""
    assert data["private_prompt"] == ""


# ============================================================================
# 3. FIRESTORE USER PROFILE REPOSITORY TESTS
# ============================================================================


