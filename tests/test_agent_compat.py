"""Checks discovery and tools, not authenticated model runs."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from agent_compat import check_agent, frontmatter_ok

class AgentCompatibilityTests(unittest.TestCase):
    def test_frontmatter(self):
        self.assertTrue(frontmatter_ok(ROOT/'SKILL.md'))
    def test_all_agent_skill_installs(self):
        for agent in ('codex','claude','cursor'):
            with self.subTest(agent=agent):
                result = check_agent(agent)
                self.assertEqual(result['status'],'compatible_not_executed')
                self.assertFalse(result['runtime_executed'])
                self.assertEqual(len(result['checks']),2)
                self.assertTrue(all(item['passed'] for item in result['checks']))
                roots=[r['expected_discovery_path'] for r in result['checks']]
                self.assertEqual(roots,{
                    'codex':['.agents/skills/anti-ai-slop','.agents/skills/anti-ai-slop'],
                    'claude':['.claude/skills/anti-ai-slop','.claude/skills/anti-ai-slop'],
                    'cursor':['.cursor/skills/anti-ai-slop','.cursor/skills/anti-ai-slop'],
                }[agent])
    def test_compatibility_not_runtime_proof(self):
        result=check_agent('codex')
        self.assertNotEqual(result['status'],'runtime_verified')
        self.assertIn('real agent',result['limitation'])

if __name__=='__main__':unittest.main()
