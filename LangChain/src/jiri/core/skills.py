"""Skill registry for loading and managing agent skills."""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class Skill:
    """Represents a loaded skill."""

    def __init__(self, name: str, description: str, content: str, path: Path):
        self.name = name
        self.description = description
        self.content = content
        self.path = path


class SkillRegistry:
    """Registry for discovering and loading skills."""

    def __init__(self, agent_dir: Path):
        self.agent_dir = agent_dir
        self.skills: Dict[str, Skill] = {}

    def load_skills(self):
        """Load all skills from the .agent/skills directory."""
        skills_dir = self.agent_dir / "skills"
        if not skills_dir.exists():
            print(f"Warning: Skills directory not found at {skills_dir}")
            return

        # Walk through directories in skills_dir
        for item in skills_dir.iterdir():
            if item.is_dir():
                skill_file = item / "SKILL.md"
                if skill_file.exists():
                    self._load_skill_from_file(skill_file)

        print(f"✓ Loaded {len(self.skills)} skills from {skills_dir}")

    def _load_skill_from_file(self, file_path: Path):
        """Parse a SKILL.md file and register the skill."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for YAML frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter_raw = parts[1]
                    body = parts[2].strip()

                    try:
                        metadata = yaml.safe_load(frontmatter_raw)
                        name = metadata.get("name", file_path.parent.name)
                        description = metadata.get("description", "")

                        self.skills[name] = Skill(
                            name=name, description=description, content=body, path=file_path
                        )
                    except yaml.YAMLError:
                        print(f"  - Error parsing frontmatter for {file_path.name}")

        except Exception as e:
            print(f"  - Error loading skill {file_path}: {e}")

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a specific skill by name."""
        return self.skills.get(name)

    def get_all_skills(self) -> List[Skill]:
        """Get all loaded skills."""
        return list(self.skills.values())

    def get_skills_index(self) -> str:
        """Get a formatted index of available skills for the system prompt."""
        if not self.skills:
            return "No local skills available."

        lines = ["Available Reasoning Skills:"]
        for name, skill in self.skills.items():
            lines.append(f"- {name}: {skill.description}")
        return "\n".join(lines)


# Global instance
def get_registry() -> SkillRegistry:
    """Get or create the global skill registry."""
    root_dir = Path(os.getcwd())
    agent_dir = root_dir / ".agent"
    registry = SkillRegistry(agent_dir)
    registry.load_skills()
    return registry
