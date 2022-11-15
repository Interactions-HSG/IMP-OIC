

def get_reltr(reltr_path, img_path, graph_path, device="cpu", topk=5):
    subprocess.check_output([f'python',
                                f"{reltr_path}/mkgraph.py",
                                "--img_path", f"{img_path}",
                                "--device", f"{device}",
                                "--resume", f"{reltr_path}/ckpt/checkpoint0149.pth",
                                "--export_path", f"{graph_path}",
                                "--topk", f"{topk}"])

def get_yolo(yolo_path, img_path, out_path, threshold=0.5):
    # TODO: implement call to yolo
    subprocess.check_output(f'./darknet', 'detector', 'demo',
                                f"{}")