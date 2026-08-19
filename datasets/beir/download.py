import os
from beir import util


# The core public open-source BEIR datasets
beir_datasets = [
    "scifact", "trec-covid", "nfcorpus", "fiqa", "arguana", 
    "scidocs", "quora", "dbpedia-entity", "fever", "climate-fever",
    "hotpotqa", "nq", "msmarco"  # Warning: msmarco is very large!
]

for dataset in beir_datasets:
    out_dir = os.path.join(os.getcwd(), "datasets")
    url = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{}.zip".format(dataset)
    if os.path.exists(os.path.join(out_dir, dataset)):
        print(f"SKIPPING: {dataset} already exists")
        continue
    data_path = util.download_and_unzip(url, out_dir)
    print("Dataset downloaded here: {}".format(data_path))