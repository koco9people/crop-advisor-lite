# AMD Compute Evidence

[`amd_compute_evidence.ipynb`](amd_compute_evidence.ipynb) demonstrates that Crop Advisor
Lite's workflow runs on **AMD Instinct GPU compute**, executed on the **AMD Developer
Cloud** (AMD Hackathon: ACT II).

The notebook:

1. Prints the AMD GPU via `rocm-smi` (hardware proof).
2. Confirms PyTorch sees the AMD GPU through ROCm.
3. Runs a timed matrix multiply on the AMD Instinct GPU (real FLOPs on AMD silicon).
4. Runs the project's **retrieval-embedding step on the AMD GPU** — loading an open-weight
   embedding model and embedding the 40-document Pakistani-agriculture corpus, then running
   a semantic search. This is Crop Advisor Lite's real next step (BM25 → dense embeddings),
   computed on AMD hardware.

Together with the app's inference path (`gpt-oss-120b` served on AMD via the Fireworks AI
API), the whole pipeline runs on AMD compute.

## How to run it

On an AMD Developer Cloud GPU pod (Jupyter):

```bash
git clone https://github.com/koco9people/crop-advisor-lite.git
```

Open `notebooks/amd_compute_evidence.ipynb` and **Run All**. The executed notebook in this
folder (with outputs) and `amd-pod-screenshot.png` are the committed evidence that it ran on
AMD hardware.
