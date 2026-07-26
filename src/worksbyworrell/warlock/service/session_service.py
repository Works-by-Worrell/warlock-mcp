from worksbyworrell.warlock.repository.base import (
    AgentRepository,
    SkillMetadataRepository,
    UserProfileRepository,
)

DIVIDER = "========================================="
PROMPT_START = "You are booting into a specialized agent session.\n\n"
AGENT_TITLE = "1. YOUR PERSONA (IDENTITY & STYLE)"
USER_TITLE = "2. USER PROFILE & CONSTRAINTS"
SKILLS_TITLE = "3. ACTIVE SKILLS (ABILITIES)"
NO_SKILLS_MESSAGE = "No specialized skills loaded."
INIT_TITLE = "SESSION INITIALIZATION INSTRUCTIONS"
INIT_MESSAGE = "Initialize your system state using the guidelines above. \
                Adhere strictly to user profile constraints."


def _generate_header(title: str) -> str:
    return f"{DIVIDER}\n{title}\n{DIVIDER}"


def _generate_block(title: str, content: str) -> str:
    return f"{_generate_header(title)}\n{content}\n"


class AgentSessionService:
    def __init__(
        self,
        agent_repo: AgentRepository,
        profile_repo: UserProfileRepository,
        skill_repo: SkillMetadataRepository,
    ):
        self.agent_repo = agent_repo
        self.profile_repo = profile_repo
        self.skill_repo = skill_repo

    def _extract_agent_prompt(self, agent_name: str) -> str:
        agent_data = self.agent_repo.get_agent(agent_name)
        return agent_data.get("system_prompt") or ""

    def _extract_user_prompt(self, username: str) -> str:
        user_data = self.profile_repo.get_profile(username)
        private_prompt = user_data.get("private_prompt") or ""
        public_prompt = user_data.get("public_prompt") or ""
        return f"--- PUBLIC PROFILE ---\n{public_prompt}\n \
                 \n--- PRIVATE PROFILE ---\n{private_prompt}\n"

    def _extract_skill_prompt(self, skills: str) -> str:
        if not skills or not skills.strip():
            return NO_SKILLS_MESSAGE

        skill_ids = [s.strip() for s in skills.split(",") if s.strip()]
        skill_list = []

        for skill in skill_ids:
            skill_data = self.skill_repo.get_skill(skill)
            if skill_data:
                skill_id = skill_data.get("skill_id") or ""
                skill_prompt = skill_data.get("system_prompt") or ""
                skill_list.append(f"### Skill: {skill_id}\n{skill_prompt}")

        return "\n".join(skill_list)

    def build_session_prompt(self, agent_name: str, username: str, skills: str = "") -> str:
        agent_prompt = _generate_block(AGENT_TITLE, self._extract_agent_prompt(agent_name))
        user_prompt = _generate_block(USER_TITLE, self._extract_user_prompt(username))
        skill_prompt = _generate_block(SKILLS_TITLE, self._extract_skill_prompt(skills))
        init_prompt = _generate_block(INIT_TITLE, INIT_MESSAGE)

        return "\n".join([PROMPT_START, agent_prompt, user_prompt, skill_prompt, init_prompt])
