import os, sys, json, time, glob, math, random, subprocess
from dataclasses import dataclass
from typing import List, Tuple, Optional
os.makedirs("./checkpoints", exist_ok=True)
os.makedirs("./samples", exist_ok=True)
os.makedirs("./logs", exist_ok=True)
_HAS_LPIPS=False
import lpips

import torch, torch.nn as nn, torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from torchvision.utils import save_image, make_grid
from PIL import Image
from tqdm.auto import tqdm

torch.backends.cudnn.benchmark = True
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"GPU: {device}")

@dataclass
class Config:
    data_root: str="./images"
    image_size: int=128
    epochs: int=100
    batch_size: int=192
    num_workers: int=0
    pin_memory: bool=True

    lr: float=2e-4
    betas: Tuple[float,float]=(0.9,0.99)
    weight_decay: float=1e-4
    amp: bool=True
    z_dim: int=512
    hidden: int=512
    init_experts_desired: int=256
    max_experts: int=512
    top_k: int=4
    epsilon_start: float=0.20
    epsilon_end: float=0.10
    tau_high: float=1.8
    tau_low: float=0.7
    capacity_alpha: float=1.2  # C = ceil(alpha * B * k / E) (min 1)
    gate_entropy_lambda_warm: float=0.05
    gate_entropy_lambda_cool: float=0.01
    repulsion_lambda: float=1e-3
    repulsion_subset: int=256
    repulsion_sigma: float=0.15
    prune_patience_epochs: int=8
    prune_share_thresh: float=0.005
    prune_contrib_thresh: float=1e-5
    spin_share_thresh: float=0.25
    spin_hhi_thresh: float=0.08
    spin_interval_epochs: int=2
    spin_noise_std: float=0.02
    stability_warm_epochs: int=5
    lora_rank: int=4
    adapters_per_expert: int=64
    growth_interval_epochs: int=3
    growth_share_thresh: float=0.06
    growth_max_children_per_round: int=4
    growth_mix_alpha: float=0.75
    growth_noise_std: float=0.02
    newbie_bias_init: float=0.5
    newbie_bias_decay: float=0.5
    evict_interval_epochs: int=2
    evict_adapter_share_thresh: float=0.02
    evict_adapter_patience: int=3
    evict_max_per_epoch: int=4096
    evict_reinit_scale: float=1e-3
    pool_spawn_min: int=64
    out_ckpt_dir: str="./checkpoints"
    out_samples_dir: str="./samples"
    out_log_dir: str="./logs"
    sample_rows: int=4
    seed: int=42

cfg = Config()
random.seed(cfg.seed); torch.manual_seed(cfg.seed)

IMG_EXTS=(".png",".jpg",".jpeg",".bmp",".webp")

class PlainImageDataset(Dataset):
    def __init__(self, root, size=128, train=True):
        self.paths=[p for p in glob.glob(os.path.join(root,"**","*"), recursive=True)
                    if os.path.splitext(p)[1].lower() in IMG_EXTS]
        if not self.paths:
            raise RuntimeError(f"No images found under {root}.")
        aug=[transforms.Resize(size), transforms.CenterCrop(size)]
        if train:
            aug.insert(1, transforms.RandomHorizontalFlip(0.5))
            aug.insert(2, transforms.ColorJitter(0.1,0.1,0.05,0.02))
        self.tf=transforms.Compose(aug+[
            transforms.ToTensor(),
            transforms.Normalize([0.5]*3,[0.5]*3)
        ])
    def __len__(self): return len(self.paths)
    def __getitem__(self, i):
        return self.tf(Image.open(self.paths[i]).convert("RGB"))

full_ds=PlainImageDataset(cfg.data_root, size=cfg.image_size, train=True)
val_ratio=0.02 if len(full_ds)>2000 else 0.1
val_len=max(16, int(len(full_ds)*val_ratio))
train_len=len(full_ds)-val_len
train_ds, val_ds = random_split(full_ds,[train_len,val_len], generator=torch.Generator().manual_seed(cfg.seed))

train_loader=DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True,
                        num_workers=cfg.num_workers, pin_memory=cfg.pin_memory, drop_last=True)
val_loader=DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False,
                      num_workers=cfg.num_workers, pin_memory=cfg.pin_memory, drop_last=False)
print(f"[Data] train={len(train_ds)} val={len(val_ds)} batch={cfg.batch_size}")

def conv_block(in_ch,out_ch,k=3,s=1,p=1):
    return nn.Sequential(nn.Conv2d(in_ch,out_ch,k,s,p), nn.GroupNorm(8,out_ch), nn.SiLU())

class Encoder(nn.Module):
    def __init__(self, z_dim):
        super().__init__()
        ch=64
        self.net=nn.Sequential(
            conv_block(3,ch), conv_block(ch,ch),
            conv_block(ch,ch*2,s=2), conv_block(ch*2,ch*2),
            conv_block(ch*2,ch*4,s=2), conv_block(ch*4,ch*4),
            conv_block(ch*4,ch*8,s=2), conv_block(ch*8,ch*8),
            conv_block(ch*8,ch*8,s=2), conv_block(ch*8,ch*8),
        )
        feat_dim = ch*8*8*8
        self.to_mu     = nn.Linear(feat_dim, z_dim)
        self.to_logvar = nn.Linear(feat_dim, z_dim)
        self.last_mu: torch.Tensor = None
        self.last_logvar: torch.Tensor = None
    def forward(self,x):
        h=self.net(x).view(x.size(0),-1)
        mu=self.to_mu(h)
        logvar=self.to_logvar(h).clamp(min=-30.0, max=20.0)
        if self.training:
            std=torch.exp(0.5*logvar)
            eps=torch.randn_like(std)
            z=mu + std*eps
        else:
            z=mu
        self.last_mu = mu
        self.last_logvar = logvar
        return z

class Decoder(nn.Module):
    def __init__(self,z_dim):
        super().__init__()
        ch=64
        self.fc=nn.Linear(z_dim, ch*8*8*8)
        self.up=nn.Sequential(
            conv_block(ch*8,ch*8),
            nn.Upsample(scale_factor=2,mode='nearest'),
            conv_block(ch*8,ch*8),
            nn.Upsample(scale_factor=2,mode='nearest'),
            conv_block(ch*8,ch*4),
            nn.Upsample(scale_factor=2,mode='nearest'),
            conv_block(ch*4,ch*2),
            nn.Upsample(scale_factor=2,mode='nearest'),
            conv_block(ch*2,ch),
            nn.Conv2d(ch,3,3,1,1), nn.Tanh()
        )
    def forward(self,z):
        h=self.fc(z).view(z.size(0),512,8,8)
        return self.up(h)

class ExpertLoRA(nn.Module):
    def __init__(self, z_dim, hidden, W, rank):
        super().__init__()
        self.z_dim=z_dim; self.hidden=hidden; self.W=W; self.r=rank
        self.a1=nn.Parameter(torch.randn(W, rank, z_dim)*0.02)
        self.b1=nn.Parameter(torch.randn(W, hidden, rank)*0.02)
        self.a2=nn.Parameter(torch.randn(W, rank, hidden)*0.02)
        self.b2=nn.Parameter(torch.randn(W, z_dim, rank)*0.02)
        self.scale=1.0
    def forward_batch(self, z, a_idx, h_pre, out_pre):
        dt = z.dtype
        A1 = self.a1[a_idx].to(dt)
        B1 = self.b1[a_idx].to(dt)
        t1 = torch.einsum('nd,nrd->nr', z, A1)
        d1 = torch.einsum('nr,nhr->nh', t1, B1) * self.scale
        h  = F.silu(h_pre + d1).to(dt)
        A2 = self.a2[a_idx].to(dt)
        B2 = self.b2[a_idx].to(dt)
        t2 = torch.einsum('nh,nrh->nr', h, A2)
        d2 = torch.einsum('nr,ndr->nd', t2, B2) * self.scale
        return (out_pre + d2).to(dt)

class MoELatent(nn.Module):
    def __init__(self, z_dim, hidden, init_experts, adapters_per_expert, rank):
        super().__init__()
        self.fc1=nn.Linear(z_dim, hidden)
        self.fc2=nn.Linear(hidden, z_dim)
        nn.init.kaiming_uniform_(self.fc1.weight, a=math.sqrt(5))
        nn.init.zeros_(self.fc1.bias); nn.init.zeros_(self.fc2.bias)

        self.z_dim=z_dim; self.hidden=hidden; self.W=adapters_per_expert; self.rank=rank
        self.experts=nn.ModuleList([ExpertLoRA(z_dim,hidden,self.W,rank) for _ in range(init_experts)])
        self.prototypes=nn.Parameter(torch.randn(init_experts, z_dim)*0.02)
        self.adapter_keys=nn.Parameter(torch.randn(init_experts, self.W, z_dim)*0.02)
        self.register_buffer("expert_bias", torch.zeros(init_experts, dtype=torch.float32))

    def num_experts(self): return len(self.experts)

    @torch.no_grad()
    def add_expert_transfer(self, src_idx:int, mix_alpha:float, noise_std:float, bias_init:float):
        """Clone src expert with partial weight transfer + noise; add newbie routing bias."""
        src = self.experts[src_idx]
        new = ExpertLoRA(self.z_dim,self.hidden,self.W,self.rank).to(self.prototypes.device)
        for name in ["a1","b1","a2","b2"]:
            src_t = getattr(src, name).data
            noise = torch.randn_like(src_t)*noise_std
            mixed = mix_alpha*src_t + (1.0-mix_alpha)*noise
            getattr(new, name).data.copy_(mixed)
        proto_src = self.prototypes.data[src_idx].clone()
        key_src   = self.adapter_keys.data[src_idx].clone()
        self.experts.append(new)
        self.prototypes = nn.Parameter(torch.cat([self.prototypes.data, proto_src[None,:]], dim=0))
        self.adapter_keys = nn.Parameter(torch.cat([self.adapter_keys.data, key_src[None,:,:]], dim=0))
        self.expert_bias = torch.cat([self.expert_bias, torch.tensor([bias_init], device=self.expert_bias.device)], dim=0)

    @torch.no_grad()
    def add_expert_from_pool(self, pool_items: List[Tuple[int,int]], mix_alpha:float, noise_std:float, bias_init:float):
        """Create a new expert by aggregating adapters from pool [(u,w), ...] length W."""
        assert len(pool_items)>=self.W, "pool too small"
        pick = pool_items[:self.W]
        new = ExpertLoRA(self.z_dim,self.hidden,self.W,self.rank).to(self.prototypes.device)
        src_expert_ids = [u for (u,_) in pick]
        proto = self.prototypes.data[src_expert_ids].mean(dim=0)
        for j,(u,w) in enumerate(pick):
            src = self.experts[u]
            for name in ["a1","b1","a2","b2"]:
                src_t = getattr(src, name).data[w].clone()
                noise = torch.randn_like(src_t)*noise_std
                mixed = mix_alpha*src_t + (1.0-mix_alpha)*noise
                getattr(new, name).data[j].copy_(mixed)
        keys = torch.stack([self.adapter_keys.data[u,w] for (u,w) in pick], dim=0)
        self.experts.append(new)
        self.prototypes = nn.Parameter(torch.cat([self.prototypes.data, proto[None,:]], dim=0))
        self.adapter_keys = nn.Parameter(torch.cat([self.adapter_keys.data, keys[None,:,:]], dim=0))
        self.expert_bias = torch.cat([self.expert_bias, torch.tensor([bias_init], device=self.expert_bias.device)], dim=0)

    @torch.no_grad()
    def remove_experts(self, indices: List[int]):
        if not indices: return
        keep=[i for i in range(self.num_experts()) if i not in set(indices)]
        self.experts=nn.ModuleList([self.experts[i] for i in keep])
        self.prototypes=nn.Parameter(self.prototypes.data[keep])
        self.adapter_keys=nn.Parameter(self.adapter_keys.data[keep])
        self.expert_bias=self.expert_bias[keep]

    def capacity_route(self, probs, top_k, capacity):
        B,E=probs.shape
        k=min(top_k, E)
        cand_k=min(E, max(k*4, k))
        vals, idxs=torch.topk(probs, k=cand_k, dim=-1)
        assigned_idx=torch.full((B,k), -1, dtype=torch.long, device=probs.device)
        assigned_w=torch.zeros(B,k, device=probs.device, dtype=probs.dtype)
        cap=torch.zeros(E, dtype=torch.int32, device=probs.device)
        cap_limit=torch.full((E,), max(1,capacity), dtype=torch.int32, device=probs.device)
        cap_hit=0; total_slots=B*k
        for b in range(B):
            slot=0
            for j in range(cand_k):
                if slot>=k: break
                e=int(idxs[b,j].item())
                if cap[e] < cap_limit[e]:
                    assigned_idx[b,slot]=e
                    assigned_w[b,slot]=vals[b,j]
                    cap[e]+=1
                    if j>0: cap_hit+=1
                    slot+=1
        cap_hit_rate = cap_hit/max(1,total_slots)
        return assigned_idx, assigned_w, cap_hit_rate

    def pick_adapters(self, z, expert_ids):
        N=z.size(0); dt=z.dtype
        a_idx=torch.zeros(N, dtype=torch.long, device=z.device)
        for u in expert_ids.unique():
            u=int(u.item())
            sel=(expert_ids==u)
            logits = z[sel] @ self.adapter_keys[u].to(dt).t()
            a_idx[sel]=torch.argmax(logits, dim=-1)
        return a_idx

    def forward(self, z, top_k, tau, epsilon, capacity, ban_expert: Optional[int]=None):
        h_pre = F.silu(self.fc1(z))
        out_pre = self.fc2(h_pre)

        logits=F.linear(z, self.prototypes) / max(tau,1e-6)
        logits = logits + self.expert_bias.to(logits.dtype)
        if ban_expert is not None and 0<=ban_expert<self.num_experts():
            logits[:, ban_expert] = -1e9
        probs=F.softmax(logits, dim=-1)
        if epsilon>0:
            probs=(1-epsilon)*probs + epsilon*(torch.ones_like(probs)/probs.size(1))

        assigned_idx, assigned_w, cap_hit_rate = self.capacity_route(probs, top_k, capacity)

        B,E=probs.shape; k=assigned_idx.size(1)
        z_out=torch.zeros_like(z)
        used_mask=torch.zeros(B,E, dtype=torch.bool, device=z.device)

        ev_e_list=[]; ev_a_list=[]

        for j in range(k):
            idx_j=assigned_idx[:,j]
            w_j  =assigned_w[:,j].unsqueeze(1).to(z.dtype)
            sel=(idx_j>=0)
            if not sel.any(): continue

            idx_j_sel=idx_j[sel]; z_sel=z[sel]
            h_sel=h_pre[sel]; out_sel=out_pre[sel]
            for u in idx_j_sel.unique():
                u=int(u.item())
                sub=(idx_j_sel==u)
                z_sub=z_sel[sub]; h_sub=h_sel[sub]; out_sub=out_sel[sub]
                a_sub=self.pick_adapters(z_sub, torch.full((z_sub.size(0),), u, dtype=torch.long, device=z.device))
                y=self.experts[u].forward_batch(z_sub, a_sub, h_sub, out_sub).to(z.dtype)
                b_idx=torch.nonzero(sel, as_tuple=False).squeeze(1)[sub]
                z_out[b_idx] = z_out[b_idx] + w_j[sel][sub] * y
                used_mask[b_idx, u]=True
                ev_e_list.append(torch.full((a_sub.numel(),), u, dtype=torch.long, device=z.device))
                ev_a_list.append(a_sub)

        ev_e = torch.cat(ev_e_list) if ev_e_list else torch.empty(0,dtype=torch.long,device=z.device)
        ev_a = torch.cat(ev_a_list) if ev_a_list else torch.empty(0,dtype=torch.long,device=z.device)

        return z + z_out, probs, used_mask, assigned_idx, assigned_w, cap_hit_rate, ev_e.detach(), ev_a.detach()

class AutoEncoderMoE(nn.Module):
    def __init__(self, init_E: int):
        super().__init__()
        self.enc=Encoder(cfg.z_dim)
        self.moe=MoELatent(cfg.z_dim, cfg.hidden, init_E, cfg.adapters_per_expert, cfg.lora_rank)
        self.dec=Decoder(cfg.z_dim)
    def forward(self, x, top_k, tau, epsilon, capacity, ban_expert: Optional[int]=None):
        z=self.enc(x)
        z_moe, probs, used_mask, aidx, aw, cap_hit, ev_e, ev_a = self.moe(z, top_k, tau, epsilon, capacity, ban_expert=ban_expert)
        x_rec=self.dec(z_moe)
        return x_rec, z, z_moe, probs, used_mask, aidx, aw, cap_hit, ev_e, ev_a

def denorm(x): return (x.clamp(-1,1)+1)*0.5

def gate_entropy(probs):
    p=probs.clamp_min(1e-8)
    return (-p * p.log()).sum(dim=-1).mean()

def repulsion_loss(protos, m=256, sigma=0.15):
    E=protos.size(0)
    if E<=1: return protos.sum()*0
    idx=torch.randperm(E, device=protos.device)[:min(m,E)]
    P=F.normalize(protos[idx], dim=-1)
    S=P @ P.t()
    mask=~torch.eye(P.size(0), device=P.device, dtype=torch.bool)
    s=S[mask]
    return torch.exp(s/sigma).mean()

def kld_gaussian_standard(mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
    return -0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).sum(dim=1).mean()

class ExpertStats:
    def __init__(self, E:int, W:int):
        self.reset(E,W)
    def reset(self,E,W):
        dev=device
        self.E=E; self.W=W
        self.usage_epoch=torch.zeros(E, dtype=torch.float32, device=dev)
        self.usage_ema  =torch.zeros(E, dtype=torch.float32, device=dev)
        self.contrib_ema=torch.zeros(E, dtype=torch.float32, device=dev)
        self.fail_epochs=torch.zeros(E, dtype=torch.int32 , device=dev)
        self.ever_used  =torch.zeros(E, dtype=torch.bool  , device=dev)
        self.adapt_usage_epoch=torch.zeros(E,W, dtype=torch.float32, device=dev)
        self.adapt_usage_ema  =torch.zeros(E,W, dtype=torch.float32, device=dev)
        self.adapt_fail_epochs=torch.zeros(E,W, dtype=torch.int32 , device=dev)
        self.evicted_total:int=0
    def on_structure_change(self, keep_idx: List[int], new_added:int=0):
        ou, oc, of, oe = [x.detach().clone().cpu().tolist() for x in [self.usage_ema, self.contrib_ema, self.fail_epochs, self.ever_used]]
        au = self.adapt_usage_ema.detach().clone().cpu()
        af = self.adapt_fail_epochs.detach().clone().cpu()
        E=len(keep_idx)+new_added; W=self.W; dev=device
        new_uema=torch.zeros(E, dtype=torch.float32, device=dev)
        new_cema=torch.zeros(E, dtype=torch.float32, device=dev)
        new_f   =torch.zeros(E, dtype=torch.int32 , device=dev)
        new_eu  =torch.zeros(E, dtype=torch.bool  , device=dev)
        new_au  =torch.zeros(E,W, dtype=torch.float32, device=dev)
        new_af  =torch.zeros(E,W, dtype=torch.int32 , device=dev)
        for new_i, old_i in enumerate(keep_idx):
            new_uema[new_i]=torch.tensor(ou[old_i], device=dev)
            new_cema[new_i]=torch.tensor(oc[old_i], device=dev)
            new_f[new_i]   =torch.tensor(of[old_i], device=dev)
            new_eu[new_i]  =torch.tensor(oe[old_i], device=dev, dtype=torch.bool)
            new_au[new_i]=torch.tensor(au[old_i].numpy(), device=dev)
            new_af[new_i]=torch.tensor(af[old_i].numpy(), device=dev, dtype=torch.int32)
        self.E=E
        self.usage_ema=new_uema; self.contrib_ema=new_cema; self.fail_epochs=new_f; self.ever_used=new_eu
        self.usage_epoch=torch.zeros(E, dtype=torch.float32, device=dev)
        self.adapt_usage_ema=new_au; self.adapt_fail_epochs=new_af
        self.adapt_usage_epoch=torch.zeros(E,W, dtype=torch.float32, device=dev)
    def epoch_decay(self, decay):
        self.usage_ema = decay*self.usage_ema + (1-decay)*self.usage_epoch
        self.adapt_usage_ema = decay*self.adapt_usage_ema + (1-decay)*self.adapt_usage_epoch
        self.usage_epoch.zero_()
        self.adapt_usage_epoch.zero_()

eviction_pool: List[Tuple[int,int]] = []
def compute_capacity(B, E, k):
    cap = int(math.ceil(cfg.capacity_alpha * B * k / max(1,E)))
    return max(1, cap)

@torch.no_grad()
def save_samples(epoch, model):
    model.eval()
    imgs=next(iter(val_loader))[:cfg.sample_rows*cfg.sample_rows].to(device)
    capacity=compute_capacity(imgs.size(0), model.moe.num_experts(), cfg.top_k)
    rec, *_ = model(imgs, top_k=cfg.top_k, tau=1.0, epsilon=0.0, capacity=capacity)
    grid=make_grid(torch.cat([denorm(imgs), denorm(rec)], dim=0), nrow=cfg.sample_rows)
    save_image(grid, os.path.join(cfg.out_samples_dir, f"epoch_{epoch:03d}.png"))
    model.train()

def share_hhi_from_usage(usage):
    tot=usage.sum().item()+1e-6
    s=usage/tot
    hhi=float((s*s).sum().item())
    return s, hhi

def summarize_epoch(epoch, model, stats, train_loss, val_loss, share, hhi, entropy_mean, cap_hit_rate, active_experts_epoch):
    E=model.moe.num_experts(); W=model.moe.W
    total_virtual_neurons = E*W
    total_hidden_neuron_scale = E*cfg.hidden
    usage=stats.usage_ema.detach().cpu()
    contrib=stats.contrib_ema.detach().cpu()
    k=min(5,E)
    if usage.sum()>0 and k>0:
        share_vec=(usage/usage.sum())
        s_vals, s_idx=torch.topk(share_vec, k=k)
        top5_share=[(int(s_idx[j]), float(s_vals[j])) for j in range(k)]
    else:
        top5_share=[]
    if E>0:
        best_id=int(torch.argmax(stats.contrib_ema).item())
        best_contrib=float(stats.contrib_ema[best_id].item())
    else:
        best_id=-1; best_contrib=0.0
    never_used=int((~stats.ever_used).sum().item())

    print(f"\n[Epoch {epoch}] Experts={E} | VirtualNeurons(E*W)={total_virtual_neurons} | HiddenScale(E*H)={total_hidden_neuron_scale}")
    print(f"  ActiveExperts@epoch={active_experts_epoch} | NeverUsedExperts={never_used} | EvictedNeurons(total)={stats.evicted_total}")
    print(f"  HHI={hhi:.4f} | Entropy={entropy_mean:.3f} | CapHit={cap_hit_rate:.3f} | TrainLoss={train_loss:.4f} | ValLoss={val_loss:.4f}")
    print("  Top-5 by SHARE (id, share):")
    for eid,s in top5_share: print(f"    - {eid:4d} | {s:.4f}")
    print(f"  Best Performer by CONTRIB: id={best_id} | ΔL_ema={best_contrib:.6f}")

    with open(os.path.join(cfg.out_log_dir, f"epoch_{epoch:03d}_report.json"),"w") as f:
        json.dump({
            "epoch": epoch,
            "experts_total": E,
            "virtual_neurons": total_virtual_neurons,
            "hidden_neuron_scale": total_hidden_neuron_scale,
            "active_experts_this_epoch": int(active_experts_epoch),
            "never_used_experts": int(never_used),
            "evicted_neurons_total": int(stats.evicted_total),
            "hhi": hhi,
            "entropy_mean": entropy_mean,
            "capacity_hit_rate": cap_hit_rate,
            "top5_share":[{"expert_id":eid,"share":s} for eid,s in top5_share],
            "best_expert_by_contrib":{"expert_id":int(best_id),"deltaL_ema":best_contrib},
            "train_loss": float(train_loss),
            "val_loss": float(val_loss),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }, f, indent=2)

@torch.no_grad()
def loo_probe_contrib(model, stats, tau, capacity, percept):
    if len(val_loader)==0: return
    batch=next(iter(val_loader))[:64].to(device)
    model.eval()
    with torch.amp.autocast("cuda", enabled=cfg.amp):
        x_rec, *_ = model(batch, top_k=cfg.top_k, tau=tau, epsilon=0.0, capacity=capacity)
        if _HAS_LPIPS:
            base_loss=0.7*F.mse_loss(x_rec,batch) + 0.3*percept(denorm(x_rec).float(), denorm(batch).float()).mean()
        else:
            base_loss=F.mse_loss(x_rec,batch)
    usage=stats.usage_ema
    k=min(8, model.moe.num_experts())
    if usage.sum()>0 and k>0:
        idx_sorted=torch.argsort(usage)
        picks=torch.unique(torch.cat([idx_sorted[:k//3], idx_sorted[len(idx_sorted)//2:len(idx_sorted)//2+k//3], idx_sorted[-k:]]))[:k]
    else:
        model.train(); return
    for e in picks.tolist():
        with torch.amp.autocast("cuda", enabled=cfg.amp):
            x_loo, *_ = model(batch, top_k=cfg.top_k, tau=tau, epsilon=0.0, capacity=capacity, ban_expert=int(e))
            if _HAS_LPIPS:
                loss_loo=0.7*F.mse_loss(x_loo,batch) + 0.3*percept(denorm(x_loo).float(), denorm(batch).float()).mean()
            else:
                loss_loo=F.mse_loss(x_loo,batch)
        dL=float((loss_loo - base_loss).item())
        stats.contrib_ema[e] = 0.9*stats.contrib_ema[e] + 0.1*torch.tensor(max(0.0, dL), device=device)
    model.train()

# --- Structure controllers ---
def maybe_spin_or_prune(epoch, model, stats, share_vec, hhi):
    E=model.moe.num_experts()
    note=""
    if epoch>cfg.stability_warm_epochs:
        prune_idx=[]
        for i in range(E):
            if share_vec[i].item()<cfg.prune_share_thresh and stats.contrib_ema[i].item()<cfg.prune_contrib_thresh:
                stats.fail_epochs[i]+=1
                if stats.fail_epochs[i]>=cfg.prune_patience_epochs and (E-len(prune_idx)>8):
                    prune_idx.append(i)
            else:
                stats.fail_epochs[i]=0
        if prune_idx:
            keep=[j for j in range(E) if j not in set(prune_idx)]
            model.moe.remove_experts(prune_idx)
            stats.on_structure_change(keep_idx=keep, new_added=0)
            note+=f"PrunedExperts={len(prune_idx)} "
    if epoch % cfg.spin_interval_epochs==0 and E<cfg.max_experts:
        max_share=float(share_vec.max().item())
        if max_share>cfg.spin_share_thresh or hhi>cfg.spin_hhi_thresh:
            src=int(torch.argmax(share_vec).item())
            model.moe.add_expert_transfer(src_idx=src, mix_alpha=cfg.growth_mix_alpha, noise_std=cfg.spin_noise_std, bias_init=cfg.newbie_bias_init)
            stats.on_structure_change(keep_idx=list(range(E)), new_added=1)
            note+=f"| SpinOffFrom={src} -> NewE={model.moe.num_experts()} "
    return note

def maybe_growth(epoch, model, stats, share_vec):
    if epoch % cfg.growth_interval_epochs!=0: return ""
    E=model.moe.num_experts()
    if E>=cfg.max_experts: return ""
    note=""
    cand=(share_vec>cfg.growth_share_thresh).nonzero(as_tuple=False).flatten().tolist()
    if not cand: return ""
    random.shuffle(cand)
    added=0
    for src in cand:
        if model.moe.num_experts()>=cfg.max_experts: break
        model.moe.add_expert_transfer(src_idx=int(src), mix_alpha=cfg.growth_mix_alpha, noise_std=cfg.growth_noise_std, bias_init=cfg.newbie_bias_init)
        stats.on_structure_change(keep_idx=list(range(E+added)), new_added=1)
        added+=1
        if added>=cfg.growth_max_children_per_round: break
    if added>0:
        note=f"Growth: +{added} (transfer α={cfg.growth_mix_alpha})"
    return note

def maybe_eviction(epoch, model, stats):
    global eviction_pool
    E=model.moe.num_experts(); W=model.moe.W
    with torch.no_grad():
        sums=(stats.adapt_usage_ema.sum(dim=1, keepdim=True)+1e-6)
        adapt_share=stats.adapt_usage_ema/sums
        bad_mask = adapt_share < cfg.evict_adapter_share_thresh
        stats.adapt_fail_epochs = torch.where(bad_mask, stats.adapt_fail_epochs+1, torch.zeros_like(stats.adapt_fail_epochs))
        if epoch % cfg.evict_interval_epochs==0:
            ev_u, ev_w = torch.where(stats.adapt_fail_epochs>=cfg.evict_adapter_patience)
            if ev_u.numel()>0:
                take=min(ev_u.numel(), cfg.evict_max_per_epoch)
                ev_u=ev_u[:take]; ev_w=ev_w[:take]
                for i in range(take):
                    u=int(ev_u[i].item()); w=int(ev_w[i].item())
                    eviction_pool.append((u,w))
                    model.moe.adapter_keys.data[u,w].normal_(mean=0.0, std=cfg.evict_reinit_scale)
                    for name in ["a1","b1","a2","b2"]:
                        getattr(model.moe.experts[u], name).data[w].normal_(mean=0.0, std=cfg.evict_reinit_scale)
                stats.evicted_total += take
                stats.adapt_fail_epochs[ev_u, ev_w]=0

            spawned=0
            while len(eviction_pool) >= cfg.pool_spawn_min and model.moe.num_experts()<cfg.max_experts:
                # pool에서 W개 꺼내서 Expert 생성
                pick = eviction_pool[:W]
                try:
                    model.moe.add_expert_from_pool(pick, mix_alpha=cfg.growth_mix_alpha, noise_std=cfg.growth_noise_std, bias_init=cfg.newbie_bias_init)
                except AssertionError:
                    break
                eviction_pool = eviction_pool[W:]
                stats.on_structure_change(keep_idx=list(range(E+spawned)), new_added=1)
                spawned+=1
            if spawned>0:
                return f"Eviction->Spawn: +{spawned} experts (pool_used={spawned*W})"
    return ""

def build_model_oom_aware(desired_E: int):
    E = max(8, desired_E)
    while True:
        try:
            model = AutoEncoderMoE(init_E=E).to(device)
            stats  = ExpertStats(E, cfg.adapters_per_expert)
            print(f"[Model] Built with E={E} experts, W={cfg.adapters_per_expert} adapters/expert")
            return model, stats
        except RuntimeError as e:
            if "out of memory" in str(e).lower() and E>8:
                print(f"[Model] OOM at E={E}. Trying E={E//2} …")
                torch.cuda.empty_cache()
                E = max(8, E//2)
            else:
                raise

model, stats = build_model_oom_aware(cfg.init_experts_desired)
percept = lpips.LPIPS(net='vgg').to(device).eval() if _HAS_LPIPS else None

opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, betas=cfg.betas, weight_decay=cfg.weight_decay)
scaler = torch.amp.GradScaler("cuda", enabled=cfg.amp)
def tau_sched(epoch):
    if epoch<=5: return cfg.tau_high
    t=(epoch-5)/max(1,(cfg.epochs-5))
    return cfg.tau_high + (cfg.tau_low-cfg.tau_high)*t

def eps_sched(epoch):
    t=(epoch-1)/max(1,(cfg.epochs-1))
    return cfg.epsilon_start + (cfg.epsilon_end-cfg.epsilon_start)*t

def ent_lambda_sched(epoch):
    return cfg.gate_entropy_lambda_warm if epoch<=5 else cfg.gate_entropy_lambda_cool

def kl_weight_sched(epoch: int) -> float:
    warmup = max(1, min(15, cfg.epochs // 6))
    return min(1.0, epoch / warmup)

global_step=0
for epoch in range(1, cfg.epochs+1):
    model.train()
    tau=tau_sched(epoch); eps=eps_sched(epoch); ent_l=ent_lambda_sched(epoch)

    running=0.0; cap_hits=0.0; cap_tot=0.0; ent_sum=0.0; ent_cnt=0
    pbar=tqdm(train_loader, desc=f"Epoch {epoch}/{cfg.epochs} (train)")

    for batch in pbar:
        batch=batch.to(device, non_blocking=True)
        B=batch.size(0)
        capacity=compute_capacity(B, model.moe.num_experts(), cfg.top_k)

        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=cfg.amp):
            out = model(batch, top_k=cfg.top_k, tau=tau, epsilon=eps, capacity=capacity)
            x_rec, z0, z_moe, probs, used_mask, aidx, aw, cap_hit, ev_e, ev_a = out
            mse=F.mse_loss(x_rec, batch)
            if _HAS_LPIPS:
                lp = percept(denorm(x_rec).float(), denorm(batch).float()).mean()
                recon = 0.7*mse + 0.3*lp
            else:
                recon = mse
            kl_w = kl_weight_sched(epoch)
            kld  = kld_gaussian_standard(model.enc.last_mu, model.enc.last_logvar)
            loss_main = recon + kl_w * kld
            H=gate_entropy(probs)
            rep=repulsion_loss(model.moe.prototypes, m=cfg.repulsion_subset, sigma=cfg.repulsion_sigma)
            loss = loss_main + ent_l*H + cfg.repulsion_lambda*rep

        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt); scaler.update()

        with torch.no_grad():
            E=model.moe.num_experts()
            stats.usage_epoch[:E]+=used_mask.float().sum(dim=0)
            cap_hits += cap_hit; cap_tot+=1.0
            ent_sum  += float(H.item()); ent_cnt+=1

            if ev_e.numel()>0:
                flat_idx = ev_e*cfg.adapters_per_expert + ev_a
                ones = torch.ones_like(flat_idx, dtype=torch.float32)
                stats.adapt_usage_epoch.view(-1).index_add_(0, flat_idx, ones)

        running+=float(loss_main.item())
        try:
            pbar.set_postfix(loss=f"{loss_main.item():.4f}", mse=f"{mse.item():.4f}", KL=f"{kld.item():.3f}", beta=f"{kl_w:.2f}", H=f"{H.item():.3f}", tau=f"{tau:.2f}", eps=f"{eps:.3f}")
        except Exception:
            pass

    active_experts_epoch=int((stats.usage_epoch>0).float().sum().item())
    stats.ever_used = stats.ever_used | (stats.usage_epoch>0)

    stats.epoch_decay(decay=0.9)
    with torch.no_grad():
        model.moe.expert_bias.mul_(cfg.newbie_bias_decay)

    model.eval(); val_loss=0.0
    with torch.no_grad():
        for batch in tqdm(val_loader, desc=f"Epoch {epoch}/{cfg.epochs} (val)"):
            batch=batch.to(device, non_blocking=True)
            capacity=compute_capacity(batch.size(0), model.moe.num_experts(), cfg.top_k)
            with torch.amp.autocast("cuda", enabled=cfg.amp):
                x_rec, *_ = model(batch, top_k=cfg.top_k, tau=tau, epsilon=0.0, capacity=capacity)
                mse_v = F.mse_loss(x_rec,batch)
                if _HAS_LPIPS:
                    lp_v = percept(denorm(x_rec).float(), denorm(batch).float()).mean()
                    recon_v = 0.7*mse_v + 0.3*lp_v
                else:
                    recon_v = mse_v
                kld_v = kld_gaussian_standard(model.enc.last_mu, model.enc.last_logvar)
                loss_v = recon_v + kl_weight_sched(epoch) * kld_v
            val_loss += float(loss_v.item())*batch.size(0)
    val_loss/=max(1,len(val_ds))

    loo_probe_contrib(model, stats, tau=tau, capacity=compute_capacity(64, model.moe.num_experts(), cfg.top_k), percept=percept)

    share_vec, hhi = share_hhi_from_usage(stats.usage_ema)
    note0 = maybe_spin_or_prune(epoch, model, stats, share_vec, hhi)
    note1 = maybe_growth(epoch, model, stats, share_vec)
    note2 = maybe_eviction(epoch, model, stats)
    if any([note0, note1, note2]):
        print(f"[Structure] {note0} {note1} {note2} | Experts={model.moe.num_experts()}")

    save_samples(epoch, model)
    torch.save({
        "epoch": epoch,
        "model": model.state_dict(),
        "optimizer": opt.state_dict(),
        "stats": {
            "usage_ema": stats.usage_ema.detach().cpu().tolist(),
            "contrib_ema": stats.contrib_ema.detach().cpu().tolist(),
            "fail_epochs": stats.fail_epochs.detach().cpu().tolist(),
            "ever_used": stats.ever_used.detach().cpu().tolist(),
            "adapt_usage_ema": stats.adapt_usage_ema.detach().cpu().tolist(),
            "adapt_fail_epochs": stats.adapt_fail_epochs.detach().cpu().tolist(),
            "evicted_total": stats.evicted_total,
        },
            "config": cfg.__dict__,
    }, os.path.join(cfg.out_ckpt_dir, f"epoch_{epoch:03d}.pt"))

    entropy_mean = ent_sum/max(1,ent_cnt)
    cap_hit_rate = cap_hits/max(1,cap_tot)
    summarize_epoch(epoch, model, stats,
                    train_loss=running/len(train_loader), val_loss=val_loss,
                    share=share_vec, hhi=hhi, entropy_mean=entropy_mean, cap_hit_rate=cap_hit_rate,
                    active_experts_epoch=active_experts_epoch)

print("end")

model.eval()
with torch.no_grad(), torch.amp.autocast("cuda", enabled=cfg.amp):
     n = 16
     z0 = torch.randn(n, cfg.z_dim, device=device)
     capacity = compute_capacity(n, model.moe.num_experts(), cfg.top_k)
     z_moe, probs, used_mask, aidx, aw, cap_hit, ev_e, ev_a = model.moe(
         z0, top_k=cfg.top_k, tau=1.0, epsilon=0.0, capacity=capacity
     )
     x = model.dec(z_moe)
     grid = make_grid(denorm(x), nrow=cfg.sample_rows)
     save_image(grid, os.path.join(cfg.out_samples_dir, f"gen_{int(time.time())}.png"))
print("end img")
