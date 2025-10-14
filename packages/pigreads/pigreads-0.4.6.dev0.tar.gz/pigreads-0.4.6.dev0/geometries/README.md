# Geometries

This folder contains geometries in the
[compressed NumPy NPZ format](https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html),
i.e. a ZIP-archive of N-dimensional arrays in NPY format:

- `header`: metadata for the geometry encoded as a string in the
  [YAML](https://yaml.org/) format
- `inhom`: 3D integer array (shape: Nz, Ny, Nx) encoding the domain and regions
  in the geometry
- `fibres`: 4D float array (shape: Nz, Ny, Nx, 3) of the fibre direction
