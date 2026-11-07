"""Plot verified exhibit summaries without changing the frozen analysis."""
import argparse
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/seventh-seat-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--exhibit',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--scripted-fixture',action='store_true');a=p.parse_args()
receipt=json.loads((a.exhibit/'EXHIBIT.json').read_text());blob=(a.exhibit/'summary.json').read_bytes()
if hashlib.sha256(blob).hexdigest()!=receipt['files']['summary.json']['sha256']:raise ValueError('summary receipt mismatch')
d=json.loads(blob);expected='scripted-fixture' if a.scripted_fixture else 'experimental'
if d['data_status']!=expected or receipt['data_status']!=expected:raise ValueError('data status mismatch')
if any(a.output.with_suffix(ext).exists() for ext in ('.png','.svg','.pdf','.json')):raise ValueError('new figure output required')
a.output.parent.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#6d7276','axes.labelcolor':'#25292c','text.color':'#25292c','xtick.color':'#424b52','ytick.color':'#25292c','pdf.fonttype':42})
fig,axes=plt.subplots(1,2,figsize=(10,4.9));fig.subplots_adjust(left=.14,right=.98,bottom=.31,top=.76,wspace=.65)
color='#26798a'
def draw(ax,entries,labels,title,nonnegative=False):
    values=[]
    for i,e in enumerate(entries):
        y=len(entries)-1-i
        if e['estimate'] is None:
            ax.text(.03,y,'Unavailable',transform=ax.get_yaxis_transform(),color='#6d7276');continue
        lo,hi=e['ci95'];v=e['estimate'];values.extend([lo,hi,v])
        ax.hlines(y,lo,hi,color=color,linewidth=2)
        ax.vlines([lo,hi],y-.08,y+.08,color=color,linewidth=1.3)
        ax.scatter([v],[y],s=42,color=color,zorder=3)
    low=min([0,*values]);high=max([0,*values]);span=max(high-low,1);pad=.13*span
    ax.set_xlim(0 if nonnegative else low-pad,high+pad)
    ax.set_ylim(-.6,len(entries)-.4);ax.set_yticks(list(range(len(entries)-1,-1,-1)),labels)
    ax.tick_params(axis='y',length=0,pad=8);ax.set_title(title,loc='left',fontsize=13,pad=16)
    ax.set_xlabel('Downstream shortfall (water units)',labelpad=10);ax.grid(axis='x',alpha=.2,zorder=0)
    if not nonnegative:ax.axvline(0,color='#7d8386',linewidth=1,linestyle='--',zorder=0)
means=d['mean_shortfall_intervals_descriptive'];cells=['E0S0','E0S1','E1S0','E1S1']
draw(axes[0],[{'estimate':means[c]['mean'],'ci95':means[c]['ci95']} for c in cells],[f"{c}  (N={means[c]['n']})" for c in cells],'A  Descriptive cell means',True)
effects=d['contrasts']['shortfall'];keys=['E','S','ExS']
draw(axes[1],[effects[k] for k in keys],['Evidence E','Reporting route S','E × S (exploratory)'],f"B  Regime contrasts (N={d['complete_scenarios']})")
fig.suptitle('The Seventh Seat  |  Downstream shortfall',x=.14,y=.97,ha='left',fontsize=17,fontweight='semibold')
status='SCRIPTED FIXTURE — NOT RESEARCH FINDINGS' if a.scripted_fixture else f"{d['evaluable_episodes']} evaluable episodes · {d['complete_scenarios']} complete scenarios · {len(d['missing_episodes'])} missing episodes"
fig.text(.14,.875,status,fontsize=10,color='#8a4529' if a.scripted_fixture else '#424b52')
caption=('Points show estimates; bars show 95% scenario-bootstrap intervals. N counts complete scenarios, not agent turns.\n'
         'Cell means are descriptive. E and S are the preregistered regime contrasts; E × S is exploratory.\n'
         'Negative contrasts indicate less shortfall. No multiplicity correction. Intervals do not establish deployed safety.')
fig.text(.14,.15,caption,fontsize=9,linespacing=1.6,va='top')
fig.text(.14,.025,'Source: verified exhibit summary · protocol '+d['protocol_commit'][:12],fontsize=8,color='#626b71')
for ext in ('.png','.svg','.pdf'):fig.savefig(a.output.with_suffix(ext),dpi=200,facecolor='white')
plt.close(fig)
meta={'data_status':expected,'summary_sha256':hashlib.sha256(blob).hexdigest(),'exhibit_manifest_sha256':d['manifest_sha256'],'matplotlib':matplotlib.__version__,'panels':{'means':means,'contrasts':effects},'files':{a.output.with_suffix(ext).name:hashlib.sha256(a.output.with_suffix(ext).read_bytes()).hexdigest() for ext in ('.png','.svg','.pdf')}}
a.output.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps({'data_status':expected,'output_stem':str(a.output),'matplotlib':matplotlib.__version__}))
