

def main():
    templates, templates_classes = import_fingerprints("templates/obj_templates.json")
    template_similarity_thresh = 0.5

    tracked = []

    generator = FrameGenerator(sample=1)
    # while we receive frames
    while(generator.has_next):




if __name__ == "__main__":
    main()