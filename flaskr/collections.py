
class DBItems:
    '''
    Contains List of model and photo team members and also overrides the __iter__() function.
    '''
    def __init__(self):
        self._modelMembers = list()
        self._photoMembers = list()
        self._videoMembers = list()
        self._siteMembers = list()

    def addModelMembers(self, members):
        self._modelMembers += members

    def addPhotoMembers(self, members):
        self._photoMembers += members

    def addVideoMembers(self, members):
        self._videoMembers += members

    def addSiteMembers(self, members):
        self._siteMembers += members

    def __iter__(self):
        ''' Returns the Iterator object '''
        return DBItemsIterator(self)
    
    def __len__(self):
        return len(self._modelMembers) + len(self._photoMembers) + len(self._videoMembers) + len(self._siteMembers)
   

class DBItemsIterator:
    """Iterator class"""
    def __init__(self, thms):
        # DBItems object reference
        self._thms = thms
        # member variable to keep track of current index
        self._index = 0

    def __next__(self): # model photo video site
        """Returns the next value from team object's lists """
        if self._index < (len(self._thms._modelMembers) + len(self._thms._photoMembers) + len(self._thms._videoMembers) + len(self._thms._siteMembers)) :
            if self._index < len(self._thms._modelMembers): # Check if model members are fully iterated or not
                result = (self._thms._modelMembers[self._index] , 'model')
            elif self._index < (len(self._thms._modelMembers) + len(self._thms._photoMembers)):
                result = (self._thms._photoMembers[self._index - len(self._thms._modelMembers)]   , 'photo')
            elif self._index < (len(self._thms._modelMembers) + len(self._thms._photoMembers) + len(self._thms._videoMembers)):
                result = (self._thms._videoMembers[self._index - (len(self._thms._modelMembers) + len(self._thms._photoMembers))]   , 'video')
            else:
                result = (self._thms._siteMembers[self._index - (len(self._thms._modelMembers) + len(self._thms._photoMembers) + len(self._thms._videoMembers))]   , 'site')
            self._index +=1
            return result
        # End of Iteration
        raise StopIteration



# just testing

# if __name__ == "__main__":
    
#     # Create team class object
#     team = DBItems()
#     # Add name of model team members
#     team.addModelMembers( [ {'href':'SamA', 'src':'JohnA', 'name':'MarshalA'},{'href':'SamB', 'src':'JohnB', 'name':'MarshalB'},{'href':'SamC', 'src':'JohnC', 'name':'MarshalC'} ] )
#     # Add name of photo team members
#     team.addPhotoMembers( [ {'href':'Riti', 'src':'Rani', 'name':'Aadi'}, 'photo2', 'photo3' ] )
#     team.addVideoMembers( [ {'href':'RitiV', 'src':'RaniV', 'name':'AadiV'}, 'video2' ] )
#     team.addSiteMembers( [ {'mlen':'RitiS', 'href':'RaniS', 'src':'AadiS', 'name':'SamS'}, 'site2' ] )

#     # Get Iterator object from Iterable Team class object
#     iterator = list(team)

#     for elem in iterator[2:9]:
#         print(elem)

    # Iterate over the team object using iterator
    #while True:
    #    try:
            # Get next element from TeamIterator object using iterator object
    #        elem = next(iterator)
            # Print the element
    #        print(elem)
    #    except StopIteration:
    #        break
