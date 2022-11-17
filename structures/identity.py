from structures.scene import *


class Fingerprint:

    def __init__(self, subject, anchors, identifier):
        self.subject = subject
        self.anchors = set(anchors)
        self.identifier = identifier

    def __str__(self):
        return f"{self.identifier} ({self.subject}) with {len(self.anchors)} anchor(s)"

    def similarity(self, other, ):
        """
        Measures similarity between this fingerprint and another.
        0 is no similarity, 1 is identical
        """
        sim_score = 0
        if self.subject.name == other.subject.name and len(other.anchors) * len(self.anchors) != 0:
            # mutual_anchors = self.anchors.intersection(other.anchors)
            mutual_anchors = []
            # Currently, we only check for same class (name) of objects
            for a in self.anchors:
                for b in other.anchors:
                    if a.name == b.name:
                        mutual_anchors.append(a)
            sim_score = len(mutual_anchors) / max(len(self.anchors), len(other.anchors))
        return sim_score



class TemporalFingerprint:

    def __init__(self, identifier):
        self.identifier = 


def test_similarity():
    """
    This method is for testing.
    The fingerprint violates the condition that fingerprint.subject == fingerprint.anchors[x].subject for all x
    """
    phone1 = SceneObject.from_desc("phone")
    keyboard1 = SceneTriple.from_desc("keyboard", "on", "desk")
    desk1 = SceneTriple.from_desc("desk", "has", "keyboard")
    screen1 = SceneTriple.from_desc("screen", "on", "desk")
    cup1 = SceneTriple.from_desc("cup", "on", "desk")
    template = Fingerprint(phone1, [keyboard1, desk1, screen1], "Donald's phone")
    perfectMatch = Fingerprint(phone1, [keyboard1, desk1, screen1], "")  # identical
    missingMatch = Fingerprint(phone1, [keyboard1, desk1], "")  # screen1 is missing
    surplusMatch = Fingerprint(phone1, [keyboard1, desk1, screen1, cup1], "")  # one object too much
    missingSurplusMatch = Fingerprint(phone1, [keyboard1, desk1, cup1], "")  # one missing and one too much

    print(template.similarity(perfectMatch), " should be 1")
    print(template.similarity(missingMatch), " should be lower than 1")
    print(template.similarity(surplusMatch), " should be lower than 1, but higher than previous")
    print(template.similarity(missingSurplusMatch), " should be lower than 1")


if __name__ == "__main__":
    test_similarity()
