class SceneTriple():

    def __init__(self, subject_name, sxmin, symin, sxmax, symax, predicate, object_name, oxmin, oymin, oxmax, oymax):
        self.subject = SceneObject(subject_name, sxmin, symin, sxmax, symax)
        self.predicate = predicate
        self.object = SceneObject(object_name, oxmin, oymin, oxmax, oymax)

    @classmethod
    def from_desc(cls, subject_name, predicate, object_name):
        return cls(
            subject_name, 0, 0, 0, 0,
            predicate,
            object_name, 0, 0, 0, 0
        )

    def __hash__(self):
        """Should only check on S, P, O, but not other variables"""
        return hash((self.subject, self.predicate, self.object))

    def __str__(self):
        return f"{self.subject} {self.predicate} {self.object}"


class SceneObject():

    def __init__(self, name, xmin, ymin, xmax, ymax):
        self.name = name
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    @classmethod
    def from_centre(cls, name, centre_x, centre_y, w, h):
        return cls(
            name,
            centre_x - w / 2,
            centre_y - h / 2,
            centre_x + w / 2,
            centre_y + h / 2)

    @classmethod
    def from_desc(cls, name):
        """
        Creates object without position
        """
        return cls(name, 0, 0, 0, 0)

    def __hash__(self):
        """Should only check on S, P, O, but not other variables"""
        return hash((self.name, self.xmin, self.ymin, self.xmax, self.ymax))

    def __str__(self):
        return f"{self.name}"

    def within(self, a):
        """
        Returns true if object is inside tuple a = (xmin, ymin, xmax, ymax), else false
        """
        return self.xmin > a[0] and self.ymin > a[1] and self.xmax < a[2] and self.ymax < a[3]

    def approximately_same(self, a, epsilon_coef):
        """
        Returns true if a has the same name and is within epsilon_coef * 100 pahcent of a's box
        """
        if self.name == a.name:
            return (abs(1 - (self.xmin / a.xmin)) < epsilon_coef) and \
                   (abs(1 - (self.ymin / a.ymin)) < epsilon_coef) and \
                   (abs(1 - (self.xmax / a.xmax)) < epsilon_coef) and \
                   (abs(1 - (self.ymax / a.ymax)) < epsilon_coef)
        else:
            return False


def test_approximately_same():
    phoneA = SceneObject("phone", 399.01727294921875, 159.24984741210938, 462.11737060546875, 212.27130126953125)
    phoneB = SceneObject("phone", 404.1158142089844, 150.51731872558594, 465.4749450683594, 208.5876007080078)
    desk = SceneObject("phone", 329.4053649902344, 189.73760986328125, 423.2495422363281, 230.81634521484375)

    print(phoneA.approximately_same(phoneB, 0.1))  # Should return true
    print(phoneA.approximately_same(desk, 0.1))  # Should return false


if __name__ == "__main__":
    test_approximately_same()
