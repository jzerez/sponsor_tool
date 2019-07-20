class Website:

    def __init__(self, url):
        self.url = url;
        self.email_sent = False;
        self.distance = None;
        self.type = None;
        self.supports_education = None;

    def make_graph(self):
        # Populates the graph of the website
        pass

    def find_dist(self):
        # Tries to find the distance of the company relative to Olin
        pass

    def get_summary(self):
        # Queries wikipedia for company value on the DJI
        pass

    def parse_text(self):
        # Parses the text found in the graph
        self.find_industry();
        self.find_educational_support();
        pass

    def find_industry(self):
        # Guesses Industry from text
        pass

    def find_educational_support(self):
        # Guesses educational support values from text
        pass
