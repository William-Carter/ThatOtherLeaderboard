import cobble.validations
import regex as re
import databaseManager as dbm
import durations

class IsCategory(cobble.validations.Validation):
    categories = ["oob", "inbounds", "legacy", "unrestricted", "glitchless"]
    def __init__(self):
        """
        Validate that an argument is a valid TOL category
        """
        super().__init__()
        self.requirements = "Must be one of: "
        for category in self.categories:
            self.requirements += f"{category}, "
        self.requirements = self.requirements[:-2] # remove trailing comma and space


    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it matches any of the predefined categories
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string is a valid category
        """
        return (x.lower() in self.categories)

class IsILCategory(cobble.validations.Validation):
    categories = ["oob", "inbounds", "glitchless"]
    def __init__(self):
        """
        Validate that an argument is a valid TOL category
        """
        super().__init__()
        self.requirements = "Must be one of: "
        for category in self.categories:
            self.requirements += f"{category}, "
        self.requirements = self.requirements[:-2] # remove trailing comma and space


    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it matches any of the predefined categories
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string is a valid category
        """
        return (x in self.categories)
    


class IsMap(cobble.validations.Validation):
    categories = ["oob", "inbounds", "glitchless"]
    def __init__(self):
        """
        Validate that an argument is a valid TOL category
        """
        super().__init__()
        self.requirements = "Must be a valid map or level name"


    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it matches any of the predefined categories
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string is a valid category
        """
        return (x in dbm.levelNames.keys() or x in dbm.levelNames.values())


class IsDuration(cobble.validations.Validation):
    def __init__(self):
        super().__init__()
        self.requirements = "Must be a valid amount of time i.e. 47.5, 1:30, 1:17:27.33"

    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it can be parsed into a number of seconds
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string was successfully parsed
        """
        try:
            seconds = durations.seconds(x)
        except:
            return False
        else:
            return True


class IsSetupElement(cobble.validations.Validation):
    def __init__(self):
        super().__init__()
        self.requirements = "Must be one of: "
        
        for element in ["sensitivity", "mouse", "keyboard", "dpi", "hz"]:
            self.requirements += f"{element}, "
        self.requirements = self.requirements[:-2] # remove trailing comma and space

    def validate(self, x: str) -> bool:
        """
        Evaluates a given string to see if it can be parsed into a number of seconds
        Parameters:
            x - The string to be tested
        Returns:
            valid - Whether the string was successfully parsed
        """
        return (x in SetupCommand.capitalisations.keys())
    

class IsNormal(cobble.validations.Validation):
    def __init__(self):
        super().__init__()
        self.requirements = "Don't be an idiot :)"

    def validate(self, x: str):
        bannedChars = r"[@]+|https://|http://"
        if re.search(bannedChars, x):
            return False
        if len(x) > 50:
            return False
        return True

class IsGoldsList(cobble.validations.Validation):
    def __init__(self):
        super().__init__()
        self.requirements = "Must be a list of 18 times, separated by newlines"

    def validate(self, x: str):
        golds = x.split("\n")
        if len(golds) != 18:
            return False
        
        for gold in golds:
            if not IsDuration.validate("", gold):
                return False
        

        return True

