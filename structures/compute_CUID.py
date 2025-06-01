import uuid
class SceneTriple():

    def __init__(self, subject_name, sxmin, symin, sxmax, symax, predicate, object_name, oxmin, oymin, oxmax, oymax):
        self.subject = SceneObject(subject_name, sxmin, symin, sxmax, symax)
        self.predicate = predicate
        self.object = SceneObject(object_name, oxmin, oymin, oxmax, oymax)

    
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


class SceneObject:

    def __init__(self, name, xmin, ymin, xmax, ymax):      #added position
        self.name = name
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.pos = None
        self.cuid = "hallo"
    

    def get_cuid (self):
        id = str(uuid.uuid4())[0:4]
        self.cuid = f"{self.name}_{id}"
        return self.cuid
    
    def get_cuid_details (self):
        characteristics_dict = dict()
        for i in self.__dict__.items():
            print("{}:{}".format(i[0], i[1]))
            characteristics_dict.update({i[0]:i[1]})
        print(hash(frozenset(characteristics_dict.items())))
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

    def approximately_same(self, a, epsilon):
        """
        Returns true if a has the same name and is within epsilon_coef * 100 pahcent of a's box
        """
        box_similarity_weight = 0.9 
        if self.name == a.name:
            diff = 1 - box_similarity_weight*self.box_similarity(a)
            return diff < epsilon
        else:
            return False

    def box_similarity(self, other):
        """
        Returns fraction of overlap with other to own box. 1 if perfect overlap, 0 if no overlap
        """
        a_self = (self.xmax - self.xmin) * (self.ymax - self.ymin)
        a_other = (other.xmax - other.xmin) * (other.ymax - other.ymin)
        overlap = max(min(self.xmax, other.xmax) - max(self.xmin, other.xmin), 0) * \
                  max(min(self.ymax, other.ymax) - max(self.ymin, other.ymin), 0)

        if a_self > a_other:
            return overlap / a_self
        else:
            return overlap / a_other

    def box_overlap(self, other):
        """
        Returns fraction of overlap with other to own box. 1 if perfect overlap, 0 if no overlap
        """
        a_self = (self.xmax - self.xmin) * (self.ymax - self.ymin)
        overlap = max(min(self.xmax, other.xmax) - max(self.xmin, other.xmin), 0) * \
                  max(min(self.ymax, other.ymax) - max(self.ymin, other.ymin), 0)
        return overlap /a_self
    
    def calculate_similarity(self, alpha, f, t, framegraph):
        """
        Calculate a similarity score between elements based on neighbor matches, bounding box similarity, and name similarity.
    
        Parameters:
        alpha (float): The weighting factor for neighbor similarity (0 <= alpha <= 1).
        f: The source element to calculate similarity from.
        t: The target element to calculate similarity to.
        framegraph: A graph representing the frames.
    
        Returns:
        float: The calculated similarity score.
        """

        # Initialize neighbor similarity and neighbor matches count
        neigh_similarity = 0
        neighbor_matches = 0
        # Get the number of neighbors for the target element
        n_neighbours = len(self.g[t])
        # Calculate neighbor similarity
        if n_neighbours > 0:
            for nt in self.g[t]:
                for nf in framegraph.g[f]:
                    if self.g.nodes[nt]["content"].name == nf.name:
                        neighbor_matches += 1
            neigh_similarity = neighbor_matches / len(self.g[t])

        # Compare bounding box similarity
        spat_similarity = f.box_similarity(self.g.nodes[t]["content"])

        # Compare name similarity
        n_similarity = name_similarity(f.name, self.g.nodes[t]["content"].name)

        # Calculate the final similarity score 
        similarity = (alpha * neigh_similarity + (1 - alpha) * spat_similarity + n_similarity) / 2
        return similarity


def test_approximately_same():
    # for the given example, the box similarity weight should be at least 0.9
    phoneA = SceneObject("phone", 399.01727294921875, 159.24984741210938, 462.11737060546875, 212.27130126953125)
    phoneB = SceneObject("phone", 404.1158142089844, 150.51731872558594, 465.4749450683594, 208.5876007080078)
    desk = SceneObject("phone", 329.4053649902344, 189.73760986328125, 423.2495422363281, 230.81634521484375)

    print(phoneA.approximately_same(phoneB, 0.3), " with ", 1- phoneA.box_similarity(phoneB))  # Should return true
    print(phoneA.approximately_same(desk, 0.3), " with ", 1-phoneA.box_similarity(desk))  # Should return false
    print(phoneA.get_cuid_details())
    print(phoneB.get_cuid())


def test_box_overlap():
    a = SceneObject("a", 399, 159, 462, 212)
    b = SceneObject("a", 400, 200, 500, 250) # partially overlapping
    c = SceneObject("a", 464, 214, 500, 300) # no overlapping parts
    print(a.box_similarity(a)) # should be 1
    print(a.box_similarity(b))  # should be 0 < x < 1
    print(a.box_similarity(c))  # should be 0


if __name__ == "__main__":
     test_approximately_same()
    #test_box_overlap()
