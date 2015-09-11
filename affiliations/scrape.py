from bs4 import BeautifulSoup
from affiliations.models import Article, Author, Address, Affiliation
from affiliations.exceptions import AddressParsingError, AuthorParsingError
from datetime import date

class Scraper():
    """
    Base class for scraping JATS XML files
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.soup = self.make_soup(filepath)
         
    def make_soup(self, filepath):
        with open(filepath, 'rb') as f:
            soup = BeautifulSoup(f, "xml", from_encoding='utf-8')
        return soup
        
    def parse(self):
        raise NotImplementedError
        
class Plos(Scraper):
    """
    Generic Scraper for Plos XML
    """
    def parse(self):
        article = self.parse_article(self.soup)
        self.address_lookup = self.parse_addresses(self.soup, article)
        authors = self.parse_authors(self.soup, article)
        for author, affs in authors.iteritems():
            for aff in affs:
                if aff and self.address_lookup:
                    Affiliation.create(author = author,
                                   address = self.address_lookup.get(aff))

        if article.corresponding_authors().count() == 0 and article.authors.count() == 1:
            lone_author = article.authors[0]
            lone_author.corresponding = True
            lone_author.save()
        return article
                                   


    def parse_article(self, soup):
        """
        Parse article metadata and create Article record
        """

        title_tag = soup.find("article-title")
        article_tag = soup.find("article")
        journal_tag = soup.find("journal-id", attrs={"journal-id-type" : "nlm-ta"})
        doi_tag = soup.find("article-id", attrs={"pub-id-type" : "doi"})
        pmid_tag = soup.find("article-id", attrs={"pub-id-type" : "pmid"})
        date_tag = soup.find("pub-date", attrs={"pub-type" : "epub"})
        related_article = soup.find("related_article")
        if related_article:
            related_article = related_article["xlink:href"]
        
        title = title_tag.get_text()
        doi = doi_tag.text
        if pmid_tag:
            pmid = pmid_tag.text
        else:
            pmid = None
        article_type = article_tag["article-type"]
        
        # 2003-2004 Bio and Med article synopses and correspondence are registered as 
        # research-articles in some cases and "other" in later years
        subject = soup.find("subject", text=["Synopsis", 
                                             "Correspondence", 
                                             "Feature",
                                             "Journal Club",
                                             "Community Page",
                                             "Essay",
                                             "Book Reviews/Science in the Media",
                                             "Unsolved Mystery",
                                             "Primer",
                                             "Correspondence and Other Communications",
                                             "Message from PLoS",
                                             "Editorial",
                                             "Obituary",
                                             "Message from the Founders",
                                             "Research in Translation",
                                             "Perspectives"
                                             "The PLoS Medicine Debate",
                                             "Policy Platform"])
        if subject and (article_type == "research-article" or
                         article_type == "other"):
            article_type = "plos/%s" % (subject.text.lower())
        journal = journal_tag.text
        pubdate = date(
                    int(date_tag.find("year").text),
                    int(date_tag.find("month").text),
                    int(date_tag.find("day").text)
                    )
        
        article = Article.create_or_update_by_doi(
                                                    { "title" : title,
                                                      "doi" : doi,
                                                      "pmid" : pmid,
                                                      "date_published" : pubdate,
                                                      "article_type" : article_type,
                                                      "journal" : journal,
                                                      "filename" : self.filepath,
                                                      "related_article" : related_article
                                                    }
                                                )

        return article

    def parse_addresses(self, soup, article):
        """
        Parse institutional addresses from the affiliations field
        """
        addresses = soup.find_all("aff")
        # If there are no addresses return None TODO Build proper exceptions
        if addresses == []:
            return None
        address_lookup = {}
        for address in addresses:
            try:
                affiliation_id = address["id"]
                if affiliation_id.startswith("edit"):
                    continue
                elements = address.find_all(True, text=True)
                address_text = [elem.text for elem in elements if (
                                                 elem.name != 'bold' and
                                                 elem.name != 'label')
                                    ]
                address_raw = ", ".join(i for i in address_text)
                if address_raw == "":
                    address_raw = address.find_all(text=True, recursive=False)[0]
            
            except (KeyError, IndexError) as e:
                if len(address.contents) == 1 and address.contents[0] == address.text:
                    address_raw = address.text
                    affiliation_id = 1
                else:
                    raise AddressParsingError, \
                        """Address tag not parsed for {0}
    Original error: {1}
    Original information: {2}""".format(self.filepath, type(e), e.args)
            
            country_raw = address_raw.split(", ")[-1]
            
            address = Address.create(article = article,
                                     affiliation_id = affiliation_id,
                                     address_raw = address_raw,
                                     country_raw = country_raw)
            address_lookup[affiliation_id] = address
            
        return address_lookup       

    def parse_authors(self, soup, article):
        author_tags = soup.find_all("contrib", attrs = {"contrib-type" : "author"})
        authors = {}
        for auth in author_tags:
            print soup
            try:
                surname = auth.find("surname").text
                given_names = auth.find("given-names").text
                affiliation_tags = auth.find_all("xref", attrs = {"ref-type" : "aff"})
                affiliation_refs = [aff["rid"] for aff in affiliation_tags]
                if self.address_lookup and affiliation_tags == []:
                    if 1 in self.address_lookup:
                        affiliation_refs = [1] #One address, no affiliation indices
                    elif 'aff1' in self.address_lookup:
                        affiliation_refs = ['aff1'] #Only one index on final author
            except AttributeError, e:
                collab = auth.find("collab")
                if collab:
                    surname = collab.text
                    given_names = None
                    affiliation_refs = [None]
                else:
                    raise AuthorParsingError, \
                        """Author tag not parsed for {0}
    Original error: {1}
    Original information: {2}""".format(self.filepath, type(e), e.args)
            
            if len(auth.find_all("xref", attrs = {"ref-type" : "corresp"})) > 0:
                corresponding = True
            else:
                try: 
                    if auth["corresp"] == "yes":
                        corresponding = True
                except KeyError:
                    corresponding = False
                
            author = Author.create(
                                        **{ "surname" : surname,
                                          "given_names" : given_names,
                                          "corresponding" : corresponding,
                                          "affiliation_refs_raw" : affiliation_refs,
                                          "article" : article
                                        }
                                    )
        
            authors[author] = affiliation_refs
            
        return authors    
