# HiClip

## Installation
hiclip can be installed using pip.
``` bash
pip install hiclip
```
Then, install the appropriate version of PyTorch. After experimental verification, hiclip works well in the environment of pytorch 2.0.1 + CUDA 11.7.
``` bash
# This is just an example, you can find the appropriate version in https://pytorch.org/get-started/previous-versions/
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2
```

## Tutorial
### generate train dataset
```python
import hiclip


# uri also support .cool file
dataset = hiclip.setup_data(
    main_cooler_uri="main/K562.mcool::/resolutions/5000",
    sub_cooler_uri="sub/K562.mcool::/resolutions/5000",
    target_cooler_uri="target/K562.mcool::/resolutions/5000",
)
dataset.write(filename="dataset", compression="gzip")
```
### train
```python
import anndata
import hiclip


dataset = anndata.read_h5ad("dataset")
hiclip.HiClip.setup_anndata(dataset)
model = hiclip.HiClip(dataset)

model.train(
    max_epochs=200,
    save_ckpt_every_n_epoch=2,
    plan_kwargs={"lr": 1e-3, "weight_decay": 0},
    batch_size=4,
    num_workers=16,
)
```
### predict or observe
```python
import anndata
import hiclip


dataset = anndata.read_h5ad("dataset")
model = hiclip.HiClip.load(
    ".hiclip/202X-XX-XX_XX-XX-XX_val_hiclip_metric/epoch=...",
    dataset
)

# if predict
pred: anndata.AnnData = model.predict(dataset)
# if observe
pred = model.observe(main_cooler_uri, sub_cooler_uri, chrom, start, end)
```

**The specific case is in the examples folder.**