class Segment():
    def __init__(self,
                 length,
                 min_angle, max_angle,
                 initial_angle
                 ):
        self.length = length
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.angle = initial_angle

    def move(self, new_angle):
        if self.min_angle <= new_angle <= self.max_angle:
            self.angle = new_angle
        else:
            raise ValueError('Angle out of range')


class Arm:
    def __init__(self, numberofsegments, segmentlength=[], jointangles=[], baserotation=0):
        self.segments = [Segment(segmentlength[i]) for i in range(numberofsegments)]
        self.numberofsegments=numberofsegments
        self.jointangles = jointangles
        self.baserotation = baserotation
        self.jointnonrelativeangles = [0 for i in range(self.numberofsegments)]

    def getangle(self, segmentnumber):
        return self.segments[segmentnumber].angle
