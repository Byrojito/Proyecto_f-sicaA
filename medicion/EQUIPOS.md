# Equipos de medición

Hardware con el que se tomaron (o se tomarán) las mediciones. Los datos de Felipe y Alejandra salen de los
encabezados de sus registros de HWiNFO; los de Samuel, del inventario de Windows.

| | Felipe | Alejandra | Samuel (1) | Samuel (2) |
| --- | --- | --- | --- | --- |
| **Equipo** | ASUS TUF Gaming F15 (FX506LHB) | ASUS VivoBook 15 (X513EA) | Lenovo ThinkPad T14 Gen 2 (20W1SF0200) | HP OMEN Transcend 14 |
| **CPU** | Intel Core i5-10300H | Intel Core i5-1135G7 | Intel Core i7-1185G7 | Intel Core Ultra 7 155H |
| **Núcleos / hilos** | 4 / 8 | 4 / 8 | 4 / 8 | 16 / 22 |
| **RAM** | 8 GB | 8 GB | 32 GB | 16 GB |
| **GPU dedicada** | NVIDIA GeForce GTX 1650 | — (Intel Iris Xe) | — (Intel Iris Xe) | NVIDIA GeForce RTX 4060 Laptop |
| **Disco** | NVMe Micron 2210, 512 GB | NVMe Intel 660p, 512 GB | NVMe SK hynix, 512 GB | NVMe KIOXIA, 1 TB |
| **Sistema** | Windows | Windows | Windows 11 Pro | Windows 11 Home |
| **Medición de CPU** (`benchmark.py`) | Silencio, Rendimiento, Turbo | Silencio, Rendimiento | Pendiente (dos modos) | — |
| **Medición de GPU** (`gpu_benchmark.py`) | Hecha (GTX 1650, hashcat 8.0) | No tiene GPU NVIDIA | No tiene GPU NVIDIA | Pendiente (RTX 4060) |

La RAM es la que reporta Windows como instalada, redondeada. Los equipos sin GPU NVIDIA no pueden correr
`gpu_benchmark.py`, porque el script lee la GPU con `nvidia-smi`.
