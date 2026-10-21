# Install the preserved visual_search version

This branch preserves the installed LabelImg++ 3.0.0rc0 source, based on upstream
commit `05d8b02b883a085eb69899953ba7e2239a158870`. The fork's `master` contains a
newer application generation; use `visual-search-installed` for this version.

## Another Windows device

```powershell
conda create -n labelimg-custom python=3.12.12 pip -y
conda activate labelimg-custom
git clone --branch visual-search-installed --single-branch https://github.com/erfanakk/labelImg-plus-plus.git
cd labelImg-plus-plus
python -m pip install -r requirements/requirements-visual-search.txt
python -m pip install .
labelimgplusplus
```

For an immutable installation, replace the branch with the full commit ID shown
by `git rev-parse HEAD` after cloning. A built wheel can also be installed with
`python -m pip install path/to/labelimgplusplus-3.0.0rc0-py3-none-any.whl`.
Install the pinned requirements first if matching the base dependency versions.

The compiled `libs/resources.py` is intentionally included so installation does
not require a separate `pyrcc5` step. If changing icons or translations, regenerate
it with `pyrcc5 -o libs/resources.py resources.qrc` and commit that file explicitly.

## Preserved changes

- Label font and outline width controls, visible labels, high-contrast label
  backgrounds, rectangle-center marker, per-class counts and selection feedback.
- Dataset class loading and the customized packaged class list.
- `0` to delete a selected annotation and `Alt+C` to edit its label, including
  migration from the original shortcut values.
- Autosave/navigation startup guards and stale-selection handling.
- Image deletion also removes its individual annotation file; shared
  `annotations.json` is retained. This is existing customized behavior.
- Crisp rendering at native zoom and above.
- Legacy flat `libs/*.py` files present in the environment, including the old
  canvas's direct right-drag Move modification. The current application imports
  `libs.widgets.canvas`; the legacy canvas change does not change that widget.

74 runtime source/data files were copied byte-for-byte from the installed
environment. Backups, caches, datasets and model weights were excluded.
The installed shape module includes the center-marker change absent from the
older local project copy, so the installed version is authoritative.
The local project's additional SAM `predict_box` method is outside the installed
package snapshot and is not applied here.

Use a dedicated environment: the separate `labelImg` package shares the `libs`
namespace and installing/uninstalling it can overwrite these modules. Launch
outside folders containing another `libs` tree to avoid import shadowing.

User preferences in `~/.labelImgSettings.json`, recent paths, datasets, optional
SAM models and GPU packages are not embedded in the repository. Configure those
on the new device. For optional ONNX SAM dependencies, use
`python -m pip install ".[sam]"`; model files still need separate configuration.

## Validation

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
python -m pytest tests/integration/test_local_customizations.py -q
python -X utf8 -m unittest discover -s tests -t .
python -m build --wheel
```

The unittest command is the Windows equivalent of this revision's `make test`.
UTF-8 mode avoids a pre-existing Unicode console-print failure on Windows.
GUI interaction and optional SAM inference on the other device require testing
there; matching source does not guarantee identical drivers, fonts or Qt scaling.

On the migration machine, the complete pytest run reported 678 passed and one
skipped, then the interpreter exited with Windows access violation `0xC0000005`
during shutdown. The five focused customization tests and the separate installed
wheel startup check exited successfully. Treat full-suite shutdown as unresolved.
