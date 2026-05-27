import sys, json, os
os.chdir('/home/openclaw/.openclaw/workspace')
sys.path.insert(0, 'bin/quality-gates')
from blog import QualityGate
path = sys.argv[1]
gate = QualityGate(path, 'health.gheware.com')
result = gate.run()
print(json.dumps(result, indent=2))
