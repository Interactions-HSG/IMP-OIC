import subprocess


def main():
    generate_scene_graph("RelTR", "RelTR/demo/vg1.jpg", "graph.json")


def generate_scene_graph(reltr_path, img_path, graph_path, device="cpu"):
    subprocess.check_output([f'python',
                             f"{reltr_path}/mkgraph.py",
                             "--img_path", f"{img_path}",
                             "--device", f"{device}",
                             "--resume", f"{reltr_path}/ckpt/checkpoint0149.pth",
                             "--export_path", f"{graph_path}"])


if __name__ == "__main__":
    main()
