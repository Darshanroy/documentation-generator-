import re

class GitHubUrlParser:
    """
    A class to parse GitHub URLs and extract the combined output as 'username/repository-name'.
    """
    def __init__(self, url):
        """
        Initializes the parser and extracts the result automatically.
        
        Args:
            url (str): The GitHub URL to parse.
        """
        self.url = url
        self.result = None
        self._parse()  # Automatically parse the URL on initialization

    def _parse(self):
        """
        Internal method to extract and format the result as 'username/repository-name',
        ensuring '.git' is removed if present.
        """
        pattern = r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$"
        match = re.match(pattern, self.url)
        if match:
            self.result = f"{match.group(1)}/{match.group(2)}"
        else:
            raise ValueError("Invalid GitHub URL format")

    def get_result(self):
        """
        Returns the formatted result as 'username/repository-name'.
        
        Returns:
            str: The formatted result.
        """
        return self.result

# Example usage
if __name__ == "__main__":
    try:
        url = input("Enter a GitHub URL: ").strip()
        parser = GitHubUrlParser(url)  # Automatically parses the URL
        print(parser.get_result())  # Output is in 'username/repository-name' format
    except ValueError as e:
        print(e)
