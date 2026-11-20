from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import datetime,json,os,subprocess,sys,time
root=Path.cwd()
base=root/'results/fyp_ideal_20261120'
ops=base/'operational'
freeze='d217ab54fc41a3a84d6a500f3ab0f3aa433059dd'
plan=json.loads((root/'results/fyp_ideal_preflight_20261120/execution_plan.json').read_text())['matrix']['include']
start=time.perf_counter()
common=[sys.executable,'-m','experiments.fyp_ideal_campaign','--freeze','docs/FYP_IDEAL_FREEZE_20261120.json','--freeze-commit',freeze]
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')

def run(item):
    if item['kind']=='generated':
        name=f"generated-{item['family']}-{item['start']:03d}-{item['stop_exclusive']-1:03d}"
        command=common+['--family',str(item['family']),'--start',str(item['start']),'--stop',str(item['stop_exclusive'])]
    else:
        name=f"anchor-{item['anchor_index']}"
        command=common+['--anchor-index',str(item['anchor_index'])]
    t=time.perf_counter()
    with (ops/(name+'.log')).open('x') as log:
        result=subprocess.run(command,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
    record={'shard':name,'returncode':result.returncode,'seconds':time.perf_counter()-t}
    (ops/(name+'.json')).write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
    print(json.dumps(record,sort_keys=True),flush=True)
    if result.returncode: raise RuntimeError('STOP: failed shard '+name)
    return record

print('Starting fixed 18-shard matrix with six workers; no quality analysis until all shards verify.',flush=True)
with ThreadPoolExecutor(max_workers=6) as executor:
    futures=[executor.submit(run,item) for item in plan]
    records=[future.result() for future in as_completed(futures)]
summary={'status':'COMPLETE_PENDING_GLOBAL_VERIFICATION','freeze_commit':freeze,'shards':len(records),'workers':6,'wall_seconds':time.perf_counter()-start,'finished_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'shard_results':sorted(records,key=lambda r:r['shard'])}
(ops/'execution.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='shard_results'},sort_keys=True),flush=True)
